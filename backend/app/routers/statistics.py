"""
API endpoints that return statistics, e.g. cancer incidence/mortality,
or sociodemographic measures.
"""

from enum import Enum
import os
import csv
from io import StringIO, BytesIO
import zipfile

from typing import Optional, Annotated
from fastapi import Depends, Query, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy import func, case
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_cache.decorator import cache

from tools.strings import slugify, slug_modelname_sans_type, sanitize
from tools.accessors import get_or_key, get_keys
from db import get_session

from settings import LIMIT_TO_STATE

from models.base import MeasureUnit
from models import (
    County,
    STATS_MODELS,
    CANCER_MODELS,
    MEASURE_DESCRIPTIONS,
    FACTOR_DESCRIPTIONS
)
from models.scp import SCP_TRENDS_MODELS, TREND_MAP, TREND_MAP_NONE


router = APIRouter(prefix="/stats")


# ============================================================================
# === statistics routes
# ============================================================================

# ----------------------------------------------------------------
# --- general info routes
# ----------------------------------------------------------------

class FIPSValue(BaseModel):
    value: Optional[float]
    aac: Optional[float]

class FIPSMeasureResponse(BaseModel):
    min: Optional[float]
    max: Optional[float]
    unit: Optional[MeasureUnit]
    values: dict[str, FIPSValue]

# provides high-level information about the available categories and measures
# by iterating over the STATS_MODELS dict

class FactorMetaResponse(BaseModel):
    label : str
    default : str | None
    values : dict[str, str]

class MeasuresMetaResponse(BaseModel):
    label: str
    factors: Optional[dict[str, FactorMetaResponse]]

class CategoryMetaResponse(BaseModel):
    label: str
    measures: dict[str, MeasuresMetaResponse]

class StatsMetaResponse(BaseModel):
    label: str
    categories: dict[str, CategoryMetaResponse]

@router.get("/measures", response_model=dict[str, StatsMetaResponse])
@cache()
async def get_measures(session: AsyncSession = Depends(get_session)):
    f"""
    Gets all distinct values of 'measure' for all stats tables.

    If FACTOR_DESCRIPTIONS[model] exists, gets labels and distinct values
    for each factor.
    """

    # stores measures by type (country vs. tract) and table
    all_measures = {}

    for type, models in STATS_MODELS.items():
        all_measures[type] = {
            "label": type.capitalize(),
            "categories": {}
        }

        for model in models:
            simple_model_name = slug_modelname_sans_type(model, type)

            measure_descs = MEASURE_DESCRIPTIONS.get(simple_model_name, {})
            factor_descs = FACTOR_DESCRIPTIONS.get(simple_model_name, {})

            if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
                query = select(model.Site).distinct().order_by(model.Site)
            else:
                query = select(model.measure).distinct().order_by(model.measure)

            # if LIMIT_TO_STATE is not None:
            #     query = query.where(model.State == LIMIT_TO_STATE)

            # query for measure categories within this measure
            result = await session.execute(query)

            async def get_factors_with_values(model, measure):
                """
                Given a model (i.e. measure category) and a measure
                (i.e, a specific value of the 'measure' field within the model),
                produces a dict of factors and their distinct values for that
                measure.
                """

                # run queries for the values of each factor for this model
                factor_results = {}
                for factor in factor_descs:
                    # gets all distinct values for the factor, ordered
                    # alphabetically
                    factor_query = (
                        select(getattr(model, factor).distinct())
                            .order_by(getattr(model, factor))
                    )

                    # further filters down to the measure category, with different
                    # handling for cancer models since they store the measure in
                    # the "Site" column
                    if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
                        factor_query = factor_query.where(model.Site == measure)
                    else:
                        factor_query = factor_query.where(model.measure == measure)

                    factor_results[factor] = await session.execute(factor_query)

                return {
                    f: {
                        "label": str(fv["label"] or f),
                        "default": fv.get("default"),
                        "values": {
                            x: fv.get("values", {}).get(x, x) or x
                            for x in factor_results[f].scalars().all()
                        }
                    }
                    for f, fv in factor_descs.items()
                }

            all_measures[type]["categories"][simple_model_name] = {
                "label": model.Config.label or simple_model_name,
                "measures": {
                    x: {
                        "label": measure_descs.get(x, {}).get('label') or x,
                        "factors": await get_factors_with_values(model, x)
                    }
                    for x in result.scalars().all()
                }
            }

    return all_measures


