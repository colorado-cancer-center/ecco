"""
Models derived from cancerinfocus.org ("cif")
"""

from sqlmodel import Field

from .base import BaseStatsModel, MeasuresByCounty, CancerStatsByCounty, MeasuresByTract

# ===========================================================================
# === stats models from CIF data export
# ===========================================================================


class CIFCancerStatsByCounty(CancerStatsByCounty):
    # 'Type' is always Incidence for CancerIncidenceCounty, Mortality for CancerMortalityCounty
    # so it's not terribly useful...
    Type: str = Field(index=True)
    # demographic data, added sometime in february 2024(?)
    RE: str = Field(index=True, nullable=True)
    Sex: str = Field(index=True, nullable=True)

    @classmethod
    def get_factors(cls):
        return (cls.RE, cls.Sex)


# ---------------------------------------------------------------------------
# -- actual tables
# ---------------------------------------------------------------------------

# county cancer measures


class CancerIncidenceCounty(CIFCancerStatsByCounty, table=True):
    class Config:
        label = "Cancer Incidence (age-adj per 100k)"

    # we add aliases for 'measure' and 'value' so that the cancer stats
    # can be treated similarly to the other stats, even though the
    # data's schema differs
    # measure : str = synonym("Site")
    # value : float = synonym("AAR")


class CancerMortalityCounty(CIFCancerStatsByCounty, table=True):
    class Config:
        label = "Cancer Mortality (age-adj per 100k)"

    # same as CancerIncidenceCounty, we alias measure and value
    # measure : str = synonym("Site")
    # value : float = synonym("AAR")


# county general measures


class EconomyCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Economics & Insurance"


class EnvironmentCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Environment"


class HousingTransCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Housing & Transportation"


class RfAndScreeningCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Screening & Risk Factors"


class SociodemographicsCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Sociodemographics"


class DisparitiesCounty(MeasuresByCounty, table=True):
    class Config:
        label = "Disparities"


# tract general measures


class EconomyTract(MeasuresByTract, table=True):
    class Config:
        label = "Economics & Insurance"


class EnvironmentTract(MeasuresByTract, table=True):
    class Config:
        label = "Environment"


class FoodDesertTract(MeasuresByTract, table=True):
    class Config:
        label = "Food Deserts"


class HousingTransTract(MeasuresByTract, table=True):
    class Config:
        label = "Housing & Transportation"


class RfAndScreeningTract(MeasuresByTract, table=True):
    class Config:
        label = "Screening & Risk Factors"


class SociodemographicsTract(MeasuresByTract, table=True):
    class Config:
        label = "Sociodemographics"


class DisparitiesTract(MeasuresByTract, table=True):
    class Config:
        label = "Disparities"


# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

CIF_CANCER_MODELS = {CancerIncidenceCounty, CancerMortalityCounty}

# NOTE: the CancerIncidenceCounty and CancerMortalityCounty models are
# commented out below because they're superseded by the SCPDeathsCounty
# and SCPIncidenceCounty models. i didn't remove them entirely because
# we might want to switch back at some point, or at least compare them.

STATS_MODELS = {
    "county": [
        SociodemographicsCounty,
        EconomyCounty,
        EnvironmentCounty,
        HousingTransCounty,
        RfAndScreeningCounty,
        DisparitiesCounty,
        # CancerIncidenceCounty,
        # CancerMortalityCounty
    ],
    "tract": [
        SociodemographicsTract,
        EconomyTract,
        EnvironmentTract,
        FoodDesertTract,
        HousingTransTract,
        RfAndScreeningTract,
        DisparitiesTract,
    ],
}

# imported from base.py to build the app's full metadata collection
from .cif_meta import CIF_MEASURE_DESCRIPTIONS, CIF_FACTOR_DESCRIPTIONS
