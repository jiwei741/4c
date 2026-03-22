from __future__ import annotations

from pathlib import Path
from typing import Any


def _normalize_path(path: Path | str) -> str:
    return str(Path(path)).replace("\\", "/")


def build_jobs_from_download_plan(
    plan_payload: dict[str, Any],
    *,
    raw_download_root: str = "data/raw/sentinel2/downloads",
    segmentation_root: str = "data/processed/segmentation",
    execution_mode: str = "remote-gpu",
) -> dict[str, Any]:
    study_area = plan_payload.get("area_name", "nanjing")
    study_segmentation_root = Path(segmentation_root) / study_area
    jobs = []
    for item in plan_payload.get("downloads", []):
        scene_id = item["scene_id"]
        jobs.append(
            {
                "study_area": study_area,
                "scene_id": scene_id,
                "tile_id": item["tile_id"],
                "priority": item["priority"],
                "scene_datetime": item.get("scene_datetime"),
                "cloud_cover": item.get("cloud_cover"),
                "remote_uri": item["remote_uri"],
                "input_safe_dir": _normalize_path(Path(raw_download_root) / scene_id),
                "output_mask_dir": _normalize_path(study_segmentation_root / scene_id / "masks"),
                "output_feature_dir": _normalize_path(study_segmentation_root / scene_id / "features"),
                "model_variant": "sam2-automatic-mask-generation",
                "bands": ["B02", "B03", "B04", "B08"],
                "execution_mode": execution_mode,
                "status": "pending",
            }
        )

    return {
        "study_area": study_area,
        "execution_mode": execution_mode,
        "job_count": len(jobs),
        "raw_download_root": _normalize_path(raw_download_root),
        "segmentation_root": _normalize_path(study_segmentation_root),
        "jobs": jobs,
    }
