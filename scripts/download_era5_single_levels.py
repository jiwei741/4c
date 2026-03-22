import argparse
import calendar
from pathlib import Path
import sys

import cdsapi
from dotenv import dotenv_values


DEFAULT_VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_temperature",
    "total_precipitation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download ERA5 single levels data for a study area."
    )
    parser.add_argument("--area-name", default="nanjing")
    parser.add_argument("--north", type=float, required=True)
    parser.add_argument("--west", type=float, required=True)
    parser.add_argument("--south", type=float, required=True)
    parser.add_argument("--east", type=float, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument(
        "--variables",
        nargs="+",
        default=DEFAULT_VARIABLES,
        help="ERA5 variable names",
    )
    parser.add_argument(
        "--days",
        nargs="+",
        type=int,
        default=None,
        help="Specific days to download. Defaults to all valid days in the month.",
    )
    parser.add_argument(
        "--times",
        nargs="+",
        default=None,
        help="Specific times like 00:00 12:00. Defaults to all 24 hours.",
    )
    parser.add_argument(
        "--data-format",
        default="netcdf",
        choices=["netcdf", "grib"],
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Defaults to data/raw/era5/<area-name>",
    )
    return parser.parse_args()


def load_cds_client(project_root: Path) -> cdsapi.Client:
    cdsapirc = Path.home() / ".cdsapirc"
    if cdsapirc.exists():
        return cdsapi.Client()

    env = dotenv_values(project_root / ".env")
    cds_url = env.get("CDSAPI_URL", "").strip()
    cds_key = env.get("CDSAPI_KEY", "").strip()

    if not cds_url or not cds_key:
        raise RuntimeError("CDSAPI_URL or CDSAPI_KEY is missing in .env")

    return cdsapi.Client(url=cds_url, key=cds_key)


def build_request(args: argparse.Namespace) -> dict:
    _, last_day = calendar.monthrange(args.year, args.month)
    days = (
        [f"{day:02d}" for day in args.days]
        if args.days
        else [f"{day:02d}" for day in range(1, last_day + 1)]
    )
    times = args.times if args.times else [f"{hour:02d}:00" for hour in range(24)]

    return {
        "product_type": ["reanalysis"],
        "variable": args.variables,
        "year": [str(args.year)],
        "month": [f"{args.month:02d}"],
        "day": days,
        "time": times,
        "data_format": args.data_format,
        "download_format": "unarchived",
        "area": [args.north, args.west, args.south, args.east],
    }


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    client = load_cds_client(project_root)

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else project_root / "data" / "raw" / "era5" / args.area_name
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"era5_{args.area_name}_{args.year}_{args.month:02d}.nc"
    request = build_request(args)

    print(f"Downloading to {output_file}")
    client.retrieve("reanalysis-era5-single-levels", request).download(str(output_file))
    print(f"Saved {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
