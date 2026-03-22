from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.quarterly_utils import (
    GridRecord,
    haversine_km,
    load_grid_records,
    parse_date_like,
    quarter_sort_key,
    read_csv_rows,
    to_quarter_label,
    write_csv_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert monthly ERA5 point data into quarterly features for Nanjing 309 grid nodes.")
    parser.add_argument("--grid", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/grid_nodes.csv")
    parser.add_argument("--era5-csv", required=True, type=Path, help="Monthly ERA5 CSV with lat/lon/time/value columns.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/era5_features.csv")
    parser.add_argument("--summary", type=Path, default=PROJECT_ROOT / "data/processed/features/nanjing/quarterly/era5_features.summary.json")
    parser.add_argument("--timestamp-column", default="valid_time")
    parser.add_argument("--lat-column", default="latitude")
    parser.add_argument("--lon-column", default="longitude")
    parser.add_argument("--max-distance-km", type=float, default=35.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    grid_records = load_grid_records(args.grid)
    rows = read_csv_rows(args.era5_csv)

    quarter_point_values: dict[tuple[str, float, float], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        year, month = parse_date_like(row[args.timestamp_column])
        quarter = to_quarter_label(year, month)
        latitude = float(row[args.lat_column])
        longitude = float(row[args.lon_column])
        key = (quarter, latitude, longitude)

        quarter_point_values[key]["t2m"].append(float(row["t2m"]))
        quarter_point_values[key]["tp"].append(float(row["tp"]))
        quarter_point_values[key]["u10"].append(float(row["u10"]))
        quarter_point_values[key]["v10"].append(float(row["v10"]))
        if "sp" in row and row["sp"] != "":
            quarter_point_values[key]["sp"].append(float(row["sp"]))
        if "lai_hv" in row and row["lai_hv"] != "":
            quarter_point_values[key]["lai_hv"].append(float(row["lai_hv"]))

    points_by_quarter: dict[str, list[dict[str, float]]] = defaultdict(list)
    for (quarter, latitude, longitude), values in quarter_point_values.items():
        points_by_quarter[quarter].append(
            {
                "latitude": latitude,
                "longitude": longitude,
                "land_surface_temperature": mean(values["t2m"]),
                "precipitation": sum(values["tp"]),
                "u10_wind": mean(values["u10"]),
                "v10_wind": mean(values["v10"]),
                "surface_pressure": mean(values["sp"]) if values["sp"] else "",
                "lai_high_vegetation": mean(values["lai_hv"]) if values["lai_hv"] else "",
            }
        )

    output_rows = []
    max_distance = 0.0
    quarter_labels = sorted(points_by_quarter.keys(), key=quarter_sort_key)
    for quarter in quarter_labels:
        points = points_by_quarter[quarter]
        for record in grid_records:
            nearest_point, distance_km = nearest_point_for_grid(record, points)
            max_distance = max(max_distance, distance_km)
            if distance_km > args.max_distance_km:
                raise ValueError(
                    f"nearest ERA5 point for node {record.node_id} in {quarter} is {distance_km:.2f} km away; "
                    f"coverage is not enough for Nanjing 309-grid training"
                )
            output_rows.append(
                {
                    "timestamp": quarter,
                    "node_id": record.node_id,
                    "land_surface_temperature": nearest_point["land_surface_temperature"],
                    "u10_wind": nearest_point["u10_wind"],
                    "v10_wind": nearest_point["v10_wind"],
                    "precipitation": nearest_point["precipitation"],
                    "surface_pressure": nearest_point["surface_pressure"],
                    "lai_high_vegetation": nearest_point["lai_high_vegetation"],
                    "source_latitude": nearest_point["latitude"],
                    "source_longitude": nearest_point["longitude"],
                    "assignment_distance_km": round(distance_km, 3),
                }
            )

    write_csv_rows(
        args.output,
        [
            "timestamp",
            "node_id",
            "land_surface_temperature",
            "u10_wind",
            "v10_wind",
            "precipitation",
            "surface_pressure",
            "lai_high_vegetation",
            "source_latitude",
            "source_longitude",
            "assignment_distance_km",
        ],
        output_rows,
    )

    summary = {
        "input_rows": len(rows),
        "output_rows": len(output_rows),
        "num_quarters": len(quarter_labels),
        "num_nodes": len(grid_records),
        "max_assignment_distance_km": round(max_distance, 3),
        "output_path": str(args.output),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def nearest_point_for_grid(record: GridRecord, points: list[dict[str, float]]) -> tuple[dict[str, float], float]:
    best_point = points[0]
    best_distance = haversine_km(record.latitude, record.longitude, points[0]["latitude"], points[0]["longitude"])
    for point in points[1:]:
        distance = haversine_km(record.latitude, record.longitude, point["latitude"], point["longitude"])
        if distance < best_distance:
            best_distance = distance
            best_point = point
    return best_point, best_distance


if __name__ == "__main__":
    main()
