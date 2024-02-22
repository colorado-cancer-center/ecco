"""
Models derived from cancerinfocus.org ("cif")
"""

from typing import Optional

from sqlmodel import Field, SQLModel


# ===========================================================================
# === stats models from CIF data export
# ===========================================================================

# ---------------------------------------------------------------------------
# -- base models that don't actually become tables
# ---------------------------------------------------------------------------

class BaseStatsModel(SQLModel):
    id: Optional[int] = Field(default=None, nullable=False, primary_key=True)

class TestModel(SQLModel):
    id: Optional[int] = Field(default=None, nullable=False, primary_key=True)
    name: str = Field()
    
class CancerStatsByCounty(BaseStatsModel):
    # NOTE: the 'measure' and 'value' columns are named 'Site' and 'AAR' in the
    # original schema, but we rename them here so they can be treated in
    # the same way as the other stats.

    FIPS : str = Field(index=True)
    County : str = Field(index=True)
    State : str = Field(index=True, foreign_key="us_state.name")
    # 'Type' is always Incidence for CancerIncidenceCounty, Mortality for CancerMortalityCounty
    # so it's not terribly useful...
    Type : str = Field(index=True)
    # demographic data, added sometime in february 2024(?)
    RE : str = Field(index=True, nullable=True)
    Sex : str = Field(index=True, nullable=True)
    # the type of cancer
    Site : str = Field(index=True)
    AAR : float
    AAC : float

class MeasuresByCounty(BaseStatsModel):
    FIPS : str = Field(index=True)
    County : str = Field(index=True)
    State : str = Field(index=True, foreign_key="us_state.name")
    measure : str = Field(index=True)
    value : float

class MeasuresByTract(MeasuresByCounty):
    Tract : Optional[str] = Field(index=True, nullable=True)


# ---------------------------------------------------------------------------
# -- actual tables
# ---------------------------------------------------------------------------

# county cancer measures

class CancerIncidenceCounty(CancerStatsByCounty, table=True):
    class Config:
        label = "Cancer Incidence (age-adj per 100k)"

    # we add aliases for 'measure' and 'value' so that the cancer stats
    # can be treated similarly to the other stats, even though the
    # data's schema differs
    # measure : str = synonym("Site")
    # value : float = synonym("AAR")

class CancerMortalityCounty(CancerStatsByCounty, table=True):
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


# ===========================================================================
# === model lists, metadata for downstream use
# === (e.g. creating routes automatically, adding human-readable labels)
# ===========================================================================

# to match the input schema, cancer models have columns named "Site" and "AAR"
# instead of "measure" and "value". to keep track of this fact, we enumerate
# the cancer models separately from the other stats models.
CANCER_MODELS = { CancerIncidenceCounty, CancerMortalityCounty }

STATS_MODELS = {
    "county": [
        SociodemographicsCounty,
        EconomyCounty,
        EnvironmentCounty,
        HousingTransCounty,
        RfAndScreeningCounty,
        CancerIncidenceCounty,
        CancerMortalityCounty
    ],
    "tract": [
        SociodemographicsTract,
        EconomyTract,
        EnvironmentTract,
        FoodDesertTract,
        HousingTransTract,
        RfAndScreeningTract
    ]
}

