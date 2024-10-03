"""
Models for Colorado-wide statistics (typically averages), and possibly other
non-county/tract data (e.g., national data).

Compiled and provided to ECCO as an Excel spreadsheet by the Colorado Cancer
Center.

Since these just need to be merged into existing responses, they lack field
metadata and factor descriptions. They are also not currently exposed in the
API, but could be in the future.
"""

from sqlmodel import Field

from .base import BaseStatsModel


# ===========================================================================
# === cancer data models
# ===========================================================================

class StateCancerStats(BaseStatsModel, table=False):
    # location of the cancer; labels based on the SCP data
    site: str = Field(index=True)

    # core statistics
    state_avg: float = Field()
    us_avg: float = Field(nullable=True, default=None)
    
    # included in the input as possible factors
    sex: str = Field(nullable=True, index=True, default=None)
    stage: str = Field(nullable=True, index=True, default=None)
    race: str = Field(nullable=True, index=True, default=None)
    age: str = Field(nullable=True, index=True, default=None)

    @classmethod
    def get_factors(cls):
        return (cls.sex, cls.stage, cls.race, cls.age)


class StateCancerIncidenceStats(StateCancerStats, table=True):
    class Config:
        label = "State Cancer Incidence (age-adj per 100k)"


class StateCancerMortalityStats(StateCancerStats, table=True):
    class Config:
        label = "State Cancer Mortality (age-adj per 100k)"


# ===========================================================================
# === sociodemographic data models
# ===========================================================================

class StateSociodemographicStats(BaseStatsModel, table=True):
    # measure category, similar to CiF
    measure_category: str = Field(index=True)

    # measure
    measure: str = Field(index=True)

    # core statistics
    state_avg: float = Field()
    us_avg: float = Field(nullable=True, default=None)

    # metadata
    source: str = Field(nullable=True, default=None)

    class Config:
        label = "State Sociodemographic Statistics"
