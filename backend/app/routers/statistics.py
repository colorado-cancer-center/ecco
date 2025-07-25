"""
API endpoints that return statistics, e.g. cancer incidence/mortality,
or sociodemographic measures.
"""

import os
import csv
from io import StringIO, BytesIO
import zipfile

from typing import Any, Optional, Annotated
from fastapi import Depends, Query, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, case
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_cache.decorator import cache

from tools.queries import get_model_factor_defaults_clause, factor_default_clauses
from tools.strings import slugify, slug_modelname_sans_type, sanitize
from tools.accessors import get_keys

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
from models.scp import (
    SCPIncidenceCounty, SCPDeathsCounty,
    SCP_TRENDS_MODELS, TREND_MAP, INVERTED_TREND_MAP, TREND_MAP_NONE
)
from models.ccc_state_stats import (
    StateCancerIncidenceStats, StateCancerMortalityStats,
    StateSociodemographicStats
)


router = APIRouter(prefix="/stats")


# ============================================================================
# === statistics routes
# ============================================================================

# ----------------------------------------------------------------
# --- general info routes
# ----------------------------------------------------------------

class FIPSValue(BaseModel):
    value: Optional[float|str]
    aac: Optional[float]

class FIPSMeasureResponse(BaseModel):
    min: Optional[float|str]
    max: Optional[float|str]
    state: Optional[float|str]
    state_source: Optional[str]
    unit: Optional[MeasureUnit]
    source: Optional[str]
    source_url: Optional[str]
    order: Optional[list[str]]
    values: dict[str, FIPSValue]

# provides high-level information about the available categories and measures
# by iterating over the STATS_MODELS dict

class FactorMetaResponse(BaseModel):
    label : str
    default : str | None
    values : dict[str, str]

class MeasuresMetaResponse(BaseModel):
    label: str
    unit: Optional[MeasureUnit]
    source: Optional[str]
    source_url: Optional[str]
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
                    measure: {
                        "label": measure_descs.get(measure, {}).get('label') or measure,
                        "unit": measure_descs.get(measure, {}).get('unit'),
                        "source": measure_descs.get(measure, {}).get('source'),
                        "source_url": measure_descs.get(measure, {}).get('source_url'),
                        "factors": await get_factors_with_values(model, measure)
                    }
                    for measure in result.scalars().all()
                }
            }

    return all_measures


# provides an overview of values for a specific county

class CountyMeasureValueResponse(BaseModel):
    label: str
    unit: MeasureUnit
    value: float
    state_value: Optional[float] = None
    state_stat_source: Optional[str] = None
    factor_constraints: dict[str, Any]

class CountyCancerMeasureValueResponse(CountyMeasureValueResponse):
    aac: float
    state_aac: Optional[float] = None

class CountyCancerTrendMeasureValueResponse(CountyMeasureValueResponse):
    order: list[str]
    value: str
    state_value: Optional[str] = None

class CountyMeasureCategoryResponse(BaseModel):
    label: str
    measures: dict[
        str,
        CountyCancerMeasureValueResponse|CountyCancerTrendMeasureValueResponse|CountyMeasureValueResponse
    ]

class ByCountyResponse(BaseModel):
    FIPS: str
    name: str
    categories: dict[str, CountyMeasureCategoryResponse]

# if true, the by-county endpoint will attempt to generate state statistics
# by averaging over the county/tract values. if false, it will query the
# CCC models for state statistics.
AUTOGENERATE_STATE_STATS = False

