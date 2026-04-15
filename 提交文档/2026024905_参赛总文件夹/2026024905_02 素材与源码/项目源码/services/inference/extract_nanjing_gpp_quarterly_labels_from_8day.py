from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.geotiff_sampling import open_geotiff, sample_value
from spatio_eco_inference.quarterly_utils import (
    load_grid_records,
    quarter_sort_key,
    to_quarter_label,
    write_csv_rows,
)


DATE_PATTERN = re.compile(r"(20\d{2})(\d{2})(\d{2})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract quarterly GPP labels for Nanjing 309-grid directly from AppEEARS MOD17A2HGF 8-day GeoTIFF files."
    )
    parser.add_argument("--grid", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv")
    parser.add_argument(
        "--tif-dir",
        type=Path,
        default=PROJECT_ROOT / "data/raw/gpp/nanjing/appeears_mod17a2hgf_061",
        help="Directory that contains AppEEARS-downloaded MOD17A2HGF Gpp_500m GeoTIFF files.",
    )
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels.csv")
    parser.add_argument("--summary", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels.summary.json")
    parser.add_argument("--label-column", default="net_carbon_flux")
    parser.add_argument(
        "--quarter-aggregator",
        choices=["sum", "mean"],
        default="sum",
        help="Gpp_500m is in kgC/m^2/8day; sum is the physically safer default for quarter totals.",
    )
    parser.add_argument("--qc-dir", type=Path, default=None, help="Directory that contains matching Psn_QC_500m GeoTIFF files.")
    parser.add_argument(
        "--apply-qc-filter",
        action="store_true",
        help="Filter GPP samples using Psn_QC_500m. Accepted values are MODLAND good, dead detector off, SCF_QC in {0,1}.",
    )
    parser.add_argument("--gpp-scale-factor", type=float, default=0.0001)
    parser.add_argument("--fallback-radius-pixels", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grid_records = load_grid_records(args.grid)
    tif_files = sorted(
        [
            path
            for path in args.tif_dir.iterdir()
            if path.suffix.lower() in {".tif", ".tiff"} and "Gpp_500m" in path.name
        ]
    )
    tif_files = [path for path in tif_files if DATE_PATTERN.search(path.name)]
    if not tif_files:
        raise FileNotFoundError(f"no AppEEARS GPP GeoTIFF files found in {args.tif_dir}")

    qc_files_by_date: dict[str, Path] = {}
    if args.apply_qc_filter:
        if args.qc_dir is None:
            raise ValueError("--apply-qc-filter requires --qc-dir")
        qc_candidates = sorted([path for path in args.qc_dir.iterdir() if path.suffix.lower() in {".tif", ".tiff"}])
        qc_candidates = [path for path in qc_candidates if "Psn_QC_500m" in path.name and DATE_PATTERN.search(path.name)]
        qc_files_by_date = {DATE_PATTERN.search(path.name).group(0): path for path in qc_candidates}  # type: ignore[union-attr]

    quarter_values: dict[tuple[str, str], list[float]] = defaultdict(list)
    sample_stats = {"fallback_count": 0, "empty_count": 0}
    time_steps: dict[str, int] = defaultdict(int)
    qc_stats = {"filtered_count": 0, "accepted_count": 0, "missing_qc_files": 0}

    for tif_path in tif_files:
        year, month, day = parse_date_from_filename(tif_path.name)
        quarter = to_quarter_label(year, month)
        time_steps[quarter] += 1
        array, georef, nodata = open_geotiff(tif_path)
        qc_array = None
        qc_georef = None
        qc_nodata = None
        date_key = f"{year:04d}{month:02d}{day:02d}"
        if args.apply_qc_filter:
            qc_path = qc_files_by_date.get(date_key)
            if qc_path is None:
                qc_stats["missing_qc_files"] += 1
                continue
            qc_array, qc_georef, qc_nodata = open_geotiff(qc_path)
        for record in grid_records:
            value, used_fallback = sample_value(
                array,
                georef,
                record.longitude,
                record.latitude,
                nodata,
                fallback_radius=args.fallback_radius_pixels,
            )
            if value != value:
                sample_stats["empty_count"] += 1
                continue
            if is_invalid_gpp_raw(value):
                sample_stats["empty_count"] += 1
                continue
            if args.apply_qc_filter:
                qc_value, _ = sample_value(
                    qc_array,
                    qc_georef,
                    record.longitude,
                    record.latitude,
                    qc_nodata,
                    fallback_radius=args.fallback_radius_pixels,
                )  # type: ignore[arg-type]
                if qc_value != qc_value or not is_psn_qc_acceptable(qc_value):
                    qc_stats["filtered_count"] += 1
                    continue
                qc_stats["accepted_count"] += 1
            if used_fallback:
                sample_stats["fallback_count"] += 1
            quarter_values[(quarter, record.node_id)].append(float(value) * args.gpp_scale_factor)

    output_rows = []
    for (quarter, node_id), values in sorted(
        quarter_values.items(),
        key=lambda item: (quarter_sort_key(item[0][0]), int(item[0][1])),
    ):
        if args.quarter_aggregator == "mean":
            label_value = float(sum(values) / len(values))
        else:
            label_value = float(sum(values))
        output_rows.append(
            {
                "timestamp": quarter,
                "node_id": node_id,
                args.label_column: label_value,
            }
        )

    write_csv_rows(args.output, ["timestamp", "node_id", args.label_column], output_rows)

    summary = {
        "tif_files": len(tif_files),
        "quarters": sorted(time_steps.keys(), key=quarter_sort_key),
        "quarter_file_counts": dict(sorted(time_steps.items(), key=lambda item: quarter_sort_key(item[0]))),
        "quarter_rows": len(output_rows),
        "num_nodes": len(grid_records),
        "fallback_count": sample_stats["fallback_count"],
        "empty_count": sample_stats["empty_count"],
        "qc_filter_applied": bool(args.apply_qc_filter),
        "qc_filtered_count": qc_stats["filtered_count"],
        "qc_accepted_count": qc_stats["accepted_count"],
        "qc_missing_files": qc_stats["missing_qc_files"],
        "gpp_scale_factor": args.gpp_scale_factor,
        "quarter_aggregator": args.quarter_aggregator,
        "output_path": str(args.output),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def parse_date_from_filename(filename: str) -> tuple[int, int, int]:
    match = DATE_PATTERN.search(filename)
    if not match:
        raise ValueError(f"cannot parse YYYYMMDD from filename: {filename}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def is_invalid_gpp_raw(value: float) -> bool:
    rounded = int(round(value))
    if rounded < 0:
        return True
    if rounded > 30000:
        return True
    return False


def is_psn_qc_acceptable(value: float) -> bool:
    qc = int(round(value))
    modland_qc = qc & 0b1
    dead_detector = (qc >> 2) & 0b1
    scf_qc = (qc >> 5) & 0b111
    return modland_qc == 0 and dead_detector == 0 and scf_qc in {0, 1}


if __name__ == "__main__":
    main()
