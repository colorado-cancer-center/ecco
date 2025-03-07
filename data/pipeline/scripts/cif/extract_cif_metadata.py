#!/usr/bin/env python

import contextlib
import glob
import csv
import json
import click
import re
from collections import defaultdict

# create warning, error colors to use in output
WARNING = '\033[93m'
ERROR = '\033[91m'
BOLD = '\033[1;37m'
ENDC = '\033[0m'

# whether to skip merging cancer data into the metadata
# (we get cancer incidence and mortality from SCP now so it's a bit redundant to include it in the CiF metadata, but the
# current hardcoded CiF meta includes it, and i could imagine wanting to compare againt the SCP data in the future...)
SKIP_CANCER_MEASURE_CATEGORIES = False

# whether to skip "SVI"(?) measure categories
# these were introduced in sometime before february 2025; we'll see about including
# them, but for now we'll ignore them
SKIP_SVI_MEASURE_CATEGORIES = True

# canonical ordering of categories, to be retained in output:
CANONICAL_CATEGORY_ORDER = [
    'sociodemographics', 'economy', 'environment', 'housingtrans',
    'rfandscreening', 'fooddesert', 'disparities',
    'cancerincidence', 'cancermortality'
]

SOURCES_TO_URLS = {
    'ACS': 'https://data.census.gov/',
    'Decennial Census': 'https://www.census.gov/programs-surveys/decennial-census.html',
    'EJScreen': 'https://www.epa.gov/ejscreen',
    'EPA': 'https://www.epa.gov/',
    'FCC': 'https://www.fcc.gov/',
    'CDC PLACES': 'https://www.cdc.gov/places/',
    'USDA ERS': "https://www.ers.usda.gov/data-products/food-access-research-atlas/",
    "US Cancer Statistics": "https://www.cdc.gov/united-states-cancer-statistics/index.html",
    "State Cancer Profiles": "https://statecancerprofiles.cancer.gov/",
}

def resolve_source_url(source):
    for key, value in SOURCES_TO_URLS.items():
        if key in source:
            return value
    return ""

FORMATS_TO_UNITS = {
    "pct": "MeasureUnit.PERCENT",
    "int": "MeasureUnit.COUNT",
}

def resolve_unit(category, label, fmt):
    if category.startswith('cancer_'):
        # all SCP cancer measures are rates
        return "MeasureUnit.RATE"
    elif "$" in label:
        # anything with a dollar sign is a dollar amount
        return "MeasureUnit.DOLLAR_AMOUNT"
    elif "Segregation" in label:
        # all segregation indices are 'least-most' ranges
        return "MeasureUnit.LEAST_MOST"
    elif fmt in FORMATS_TO_UNITS:
        # otherwise, defer to the codebook
        return FORMATS_TO_UNITS[fmt]
    else:
        raise Exception(f"Unknown format '{fmt}' for measure '{label}'")
    
@contextlib.contextmanager
def newlines_before_after():
    print()
    yield
    print()