async def _query_state_stats(session, model, factor_constraints, measure_label=None):
    """
    Queries the state-level statistics for a given model. If measure_label is
    unspecified, returns a dict of measure names to state values, where each
    value is a dict containing the value and the source of the statistic. If
    measure_label is specified, returns a single dict with the state value and
    source.

    Notes:
    - The factor_constraints argument is only used when querying cancer models,
      since only the state-level cancer models have factors defined. (As of this
      writing, many combinations of factors don't have state-level statistics in
      the database, especially for mortality stats.)
    - The source returned by this method will always be "ccc", i.e. "Colorado
      Cancer Center", since this method just queries the Colorado Cancer Center
      models for state-level statistics.

    :param session: a database session
    :param model: the model class to query
    :param factor_constraints: a dict of factor constraints to apply to the query; this is only used for cancer models
    :param measure_label: an optional label for the measure to filter by
    :return: a dict of measure names to state values + sources, or if measure_label is specified,
        a single dict with the information for that measure.
    """
    # retrieve state values by querying CCC models
    if model in [SCPIncidenceCounty, SCPDeathsCounty]:
        state_model = StateCancerIncidenceStats if model is SCPIncidenceCounty else StateCancerMortalityStats

        # if we've specified a measure, we need to remap the value in such a way
        # that it can be passed to factor_default_clauses(), which expects a dict
        # of measures, then factor values for each measure
        if measure_label is not None:
            factor_constraints = {
                measure_label: factor_constraints
            }

        state_query = (
            select(
                state_model.site.label("measure"),
                state_model.state_avg.label("value"),
            ).where(
                factor_default_clauses(factor_constraints, state_model, state_model.site)
            )
        )

         # if a measure (really, a site in this case) was specified, filter the query to that site
        if measure_label is not None:
            state_query = state_query.where(state_model.site == measure_label)

    else:
        state_model = StateSociodemographicStats
        state_query = (
            select(
                state_model.measure.label("measure"),
                state_model.state_avg.label("value"),
            ).where(
                state_model.measure_category == model.Config.label
            )
        )

        # if a measure was specified, filter the query to that measure
        if measure_label is not None:
            state_query = state_query.where(state_model.measure == measure_label)

    # query and produce a dict of state values
    result = await session.execute(state_query)
    state_values = {
        x["measure"]: {**x, **{"stat_source": "ccc"}} for x in result.mappings().all()
    }

    # again, if only a specific measure was requested, return just that measure
    # (note that rather than returning {measure: value}, we return just the value and its source)
    if measure_label is not None and measure_label in state_values:
        return state_values.get(measure_label)

    return state_values

