from __future__ import annotations

import argparse
import contextlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import xarray as xr

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.quarterly_utils import load_grid_records, write_csv_rows


VARIABLE_MAP = {
    "t2m": "t2m",
    "tp": "tp",
    "u10": "u10",
    "v10": "v10",
    "sp": "sp",
    "lai_hv": "lai_hv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract monthly ERA5 point values for Nanjing 309 grid nodes.")
    parser.add_argument(
        "--grid",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv",
    )
    parser.add_argument(
        "--netcdf",
        type=Path,
        default=PROJECT_ROOT / "data/raw/era5/nanjing/era5_land_monthly_nanjing_2020_2024.nc",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/monthly/era5_monthly_points.csv",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/monthly/era5_monthly_points.summary.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grid_records = load_grid_records(args.grid)
    with open_era5_dataset(args.netcdf) as dataset_info:
        dataset = dataset_info["dataset"]
        container_type = dataset_info["container_type"]
        opened_path = dataset_info["opened_path"]

        time_name = resolve_name(dataset, ["valid_time", "time", "date"])
        lat_name = resolve_name(dataset, ["latitude", "lat"])
        lon_name = resolve_name(dataset, ["longitude", "lon"])

        available = {name: name for name in dataset.data_vars}
        selected_variables = {alias: available[name] for alias, name in VARIABLE_MAP.items() if name in available}
        if not selected_variables:
            raise ValueError(f"no expected ERA5 variables found in dataset: {list(dataset.data_vars)}")

        rows = []
        for record in grid_records:
            selected = dataset.sel({lat_name: record.latitude, lon_name: record.longitude}, method="nearest")
            lat_value = float(selected[lat_name].values)
            lon_value = float(selected[lon_name].values)
            for index in range(selected.sizes[time_name]):
                time_value = str(selected[time_name].values[index])[:10]
                row = {
                    "node_id": record.node_id,
                    "valid_time": time_value,
                    "latitude": record.latitude,
                    "longitude": record.longitude,
                    "source_latitude": lat_value,
                    "source_longitude": lon_value,
                }
                for alias, variable_name in selected_variables.items():
                    value = selected[variable_name].values[index]
                    row[alias] = float(value)
                rows.append(row)

    fieldnames = [
        "node_id",
        "valid_time",
        "latitude",
        "longitude",
        "source_latitude",
        "source_longitude",
        "t2m",
        "tp",
        "u10",
        "v10",
        "sp",
        "lai_hv",
    ]
    write_csv_rows(args.output, fieldnames, rows)
    summary = {
        "rows": len(rows),
        "num_nodes": len(grid_records),
        "time_steps": len(rows) // max(len(grid_records), 1),
        "variables": list(selected_variables.keys()),
        "container_type": container_type,
        "source_path": str(args.netcdf),
        "opened_path": str(opened_path),
        "output_path": str(args.output),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def resolve_name(dataset: xr.Dataset, candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate in dataset.coords or candidate in dataset.dims:
            return candidate
    raise KeyError(f"cannot find any of {candidates} in dataset")


@contextlib.contextmanager
def open_era5_dataset(path: Path):
    dataset_path = path
    container_type = "netcdf"
    temporary_directory: tempfile.TemporaryDirectory[str] | None = None

    if zipfile.is_zipfile(path):
        container_type = "zip"
        temporary_directory = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(path) as archive:
            members = [member for member in archive.namelist() if member.lower().endswith(".nc")]
            if not members:
                raise ValueError(f"zip container does not contain any .nc file: {path}")
            member_name = members[0]
            extracted_path = Path(temporary_directory.name) / Path(member_name).name
            extracted_path.write_bytes(archive.read(member_name))
            dataset_path = extracted_path

    dataset = xr.open_dataset(dataset_path, engine="netcdf4")
    try:
        yield {
            "dataset": dataset,
            "container_type": container_type,
            "opened_path": dataset_path,
        }
    finally:
        dataset.close()
        if temporary_directory is not None:
            temporary_directory.cleanup()


if __name__ == "__main__":
    main()
