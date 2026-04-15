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

from spatio_eco_inference.quarterly_utils import (
    load_grid_records,
    parse_date_like,
    quarter_sort_key,
    to_quarter_label,
    write_csv_rows,
)
from spatio_eco_inference.geotiff_sampling import open_geotiff, sample_value


FILENAME_PATTERN = re.compile(r"(\d{4})(\d{2})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract quarterly GPP labels for Nanjing 309-grid from monthly GeoTIFF files.")
    parser.add_argument("--grid", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv")
    parser.add_argument("--tif-dir", required=True, type=Path, help="Directory that contains monthly GPP GeoTIFF files.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels.csv")
    parser.add_argument("--summary", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels.summary.json")
    parser.add_argument("--label-column", default="net_carbon_flux")
    parser.add_argument("--quarter-aggregator", choices=["mean", "sum"], default="mean")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grid_records = load_grid_records(args.grid)
    tif_files = sorted([path for path in args.tif_dir.iterdir() if path.suffix.lower() in {".tif", ".tiff"}])
    if not tif_files:
        raise FileNotFoundError(f"no tif files found in {args.tif_dir}")

    monthly_values: dict[tuple[str, str], list[float]] = defaultdict(list)
    monthly_timestamps: set[str] = set()
    sample_stats = {"fallback_count": 0, "empty_count": 0}

    for tif_path in tif_files:
        year, month = parse_timestamp_from_filename(tif_path.name)
        timestamp = f"{year}-{month:02d}"
        monthly_timestamps.add(timestamp)

        array, georef, nodata = open_geotiff(tif_path)
        for record in grid_records:
            value, used_fallback = sample_value(array, georef, record.longitude, record.latitude, nodata)
            if value != value:
                sample_stats["empty_count"] += 1
                continue
            if used_fallback:
                sample_stats["fallback_count"] += 1
            monthly_values[(timestamp, record.node_id)].append(value)

    quarter_groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for (timestamp, node_id), values in monthly_values.items():
        year, month = parse_date_like(timestamp)
        quarter = to_quarter_label(year, month)
        quarter_groups[(quarter, node_id)].extend(values)

    output_rows = []
    for (quarter, node_id), values in sorted(
        quarter_groups.items(),
        key=lambda item: (quarter_sort_key(item[0][0]), int(item[0][1])),
    ):
        if args.quarter_aggregator == "sum":
            label_value = float(sum(values))
        else:
            label_value = float(sum(values) / len(values))
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
        "monthly_timestamps": len(monthly_timestamps),
        "quarter_rows": len(output_rows),
        "num_nodes": len(grid_records),
        "fallback_count": sample_stats["fallback_count"],
        "empty_count": sample_stats["empty_count"],
        "output_path": str(args.output),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def parse_timestamp_from_filename(filename: str) -> tuple[int, int]:
    match = FILENAME_PATTERN.search(filename)
    if not match:
        raise ValueError(f"cannot parse YYYYMM from filename: {filename}")
    return int(match.group(1)), int(match.group(2))


if __name__ == "__main__":
    main()
