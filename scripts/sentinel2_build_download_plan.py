import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a first-round Sentinel-2 download plan from ranked tile results."
    )
    parser.add_argument("--tiles-json", required=True)
    parser.add_argument("--max-tiles", type=int, default=4)
    parser.add_argument("--min-overlap-ratio", type=float, default=0.05)
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tiles_path = Path(args.tiles_json)
    payload = json.loads(tiles_path.read_text(encoding="utf-8"))

    selected = [
        tile
        for tile in payload["tiles"]
        if (tile.get("best_scene_overlap_ratio") or 0.0) >= args.min_overlap_ratio
    ][: args.max_tiles]

    plan_rows: list[dict[str, Any]] = []
    for order, tile in enumerate(selected, start=1):
        scene_id = tile["best_scene_id"]
        plan_rows.append(
            {
                "priority": order,
                "tile_id": tile["tile_id"],
                "scene_id": scene_id,
                "scene_datetime": tile.get("best_scene_datetime"),
                "cloud_cover": tile.get("best_scene_cloud_cover"),
                "overlap_ratio": tile.get("best_scene_overlap_ratio"),
                "remote_uri": tile.get("best_scene_s3_href"),
                "target_filename": scene_id if scene_id.endswith(".SAFE") else f"{scene_id}.SAFE",
                "notes": "first_round_download",
            }
        )

    output_dir = Path(args.output_dir) if args.output_dir else tiles_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = tiles_path.stem.replace("sentinel2_tiles_", "sentinel2_download_plan_")
    json_out = output_dir / f"{stem}.json"
    csv_out = output_dir / f"{stem}.csv"

    result = {
        "area_name": payload["area_name"],
        "bbox": payload["bbox"],
        "max_tiles": args.max_tiles,
        "min_overlap_ratio": args.min_overlap_ratio,
        "selected_count": len(plan_rows),
        "downloads": plan_rows,
    }
    json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "priority",
        "tile_id",
        "scene_id",
        "scene_datetime",
        "cloud_cover",
        "overlap_ratio",
        "remote_uri",
        "target_filename",
        "notes",
    ]
    with csv_out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(plan_rows)

    print(f"Saved {len(plan_rows)} planned downloads")
    print(f"JSON: {json_out}")
    print(f"CSV:  {csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
