from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.feature_stitching import haversine_km


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill missing quarterly labels for the Nanjing grid using scaled same-node fallback and spatial nearest-neighbor fill."
    )
    parser.add_argument("--grid", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv")
    parser.add_argument("--primary", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels_qc.csv")
    parser.add_argument("--backup", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels_scaled.csv")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels_qc_complete.csv",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/labels_qc_complete.summary.json",
    )
    parser.add_argument("--label-column", default="net_carbon_flux")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grid_rows = read_csv_rows(args.grid)
    grid_order = [row["node_id"].strip() for row in grid_rows]
    coords = {
        row["node_id"].strip(): (float(row["latitude"]), float(row["longitude"]))
        for row in grid_rows
    }

    primary = read_label_rows(args.primary, args.label_column, "qc")
    backup = read_label_rows(args.backup, args.label_column, "scaled_fallback")

    timestamps = sorted(
        {timestamp for timestamp, _ in primary.keys()} | {timestamp for timestamp, _ in backup.keys()}
    )
    completed_rows: list[dict[str, str | float]] = []
    summary = {
        "timestamps": timestamps,
        "primary_rows": len(primary),
        "backup_rows": len(backup),
        "filled_from_primary": 0,
        "filled_from_backup": 0,
        "filled_from_nearest": 0,
    }

    for timestamp in timestamps:
        values_for_timestamp: dict[str, tuple[float, str]] = {}

        for node_id in grid_order:
            key = (timestamp, node_id)
            if key in primary:
                value = primary[key]
                values_for_timestamp[node_id] = (value, "qc")
                summary["filled_from_primary"] += 1
            elif key in backup:
                value = backup[key]
                values_for_timestamp[node_id] = (value, "scaled_fallback")
                summary["filled_from_backup"] += 1

        missing_nodes = [node_id for node_id in grid_order if node_id not in values_for_timestamp]
        if missing_nodes:
            available = list(values_for_timestamp.items())
            if not available:
                raise ValueError(f"timestamp {timestamp} has no available labels to impute from")
            for missing_node in missing_nodes:
                nearest_node, nearest_value = find_nearest_value(missing_node, available, coords)
                values_for_timestamp[missing_node] = (nearest_value, f"nearest:{nearest_node}")
                summary["filled_from_nearest"] += 1

        for node_id in grid_order:
            value, source = values_for_timestamp[node_id]
            completed_rows.append(
                {
                    "timestamp": timestamp,
                    "node_id": node_id,
                    args.label_column: value,
                    "label_source": source,
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "node_id", args.label_column, "label_source"])
        writer.writeheader()
        writer.writerows(completed_rows)

    summary["output_rows"] = len(completed_rows)
    summary["output_path"] = str(args.output)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_label_rows(path: Path, label_column: str, source_name: str) -> dict[tuple[str, str], float]:
    rows = read_csv_rows(path)
    values: dict[tuple[str, str], float] = {}
    for row in rows:
        key = (row["timestamp"].strip(), row["node_id"].strip())
        if key in values:
            raise ValueError(f"duplicate label row in {source_name}: {key}")
        values[key] = float(row[label_column])
    return values


def find_nearest_value(
    missing_node_id: str,
    available: list[tuple[str, tuple[float, str]]],
    coords: dict[str, tuple[float, float]],
) -> tuple[str, float]:
    source_lat, source_lon = coords[missing_node_id]
    best_node_id = ""
    best_value = math.nan
    best_distance = float("inf")
    for node_id, (value, _) in available:
        target_lat, target_lon = coords[node_id]
        distance = haversine_km(source_lat, source_lon, target_lat, target_lon)
        if distance < best_distance:
            best_distance = distance
            best_node_id = node_id
            best_value = value
    if best_node_id == "":
        raise RuntimeError(f"failed to find nearest value for node {missing_node_id}")
    return best_node_id, best_value


if __name__ == "__main__":
    main()