# provides an overview of values for a specific county

class CountyMeasureValueResponse(BaseModel):
    label: str
    value: Optional[float]
    aac: Optional[float]

class CountyMeasureCategoryResponse(BaseModel):
    label: str
    measures: dict[str, CountyMeasureValueResponse]

class ByCountyResponse(BaseModel):
    FIPS: str
    name: str
    categories: dict[str, CountyMeasureCategoryResponse]

@router.get("/by-county/{county_fips}", response_model=ByCountyResponse)
@cache()
async def get_county_measures(county_fips:str, session: AsyncSession = Depends(get_session)):
    f"""
    For a given county specified by its FIPS, returns all statistics associated
    with the county.
    """

    # store info about measure for the specified county
    county_name = (
        await session.execute(select(County.full).where(County.us_fips == county_fips))
    ).scalar()

    if county_name is None:
        raise HTTPException(
            status_code=404,
            detail=f"County with FIPS {county_fips} not found"
        )

    all_measures = {
        "FIPS": county_fips,
        "name": county_name,
        "categories": {}
    }
    type = "county"

    for model in STATS_MODELS[type]:
        simple_model_name = slug_modelname_sans_type(model, type)
        measure_descs = MEASURE_DESCRIPTIONS.get(simple_model_name, {})

        if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
            query = select(model.Site.label("label"), model.AAR.label("value"), model.AAC.label("aac")).order_by(model.Site)
        else:
            query = select(model.measure.label("label"), model.value).order_by(model.measure)

        # furthermore, limit the query to the specified county
        query = query.where(model.FIPS == county_fips)

        # query for measure categories within this measure
        result = await session.execute(query)

        # process measures for this model, replacing 'label' with a human-readable
        # version from the metadata, if available
        measure_values = {
            x["label"]: {
                **x, # brings in either 'value', or 'value' + 'aac' if it's a cancer/SCP model
                **{ "label": measure_descs.get(x["label"], {}).get('label') or x["label"] }
            }
            for x in result.all()
        }

        all_measures["categories"][simple_model_name] = {
            "label": model.Config.label or simple_model_name,
            "measures":  measure_values
        }

    return all_measures


# ----------------------------------------------------------------
# --- model-specific routes
# ----------------------------------------------------------------

def parse_filter_str(filters):
    """
    Takes a string of the form "<factor1>:<value1>;<factor2>:<value2>;..." and
    returns a dict of factor-value pairs. Removes trailing whitespace on either
    end of the factor or value.

    >>> parse_filter_str("RE:White;Sex:Female")
    {"RE":"White","Sex":"Female"}
    >>> parse_filter_str("RE:  White NH  ; Sex: Female  ")
    {"RE":"White NH","Sex":"Female"}
    """
    return dict(
        tuple(z.strip() for z in x.split(":", maxsplit=2))
        for x in filters.split(";")
    )

class FactorsFilter(BaseModel):
    factors : dict[str,str]

# collects a set of routes for downloading each model as a CSV
# since we're going to compile them all into a zip
download_routes = []

