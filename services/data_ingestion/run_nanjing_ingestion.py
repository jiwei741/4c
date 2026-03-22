from __future__ import annotations

import argparse
import sys
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_data_ingestion.runner import run_python_script


REPO_ROOT = SERVICE_ROOT.parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
INFERENCE_ROOT = REPO_ROOT / "services" / "inference"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Entry point for the Nanjing data ingestion service.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("sentinel-search", help="Search Sentinel-2 catalog for Nanjing.")
    search.add_argument("--start-date", default="2025-01-01")
    search.add_argument("--end-date", default="2025-01-31")
    search.add_argument("--cloud-cover-max", default="20")
    search.add_argument("--top", default="20")

    download = subparsers.add_parser("sentinel-download", help="Download Sentinel-2 SAFE by plan.")
    download.add_argument("--plan-json", required=True)
    download.add_argument("--priority", default="1")

    era5 = subparsers.add_parser("era5-land", help="Download ERA5-Land monthly means for Nanjing.")
    era5.add_argument("--start-year", default="2020")
    era5.add_argument("--end-year", default="2024")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "sentinel-search":
        return run_python_script(
            SCRIPTS_ROOT / "sentinel2_search.py",
            [
                "--area-name",
                "nanjing",
                "--north",
                "32.7",
                "--west",
                "118.3",
                "--south",
                "31.2",
                "--east",
                "119.3",
                "--start-date",
                args.start_date,
                "--end-date",
                args.end_date,
                "--cloud-cover-max",
                args.cloud_cover_max,
                "--top",
                args.top,
            ],
            cwd=REPO_ROOT,
        )

    if args.command == "sentinel-download":
        return run_python_script(
            SCRIPTS_ROOT / "sentinel2_download.py",
            [
                "--plan-json",
                args.plan_json,
                "--priority",
                args.priority,
            ],
            cwd=REPO_ROOT,
        )

    if args.command == "era5-land":
        return run_python_script(
            INFERENCE_ROOT / "download_nanjing_era5_land_monthly.py",
            [
                "--start-year",
                args.start_year,
                "--end-year",
                args.end_year,
            ],
            cwd=REPO_ROOT,
        )

    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
