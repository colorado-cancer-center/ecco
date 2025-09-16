#!/usr/bin/env python

import sys

sys.path.append("/app")

from tools.excel_sheet_import import import_measures_from_sheets

import click
import asyncio

from models.uv import (
    UVExposureCounty
)

# metadata about each sheet in the radon spreadsheet, since there's both a
# county and tract sheet. we assume they're in the same order as this list.
UV_SHEETS_META = [
    {
        "name": "Sheet1",
        "model": UVExposureCounty,
        "fips_col": "COUNTY_FIPS",
        "county_col": "COUNTY",
        "measures": [
            {
                "column": "UV_Wh/m2 2020-2024",
                "measure": "UV_Wh_m2"
            }
        ]
    },
]

@click.command()
@click.argument('excel-path', type=str)
def main(excel_path):
    asyncio.run(import_measures_from_sheets(
        excel_path,
        UV_SHEETS_META,
    ))

if __name__ == '__main__':
    main()