# the loop below creates routes dynamically from the models specified in the
# STATS_MODELS dict; we get one set of routes per model in that dict
for type, family in STATS_MODELS.items():
    # data from CancerInFocus is represented on either a county or tract level.
    # the "family" here is the geographic entity associated with the model,
    # i.e. "county" or "tract"
    for model in family:
        simple_model_name = slug_modelname_sans_type(model, type)

        # despite us iterating over 'model' in the loop, we need to use a closure to
        # capture the value of 'model' at the time of the loop iteration. in this
        # case, the closure is the "generate_routes" function below that closes
        # model as an argument.
        # otherwise the methods will use the most recent value of 'model', which
        # will always be the last model in the list.

        def generate_routes(type=type, model=model, simple_model_name=simple_model_name):
            # ----------------------------------------------------------------
            # --- measures, but for a specific model
            # ----------------------------------------------------------------
            @router.get(
                f"/{type}/{simple_model_name}/measures", 
                response_model=list[str],
                description=f"""
                Autogenerated method; gets all distinct values of 'measure' for the {model.__name__} table.
                """
            )
            async def get_dataset_measures(session: AsyncSession = Depends(get_session)):
                # check if model is a cancer model
                # if so, we need to use the "Site" column instead of "measure"
                if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
                    query = select(model.Site).distinct().order_by(model.Site)
                else:
                    query = select(model.measure).distinct().order_by(model.measure)
                
                if LIMIT_TO_STATE is not None:
                    query = query.where(model.State == LIMIT_TO_STATE)

                result = await session.execute(query)
                objects = result.scalars().all()

                return objects

            # ----------------------------------------------------------------
            # --- all records from a specific model
            # ----------------------------------------------------------------
            @router.get(
                f"/{type}/{simple_model_name}",
                response_model=Page[model], 
                description=f"""
                Autogenerated method; gets all rows from the {model.__name__} table. Returns the results as a paginated list.
                """
            )
            async def get_dataset(
                measure: Optional[str] = None, session: AsyncSession = Depends(get_session)
            ):
                query = select(model)
                
                if LIMIT_TO_STATE is not None:
                    query = query.where(model.State == LIMIT_TO_STATE)

                if measure is not None:
                    query = query.where(model.measure == measure)

                result = await paginate(session, query)

                return result
            
            # ----------------------------------------------------------------
            # --- a list of FIPS-to-value pairs for populating the map
            # ----------------------------------------------------------------
            @router.get(
                f"/{type}/{simple_model_name}/fips-value",
                response_model=FIPSMeasureResponse,
                description=f"""
                Autogenerated method; gets pairings of FIPS (an ID that, in this
                case, specifies geographic regions) and the value of the given
                measure for that region. If the given model has associated
                factors, then values for those factors can be provided through
                the 'filters' argument. The 'filters' argument takes a
                semicolon-delimited string of factor:value pairs, each delimited
                by a colon. For example, "RE:White NH;Sex:Female" is parsed into
                two filters, RE="White NH" and Sex="Female".
                """
            )
            async def get_dataset_fips(
                measure: str,
                # filter: Optional[FactorsFilter] = json_param(
                #     "filter", FactorsFilter,
                #     description="A set of factor/value pairs on which to filter"
                # ),
                filters : Annotated[
                    str | None, Query(pattern="^([^:]+:[^:;]+;)*([^:]+:[^:;]+)$"),
                ] = None,
                session: AsyncSession = Depends(get_session)
            ):
                print(f"Processing {model.__name__} for measure {measure}")

                # ----------------------------------------------------------------
                # step 1. build initial queries for rows and statistics
                # ----------------------------------------------------------------

                if model in SCP_TRENDS_MODELS:
                    # FIXME: ideally this should be a computed field on the model
                    # but sqlmodel doesn't support computed fields yet.
                    # note that the SCP 'trends' model is effectively a cancer
                    # model, so instead of "measure" it has "Site".
                    query = select(
                        (
                            model.FIPS,
                            case(
                                (model.trend == 'falling', TREND_MAP['falling']),
                                (model.trend == 'stable', TREND_MAP['stable']),
                                (model.trend == 'rising', TREND_MAP['rising']),
                                else_=TREND_MAP_NONE
                            ).label("value")
                        )
                    ).where(model.Site == measure)
                elif model in CANCER_MODELS:
                    query = select((model.FIPS, model.AAR.label("value"), model.AAC.label("aac"))).where(model.Site == measure)
                else:
                    query = select((model.FIPS, model.value)).where(model.measure == measure)

                if LIMIT_TO_STATE is not None:
                    query = query.where(model.State == LIMIT_TO_STATE)

                # compute mins and maxes so we can build a color scale
                # # if it's a cancer endpint, we need to use the "Site" column instead of "measure", and "AAR" instead of "value
                if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
                    stats_query = select(func.min(model.AAR), func.max(model.AAR)).where(model.Site == measure)
                else:
                    stats_query = select(func.min(model.value), func.max(model.value)).where(model.measure == measure)
                
                # ----------------------------------------------------------------
                # step 2. apply factors to the queries
                # ----------------------------------------------------------------

                # apply factor fields to the query, if the model has factors defined
                factor_labels = FACTOR_DESCRIPTIONS.get(simple_model_name, None)

                # takes a string of the form "<factor1>:<value1>;<factor2>:<value2>;..."
                # and produces a dict of factor-value pairs on which to filter
                # (unless filters wasn't specified, in which case don't apply any filters)
                filter_factors = parse_filter_str(filters) if filters is not None else {}

                if factor_labels:
                    for f, fv in factor_labels.items():
                        # filter each column of the model identified by the current
                        # factor, either to the supplied value, its default if available,
                        # or 'None'
                        query = query.where(
                            getattr(model, f) == (
                                filter_factors.get(f, fv.get("default", None))
                            )
                        )
                        # do the same for the stats query
                        # FIXME: ideally we wouldn't repeat the above where clause
                        stats_query = stats_query.where(
                            getattr(model, f) == (
                                filter_factors.get(f, fv.get("default", None))
                            )
                        )

                elif filters is not None:
                    # FIXME: should we throw an error, as we do here, or should we just ignore unused params?
                    raise HTTPException(
                        status_code=400,
                        detail=f"The 'filters' argument was specified, but the model '{simple_model_name}' has no defined factors"
                    )

                # ----------------------------------------------------------------
                # step 3. execute queries, return response
                # ----------------------------------------------------------------

                stats_result = await session.execute(stats_query)
                stats = stats_result.all()[0]

                result = await session.execute(query)
                objects = result.all()

                # for cancer models, return a dict of FIPS and a sub-dict of AAR and AAC values
                # for non-cancer models, return a dict of FIPS and values
                if model in CANCER_MODELS:
                    values = {x["FIPS"]: {"value": x["value"], "aac": x["aac"]} for x in objects}
                else:
                    values = {x["FIPS"]: {"value": x["value"]} for x in objects}

                # determine the unit of measurement for the measure from the metadata
                # (if available)
                unit = (
                    MEASURE_DESCRIPTIONS
                        .get(simple_model_name, {})
                        .get(measure, {})
                        .get("unit", None)
                )

                return FIPSMeasureResponse(
                    min=stats[0],
                    max=stats[1],
                    unit=unit,
                    values=values
                )

            # ----------------------------------------------------------------
            # --- a CSV-formatted version of the model for downloading
            # ----------------------------------------------------------------
            @router.get(
                f"/{type}/{simple_model_name}/as-csv",
                response_class=StreamingResponse,
                description=f"""
                Autogenerated method; download {type}-level {simple_model_name} data for a given measure, if provided, as a CSV.
                """
            )
            async def download_dataset(
                measure: Optional[str] = None,
                session: AsyncSession = Depends(get_session)
            ):
                # get human labels for measures within this model, if available
                model_measure_meta = MEASURE_DESCRIPTIONS.get(simple_model_name, {})
                # get factors associated with this model, if any
                # (they'll be added as columns to the output)
                factor_labels = FACTOR_DESCRIPTIONS.get(simple_model_name, None)

                def model_to_fields(x, factor_labels):
                    model_measure_label = (
                        model_measure_meta
                            .get(x["measure"], {})
                            .get("label") or x["measure"]
                    )
                    
                    fields = [
                        x["GEOID"],
                        x["County"],
                        x["State"],
                        model_measure_label,
                        x["value"],
                    ]

                    if factor_labels is not None:
                        fields += [x[f] for f in factor_labels.keys()]

                    return fields

                if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
                    value_col = (
                        model.AAR.label("value") if model in CANCER_MODELS else model.trend.label("value")
                    )

                    # exports the 'Site' column as 'measure' for consistency with
                    # other models. also includes all the factors defined on the
                    # current model as additional columns.
                    query = select(
                        (model.FIPS.label("GEOID"), model.County, model.State, model.Site.label("measure"), value_col, *model.get_factors())
                    )
                    
                    if measure is not None:
                        query = query.where(model.Site == measure)

                else:
                    query = select(
                        (model.FIPS.label("GEOID"), model.County, model.State, model.measure, model.value, *model.get_factors())
                    )

                    if measure is not None:
                        query = query.where(model.measure == measure)

                
                if LIMIT_TO_STATE is not None:
                    query = query.where(model.State == LIMIT_TO_STATE)

                result = await session.execute(query)
                objects = result.all()

                with StringIO() as fp:
                    writer = csv.writer(fp)

                    header_cols = ["GEOID", "County", "State", "measure", "value"]

                    if factor_labels is not None:
                        header_cols += [str(x) for x in factor_labels.keys()]

                    writer.writerow(header_cols)
                    writer.writerows(
                        model_to_fields(
                            x,
                            factor_labels=factor_labels
                        )
                        for x in objects
                    )

                    response = StreamingResponse(iter([fp.getvalue()]), media_type="text/csv")
                    response.headers["Content-Disposition"] = f"attachment; filename=ECCO_{slugify(measure or simple_model_name)}_{type}.csv"

                    return response
            
            # append the endpoint to the download_routes dict; we'll
            # iterate over this later to produce a set of all possible
            # downloadable CSVs
            download_routes.append({
                'type': type,
                'model': model,
                'route': download_dataset
            })
            
        # finally, execute the generate_routes() method closed over the
        # 'type', 'model', and 'simple_model_name' vars
        generate_routes()


