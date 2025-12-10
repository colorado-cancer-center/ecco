# UCCC Research Participant Data

The contents of this folder pertain to this issue:
https://github.com/colorado-cancer-center/ecco/issues/150

The file `PRMS.Zipcodes.for.CO.Adult.only.xlsx` is intended to be used to
annotate the zip code geometries in
`/data/reference/ccc-team-data/uccc-research/co_colorado_zip_codes_geo.min.json`
with whether the zip code is considered urban or rural according.

From JL:
> Goal is to visualize where UCCC research participants come from across the state. Data source is ONCORE - delivered by PRMS group

Here's a sample zip code entry from the GeoJSON:
```json
{
    "type":"FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "STATEFP10": "08",
                "ZCTA5CE10": "81601",
                "GEOID10": "0881601",
                "CLASSFP10": "B5",
                "MTFCC10": "G6350",
                "FUNCSTAT10": "S",
                "ALAND10": 894341605,
                "AWATER10": 3633800,
                "INTPTLAT10": "+39.6014483",
                "INTPTLON10": "-107.3043137",
                "PARTFLG10": "N"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -107.353824,
                            39.631823
                        ],
                        ...
                    ]
                ]
            }
        },
        ...
    ]
}
```

Here's a sample row from the Excel file pertaining to that zip code:

|ZipCode|County  |Urbanicity|
|-------|--------|----------|
|81601  |GARFIELD|Rural     |

The GeoJSON `properties` for each zip code should be updated to include a new field
`area_type` with a value of either `Urban` or `Rural` based on the Excel file.