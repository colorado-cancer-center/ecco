"""
Holds metadata for models defined in cif.py

(Other modules store the metadata alongside the models, but the CIF
data is so verbose that i decided to split it into a separate module.)
"""

from .base import MeasureUnit

CIF_MEASURE_DESCRIPTIONS = {
    "sociodemographics": {
        "18 to 64": {
            "label": "18 to 64 Years Old",
            "unit": MeasureUnit.PERCENT
        },
        "Advanced Degree": {
            "label": "Completed a Graduate Degree",
            "unit": MeasureUnit.PERCENT,
        },
        "Asian": {
            "label": "Asian (non-Hispanic)",
            "unit": MeasureUnit.PERCENT
        },
        "Below 9th grade": {
            "label": "Did Not Attend High School",
            "unit": MeasureUnit.PERCENT
        },
        "Black": {
            "label": "Black (non-Hispanic)",
            "unit": MeasureUnit.PERCENT
        },
        "College": {
            "label": "Graduated College",
            "unit": MeasureUnit.PERCENT
        },
        "High School": {
            "label": "Graduated High School",
            "unit": MeasureUnit.PERCENT
        },
        "Hispanic": {
            "label": "Hispanic",
            "unit": MeasureUnit.PERCENT
        },
        # moved to disparities as of 2024-09
        # "Lack_English_Prof": {
        #     "label": "Lack Proficiency in English",
        #     "unit": MeasureUnit.PERCENT,
        # },
        "Other_Races": {
            "label": "Other Non-Hispanic Race",
            "unit": MeasureUnit.PERCENT,
        },
        "Over 64": {
            "label": "Over 64 Years Old",
            "unit": MeasureUnit.PERCENT
        },
        "Total": {
            "label": "Total Population",
            "unit": MeasureUnit.COUNT
        },
        "Under 18": {
            "label": "Under 18 Years Old",
            "unit": MeasureUnit.PERCENT
        },
        "Urban_Percentage": {
            "label": "Urbanized Residents",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        "White": {
            "label": "White (non-Hispanic)",
            "unit": MeasureUnit.PERCENT
        },
    },
    "economy": {
        "Annual Labor Force Participation Rate": {
            "label": "Annual Labor Force Participation",
            "unit": MeasureUnit.PERCENT,
        },
        "Annual Unemployment Rate": {
            "label": "Annual Unemployment Rate",
            "unit": MeasureUnit.PERCENT,
        },
        "Below Poverty": {
            "label": "Living Below Poverty",
            "unit": MeasureUnit.PERCENT
        },
        # moved to rfandscreening as of 2024-09
        # "Gini Coefficient": {
        #     "label": "Income Inequality (Gini Coefficient)",
        #     "unit": MeasureUnit.PERCENT,
        # },
        "Household Income": {
            "label": "Household Income ($)",
            "unit": MeasureUnit.DOLLAR_AMOUNT,
        },
        "Insurance Coverage": {
            "label": "Insured",
            "unit": MeasureUnit.PERCENT
        },
        "Medicaid Enrollment": {
            "label": "Enrolled in Medicaid",
            "unit": MeasureUnit.PERCENT,
        },
        "Monthly Unemployment Rate": {
            "label": "Monthly Unemployment Rate",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        "Received Public Assistance": {
            "label": "Received TANF or SNAP Public Assistance",
            "unit": MeasureUnit.PERCENT,
        },
        "Uninsured": {
            "label": "Uninsured",
            "unit": MeasureUnit.PERCENT
        },
    },
    # environment is now completely different between counties
    # and tracts; we'll use the county_only and tract_only fields
    # to differentiate between the two, e.g. for tests
    "environment": {
        # county fields
        "LILATracts_Vehicle": {
            "label": "Tracts that are Food Deserts",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        # missing as of the 2024-04 release?
        # "PWS_Violations_Since_2016": {
        #     "label": "Public Water System Violations since 2016",
        #     "unit": MeasureUnit.COUNT,
        #     "county_only": True
        # },
        "pct5G_35_3": {
            "label": "Area with 35/3 Mbps Mobile 5G Coverage",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        "pct5G_7_1": {
            "label": "Area with 7/1 Mbps Mobile 5G Coverage",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        "pctBB_100_20": {
            "label": "Housing Units with 100/20 Mbps Broadband Service",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        "pctBB_1000_10": {
            "label": "Housing Units with 1000/10 Mbps Broadband Service",
            "unit": MeasureUnit.PERCENT,
            "county_only": True
        },
        # tract fields
        # FIXME: validate labels, units against CIF site
        # introduced in 2024-07 release, removed in 2024-09 release?
        # "Air Toxics Cancer": {
        #     "label": "Air Toxics Cancer Risk",
        #     "unit": MeasureUnit.RATE,
        #     "tract_only": True
        # },
        # "Air Toxics Resp": {
        #     "label": "Air Toxics Respiratory Risk",
        #     "unit": MeasureUnit.RATE,
        #     "tract_only": True
        # },
        "Diesel PM": {
            "label": "Diesel Particulate Matter (annual avg. mcg/m^3)",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Drinking Water Noncompliance": {
            "label": "Drinking Water Non-Compliance",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Hazardous Waste Proximity": {
            "label": "Hazardous Waste Proximity",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Lead Paint": {
            "label": "Housing Units Built Pre-1960",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Nitrogen Dioxide": {
            "label": "Nitrogen Dioxide (annual avg. part per billion)",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Ozone": {
            "label": "Annual Ozone Average (ppm)",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "PM25": {
            "label": "Particulate Matter 2.5 (annual avg. mcg/m^3)",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "RMP Proximity": {
            "label": "Risk Management Plan Facility Proximity",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Superfund Proximity": {
            "label": "Superfund Proximity",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Toxics Release to Air": {
            "label": "Toxic Releases to Air",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Traffic Proximity": {
            "label": "Traffic Volume",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Underground Storage Tanks": {
            "label": "Underground Storage Tanks",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
        "Water Discharge": {
            "label": "Toxic Water Discharge",
            "unit": MeasureUnit.RATE,
            "tract_only": True
        },
    },
    "housingtrans": {
        "Crowded Housing": {
            "label": "Crowded Homes",
            "unit": MeasureUnit.PERCENT
        },
        "Lack Complete Plumbing": {
            "label": "Homes without Complete Plumbing",
            "unit": MeasureUnit.PERCENT,
        },
        "Median Gross Rent": {
            "label": "Median Gross Rent ($)",
            "unit": MeasureUnit.DOLLAR_AMOUNT,
        },
        "Median Home Value": {
            "label": "Median Home Value ($)",
            "unit": MeasureUnit.DOLLAR_AMOUNT,
        },
        "Median Monthly Mortgage": {
            "label": "Median Monthly Mortgage ($)",
            "unit": MeasureUnit.DOLLAR_AMOUNT,
        },
        "Mobile Homes": {
            "label": "Housing in Mobile Homes",
            "unit": MeasureUnit.PERCENT,
        },
        "Multi-Unit Structures": {
            "label": "Housing in Multi-Unit Structures",
            "unit": MeasureUnit.PERCENT,
        },
        "No Home Broadband": {
            "label": "Homes without Broadband Internet",
            "unit": MeasureUnit.PERCENT,
        },
        "No Vehicle": {
            "label": "No Household Vehicle Access",
            "unit": MeasureUnit.PERCENT,
        },
        "Owner Occupied Housing": {
            "label": "Owner-occupied Housing Units",
            "unit": MeasureUnit.PERCENT,
        },
        "Rent Burden (40% Income)": {
            "label": "High Rent Burden",
            "unit": MeasureUnit.PERCENT,
        },
        "Single Parent Household": {
            "label": "Single Parent Homes",
            "unit": MeasureUnit.PERCENT,
        },
        "Vacancy Rate": {
            "label": "Vacant Housing",
            "unit": MeasureUnit.PERCENT
        },
    },
    "rfandscreening": {
        "Asthma": {
            "label": "Diagnosed with Asthma",
            "unit": MeasureUnit.PERCENT
        },
        "Bad_Health": {
            "label": "Report Fair or Poor Overall Health",
            "unit": MeasureUnit.PERCENT,
        },
        "Binge_Drinking": {
            "label": "Binge Drink",
            "unit": MeasureUnit.PERCENT
        },
        "BMI_Obese": {
            "label": "Obese (BMI over 30)",
            "unit": MeasureUnit.PERCENT
        },
        "BP_Medicine": {
            "label": "On Blood Pressure Medication",
            "unit": MeasureUnit.PERCENT,
        },
        "Cancer_Prevalence": {
            "label": "History of Cancer Diagnosis",
            "unit": MeasureUnit.PERCENT,
        },
        "Cognitive_Disability": {
            "label": "Cognitive Disability",
            "unit": MeasureUnit.PERCENT
        },
        "CHD": {
            "label": "Have Coronary Heart Disease",
            "unit": MeasureUnit.PERCENT
        },
        "COPD": {
            "label": "Have COPD",
            "unit": MeasureUnit.PERCENT
        },
        "Currently_Smoke": {
            "label": "Currently Smoke (adults)",
            "unit": MeasureUnit.PERCENT
        },
        "Depression": {
            "label": "Have Depression",
            "unit": MeasureUnit.PERCENT
        },
        "Diabetes_DX": {
            "label": "Diagnosed with Diabetes",
            "unit": MeasureUnit.PERCENT,
        },
        "Food_Insecure": {
            "label": "Experienced Food Insecurity in Last 12 Months",
            "unit": MeasureUnit.PERCENT
        },
        "Had_Stroke": {
            "label": "Had a Stroke",
            "unit": MeasureUnit.PERCENT
        },
        "Hearing_Disability": {
            "label": "Hearing Disability",
            "unit": MeasureUnit.PERCENT
        },
        "High_BP": {
            "label": "Have High Blood Pressure",
            "unit": MeasureUnit.PERCENT
        },
        # removed in 2024-09 release?
        # "Kidney_Disease": {
        #     "label": "Have Chronic Kidney Disease",
        #     "unit": MeasureUnit.PERCENT,
        # },
        "High_Cholesterol": {
            "label": "Have High Cholesterol",
            "unit": MeasureUnit.PERCENT
        },
        "Housing_Insecure": {
            "label": "Experienced Housing Insecurity in Last 12 Months",
            "unit": MeasureUnit.PERCENT
        },
        "Independent_Living_Disability": {
            "label": "Independent Living Disability",
            "unit": MeasureUnit.PERCENT
        },
        "Lacked_Reliable_Transportation": {
            "label": "Lacked Reliable Transportation in Last 12 Months",
            "unit": MeasureUnit.PERCENT
        },
        "Lacked_Social_Emotional_Support": {
            "label": "Lacked Social/Emotional Support in Last 12 Months",
            "unit": MeasureUnit.PERCENT
        },
        "Met_Breast_Screen": {
            "label": "Met Breast Screening Recommendations",
            "unit": MeasureUnit.PERCENT,
        },
        # removed in 2024-09 release?
        # "Met_Cervical_Screen": {
        #     "label": "Met Cervical Screening Recommendations",
        #     "unit": MeasureUnit.PERCENT,
        # },
        "Met_Colon_Screen": {
            "label": "Met Colorectal Screening Recommendations",
            "unit": MeasureUnit.PERCENT,
        },
        "Mobility_Disability": {
            "label": "Mobility Disability",
            "unit": MeasureUnit.PERCENT
        },
        "No_Teeth": {
            "label": "All Adult Teeth Lost",
            "unit": MeasureUnit.PERCENT
        },
        "Physically_Inactive": {
            "label": "Physically Inactive",
            "unit": MeasureUnit.PERCENT,
        },
        "Poor_Mental": {
            "label": "Report Frequent Mental Health Distress",
            "unit": MeasureUnit.PERCENT,
        },
        "Poor_Physical": {
            "label": "Report Frequent Physical Health Distress",
            "unit": MeasureUnit.PERCENT,
        },
        "Recent_Checkup": {
            "label": "Had a Medical Checkup in the Last Year",
            "unit": MeasureUnit.PERCENT,
        },
        "Recent_Dentist": {
            "label": "Had a Dental Visit in the Last Year",
            "unit": MeasureUnit.PERCENT,
        },
        "Selfcare_Disability": {
            "label": "Self-care Disability",
            "unit": MeasureUnit.PERCENT
        },
        "Sleep_Debt": {
            "label": "Sleep < 7 Hours a Night",
            "unit": MeasureUnit.PERCENT
        },
        "Socially_Isolated": {
            "label": "Felt Socially Isolated in Last 12 Months",
            "unit": MeasureUnit.PERCENT
        },
        "Vision_Disability": {
            "label": "Vision Disability",
            "unit": MeasureUnit.PERCENT
        },
    },
    "fooddesert": {
        "LILATracts_Vehicle": {
            "label": "Tracts that are Food Deserts",
            "unit": MeasureUnit.PERCENT,
        },
    },
    "disparities": {
        "Living Below Poverty (Black)": {
            "label": "Black Population Living Below Poverty",
            "unit": MeasureUnit.PERCENT,
        },
        "Uninsured (Black)": {
            "label": "Black Population without Health Insurance",
            "unit": MeasureUnit.PERCENT,
        },
        "Uninsured Children": {
            "label": "Children without Health Insurance",
            "unit": MeasureUnit.PERCENT,
        },
        "Economic Segregation": {
            "label": "Economic Segregation",
            "unit": MeasureUnit.LEAST_MOST,
        },
        "Gender Pay Gap": {
            "label": "Gender Pay Gap",
            "unit": MeasureUnit.PERCENT
        },
        "Living Below Poverty (Hispanic)": {
            "label": "Hispanic Population Living Below Poverty",
            "unit": MeasureUnit.PERCENT,
        },
        "Uninsured (Hispanic)": {
            "label": "Hispanic Population without Health Insurance",
            "unit": MeasureUnit.PERCENT,
        },
        "Gini Coefficient": {
            "label": "Income Inequality (Gini Coefficient)",
            "unit": MeasureUnit.PERCENT,
        },
        "Racial Economic Segregation": {
            "label": "Racial Economic Segregation",
            "unit": MeasureUnit.LEAST_MOST,
        },
        "Racial Segregation": {
            "label": "Racial Segregation",
            "unit": MeasureUnit.LEAST_MOST,
        },
        "Lack_English_Prof": {
            "label": "Lack Proficiency in English",
            "unit": MeasureUnit.PERCENT,
        },
    },
    "cancerincidence": {
        "All Site": {
            "label": "All Cancer Sites",
            "unit": MeasureUnit.RATE
        },
        "Bladder": {
            "label": "Bladder",
            "unit": MeasureUnit.RATE
        },
        "Brain & ONS": {
            "label": "Brain & ONS",
            "unit": MeasureUnit.RATE
        },
        "Cervix": {
            "label": "Cervix",
            "unit": MeasureUnit.RATE
        },
        "Colon & Rectum": {
            "label": "Colon & Rectum",
            "unit": MeasureUnit.RATE
        },
        "Corpus Uteri & Uterus, NOS": {
            "label": "Corpus Uteri & Uterus, NOS",
            "unit": MeasureUnit.RATE,
        },
        "Esophagus": {
            "label": "Esophagus",
            "unit": MeasureUnit.RATE
        },
        "Female Breast": {
            "label": "Female Breast",
            "unit": MeasureUnit.RATE
        },
        "Kidney & Renal Pelvis": {
            "label": "Kidney & Renal Pelvis",
            "unit": MeasureUnit.RATE,
        },
        "Leukemia": {
            "label": "Leukemia",
            "unit": MeasureUnit.RATE
        },
        "Liver & IBD": {
            "label": "Liver & IBD",
            "unit": MeasureUnit.RATE
        },
        "Lung & Bronchus": {
            "label": "Lung & Bronchus",
            "unit": MeasureUnit.RATE
        },
        "Melanoma of the Skin": {
            "label": "Melanoma of the Skin",
            "unit": MeasureUnit.RATE,
        },
        "Non-Hodgkin Lymphoma": {
            "label": "Non-Hodgkin Lymphoma",
            "unit": MeasureUnit.RATE,
        },
        "Oral Cavity & Pharynx": {
            "label": "Oral Cavity & Pharynx",
            "unit": MeasureUnit.RATE,
        },
        "Ovary": {
            "label": "Ovary",
            "unit": MeasureUnit.RATE
        },
        "Pancreas": {
            "label": "Pancreas",
            "unit": MeasureUnit.RATE
        },
        "Prostate": {
            "label": "Prostate",
            "unit": MeasureUnit.RATE
        },
        "Stomach": {
            "label": "Stomach",
            "unit": MeasureUnit.RATE
        },
        "Thyroid": {
            "label": "Thyroid",
            "unit": MeasureUnit.RATE
        },
    },
    "cancermortality": {
        "All Site": {
            "label": "All Cancer Sites",
            "unit": MeasureUnit.RATE
        },
        "Bladder": {
            "label": "Bladder",
            "unit": MeasureUnit.RATE
        },
        "Brain & ONS": {
            "label": "Brain & ONS",
            "unit": MeasureUnit.RATE
        },
        "Cervix": {
            "label": "Cervix",
            "unit": MeasureUnit.RATE
        },
        "Colon & Rectum": {
            "label": "Colon & Rectum",
            "unit": MeasureUnit.RATE
        },
        "Corpus Uteri & Uterus, NOS": {
            "label": "Corpus Uteri & Uterus, NOS",
            "unit": MeasureUnit.RATE,
        },
        "Esophagus": {
            "label": "Esophagus",
            "unit": MeasureUnit.RATE
        },
        "Female Breast": {
            "label": "Female Breast",
            "unit": MeasureUnit.RATE
        },
        "Kidney & Renal Pelvis": {
            "label": "Kidney & Renal Pelvis",
            "unit": MeasureUnit.RATE,
        },
        "Leukemia": {
            "label": "Leukemia",
            "unit": MeasureUnit.RATE
        },
        "Liver & IBD": {
            "label": "Liver & IBD",
            "unit": MeasureUnit.RATE
        },
        "Lung & Bronchus": {
            "label": "Lung & Bronchus",
            "unit": MeasureUnit.RATE
        },
        "Melanoma of the Skin": {
            "label": "Melanoma of the Skin",
            "unit": MeasureUnit.RATE,
        },
        "Non-Hodgkin Lymphoma": {
            "label": "Non-Hodgkin Lymphoma",
            "unit": MeasureUnit.RATE,
        },
        "Oral Cavity & Pharynx": {
            "label": "Oral Cavity & Pharynx",
            "unit": MeasureUnit.RATE,
        },
        "Ovary": {
            "label": "Ovary",
            "unit": MeasureUnit.RATE
        },
        "Pancreas": {
            "label": "Pancreas",
            "unit": MeasureUnit.RATE
        },
        "Prostate": {
            "label": "Prostate",
            "unit": MeasureUnit.RATE
        },
        "Stomach": {
            "label": "Stomach",
            "unit": MeasureUnit.RATE
        },
        "Thyroid": {
            "label": "Thyroid",
            "unit": MeasureUnit.RATE
        },
    },
}

# region "Commentary On Measure Descriptions"
# -----------------
# notes on differences from KYCancerNeeds in the above metdata:

# on the KY site, there are many more measures than in the data we have
# available. above, we only include the ones that are present in the data.

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

# cancer measure labels, from KY site:
# * cancer incidence labels:
#   - All Cancer Sites
#   - Bladder Cancer
#   - Brain Cancer
#   - Cervical Cancer
#   - Colorectal Cancer
#   - Esophageal Cancer
#   - Female Breast Cancer
#   - Hodgkin Lymphoma
#   - Kidney Cancer
#   - Laryngeal Cancer
#   - Leukemia
#   - Liver Cancer
#   - Lung Cancer
#   - Melanoma
#   - Myeloma
#   - Non-Hodgkin Lymphoma
#   - Oral Cavity and Pharynx Cancer
#   - Ovarian Cancer
#   - Pancreatic Cancer
#   - Prostate Cancer
#   - Stomach Cancer
#   - Thyroid Cancer
#   - Uterine Cancer
#   - Uterine, NOS Cancer
# * cancer mortality labels:
#   - All Cancer Sites
#   - Bladder Cancer
#   - Brain Cancer
#   - Cervical Cancer
#   - Colorectal Cancer
#   - Esophageal Cancer
#   - Female Breast Cancer
#   - Hodgkin Lymphoma
#   - Kidney Cancer
#   - Laryngeal Cancer
#   - Leukemia
#   - Liver Cancer
#   - Lung Cancer
#   - Melanoma
#   - Myeloma
#   - Non-Hodgkin Lymphoma
#   - Oral Cavity and Pharynx Cancer
#   - Ovarian Cancer
#   - Pancreatic Cancer
#   - Prostate Cancer
#   - Stomach Cancer
#   - Thyroid Cancer
#   - Uterine Cancer
#   - Uterine, NOS Cancer
# -----------------
# endregion

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
CIF_FACTOR_DESCRIPTIONS = {
    "cancerincidence": {
        "RE": {
            "label": "Race/Ethnicity",
            "default": "All",
            "values": {
                "All": "All",
                "Black NH": "Black (non-Hispanic)",
                "Hispanic": "Hispanic",
                "White NH": "White (Non-Hispanic)",
            },
        },
        "Sex": {
            "label": "Sex",
            "default": "All",
            "values": {
                "All": "All",
                "Female": "Female",
                "Male": "Male"
            },
        },
    },
    "cancermortality": {
        "RE": {
            "label": "Race/Ethnicity",
            "default": "All",
            "values": {
                "All": "All",
                "Black NH": "Black (non-Hispanic)",
                "Hispanic": "Hispanic",
                "White NH": "White (Non-Hispanic)",
            },
        },
        "Sex": {
            "label": "Sex",
            "default": "All",
            "values": {
                "All": "All",
                "Female": "Female",
                "Male": "Male"
            },
        },
    },
}