# ============================================================================
# === aggregate download route(s)
# ============================================================================

# ----------------------------------------------------------------
# --- a CSV-formatted version of the model for downloading
# ----------------------------------------------------------------
@router.get(
    f"/download-all",
    response_class=StreamingResponse,
    description=f"""
    Produces a CSV of each stats model, then adds them all to a zip file and
    returns the zip file for download.
    """
)
async def download_all(
    session: AsyncSession = Depends(get_session)
):
    with BytesIO() as zip_fp:
        with zipfile.ZipFile(zip_fp, "w") as z:
            # iterate over the download_routes dict and add each CSV to the zip
            for route_info in download_routes:
                type, model, route = get_keys(route_info, "type", "model", "route")
                simple_model_name = slug_modelname_sans_type(model, type)

                # get human labels for measures within this model, if available
                model_measure_meta = MEASURE_DESCRIPTIONS.get(simple_model_name, {})

                # retrieve the measures for the model, depending on what type of model it is
                # (SCP trends models resemble cancer models in this case but they're handled
                # differently elsewhere, so we can't add them to CANCER_MODELS. instead, we
                # just check for either model type here.)
                if model in CANCER_MODELS or model in SCP_TRENDS_MODELS:
                    query = select(model.Site).distinct().order_by(model.Site)
                else:
                    query = select(model.measure).distinct().order_by(model.measure)

                measures_result = await session.execute(query)
                measures = measures_result.scalars().all()

                # iterate over the measures for each model
                for measure in measures:
                    # query the download csv endpoint
                    result = await route(measure=measure, session=session)

                    # if you want to parse out the filename, you'd do it like so:
                    # filename = result.headers["Content-Disposition"].split("filename=", maxsplit=1)[1]
                    # (but at the moment we're overriding the filename with what
                    # we know it should be.)

                    # read the response into a buffer, then write it into the zip
                    with StringIO() as str_fp:
                        async for chunk in result.body_iterator:
                            str_fp.write(chunk)

                        # get the human-readable name of the model (aka the
                        # measure category), if available, and default to the
                        # model's simple name if not
                        try:
                            model_name = model.Config.label or simple_model_name
                        except AttributeError:
                            model_name = simple_model_name

                        # produce a human-readable name for the measure, if available,
                        # from the MEASURE_DESCRIPTIONS entry for this model
                        model_measure_label = model_measure_meta.get(measure, {}).get("label") or measure
                        final_name = f"{model_measure_label}.csv"
                        
                        # produce a complete path consisting of the type, the
                        # name of the model (aka measure category), and the
                        # measure name.
                        # sanitize() removes only characters known to be
                        # problematic, so we may need to tweak it later if we
                        # run into issues.
                        zip_path = os.path.join(*(
                            sanitize(x)
                            for x in (type, model_name, final_name)
                        ))
                        
                        z.writestr(zip_path, str_fp.getvalue())

        # stream the finished zip back to the user           
        response = StreamingResponse(iter([zip_fp.getvalue()]), media_type="application/zip")
        response.headers["Content-Disposition"] = f"attachment; filename=ECCO_All_Measures.zip"

        return response
