from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GPP_PATTERN = re.compile(r"^map_(\d{4})(\d{2})\.tif$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether Nanjing quarterly small-model training inputs are ready.")
    parser.add_argument(
        "--summary",
        type=Path,
        default=PROJECT_ROOT / "data/processed/inference/nanjing_quarterly_readiness.json",
    )
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2024)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    expected_months = [
        f"{year}{month:02d}"
        for year in range(args.start_year, args.end_year + 1)
        for month in range(1, 13)
    ]
    summary = {
        "sentinel2": check_file(PROJECT_ROOT / "data/processed/features/nanjing/quarterly/sentinel2_features.csv"),
        "grid_nodes": check_file(PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv"),
        "era5_raw": describe_era5_raw(PROJECT_ROOT / "data/raw/era5/nanjing/era5_land_monthly_nanjing_2020_2024.nc"),
        "era5_monthly_points": check_file(PROJECT_ROOT / "data/processed/features/nanjing/monthly/era5_monthly_points.csv"),
        "era5_quarterly": check_file(PROJECT_ROOT / "data/processed/features/nanjing/quarterly/era5_features.csv"),
        "gpp_monthly": describe_gpp_directory(PROJECT_ROOT / "data/raw/gpp/nanjing/monthly", expected_months),
        "gpp_appeears_8day": describe_appeears_directory(PROJECT_ROOT / "data/raw/gpp/nanjing/appeears_mod17a2hgf_061"),
        "labels": check_file(PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels.csv"),
    }
    summary["training_ready"] = all(
        [
            summary["sentinel2"]["exists"],
            summary["grid_nodes"]["exists"],
            summary["era5_quarterly"]["exists"],
            summary["labels"]["exists"],
        ]
    )
    if summary["training_ready"]:
        summary["next_step"] = (
            "run build_training_dataset.py with configs/nanjing_quarterly_dataset.yaml, "
            "then train lstm_baseline_quarterly.yaml and stgnn_gcn_lstm_quarterly.yaml"
        )
    else:
        missing = []
        if not summary["era5_quarterly"]["exists"]:
            missing.append("generate ERA5 quarterly features")
        if not summary["labels"]["exists"]:
            missing.append("prepare GPP monthly GeoTIFF files or AppEEARS 8-day GeoTIFF files, then generate labels.csv")
        summary["next_step"] = "; ".join(missing) if missing else "check file integrity"

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def check_file(path: Path) -> dict[str, object]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def describe_era5_raw(path: Path) -> dict[str, object]:
    data = check_file(path)
    if not path.exists():
        data["container_type"] = "missing"
        return data
    header = path.read_bytes()[:4]
    data["container_type"] = "zip" if header == b"PK\x03\x04" else "netcdf"
    return data


def describe_gpp_directory(path: Path, expected_months: list[str]) -> dict[str, object]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "existing_count": 0,
            "missing_count": len(expected_months),
            "missing_preview": expected_months[:12],
        }

    existing: dict[str, str] = {}
    invalid: list[str] = []
    for child in sorted(path.iterdir()):
        if child.is_dir():
            continue
        if child.suffix.lower() not in {".tif", ".tiff"}:
            continue
        match = GPP_PATTERN.match(child.name)
        if not match:
            invalid.append(child.name)
            continue
        existing[f"{match.group(1)}{match.group(2)}"] = child.name

    missing = [month for month in expected_months if month not in existing]
    return {
        "path": str(path),
        "exists": True,
        "existing_count": len(existing),
        "invalid_filenames": invalid,
        "missing_count": len(missing),
        "missing_preview": missing[:12],
    }


def describe_appeears_directory(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "tif_count": 0,
        }
    tif_count = sum(1 for child in path.iterdir() if child.is_file() and child.suffix.lower() in {".tif", ".tiff"})
    return {
        "path": str(path),
        "exists": True,
        "tif_count": tif_count,
    }


if __name__ == "__main__":
    main()
