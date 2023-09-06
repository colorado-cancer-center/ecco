# Data Gathering Notes

This document lists the sources of data for this app, specifically:
- geometry: county, tract, and other regions that are drawn as map regions
- cancer incidence/mortality, and other metrics that are used to color map
  regions
- other metadata needed to describe that data (e.g., human-readable metric
  names, points of interest in the map regions, groupings of map regions like
  the economic development districts, etc.)

## Metrics

All our metrics currently come from Cancer InFocus; public data is listed here:
https://cancerinfocus.org/public-data/. Our pipeline will likely pull either
https://cancerinfocus.org/public-data/Current/us.zip and subset it dynamically
to the US state for which the stack is set up, or will pull a state-specific
archive (e.g., https://cancerinfocus.org/public-data/Current/colorado.zip).

The US data differs from the Colorado data only in that the `colorado.zip`
archive includes shapefiles for county and tract borders. The tables are
otherwise from the same schema, but assumedly the data is subsetted to CO.

In the public data made available from Cancer InFocus, there appear to be other
archives for specific institutions or groups; I haven't yet verified that their
schema matches the US and Colorado data.

## GIS Data Gathering Notes

This document lists places where we might get GIS data for
Colorado, for the COE project. Ideally the GIS data should be in
GeoJSON format as that removes a lot of ambiguities, but we could conceivably
take any format that [ogr2ogr](https://gdal.org/programs/ogr2ogr.html) can parse.

Here are some sources for Colorado boundaries in GeoJSON as well as other formats:
- **CO county borders:** https://data-cdphe.opendata.arcgis.com/datasets/colorado-county-boundaries/
- **CO tract borders:** https://data-cdphe.opendata.arcgis.com/datasets/colorado-census-tract-boundaries/
- **CO area/economic development districts:** (merged from the EDD list, filtered to Colorado)

The "Area Development Districts" mentioned in the KY cancer focus site
come from a list of "Economic Development Districts", which are groupings
of counties. These can be found in tabular form on StatsAmerica for the
US, released once per year in January.

- **Economic Development Districts:** https://www.statsamerica.org/geography-tools.aspx
