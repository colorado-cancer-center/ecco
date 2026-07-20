#!/usr/bin/env bash
set -Eeuo pipefail

# ==============================================================================
# Download, classify, dissolve, simplify, and split Colorado's 2020 Census
# blocks into urban and rural GeoJSON files.
#
# The data comes from the following source:
# https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html
# specifically the TIGER 2020 tabulation blocks for Colorado, which include the
# Census urban/rural indicator.
#
# Requirements:
#   curl
#   unzip
#   ogr2ogr
#   ogrinfo
#   mapshaper
#
# Installation examples:
#   npm install -g mapshaper
#   apt-get install -y curl unzip gdal-bin
#
# Usage:
#   chmod +x get_urban_rural_geojson.sh
#   ./get_urban_rural_geojson.sh
#
# Optional overrides:
#   RETAIN=25% PRECISION=0.00001 PRECISION_DECIMALS=5 \
#     ./get_urban_rural_geojson.sh
# ==============================================================================

# Percentage of vertices retained by Mapshaper.
RETAIN="${RETAIN:-25%}"

# Mapshaper coordinate precision in decimal degrees.
PRECISION="${PRECISION:-0.00001}"

# GDAL GeoJSON coordinate precision in decimal places.
# Keep this consistent with PRECISION:
#   0.0001  -> 4
#   0.00001 -> 5
PRECISION_DECIMALS="${PRECISION_DECIMALS:-5}"

CENSUS_URL="https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_08_tabblock20.zip"

WORK_DIR="${WORK_DIR:-/tmp/colorado-urban-rural-work}"
OUTPUT_DIR="${OUTPUT_DIR:-./colorado-urban-rural-output}"

ZIP_FILE="${WORK_DIR}/tl_2020_08_tabblock20.zip"
SOURCE_SHP="${WORK_DIR}/tl_2020_08_tabblock20.shp"

BLOCKS_GEOJSON="${WORK_DIR}/colorado-blocks-wgs84.geojson"
COMBINED_GEOJSON="${WORK_DIR}/colorado-urban-rural-simplified.geojson"

URBAN_GEOJSON="${OUTPUT_DIR}/colorado-urban.geojson"
RURAL_GEOJSON="${OUTPUT_DIR}/colorado-rural.geojson"

require_command() {
  local command_name="$1"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Error: required command '$command_name' was not found." >&2
    exit 1
  fi
}

get_feature_count() {
  local file="$1"
  local layer="$2"

  ogrinfo -ro -so "$file" "$layer" 2>/dev/null |
    awk '/Feature Count:/ { print $3; exit }'
}

for command_name in curl unzip ogr2ogr ogrinfo mapshaper; do
  require_command "$command_name"
done

mkdir -p "$WORK_DIR" "$OUTPUT_DIR"

# ------------------------------------------------------------------------------
# Download
# ------------------------------------------------------------------------------

if [[ -s "$ZIP_FILE" ]]; then
  echo "Census ZIP already exists; skipping download:"
  echo "  $ZIP_FILE"
else
  echo "Downloading official Colorado 2020 Census blocks..."

  curl \
    --fail \
    --location \
    --retry 3 \
    --retry-delay 2 \
    --output "${ZIP_FILE}.tmp" \
    "$CENSUS_URL"

  mv "${ZIP_FILE}.tmp" "$ZIP_FILE"
fi

# ------------------------------------------------------------------------------
# Extract
# ------------------------------------------------------------------------------

if [[ -s "$SOURCE_SHP" ]]; then
  echo "Source shapefile already exists; skipping extraction:"
  echo "  $SOURCE_SHP"
else
  echo "Extracting Census shapefile..."

  unzip -o "$ZIP_FILE" -d "$WORK_DIR" >/dev/null
fi

if [[ ! -s "$SOURCE_SHP" ]]; then
  echo "Error: expected shapefile was not found after extraction:" >&2
  echo "  $SOURCE_SHP" >&2
  exit 1
fi

# A shapefile requires its associated DBF and SHX files.
for required_extension in dbf shx; do
  required_file="${SOURCE_SHP%.shp}.${required_extension}"

  if [[ ! -s "$required_file" ]]; then
    echo "Error: required shapefile component is missing:" >&2
    echo "  $required_file" >&2
    exit 1
  fi
done

# ------------------------------------------------------------------------------
# Remove generated files from previous runs
#
# GeoJSON does not reliably support ogr2ogr's DeleteLayer operation, so remove
# the entire destination file instead of using ogr2ogr -overwrite.
# ------------------------------------------------------------------------------

