from __future__ import annotations

import argparse
import json
from pathlib import Path

import cdsapi


NANJING_BBOX = [32.70, 118.30, 31.20, 119.30]
DEFAULT_VARIABLES = [
    "2m_temperature",
    "total_precipitation",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_pressure",
    "leaf_area_index_high_vegetation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download ERA5-Land monthly means for Nanjing.")
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("d:/4c/data/raw/era5/nanjing/era5_land_monthly_nanjing_2020_2024.nc"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("d:/4c/data/raw/era5/nanjing/era5_land_monthly_nanjing_2020_2024.request.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    years = [str(year) for year in range(args.start_year, args.end_year + 1)]
    months = [f"{month:02d}" for month in range(1, 13)]
    request = {
        "product_type": "monthly_averaged_reanalysis",
        "variable": DEFAULT_VARIABLES,
        "year": years,
        "month": months,
        "time": "00:00",
        "area": NANJING_BBOX,
        "format": "netcdf",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(
            {
                "dataset": "reanalysis-era5-land-monthly-means",
                "request": request,
                "output_path": str(args.output),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    client = cdsapi.Client(timeout=8640, quiet=False)
    client.retrieve("reanalysis-era5-land-monthly-means", request, str(args.output))
    print(json.dumps({"output_path": str(args.output), "years": years, "variables": DEFAULT_VARIABLES}, indent=2))


if __name__ == "__main__":
    main()