MEASURE_DESCRIPTIONS = {
    "sociodemographics": {
        "18 to 64": "18 to 64 Years Old",
        "Advanced Degree": "Completed a Graduate Degree",
        "Asian": "Asian (non-Hispanic)",
        "Below 9th grade": "Below 9th grade",
        "Black": "Black (non-Hispanic)",
        "College": "Graduated College",
        "High School": "Graduated High School",
        "Hispanic": "Hispanic",
        "Lack_English_Prof": "Lack Proficiency in English",
        "Other_Races": "Other Non-Hispanic Race",
        "Over 64": "Over 64 Years Old",
        "Total": "Total Population",
        "Under 18": "Under 18 Years Old",
        "Urban_Percentage": "Urbanized Residents",
        "White": "White (non-Hispanic)"
        # Total Population
        # Under 18 Years Old
        # 18 to 64 Years Old
        # Over 64 Years Old
        # White (non-Hispanic)
        # Black (non-Hispanic)
        # Hispanic
        # Asian (non-Hispanic)
        # Other Non-Hispanic Race
        # Did Not Attend High School
        # Graduated High School
        # Graduated College
        # Completed a Graduate Degree
        # Urbanized Residents
        # Lack Proficiency in English
    },
    "economy": {
        "Annual Labor Force Participation Rate": "Annual Labor Force Participation",
        "Annual Unemployment Rate": "Annual Unemployment Rate",
        "Below Poverty": "Living Below Poverty",
        "Gini Coefficient": "Income Inequality (Gini Coefficient)",
        "Household Income": "Household Income ($)",
        "Insurance Coverage": "Insured",
        "Medicaid Enrollment": "Enrolled in Medicaid",
        "Monthly Unemployment Rate (Apr)": "Monthly Unemployment Rate", # ???
        "Received Public Assistance": "Received TANF or SNAP Public Assistance",
        "Uninsured": "Uninsured",
        # Annual Labor Force Participation
        # Annual Unemployment Rate
        # Enrolled in Medicaid
        # Household Income ($)
        # Income Inequality (Gini Coefficient)
        # Insured
        # Living Below Poverty
        # Received TANF or SNAP Public Assistance
        # Uninsured
    },
    "environment": {
        "LILATracts_Vehicle": "Tracts that are Food Deserts",
        "PWS_Violations_Since_2016": "Public Water System Violations since 2016",
        # Public Water System Violations since 2016
        # Tracts that are Food Deserts
    },
    "housingtrans": {
        "Crowded Housing": "Crowded Homes",
        "Lack Complete Plumbing": "Homes without Complete Plumbing",
        "Median Gross Rent": "Median Gross Rent ($)",
        "Median Home Value": "Median Home Value ($)",
        "Median Monthly Mortgage": "Median Monthly Mortgage ($)",
        "Mobile Homes": "Housing in Mobile Homes",
        "Multi-Unit Structures": "Housing in Multi-Unit Structures",
        "No Home Broadband": "Homes without Broadband Internet",
        "No Vehicle": "No Household Vehicle Access",
        "Owner Occupied Housing": "Owner-occupied Housing Units",
        "Rent Burden (40% Income)": "High Rent Burden",
        "Single Parent Household": "Single Parent Homes",
        "Vacancy Rate": "Vacant Housing"
        # Crowded Homes
        # High Rent Burden
        # Homes without Broadband Internet
        # Homes without Complete Plumbing
        # Housing in Mobile Homes
        # Housing in Multi-Unit Structures
        # Median Gross Rent ($)
        # Median Home Value ($)
        # Median Monthly Mortgage ($)
        # No Household Vehicle Access
        # Owner-occupied Housing Units
        # Single Parent Homes
        # Vacant Housing
    },
    "rfandscreening": {
        "Asthma": "Diagnosed with Asthma",
        "Bad_Health": "Report Fair or Poor Overall Health",
        "Binge_Drinking": "Binge Drink",
        "BMI_Obese": "Obese (BMI over 30)",
        "BP_Medicine": "On Blood Pressure Medication",
        "Cancer_Prevalence": "History of Cancer Diagnosis",
        "CHD": "Have Coronary Heart Disease",
        "COPD": "Have COPD",
        "Currently_Smoke": "Currently Smoke",
        "Depression": "Have Depression",
        "Diabetes_DX": "Diagnosed with Diabetes",
        "Had_Stroke": "Had a Stroke",
        "High_BP": "Have High Blood Pressure",
        "Kidney_Disease": "Have Chronic Kidney Disease",
        "Met_Breast_Screen": "Met Breast Screening Recommendations",
        "Met_Cervical_Screen": "Met Cervical Screening Recommendations",
        "Met_Colon_Screen": "Met Colorectal Screening Recommendations",
        "No_Teeth": "All Adult Teeth Lost",
        "Physically_Inactive": "Physically Inactive",
        "Poor_Mental": "Report Frequent Mental Health Distress",
        "Poor_Physical": "Report Frequent Physical Health Distress",
        "Recent_Checkup": "Had a Medical Checkup in the Last Year",
        "Recent_Dentist": "Had a Dental Visit in the Last Year",
        "Sleep_Debt": "Sleep < 7 Hours a Night",

        # NOTE: in the KY site, rfandscreening seems to be split between
        #  "Screening & Risk Factors" and "Other Health Factors" but in
        #  the data they're merged into rfandscreening (akak "Screening & Risk
        #  Factors")

        # labels from "Screening & Risk Factors" category on the KY site
        # - Met Breast Screening Recommendations
        # - Had Pap Test in Last 3 Years, Age 21-64
        # - Met Colorectal Screening Recommendations
        # - Currently Smoke (adults)
        # - Obese (BMI over 30)
        # - Physical Inactive
        # - Binge Drink
        # - Sleep < 7 Hours a Night
        # - History of Cancer Diagnosis

        # labels from "Other Health Factors" category
        # - Report Fair or Poor Overall Health
        # - Report Frequent Physical Health Distress
        # - Report Frequent Mental Health Distress
        # - Have Depression
        # - Diagnosed with Diabetes
        # - Have High Blood Pressure
        # - On Blood Pressure Medication
        # - Have Coronary Heart Disease
        # - Had a Stroke
        # - Have Chronic Kidney Disease
        # - Diagnosed with Asthma
        # - Have COPD
        # - All Adult Teeth Lost
        # - Had a Medical Checkup in the Last Year
        # - Had a Dental Visit in the Last Year
    },
    "fooddesert": {
        "LILATracts_Vehicle": "Tracts that are Food Deserts",
    },

    # on the KY site, there are many more measures than in the data we have
    # available. above, we only include the ones that are present in the data.

    "cancerincidence": {
        "All Site": "All Cancer Sites",
        "Bladder": "",
        "Brain & ONS": "",
        "Cervix": "",
        "Colon & Rectum": "",
        "Corpus Uteri & Uterus, NOS": "",
        "Esophagus": "",
        "Female Breast": "",
        "Kidney & Renal Pelvis": "",
        "Leukemia": "",
        "Liver & IBD": "",
        "Lung & Bronchus": "",
        "Melanoma of the Skin": "",
        "Non-Hodgkin Lymphoma": "",
        "Oral Cavity & Pharynx": "",
        "Ovary": "",
        "Pancreas": "",
        "Prostate": "",
        "Stomach": "",
        "Thyroid": "",

    },
    "cancermortality": {
        "All Site": "All Cancer Sites",
        "Bladder": "",
        "Brain & ONS": "",
        "Cervix": "",
        "Colon & Rectum": "",
        "Corpus Uteri & Uterus, NOS": "",
        "Esophagus": "",
        "Female Breast": "",
        "Kidney & Renal Pelvis": "",
        "Leukemia": "",
        "Liver & IBD": "",
        "Lung & Bronchus": "",
        "Melanoma of the Skin": "",
        "Non-Hodgkin Lymphoma": "",
        "Oral Cavity & Pharynx": "",
        "Ovary": "",
        "Pancreas": "",
        "Prostate": "",
        "Stomach": "",
        "Thyroid": "",
    }

    # from KY site:
    # cancer incidence labels:
    # - All Cancer Sites
    # - Bladder Cancer
    # - Brain Cancer
    # - Cervical Cancer
    # - Colorectal Cancer
    # - Esophageal Cancer
    # - Female Breast Cancer
    # - Hodgkin Lymphoma
    # - Kidney Cancer
    # - Laryngeal Cancer
    # - Leukemia
    # - Liver Cancer
    # - Lung Cancer
    # - Melanoma
    # - Myeloma
    # - Non-Hodgkin Lymphoma
    # - Oral Cavity and Pharynx Cancer
    # - Ovarian Cancer
    # - Pancreatic Cancer
    # - Prostate Cancer
    # - Stomach Cancer
    # - Thyroid Cancer
    # - Uterine Cancer
    # - Uterine, NOS Cancer

    # cancer mortality labels:
    # - All Cancer Sites
    # - Bladder Cancer
    # - Brain Cancer
    # - Cervical Cancer
    # - Colorectal Cancer
    # - Esophageal Cancer
    # - Female Breast Cancer
    # - Hodgkin Lymphoma
    # - Kidney Cancer
    # - Laryngeal Cancer
    # - Leukemia
    # - Liver Cancer
    # - Lung Cancer
    # - Melanoma
    # - Myeloma
    # - Non-Hodgkin Lymphoma
    # - Oral Cavity and Pharynx Cancer
    # - Ovarian Cancer
    # - Pancreatic Cancer
    # - Prostate Cancer
    # - Stomach Cancer
    # - Thyroid Cancer
    # - Uterine Cancer
    # - Uterine, NOS Cancer
}

# descriptions of factors, i.e. additional enumerated values associated
# with each record. for example, cancer stats have race/ethnicity and sex
# associated with them, and can be filtered by those values.
# format: { <model name>: { <field id>: { label: <field label>, values: { <value>: <label> } } } }
FACTOR_DESCRIPTIONS = {
    "cancerincidence": {
        "RE": {
            "label": "Race/Ethnicity",
            "values": {
                "All": "All",
                "Black NH": "Black (non-Hispanic)",
                "Hispanic": "Hispanic",
                "White NH": "White (Non-Hispanic)"
            }
        },
        "Sex": {
            "label": "Sex",
            "values": {
                "All": "All",
                "Female": "Female",
                "Male": "Male"
            }
        }
    },
    "cancermortality": {
        "RE": {
            "label": "Race/Ethnicity",
            "values": {
                "All": "All",
                "Black NH": "Black (non-Hispanic)",
                "Hispanic": "Hispanic",
                "White NH": "White (Non-Hispanic)"
            }
        },
        "Sex": {
            "label": "Sex",
            "values": {
                "All": "All",
                "Female": "Female",
                "Male": "Male"
            }
        }
    }
}