@click.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output JSON file', type=click.File(mode='w'), default='-')
def extract_cif_metadata(input, output):
    """
    Iterates over folder of CiF files and extracts metadata
    in JSON format, defaulting to writing it to stdout.
    """

    # identify the codebook, named measure_dictionary_*.csv
    # and read it into a dictionary

    codebook = {}

    for entry in glob.glob(f'{input}/measure_dictionary_*.csv'):
        with open(entry, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if SKIP_CANCER_MEASURE_CATEGORIES:
                    # skip cancer statistics, since we get cancer data from SCP
                    if 'Cancer' in row['source']:
                        continue
                codebook[row['measure']] = row
            break

    # patch in Monthly Unemployment Rate, since for some
    # reason it's not in the codebook
    codebook["Monthly Unemployment Rate"] = {
        "measure": "Monthly Unemployment Rate",
        "def": "Monthly Unemployment Rate",
        "fmt": "pct",
        "source": "ACS 5-Year, 2019 - 2023"
    }

    # for each csv file in the input folder with a filename
    # of the form us_*_long_*.csv, open the file and read it
    # via csv.DictReader

    # store the results to this 'stats' dict of the form
    # { <measure_category>: { <measure>: <geoms:set>, ... } }
    stats = defaultdict(lambda: defaultdict(set))

    for entry in glob.glob(f'{input}/us_*_*_long_*.csv'):
        if SKIP_CANCER_MEASURE_CATEGORIES:
            # skip cancer, since we get it from SCP
            if '_cancer_' in entry:
                continue

        if SKIP_SVI_MEASURE_CATEGORIES:
            # skip cancer, since we get it from SCP
            if '_svi_' in entry:
                continue

        # use a regex to extract the name of the measure category
        # from the filename
        match = re.search(r'us_(.*)_(.*)_long_', entry)
        if match:
            category = match.group(1)
            geom = match.group(2)
        else:
            raise Exception(f"Could not extract category from {entry}")
        
        # more patches: disparity in the input is 'disparities' in our system
        if category == 'disparity':
            category = 'disparities'
            print(f"* Patching category from 'disparity' to 'disparities'")

        print(f"* Processing {entry} ({category})")

        with open(entry, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['State'] != 'Colorado':
                    continue

                # cancer data refers to the measure as 'Site', so remap
                # it here
                if 'Site' in row:
                    row['measure'] = row['Site']

                # remap the weird measure that's suffixed with a month,
                # e.g. "Monthly Unemployment Rate (Nov)"
                if row['measure'].startswith('Monthly Unemployment Rate'):
                    row['measure'] = 'Monthly Unemployment Rate'
                
                stats[category][row['measure']].add(geom)

    # for each category in stats, check that each measure within it occurs
    # as a key in codebook; if it occurs in a different form, e.g. with
    # underscores replaced with spaces, print a warning. if it doesn't occur
    # at all, print it as an error
    error_results = []
    found_in_codebook = set()

    for category in stats:
        for measure in stats[category].keys():
            if measure in codebook:
                found_in_codebook.add(measure)
            elif (measure_without_underscores := measure.replace('_', ' ')) in codebook:
                # check that the version without underscores is in the codebook
                error_results += [f"{WARNING}Warning:{ENDC} {BOLD}{category} -> {measure}{ENDC} not found in codebook, but {BOLD}{measure_without_underscores}{ENDC} is"]
                found_in_codebook.add(measure_without_underscores)
            elif category.startswith('cancer_') and (cancer_type_prefixed := f"{category.replace('cancer_', '').capitalize()} {measure}") in codebook:
                # for some reason SCP cancer entries are all prefixed with 'Incidence ' or 'Mortality '
                # in the codebook, so we need to add that prefix here
                found_in_codebook.add(cancer_type_prefixed)
            else:
                error_results += [f"{ERROR}Error:{ENDC} {BOLD}{category} -> {measure}{ENDC} not found in codebook"]

    
    # find all keys in the codebook that don't exist in
    # found_in_codebook and print them
    with newlines_before_after():
        print("Measures in codebook but not found in data:")
        for measure in codebook:
            if measure not in found_in_codebook:
                print(measure)
        else:
            print("( no missing measures )")

    # sort error results and print it
    with newlines_before_after():
        for line in sorted(error_results):
            print(line)

    # metadata is of the form:
    # { <measure_category>: { <measure1>: { 
    #     "label": "18 to 64 Years Old",
    #     "source": "ACS 5-Year, 2017 - 2021",
    #     "source_url": "https://data.census.gov/",
    #     "unit": MeasureUnit.PERCENT
    # }, ... }, ... }
    metadata = defaultdict(dict)

    for category in stats:
        for measure, geoms in stats[category].items():
            if measure in codebook:
                codebook_entry = codebook[measure]
            elif measure.replace('_', ' ') in codebook:
                codebook_entry = codebook[measure.replace('_', ' ')]
            elif category.startswith('cancer_'):
                # for some reason SCP cancer entries are all prefixed with 'Incidence ' or 'Mortality '
                # in the codebook, so we need to add that prefix here
                codebook_entry = codebook[f"{category.replace('cancer_', '').capitalize()} {measure}"]
            else:
                raise Exception(f"Measure '{measure}' not found in codebook")

            candidate = {
                "label": codebook_entry['def'],
                "source": codebook_entry['source'],
                "source_url": resolve_source_url(codebook_entry['source']),
                "unit": resolve_unit(category, codebook_entry['def'], codebook_entry['fmt'])
            }

            # determine if a measure exists just for counties or tracts, but not both
            if 'county' in geoms and 'tract' not in geoms:
                candidate['county_only'] = True
            elif 'tract' in geoms and 'county' not in geoms:
                candidate['tract_only'] = True

            metadata[category.replace('_', '')][measure] = candidate

    # intersect metadata.keys() and CANONICAL_CATEGORY_ORDER to ensure
    # that there isn't an entry in one that's not in the other
    metadata_keys = set(metadata.keys())
    canonical_keys = set(CANONICAL_CATEGORY_ORDER)

    if metadata_keys != canonical_keys:
        raise Exception(f"{ERROR}Error:{ENDC} Metadata keys {sorted(metadata_keys)} do not match canonical keys {sorted(canonical_keys)}")

    metadata_ordered = {
        category: metadata[category]
        for category in CANONICAL_CATEGORY_ORDER
    }

    # json.dump({k: v for k, v in metadata.items()}, output, indent=2)
    json.dump(metadata_ordered, output, indent=2)

if __name__ == '__main__':
    extract_cif_metadata()
