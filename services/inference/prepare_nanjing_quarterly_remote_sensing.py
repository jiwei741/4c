from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.quarterly_utils import (
    load_grid_records,
    normalize_quarter_label,
    normalize_node_id,
    read_csv_rows,
    quarter_sort_key,
    write_csv_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize high-precision quarterly Sentinel-2 inputs for Nanjing 309-grid training.")
    parser.add_argument(
        "--grid-input",
        type=Path,
        default=PROJECT_ROOT / "data_for_memberA/data_for_memberA/grid_nodes.csv",
    )
    parser.add_argument(
        "--features-input",
        type=Path,
        default=PROJECT_ROOT / "data_for_memberA/data_for_memberA/sentinel2_features.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    grid_records = load_grid_records(args.grid_input)
    feature_rows = read_csv_rows(args.features_input)

    clean_grid_path = output_dir / "grid_nodes.csv"
    clean_features_path = output_dir / "sentinel2_features.csv"
    summary_path = output_dir / "sentinel2_features.summary.json"

    write_csv_rows(
        clean_grid_path,
        ["node_id", "latitude", "longitude", "max_lat", "max_lon", "min_lat", "min_lon"],
        [
            {
                "node_id": record.node_id,
                "latitude": record.latitude,
                "longitude": record.longitude,
                "max_lat": record.extra.get("max_lat", ""),
                "max_lon": record.extra.get("max_lon", ""),
                "min_lat": record.extra.get("min_lat", ""),
                "min_lon": record.extra.get("min_lon", ""),
            }
            for record in grid_records
        ],
    )

    normalized_features = []
    for row in feature_rows:
        timestamp = normalize_quarter_label(row["timestamp"])
        year_str, quarter_token = timestamp.split("-Q", 1)
        normalized_features.append(
            {
                "timestamp": timestamp,
                "node_id": normalize_node_id(row["node_id"]),
                "year": row.get("year", "").strip() or year_str,
                "quarter": row.get("quarter", "").strip() or f"Q{quarter_token}",
                "ndvi_mean": row.get("ndvi_mean", "").strip(),
                "forest_ratio": row.get("forest_ratio", "").strip(),
                "farmland_ratio": row.get("farmland_ratio", "").strip(),
                "water_ratio": row.get("water_ratio", "").strip(),
                "built_ratio": row.get("built_ratio", "").strip(),
                "vegetation_area_ratio": row.get("vegetation_area_ratio", "").strip(),
            }
        )

    normalized_features.sort(key=lambda row: (quarter_sort_key(row["timestamp"]), int(row["node_id"])))

    write_csv_rows(
        clean_features_path,
        [
            "timestamp",
            "node_id",
            "year",
            "quarter",
            "ndvi_mean",
            "forest_ratio",
            "farmland_ratio",
            "water_ratio",
            "built_ratio",
            "vegetation_area_ratio",
        ],
        normalized_features,
    )

    timestamps = sorted({row["timestamp"] for row in normalized_features}, key=quarter_sort_key)
    node_ids = {row["node_id"] for row in normalized_features}
    counts = Counter(row["timestamp"] for row in normalized_features)
    summary = {
        "source_grid_path": str(args.grid_input),
        "source_features_path": str(args.features_input),
        "grid_rows": len(grid_records),
        "feature_rows": len(normalized_features),
        "num_nodes": len(node_ids),
        "num_timestamps": len(timestamps),
        "timestamps": timestamps,
        "feature_columns": [
            "ndvi_mean",
            "forest_ratio",
            "farmland_ratio",
            "water_ratio",
            "built_ratio",
            "vegetation_area_ratio",
        ],
        "rows_per_timestamp": dict(sorted(counts.items(), key=lambda item: quarter_sort_key(item[0]))),
        "clean_grid_path": str(clean_grid_path),
        "clean_features_path": str(clean_features_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
