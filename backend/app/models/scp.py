"""
Models derived from scraped data from statecancerprofiles.cancer.gov.

Note that these models supersede the CIF cancer incidence and death models,
which originally come from SCP anyway.
"""

from typing import Optional

from sqlmodel import Field, SQLModel

from .base import CancerStatsByCounty


# ===========================================================================
# === data models
# ===========================================================================

class SCPCountyModel(CancerStatsByCounty):
    # pulled out for use as factors
    sex : str = Field(nullable=True, index=True)
    stage : str = Field(nullable=True, index=True)
    race : str = Field(nullable=True, index=True)
    age : str = Field(nullable=True, index=True)

    # since it's based on CancerStatsByCounty, we get the
    # 'Site', 'AAR', and 'AAC' fields from our parent
    # AAR is used in place of 'value' in most places, and
    # AAC is provided as additional data for cancer models

    # pulled out to use in the 'trends' views
    trend : str = Field(nullable=True)

    @classmethod
    def get_factors(cls):
        return (cls.sex, cls.stage, cls.race, cls.age)

class SCPDeathsCounty(SCPCountyModel, table=True):
    class Config:
        # label = "State Cancer Profiles: Deaths"
        label = "Cancer Mortality (age-adj per 100k)"

class SCPIncidenceCounty(SCPCountyModel, table=True):
    class Config:
        # label = "State Cancer Profiles: Incidence"
        label = "Cancer Incidence (age-adj per 100k)"


# ===========================================================================
# === trend views
# ===========================================================================

# the trend models are actually proxies on the existing models, but they
# convert the 'trend' field to an ordinal value and expose it as the
# 'value' field for compatibility with the existing schema

# the values of the 'trend' field are mapped to these numerical values
# since the API schema only exposes values as numbers currently
TREND_MAP = {
    "falling": 1,
    "stable": 2,
    "rising": 3
}
# for when the trend value is not mappable; we should choose something the
# frontend will display as 'no data'
TREND_MAP_NONE = 0

class SCPDeathsTrendCounty(SCPCountyModel, table=True):
    __tablename__ = SCPDeathsCounty.__tablename__
    __table_args__ = {'extend_existing': True} 

    class Config:
        skip_autogenerate = True
        arbitrary_types_allowed = True
        label = "Cancer Mortality: Trends"

class SCPIncidenceTrendCounty(SCPCountyModel, table=True):
    __tablename__ = SCPIncidenceCounty.__tablename__
    __table_args__ = {'extend_existing': True} 

    class Config:
        skip_autogenerate = True
        arbitrary_types_allowed = True
        label = "Cancer Incidence: Trends"


# ===========================================================================
# === metadata
# ===========================================================================

SCP_MODELS = {
    "county": [
        SCPDeathsCounty,
        SCPIncidenceCounty,
        SCPDeathsTrendCounty,
        SCPIncidenceTrendCounty
    ],
    "tract": []
}

SCP_CANCER_MODELS = {
    SCPDeathsCounty, SCPIncidenceCounty
}

# models for which the API uses 'trend_value' property as the 'value' field
SCP_TRENDS_MODELS = {
    SCPDeathsTrendCounty,
    SCPIncidenceTrendCounty,
}


# just default to literal values unless we need to override them
SCP_MEASURE_DESCRIPTIONS = {}

# descriptions of factors, i.e. additional enumerated values associated
# with each record. for example, cancer stats have race/ethnicity and sex
# associated with them, and can be filtered by those values.
# the 'default' field identifies which value is used if the user doesn't
# supply one when querying.
# format:
# {
#  <model name>: {
#   <field id>: {
#     label: <field label>,
#     default: <default val>,
#     values: { <value>: <label> }
#   }, ...
#  }, ...
# }
SCP_SHARED_FACTORS = {
    "sex": {
        "label": "Sex",
        "default": "All",
        "values": {
            "All": "All",
            "Female": "Female",
            "Male": "Male"
        }
    },
    "stage": {
        "label": "Stage",
        "default": "All Stages",
        "values": {}
    },
    "race": {
        "label": "Race",
        "default": "All Races (includes Hispanic)",
        "values": {}
    },
    "age": {
        "label": "Age",
        "default": "All Ages",
        "values": {}
    }
}

# for now, deaths and incidence share the same data
SCP_FACTOR_DESCRIPTIONS = {
    "scpdeaths": { **SCP_SHARED_FACTORS },
    "scpincidence": { **SCP_SHARED_FACTORS },
    "scpdeathstrend": { **SCP_SHARED_FACTORS },
    "scpincidencetrend": { **SCP_SHARED_FACTORS }
}
