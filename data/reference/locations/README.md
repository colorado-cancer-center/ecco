# Locations Fixtures

This folder contains data fixtures for the `Location` model and derived models.

This was previously compiled by VR and was hardcoded into the frontend in
GeoJSON format.

The data includes:
- points of interest, i.e. cancer centers
- house and senate district maps + info on representatives

Data originally copied in by FA from the frontend on July 18th, 2024.


## Sources:

First, the file `locations.json` in the is folder consists of hand-labeled
categories and key references into the location data from our various sources.
This file was created by VR with ECCO leadership's guidance.

Location data in ECCO comes from a few sources:
- CancerInFocus (CIF), specifically the file that matches
  "us_facilities_and_providers_*.csv", but filtered down to just CO locations
- CU Cancer Center's Colorado Cancer Resource Map (CCRM), found at 
  https://medschool.cuanschutz.edu/colorado-cancer-center/community/CommunityOutreachEngagement/Colorado-Cancer-map
  - the backend data was originally retrieved from the following URL:
    https://ucdamc-geo.maps.arcgis.com/sharing/rest/content/items/5aaf9f6df8584a5aa6828ba118527e2b/data?f=json
  - *update from February 28th, 2025:* the URL for the backend data was:
    https://ucdamc-geo.maps.arcgis.com/sharing/rest/content/items/5ab17916dd07440f98f9bb35988cd434/data?f=json
    - (TODO: get a stable URL for this data; it shouldn't be that hard, since it's CCC-managed.)
- House, Senate, and Congressional District shapefiles from the Colorado
  Secretary of State's office
  - original data sources:
    - house, senate maps: https://github.com/colorado-cancer-center/ecco/issues/75
    - congressional maps: https://github.com/colorado-cancer-center/ecco/issues/107
  - *update from March 7th, 2025:* rather than relying on ECCO members to get
    the data for us and post it in issues, the new pipeline now pulls from
    (hopefully) up-to-date primary sources for each release w create.

See https://github.com/colorado-cancer-center/ecco/pull/19 for more information
about these sources.

**Update Feb 28th, 2025:**

The Colorado Cancer Center Resource Map appears to have changed its URL to
something new; we need to find a way to programmatically get these resources.

Anyway, the new URL appears to be

and the data we're interested in is under the key `operationalLayers`.

## Processing:

The actual location data is acquired via the pipeline implemented in
`/data/pipeline/`; this folder now contains just the hardcoded `locations.json`,
i.e. an organization of the keys found in each of the sources mentioned above.
The pipeline relies on that file to produce a `locations-data.json` for the
current release, which contains the actual GeoJSON data that gets imported into
the backend.

## Storage in ECCO:

The location data ends up being stored in the tables:
- `LocationCategory` (derived from `locations.json`)
- `Location` (derived from `locations-data.json`)
