from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

import xarray as xr

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.quarterly_utils import load_grid_records, to_quarter_label, write_csv_rows


YEAR_PATTERN = re.compile(r"_CO2_(20\d{2})_[A-Z_]+_emi\.nc$")
SECTOR_CODES = ["ENE", "IND", "PRO_FFF", "CHE"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build quarterly EDGAR features for Nanjing 309-grid from EDGAR 2025 annual CO2 sector gridmaps."
    )
    parser.add_argument(
        "--grid",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT / "data/raw/edgar/nanjing",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2020, 2021, 2022, 2023, 2024],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/edgar_features.csv",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/edgar_features.summary.json",
    )
    parser.add_argument(
        "--emission-scale",
        choices=["tonnes", "kilotonnes", "megatonnes"],
        default="megatonnes",
        help="Scale used for exported edgar_emission values.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grid_records = load_grid_records(args.grid)
    scale_divisor = {"tonnes": 1.0, "kilotonnes": 1_000.0, "megatonnes": 1_000_000.0}[args.emission_scale]

    sector_zip_paths = {}
    for sector in SECTOR_CODES:
        zip_path = args.input_dir / f"{sector}_emi_nc.zip"
        if not zip_path.exists():
            raise FileNotFoundError(f"missing EDGAR zip for sector {sector}: {zip_path}")
        sector_zip_paths[sector] = zip_path

    samples_by_year: dict[int, dict[str, dict[str, float]]] = defaultdict(dict)
    per_sector_stats: dict[str, dict[str, float]] = {}

    for sector, zip_path in sector_zip_paths.items():
        sector_samples = sample_sector_for_years(zip_path, args.years, grid_records)
        for year, node_values in sector_samples.items():
            for node_id, value in node_values.items():
                samples_by_year[year].setdefault(node_id, {})[sector] = value / scale_divisor
        flat_values = [value / scale_divisor for node_values in sector_samples.values() for value in node_values.values()]
        per_sector_stats[sector] = {
            "min": min(flat_values),
            "max": max(flat_values),
            "mean": sum(flat_values) / len(flat_values),
        }

    output_rows = []
    total_values: list[float] = []
    for year in sorted(args.years):
        for quarter in range(1, 5):
            quarter_label = f"{year}-Q{quarter}"
            for record in grid_records:
                sector_values = samples_by_year[year][record.node_id]
                edgar_total = sum(sector_values.values())
                total_values.append(edgar_total)
                output_rows.append(
                    {
                        "timestamp": quarter_label,
                        "node_id": record.node_id,
                        "edgar_emission": round(edgar_total, 6),
                        "edgar_ene": round(sector_values["ENE"], 6),
                        "edgar_ind": round(sector_values["IND"], 6),
                        "edgar_pro_fff": round(sector_values["PRO_FFF"], 6),
                        "edgar_che": round(sector_values["CHE"], 6),
                        "unit": args.emission_scale,
                        "source_year": year,
                    }
                )

    write_csv_rows(
        args.output,
        [
            "timestamp",
            "node_id",
            "edgar_emission",
            "edgar_ene",
            "edgar_ind",
            "edgar_pro_fff",
            "edgar_che",
            "unit",
            "source_year",
        ],
        output_rows,
    )

    summary = {
        "release": "EDGAR_2025_GHG",
        "substance": "CO2",
        "years": sorted(args.years),
        "num_nodes": len(grid_records),
        "num_rows": len(output_rows),
        "unit": args.emission_scale,
        "output_path": str(args.output),
        "total_stats": {
            "min": min(total_values),
            "max": max(total_values),
            "mean": sum(total_values) / len(total_values),
        },
        "sector_stats": per_sector_stats,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def sample_sector_for_years(
    zip_path: Path,
    years: list[int],
    grid_records,
) -> dict[int, dict[str, float]]:
    requested_years = set(years)
    out: dict[int, dict[str, float]] = {}
    with zipfile.ZipFile(zip_path) as archive:
        members = {extract_year(name): name for name in archive.namelist() if extract_year(name) is not None}
        missing = sorted(requested_years - set(members.keys()))
        if missing:
            raise FileNotFoundError(f"{zip_path.name} is missing years: {missing}")
        for year in sorted(requested_years):
            member = members[year]
            with tempfile.TemporaryDirectory() as temp_dir:
                extracted = Path(temp_dir) / Path(member).name
                extracted.write_bytes(archive.read(member))
                dataset = xr.open_dataset(extracted)
                try:
                    values = {}
                    emissions = dataset["emissions"]
                    for record in grid_records:
                        sampled = float(
                            emissions.sel(
                                lat=record.latitude,
                                lon=record.longitude,
                                method="nearest",
                            ).values
                        )
                        values[record.node_id] = sampled
                finally:
                    dataset.close()
            out[year] = values
    return out


def extract_year(filename: str) -> int | None:
    match = YEAR_PATTERN.search(filename)
    if not match:
        return None
    return int(match.group(1))


if __name__ == "__main__":
    main()
