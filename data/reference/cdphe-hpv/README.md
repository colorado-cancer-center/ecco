# HPV Teen Vaccination Data

The request to integrate the HPV data into ECCO and replies containing datasets and other
information are tracked in this issue: https://github.com/colorado-cancer-center/ecco/issues/35.

## Original data: CDPHE Vaccination Rates

Originally, we used data from the Colorado Department of Public Health (CDPHE) for teen HPV vaccination data,
specifically the dashboard at
https://cohealthviz.dphe.state.co.us/t/DCEED_Public/views/CountyRateMaps-Storyboard/CountyRateMapsCombined.

The dashboard contains Colorado vaccination rates for children and teenagers for a variety of disease, but
we only obtain and visualize the teenager HPV vaccination data. The data in this folder was produced
by:
1. selecting the 'Teen Immunization' tab in the dashboard linked above,
2. selecting the most recent period in the 'Time Period' dropdown, and
3. selecting from the 'Vaccine' dropdown: 'Patients (<gender>) UTD for HPV'
    1. selecting 'Any Gender', 'Male', and 'Female', then for each
    2. clicking the 'Download Data' button at the bottom

This folder contains Excel sheets obtained from the dashboard through the above process, specifically:
- `CO_Teen_Rates_anygender.xlsx`
- `CO_Teen_Rates_female.xlsx`
- `CO_Teen_Rates_male.xlsx`

## New Data: CIIS 13-17yo HPV Vaccination Rates, 2025-01-24

As of a [reply posted to issue 35](https://github.com/colorado-cancer-center/ecco/issues/35#issuecomment-2622151761)
on January 29th, a new CSV was posted; the attached CSV is stored here as `13-17yo.HPV.vaccination.rates.CIIS.2025-01-24.csv`

## Ingest into ECCO

Currently, the Excel sheets mentioned above are imported into ECCO
via the management command `/backend/app/commands/import_hpv.py`, which
takes any number of Excel sheets and merges them into the `HPVCounty` model.

The script currently expects each sheet to have a header with the following
columns defined:
- `County`: the name of the Colorado county
- `Up-To-Date Percent`: the percentage of up-to-date vaccinations for the county
- `Vaccine`: a column indicating the vaccine type and gender, which is used to
populate the "Gender" factor for the `HPVCounty` model
