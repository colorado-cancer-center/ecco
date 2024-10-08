"""
Utilities for producing common queries or parts of queries
over the entities in the ECCO data model.
"""


from collections import defaultdict
from typing import Any
from models import CANCER_MODELS, FACTOR_DESCRIPTIONS
from models.base import BaseStatsModel
from models.scp import SCP_TRENDS_MODELS
from tools.accessors import omit
from tools.strings import slug_modelname_sans_type


from sqlalchemy import and_, or_, distinct, func
from sqlmodel import select


async def get_category_factors_with_values(model:BaseStatsModel, type:str, session, measures:list[str]=None):
    """
    Given a model (i.e. measure category), produces factors and the set of
    factor values observed in the data for each measure under that category. If
    'measures', a list, is supplied, filters the response down to just those
    measures.

    Response is of the form:
    {
        <measure>: {
            <factor>: {
                "label": str,
                "default": str,
                "values": {
                    <value:str>: <label:str>
                }
            }
        }
    }
    """

    # retrieve metadata about the factors for the given model+type
    simple_model_name = slug_modelname_sans_type(model, type)
    factor_descs = FACTOR_DESCRIPTIONS.get(simple_model_name, {})

    # if there are no factors, return an empty dict
    if not factor_descs:
        return {}

    # determine the measure column ('Site' for cancer-related, 'measure' otherwise)
    measure_col = (
        model.Site
        if model in CANCER_MODELS or model in SCP_TRENDS_MODELS else
        model.measure
    ).label("measure")

    # select a list of all distinct factor values for each measure...
    select_factor_args = [
        func.array_agg(distinct(getattr(model, col))).label(col)
        for col in factor_descs
    ]
    # ...but only for factor values that actually occur in the measure
    having_factor_args = [
        func.count(distinct(getattr(model, col))) > 0
        for col in factor_descs
    ]

    # query for all factor values for each measure
    query = (
        select(
            measure_col,
            *select_factor_args
        )
        .group_by(measure_col)
        .having(and_(*having_factor_args))
        .distinct()
    )

    if measures is not None:
        query = query.where(measure_col.in_(measures))

    result = await session.execute(query)
    factor_results = result.mappings().all()

    # produce a response that looks very much like the factor response
    # for a specific measure, but over all measures
    return {
        x["measure"]: {
            k: {
                "label": str(factor_descs[k]["label"] or k),
                "default": factor_descs[k].get("default"),
                "values": {
                    value: label
                    for value, label in factor_descs[k]["values"].items() if
                    value in v
                }
            }
            for k, v in omit(x, 'measure').items()
        }
        for x in factor_results
    }

def factor_default_clauses(constraints:dict[str,dict[str,Any]], model:BaseStatsModel, measure_col:str):
    """
    Converts a factor constraints dict to a set of clauses that can be applied
    to a query for a specific model, to limit the results to the factor values
    specified for each measure. The constraints dict is of the following form:
    { <measure>: { <factor>: <value> } }.

    Returns a clause for use in the 'where' portion of a query, consisting of:
    1. A set of 'and' clauses, each of which specifies a measure and, for
       each factor in the model, a value on which to filter.
    3. An 'or' clause that combines all of the 'and' clauses.

    :param constraints: a dict of the form { <measure>: { <factor>: <value> } }
    :param model: an instance of the model class to query
    :param measure_col: the column in the model that contains the measure
    :return: a clause that can be applied to a query to limit the results to
        the factor values specified in the constraints dict
    """
    clauses = []

    for measure, factor_values in constraints.items():
        clauses += [
            and_(
                measure_col == measure,
                *[
                    getattr(model, factor) == default
                    for factor, default in factor_values.items()
                ]
            ).self_group()
        ]

    # OR all of the clauses together and return that
    return or_(*clauses).self_group()

async def get_model_factor_defaults_clause(model, type, session, measures:list[str]=None, choices:dict[str,dict[str,Any]]=None):
    """
    For a given model, returns a clause that can be applied to a query to limit
    the results to either the populated factor values for each measure, or the
    default factor values if no data is present for a given measure.

    :param model: an instance of the model class to query
    :param type: the type of the model (e.g. 'county', 'tract')
    :param session: a database session
    :param measures: an optional list of measures to constrain the query
    :param choices: an optional dict of the form { <measure>: { <factor>: <value> } }
        that specifies the factor values to use for each measure, overriding the
        defaults. If a measure is not present in this dict, the default factor
        values will be used.
    :return: a tuple of the form (factor_constraints, factor_default_clause);
        the first element is a dict of the form `{ <measure>: { <factor>: <value> } }`
        that specifies the applied factor values for each measure, and the second
        element is a clause that can be applied to a query to limit the results to
        the factor values specified in the first element.
    """

    # first, resolve the 'simple' model name (i.e., normalized and without the
    # geometry type) so we can retrieve the factor defaults from the metadata
    simple_model_name = slug_modelname_sans_type(model, type)

    # if the model has factors, constrain them to their default values
    # for example, for SCP models, this selects the following factor values:
    # "sex": "All", "stage": "All Stages", "race": "All Races (includes Hispanic)", "age": "All Ages"
    factor_labels = FACTOR_DESCRIPTIONS.get(simple_model_name, None)
    all_factor_values = await get_category_factors_with_values(model, type, session, measures=measures)

    # determine the measure column ('Site' for cancer-related, 'measure' otherwise)
    measure_col = (
        model.Site
        if model in CANCER_MODELS or model in SCP_TRENDS_MODELS else
        model.measure
    ).label("measure")

    # record the factor constraints so we can apply them to both our queries
    factor_constraints = defaultdict(dict)

    if factor_labels:
        for f, fv in factor_labels.items():
            for measure in all_factor_values:
                # if a choice was specified for this measure in choices, just
                # use that and abort
                if choices and measure in choices and f in choices[measure]:
                    factor_constraints[measure][f] = choices[measure][f]
                    continue

                # get a list of observed factor values for this measure
                # (we get .keys() here because those are the 'internal' factor
                # names; the .values() portion of the dict is the human-readable
                # labels)
                measure_values = list(all_factor_values[measure][f]["values"].keys())

                # this is the hardcoded default value, regardless of what's in the data
                naive_default = fv.get("default")

                if len(measure_values) > 0:
                    # get the default if it occurs in the data
                    # otherwise get the first value that actually occurs
                    effective_default = naive_default if naive_default in measure_values else measure_values[0]
                else:
                    # we have no data for this factor, so just use the default
                    effective_default = fv.get("default")

                # populate factor_constraints with the effective default
                factor_constraints[measure][f] = effective_default

        # create a big OR'd where here, because each measure has its own set of possible factor values
        factor_clause = factor_default_clauses(factor_constraints, model, measure_col)

        return factor_constraints, factor_clause

    return factor_constraints, None