@router.get("/by-county/{county_fips}", response_model=ByCountyResponse)
@cache()
async def get_county_measures(county_fips:str, session: AsyncSession = Depends(get_session)):
    f"""
    For a given county specified by its FIPS, returns all statistics associated
    with the county as well as corresponding state-level statistics, when available.
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

        # =========================================================================
        # === construct initial query objects for the current model
        # =========================================================================

        # since we need both the average values for all regions and individual
        # values for the specified county, we have to issue two queries:
        # 1. a query for the average values of all regions
        # 2. a restricted query just for the specified region
        # (of course, taking the average or median for a single number just
        # produces that number, so we can use the same query for both.)

        if model in CANCER_MODELS:
            query = select(
                model.Site.label("measure"),
                func.avg(model.AAR).label("value"),
                func.avg(model.AAC).label("aac")
            ).group_by(model.Site).order_by(model.Site)

        elif model in SCP_TRENDS_MODELS:
            # for trend models, since we're dealing with ordinal values
            # stored as strings in the database, we have to do the following:
            # 1. map string values to ordinal values so that they're ordered
            # 2. take the median
            # 3. map the ordinal values back to their string values
            query = select(
                model.Site.label("measure"),
                func.percentile_cont(0.5).within_group(case(
                    (model.trend == 'falling', TREND_MAP['falling']),
                    (model.trend == 'stable', TREND_MAP['stable']),
                    (model.trend == 'rising', TREND_MAP['rising']),
                    else_=TREND_MAP_NONE
                )).label("value")
            ).group_by(model.Site).where(model.trend != "").order_by(model.Site)

        else:
            query = select(
                model.measure.label("measure"),
                func.avg(model.value).label("value")
            ).group_by(model.measure).order_by(model.measure)

        # =========================================================================
        # === resolve factor values for current measure category
        # =========================================================================

        # if there are factors defined for this model, constrain the query to
        # the default values for each factor, or a possible value if the default
        # doesn't exist (e.g., if the default for sex is "All" but the data only has
        # "Female" entries due to being a sex-linked cancer, e.g. ovarian cancer)

        factor_constraints, factor_defaults_clause = await get_model_factor_defaults_clause(model, type, session)
        if factor_defaults_clause is not None:
            query = query.where(factor_defaults_clause)

        # =========================================================================
        # === retrieve (or compute) state-level values
        # =========================================================================

        # retrieve state values by querying CCC models
        state_values = await _query_state_stats(session, model, factor_constraints)

        # if AUTOGENERATE_STATE_STATS is true, we'll compute the state values
        # and merge them with the CCC-suplied values, preferring given values
        # over computed ones if both exist
        if AUTOGENERATE_STATE_STATS:
            # issue the query before we filter down to a FIPS to get the average
            # over all regions
            result = await session.execute(query)
            
            # note that we retrieve stats by label, not by measure name,
            # which is why we're pulling the label out of the metadata
            autogen_state_values = {
                (measure_descs.get(x["measure"], {}).get("label") or x["measure"]):
                {**dict(zip(x.keys(), x)), **{"stat_source": "computed"}}
                for x in result.all()
            }

            # map the trend values back to their human-readable labels
            if model in SCP_TRENDS_MODELS:
                for x in autogen_state_values:
                    autogen_state_values[x]["value"] = INVERTED_TREND_MAP.get(
                        int(autogen_state_values[x]["value"]), ""
                    )

            # merge existing state values and autogenerated values, preferring
            # the given state values over the computed ones
            state_values = {
                **autogen_state_values,
                **state_values
            }

        # =========================================================================
        # === final query, response generation
        # =========================================================================

        # limit the query to the specified county and query for measure
        # categories within this measure
        query = query.where(model.FIPS == county_fips)
        result = await session.execute(query)

        # process measures for this model, replacing 'label' with a human-readable
        # version from the metadata, if available
        measure_values = {
            x["measure"]: {
                # bring in unit + extra data, e.g. ordinal ordering for SCP trends
                **measure_descs.get(x["measure"], {}),
                # bring in all the fields in the row
                **x,
                # process columns that require special handling or cross-refs
                **{
                    "value": x["value"] if model not in SCP_TRENDS_MODELS else INVERTED_TREND_MAP.get(int(x["value"]), ""),
                    "label": measure_descs.get(x["measure"], {}).get('label') or x["measure"],
                    "state_value": state_values.get(measure_descs.get(x["measure"], {}).get('label'), {}).get("value", None),
                    "state_aac": state_values.get(measure_descs.get(x["measure"], {}).get('label'), {}).get("aac", None),
                    "state_stat_source": state_values.get(measure_descs.get(x["measure"], {}).get('label'), {}).get("stat_source", None),
                    "factor_constraints": factor_constraints.get(x["measure"], {})
                }
            }
            for x in result.all()
        }

        # add it to the set of all measure categories
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
                            # case(
                            #     (model.trend == 'falling', TREND_MAP['falling']),
                            #     (model.trend == 'stable', TREND_MAP['stable']),
                            #     (model.trend == 'rising', TREND_MAP['rising']),
                            #     else_=TREND_MAP_NONE
                            # ).label("value")
                            model.trend.label("value")
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
                if model in CANCER_MODELS:
                    stats_query = select(func.min(model.AAR), func.max(model.AAR)).where(model.Site == measure)
                elif model in SCP_TRENDS_MODELS:
                    # we compute the min and max over the trends' numeric value, excluding regions without a trend
                    stats_query = select(
                        func.min(case(
                            (model.trend == 'falling', TREND_MAP['falling']),
                            (model.trend == 'stable', TREND_MAP['stable']),
                            (model.trend == 'rising', TREND_MAP['rising'])
                        )),
                        func.max(case(
                            (model.trend == 'falling', TREND_MAP['falling']),
                            (model.trend == 'stable', TREND_MAP['stable']),
                            (model.trend == 'rising', TREND_MAP['rising'])
                        ))
                    ).where(model.Site == measure)
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
                measure_meta = (
                    MEASURE_DESCRIPTIONS
                        .get(simple_model_name, {})
                        .get(measure, {})
                )

                # retrieve state values, if available, by querying CCC models
                state_values = await _query_state_stats(
                    session, model, factor_constraints=filter_factors, measure_label=measure_meta['label']
                )

                return FIPSMeasureResponse(
                    min=stats[0] if model not in SCP_TRENDS_MODELS else INVERTED_TREND_MAP.get(stats[0], stats[0]),
                    max=stats[1] if model not in SCP_TRENDS_MODELS else INVERTED_TREND_MAP.get(stats[1], stats[1]),
                    state=state_values.get("value", None),
                    state_source=state_values.get("stat_source", None),
                    source=measure_meta.get("source", None),
                    source_url=measure_meta.get("source_url", None),
                    unit=measure_meta.get("unit", None),
                    order=measure_meta.get("order", None),
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