rm -f \
  "$BLOCKS_GEOJSON" \
  "$COMBINED_GEOJSON" \
  "$URBAN_GEOJSON" \
  "$RURAL_GEOJSON"

# ------------------------------------------------------------------------------
# Convert source blocks to WGS84 GeoJSON
# ------------------------------------------------------------------------------

echo "Converting the source shapefile to WGS84 GeoJSON..."

ogr2ogr \
  -f GeoJSON \
  -t_srs EPSG:4326 \
  -select UR20 \
  -lco RFC7946=YES \
  "$BLOCKS_GEOJSON" \
  "$SOURCE_SHP"

if [[ ! -s "$BLOCKS_GEOJSON" ]]; then
  echo "Error: block conversion did not create a GeoJSON file." >&2
  exit 1
fi

# ------------------------------------------------------------------------------
# Classify, dissolve, and simplify
#
# UR20 values:
#   U = urban
#   R = rural
#
# Both classes are processed in the same Mapshaper dataset so their shared
# generalized boundaries remain aligned.
# ------------------------------------------------------------------------------

echo "Classifying, dissolving, and simplifying with Mapshaper..."
echo "  Vertex retention: $RETAIN"
echo "  Coordinate precision: $PRECISION"

mapshaper "$BLOCKS_GEOJSON" \
  -each 'classification = UR20 === "U" ? "urban" : "rural"' \
  -dissolve classification \
  -simplify "$RETAIN" weighted keep-shapes \
  -clean \
  -filter-fields classification \
  -o \
    format=geojson \
    precision="$PRECISION" \
    "$COMBINED_GEOJSON"

if [[ ! -s "$COMBINED_GEOJSON" ]]; then
  echo "Error: Mapshaper did not create the combined GeoJSON file." >&2
  exit 1
fi

# ------------------------------------------------------------------------------
# Split the simplified dataset
#
# Explicit output layer names make ogrinfo validation predictable.
# ------------------------------------------------------------------------------

echo "Splitting the simplified layer into urban and rural GeoJSON files..."

ogr2ogr \
  -f GeoJSON \
  -where "classification = 'urban'" \
  -nln urban \
  -lco RFC7946=YES \
  -lco COORDINATE_PRECISION="$PRECISION_DECIMALS" \
  "$URBAN_GEOJSON" \
  "$COMBINED_GEOJSON"

ogr2ogr \
  -f GeoJSON \
  -where "classification = 'rural'" \
  -nln rural \
  -lco RFC7946=YES \
  -lco COORDINATE_PRECISION="$PRECISION_DECIMALS" \
  "$RURAL_GEOJSON" \
  "$COMBINED_GEOJSON"

# ------------------------------------------------------------------------------
# Validate outputs
# ------------------------------------------------------------------------------

if [[ ! -s "$URBAN_GEOJSON" ]]; then
  echo "Error: the urban GeoJSON file was not created or is empty." >&2
  exit 1
fi

if [[ ! -s "$RURAL_GEOJSON" ]]; then
  echo "Error: the rural GeoJSON file was not created or is empty." >&2
  exit 1
fi

urban_count="$(get_feature_count "$URBAN_GEOJSON" urban || true)"
rural_count="$(get_feature_count "$RURAL_GEOJSON" rural || true)"

if [[ ! "$urban_count" =~ ^[0-9]+$ ]]; then
  echo "Error: unable to determine the urban feature count." >&2
  echo "Inspect the file with:" >&2
  echo "  ogrinfo -al -so \"$URBAN_GEOJSON\"" >&2
  exit 1
fi

if [[ ! "$rural_count" =~ ^[0-9]+$ ]]; then
  echo "Error: unable to determine the rural feature count." >&2
  echo "Inspect the file with:" >&2
  echo "  ogrinfo -al -so \"$RURAL_GEOJSON\"" >&2
  exit 1
fi

if (( urban_count == 0 )); then
  echo "Error: the urban output contains no features." >&2
  exit 1
fi

if (( rural_count == 0 )); then
  echo "Error: the rural output contains no features." >&2
  exit 1
fi

# ------------------------------------------------------------------------------
# Results
# ------------------------------------------------------------------------------

echo
echo "Finished successfully."
echo
echo "Urban:"
echo "  File:     $URBAN_GEOJSON"
echo "  Features: $urban_count"
du -h "$URBAN_GEOJSON" | awk '{ print "  Size:     " $1 }'

echo
echo "Rural:"
echo "  File:     $RURAL_GEOJSON"
echo "  Features: $rural_count"
du -h "$RURAL_GEOJSON" | awk '{ print "  Size:     " $1 }'

echo
echo "Combined intermediate:"
echo "  $COMBINED_GEOJSON"