"""
Holds metadata for models defined in cif.py

(Other modules store the metadata alongside the models, but the CIF
data is so verbose that i decided to split it into a separate module.)
"""

from .base import MeasureUnit

CIF_MEASURE_DESCRIPTIONS = {
  "sociodemographics": {
    "Total": {
      "label": "Total Population",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.COUNT
    },
    "Under 18": {
      "label": "Under 18 Years Old",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "18 to 64": {
      "label": "18 to 64 Years Old",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Over 64": {
      "label": "Over 64 Years Old",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "White": {
      "label": "White (non-Hispanic)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Black": {
      "label": "Black (non-Hispanic)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "AIAN": {
      "label": "American Indian and Alaska Native (non-Hispanic)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Asian": {
      "label": "Asian (non-Hispanic)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "NHOPI": {
      "label": "Native Hawaiian and Other Pacific Islander (non-Hispanic)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Hispanic": {
      "label": "Hispanic",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Other_Races": {
      "label": "Other Non-Hispanic Race",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Below 9th grade": {
      "label": "Did Not Attend High School",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "High School": {
      "label": "Graduated High School",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "College": {
      "label": "Graduated College",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Advanced Degree": {
      "label": "Completed a Graduate Degree",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Urban_Percentage": {
      "label": "Urbanized Residents",
      "source": "US Census Bureau, 2020 Decennial Census",
      "source_url": "https://www.census.gov/programs-surveys/decennial-census.html",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    }
  },
  "economy": {
    "Insurance Coverage": {
      "label": "Insured",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Medicaid Enrollment": {
      "label": "Enrolled in Medicaid",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Household Income": {
      "label": "Household Income ($)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.DOLLAR_AMOUNT
    },
    "Annual Labor Force Participation Rate": {
      "label": "Annual Labor Force Participation",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Annual Unemployment Rate": {
      "label": "Annual Unemployment Rate",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Below Poverty": {
      "label": "Living Below Poverty",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Received Public Assistance": {
      "label": "Received TANF or SNAP Public Assistance",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Monthly Unemployment Rate": {
      "label": "Monthly Unemployment Rate",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    },
    "Uninsured": {
      "label": "Uninsured",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    }
  },
  "environment": {
    "pctBB_1000_10": {
      "label": "Housing Units with 1000/10 Mbps Broadband Service",
      "source": "FCC, December 2023",
      "source_url": "https://www.fcc.gov/",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    },
    "pctBB_100_20": {
      "label": "Housing Units with 100/20 Mbps Broadband Service",
      "source": "FCC, December 2023",
      "source_url": "https://www.fcc.gov/",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    },
    "pct5G_7_1": {
      "label": "Area with 7/1 Mbps Mobile 5G Coverage",
      "source": "FCC, December 2023",
      "source_url": "https://www.fcc.gov/",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    },
    "pct5G_35_3": {
      "label": "Area with 35/3 Mbps Mobile 5G Coverage",
      "source": "FCC, December 2023",
      "source_url": "https://www.fcc.gov/",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    },
    "LILATracts_Vehicle": {
      "label": "Tracts that are Food Deserts",
      "source": "USDA ERS, 2019",
      "source_url": "https://www.ers.usda.gov/data-products/food-access-research-atlas/",
      "unit": MeasureUnit.PERCENT,
      "county_only": True
    },
    "PM25": {
      "label": "Particulate Matter 2.5 (annual avg. mcg/m^3)",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Lead Paint": {
      "label": "Housing Units Built Pre-1960",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Diesel PM": {
      "label": "Diesel Particulate Matter (annual avg. mcg/m^3)",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Toxics Release to Air": {
      "label": "Toxic Releases to Air",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Traffic Proximity": {
      "label": "Traffic Volume",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Water Discharge": {
      "label": "Toxic Water Discharge",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Superfund Proximity": {
      "label": "Superfund Proximity",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "RMP Proximity": {
      "label": "Risk Management Plan Facility Proximity",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Hazardous Waste Proximity": {
      "label": "Hazardous Waste Proximity",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Ozone": {
      "label": "Annual Ozone Average (ppb)",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Underground Storage Tanks": {
      "label": "Underground Storage Tanks",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Nitrogen Dioxide": {
      "label": "Nitrogen Dioxide (average annual part per billion)",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    },
    "Drinking Water Noncompliance": {
      "label": "Drinking Water Non-Compliance",
      "source": "EJScreen, 2024",
      "source_url": "https://www.epa.gov/ejscreen",
      "unit": MeasureUnit.RATE,
      "tract_only": True
    }
  },
  "housingtrans": {
    "Vacancy Rate": {
      "label": "Vacant Housing",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "No Vehicle": {
      "label": "No Household Vehicle Access",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Single Parent Household": {
      "label": "Single Parent Homes",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Multi-Unit Structures": {
      "label": "Housing in Multi-Unit Structures",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Mobile Homes": {
      "label": "Housing in Mobile Homes",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Owner Occupied Housing": {
      "label": "Owner-occupied Housing Units",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Crowded Housing": {
      "label": "Crowded Homes",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Lack Complete Plumbing": {
      "label": "Homes without Complete Plumbing",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Median Home Value": {
      "label": "Median Home Value ($)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.DOLLAR_AMOUNT
    },
    "Median Monthly Mortgage": {
      "label": "Median Monthly Mortgage ($)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.DOLLAR_AMOUNT
    },
    "Median Gross Rent": {
      "label": "Median Gross Rent ($)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.DOLLAR_AMOUNT
    },
    "No Home Broadband": {
      "label": "Homes without Broadband Internet",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Rent Burden (40% Income)": {
      "label": "High Rent Burden",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    }
  },
  "rfandscreening": {
    "Met_Breast_Screen": {
      "label": "Met Breast Screening Recommendations",
      "source": "CDC PLACES, 2024  (HP2030 Goal: 80.5%)",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Met_Colon_Screen": {
      "label": "Met Colorectal Screening Recommendations",
      "source": "CDC PLACES, 2024 (HP2030 Goal: 74.4%)",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Currently_Smoke": {
      "label": "Currently Smoke (adults)",
      "source": "CDC PLACES, 2024 (HP2030 Goal: 6.1%)",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "BMI_Obese": {
      "label": "Obese (BMI over 30)",
      "source": "CDC PLACES, 2024 (HP2030 Goal: 36.0%)",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Physically_Inactive": {
      "label": "Physically Inactive",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Binge_Drinking": {
      "label": "Binge Drink",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Sleep_Debt": {
      "label": "Sleep < 7 Hours a Night",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Cancer_Prevalence": {
      "label": "History of Cancer Diagnosis",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Bad_Health": {
      "label": "Report Fair or Poor Overall Health",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Poor_Physical": {
      "label": "Report Frequent Physical Health Distress",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Poor_Mental": {
      "label": "Report Frequent Mental Health Distress",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Depression": {
      "label": "Have Depression",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Diabetes_DX": {
      "label": "Diagnosed with Diabetes",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "High_BP": {
      "label": "Have High Blood Pressure",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "High_Cholesterol": {
      "label": "Have High Cholesterol",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "BP_Medicine": {
      "label": "On Blood Pressure Medication",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "CHD": {
      "label": "Have Coronary Heart Disease",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Had_Stroke": {
      "label": "Had a Stroke",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Asthma": {
      "label": "Diagnosed with Asthma",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "COPD": {
      "label": "Have COPD",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "No_Teeth": {
      "label": "All Adult Teeth Lost",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Recent_Checkup": {
      "label": "Had a Medical Checkup in the Last Year",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Recent_Dentist": {
      "label": "Had a Dental Visit in the Last Year",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Hearing_Disability": {
      "label": "Hearing Disability",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Vision_Disability": {
      "label": "Vision Disability",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Cognitive_Disability": {
      "label": "Cognitive Disability",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Mobility_Disability": {
      "label": "Mobility Disability",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Selfcare_Disability": {
      "label": "Self-care Disability",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Independent_Living_Disability": {
      "label": "Independent Living Disability",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Socially_Isolated": {
      "label": "Felt Socially Isolated in Last 12 Months",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Food_Insecure": {
      "label": "Experienced Food Insecurity in Last 12 Months",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Housing_Insecure": {
      "label": "Experienced Housing Insecurity in Last 12 Months",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Lacked_Reliable_Transportation": {
      "label": "Lacked Reliable Transportation in Last 12 Months",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    },
    "Lacked_Social_Emotional_Support": {
      "label": "Lacked Social/Emotional Support in Last 12 Months",
      "source": "CDC PLACES, 2024",
      "source_url": "https://www.cdc.gov/places/",
      "unit": MeasureUnit.PERCENT
    }
  },
  "fooddesert": {
    "LILATracts_Vehicle": {
      "label": "Tracts that are Food Deserts",
      "source": "USDA ERS, 2019",
      "source_url": "https://www.ers.usda.gov/data-products/food-access-research-atlas/",
      "unit": MeasureUnit.PERCENT,
      "tract_only": True
    }
  },
  "disparities": {
    "Gini Coefficient": {
      "label": "Income Inequality (Gini Coefficient)",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.COUNT
    },
    "Economic Segregation": {
      "label": "Economic Segregation",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.LEAST_MOST
    },
    "Racial Economic Segregation": {
      "label": "Racial Economic Segregation",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.LEAST_MOST
    },
    "Racial Segregation": {
      "label": "Racial Segregation",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.LEAST_MOST
    },
    "Gender Pay Gap": {
      "label": "Gender Pay Gap",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.COUNT
    },
    "Uninsured Children": {
      "label": "Children without Health Insurance",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Uninsured (Black)": {
      "label": "Black Population without Health Insurance",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Uninsured (Hispanic)": {
      "label": "Hispanic Population without Health Insurance",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Living Below Poverty (Black)": {
      "label": "Black Population Living Below Poverty",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Living Below Poverty (Hispanic)": {
      "label": "Hispanic Population Living Below Poverty",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    },
    "Lack_English_Prof": {
      "label": "Lack Proficiency in English",
      "source": "ACS 5-Year, 2019 - 2023",
      "source_url": "https://data.census.gov/",
      "unit": MeasureUnit.PERCENT
    }
  },
  "cancerincidence": {
    "All Site": {
      "label": "All Cancer Site ",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Bladder": {
      "label": "Bladder Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Brain & ONS": {
      "label": "Brain Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Cervix": {
      "label": "Cervical Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Cervix (Early Stage)": {
      "label": "Cervical Cancer (Early Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Cervix (Late Stage)": {
      "label": "Cervical Cancer (Late Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Cervix (21-65 years)": {
      "label": "Cervical Cancer (21-65 years)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Colon & Rectum": {
      "label": "Colorectal Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Colon & Rectum (Early Stage)": {
      "label": "Colorectal Cancer (Early Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Colon & Rectum (Late Stage)": {
      "label": "Colorectal Cancer (Late Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Colon & Rectum (45-75 years)": {
      "label": "Colorectal Cancer (45-75 years)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Corpus Uteri & Uterus, NOS": {
      "label": "Uterine Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Esophagus": {
      "label": "Esophageal Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Female Breast": {
      "label": "Female Breast Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Female Breast (Early Stage)": {
      "label": "Female Breast Cancer (Early Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Female Breast (Late Stage)": {
      "label": "Female Breast Cancer (Late Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Female Breast (40-74 years)": {
      "label": "Female Breast Cancer (40-74 years)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Kidney & Renal Pelvis": {
      "label": "Kidney Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Leukemia": {
      "label": "Leukemia",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Liver & IBD": {
      "label": "Liver Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Lung & Bronchus": {
      "label": "Lung Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Lung & Bronchus (Early Stage)": {
      "label": "Lung Cancer (Early Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Lung & Bronchus (Late Stage)": {
      "label": "Lung Cancer (Late Stage)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Lung & Bronchus (50-80 years)": {
      "label": "Lung Cancer (50-80 years)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Melanoma of the Skin": {
      "label": "Melanoma",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Non-Hodgkin Lymphoma": {
      "label": "Non-Hodgkin Lymphoma",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Oral Cavity & Pharynx": {
      "label": "Oral Cavity and Pharynx Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Ovary": {
      "label": "Ovarian Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Pancreas": {
      "label": "Pancreatic Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Prostate": {
      "label": "Prostate Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Stomach": {
      "label": "Stomach Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Thyroid": {
      "label": "Thyroid Cancer",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Alcohol-associated": {
      "label": "Alcohol-associated Cancers",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "HPV-associated": {
      "label": "HPV-associated Cancers",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Obesity-associated": {
      "label": "Obesity-associated Cancers",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Tobacco-associated": {
      "label": "Tobacco-associated Cancers",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Head and Neck": {
      "label": "Head and Neck Cancers",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Pediatric (0-19 years)": {
      "label": "Pediatric Cancers (0-19 years)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "AYA (15-39 years)": {
      "label": "Adolescent and Young Adults Cancers (15-39 years)",
      "source": "US Cancer Statistics, 2017 - 2021",
      "source_url": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
      "unit": MeasureUnit.RATE,
      "county_only": True
    }
  },
  "cancermortality": {
    "All Site": {
      "label": "All Cancer Site ",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Bladder": {
      "label": "Bladder Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Brain & ONS": {
      "label": "Brain Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Cervix": {
      "label": "Cervical Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Colon & Rectum": {
      "label": "Colorectal Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Corpus Uteri & Uterus, NOS": {
      "label": "Uterine Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Esophagus": {
      "label": "Esophageal Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Female Breast": {
      "label": "Female Breast Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Kidney & Renal Pelvis": {
      "label": "Kidney Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Leukemia": {
      "label": "Leukemia",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Liver & IBD": {
      "label": "Liver Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Lung & Bronchus": {
      "label": "Lung Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Melanoma of the Skin": {
      "label": "Melanoma",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Non-Hodgkin Lymphoma": {
      "label": "Non-Hodgkin Lymphoma",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Oral Cavity & Pharynx": {
      "label": "Oral Cavity and Pharynx Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Ovary": {
      "label": "Ovarian Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Pancreas": {
      "label": "Pancreatic Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Prostate": {
      "label": "Prostate Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Stomach": {
      "label": "Stomach Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    },
    "Thyroid": {
      "label": "Thyroid Cancer",
      "source": "State Cancer Profiles, 2018 - 2022",
      "source_url": "https://statecancerprofiles.cancer.gov/",
      "unit": MeasureUnit.RATE,
      "county_only": True
    }
  }
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
