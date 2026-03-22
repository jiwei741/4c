import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Group Sentinel-2 catalog results by tile and rank them for an AOI."
    )
    parser.add_argument("--catalog-json", required=True)
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def parse_tile_id(product_id: str) -> str:
    parts = product_id.split("_")
    return parts[5] if len(parts) > 5 else "UNKNOWN"


def intersection_area(a: list[float], b: list[float]) -> float:
    a_west, a_south, a_east, a_north = a
    b_west, b_south, b_east, b_north = b
    overlap_west = max(a_west, b_west)
    overlap_south = max(a_south, b_south)
    overlap_east = min(a_east, b_east)
    overlap_north = min(a_north, b_north)
    if overlap_east <= overlap_west or overlap_north <= overlap_south:
        return 0.0
    return (overlap_east - overlap_west) * (overlap_north - overlap_south)


def normalize_scene(scene: dict[str, Any], aoi_bbox: list[float]) -> dict[str, Any]:
    bbox = scene.get("bbox") or [0.0, 0.0, 0.0, 0.0]
    overlap = intersection_area(aoi_bbox, bbox)
    aoi_area = intersection_area(aoi_bbox, aoi_bbox)
    return {
        **scene,
        "tile_id": parse_tile_id(scene["id"]),
        "overlap_area": round(overlap, 6),
        "overlap_ratio": round(overlap / aoi_area, 6) if aoi_area else 0.0,
    }


def scene_rank_key(scene: dict[str, Any]) -> tuple[float, float, str]:
    cloud_cover = scene.get("cloud_cover")
    cloud_score = cloud_cover if cloud_cover is not None else 9999.0
    return (-scene["overlap_ratio"], cloud_score, scene.get("datetime") or "")


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.catalog_json)
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))

    bbox_info = payload["bbox"]
    aoi_bbox = [
        bbox_info["west"],
        bbox_info["south"],
        bbox_info["east"],
        bbox_info["north"],
    ]

    scenes = [normalize_scene(scene, aoi_bbox) for scene in payload["products"]]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for scene in scenes:
        grouped[scene["tile_id"]].append(scene)

    rows: list[dict[str, Any]] = []
    for tile_id, tile_scenes in grouped.items():
        best_scene = sorted(tile_scenes, key=scene_rank_key)[0]
        rows.append(
            {
                "tile_id": tile_id,
                "scene_count": len(tile_scenes),
                "best_scene_id": best_scene["id"],
                "best_scene_datetime": best_scene.get("datetime"),
                "best_scene_cloud_cover": best_scene.get("cloud_cover"),
                "best_scene_overlap_ratio": best_scene.get("overlap_ratio"),
                "best_scene_s3_href": best_scene.get("s3_href"),
            }
        )

    rows.sort(
        key=lambda row: (
            -(row["best_scene_overlap_ratio"] or 0.0),
            row["best_scene_cloud_cover"] if row["best_scene_cloud_cover"] is not None else 9999.0,
            row["best_scene_datetime"] or "",
        )
    )

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else catalog_path.parent
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = catalog_path.stem.replace("sentinel2_", "sentinel2_tiles_")
    json_out = output_dir / f"{stem}.json"
    csv_out = output_dir / f"{stem}.csv"

    result = {
        "area_name": payload["area_name"],
        "bbox": payload["bbox"],
        "tile_count": len(rows),
        "tiles": rows,
    }
    json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "tile_id",
        "scene_count",
        "best_scene_id",
        "best_scene_datetime",
        "best_scene_cloud_cover",
        "best_scene_overlap_ratio",
        "best_scene_s3_href",
    ]
    with csv_out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} ranked tiles")
    print(f"JSON: {json_out}")
    print(f"CSV:  {csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
