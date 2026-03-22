from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _normalize(path: Path | str) -> str:
    return str(Path(path)).replace("\\", "/")


def export_remote_bundle(
    manifest_payload: dict[str, Any],
    *,
    bundle_root: Path,
    server_workdir: str,
    feature_output_csv: str,
) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_dir = bundle_root / f"sam2_remote_bundle_{timestamp}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = bundle_dir / "sam2_job_manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    server_plan = {
        "study_area": manifest_payload.get("study_area", "nanjing"),
        "execution_mode": manifest_payload.get("execution_mode", "remote-gpu"),
        "generated_at_utc": timestamp,
        "server_workdir": server_workdir,
        "manifest_relpath": "sam2_job_manifest.json",
        "expected_download_root": _normalize(Path(server_workdir) / manifest_payload.get("raw_download_root", "data/raw/sentinel2/downloads")),
        "expected_segmentation_root": _normalize(Path(server_workdir) / manifest_payload.get("segmentation_root", "data/processed/segmentation/nanjing")),
        "expected_feature_output_csv": _normalize(Path(server_workdir) / feature_output_csv),
        "job_count": manifest_payload.get("job_count", 0),
        "next_step": "Run prepare_remote_sam2_workspace.py on the GPU server, then connect the real SAM-2 inference runner.",
    }
    server_plan_path = bundle_dir / "server_execution_plan.json"
    server_plan_path.write_text(json.dumps(server_plan, ensure_ascii=False, indent=2), encoding="utf-8")

    checklist_lines = [
        "# SAM-2 Remote Bundle Checklist",
        "",
        "1. Copy this entire bundle directory to the GPU server.",
        f"2. Ensure the repo exists at `{server_workdir}` on the server.",
        f"3. Mirror Sentinel-2 SAFE folders into `{server_plan['expected_download_root']}`.",
        "4. Run `python services/segmentation/prepare_remote_sam2_workspace.py --manifest <bundle>/sam2_job_manifest.json --server-workdir <repo_root>` on the server.",
        "5. Execute the real SAM-2 inference service there.",
        "6. Copy masks/features back, then run import_remote_segmentation_results.py locally.",
        "",
        "Outputs expected from the server:",
        f"- Scene masks under `{server_plan['expected_segmentation_root']}/<scene_id>/masks/`",
        f"- Scene features under `{server_plan['expected_segmentation_root']}/<scene_id>/features/`",
        f"- Merged quarterly CSV at `{server_plan['expected_feature_output_csv']}`",
    ]
    (bundle_dir / "TRANSFER_CHECKLIST.md").write_text("\n".join(checklist_lines), encoding="utf-8")

    return {
        "bundle_dir": _normalize(bundle_dir),
        "manifest_path": _normalize(manifest_path),
        "server_execution_plan_path": _normalize(server_plan_path),
        "job_count": manifest_payload.get("job_count", 0),
    }


def summarize_remote_results(
    manifest_payload: dict[str, Any],
    *,
    results_root: Path,
    feature_csv_path: Path | None = None,
    copy_feature_to: Path | None = None,
) -> dict[str, Any]:
    jobs = manifest_payload.get("jobs", [])
    missing_scene_dirs: list[str] = []
    scene_summaries: list[dict[str, Any]] = []

    for job in jobs:
        scene_dir = results_root / job["scene_id"]
        mask_dir = scene_dir / "masks"
        feature_dir = scene_dir / "features"
        mask_file_count = sum(1 for item in mask_dir.rglob("*") if item.is_file()) if mask_dir.exists() else 0
        feature_file_count = sum(1 for item in feature_dir.rglob("*") if item.is_file()) if feature_dir.exists() else 0
        scene_ok = scene_dir.exists() and (mask_file_count > 0 or feature_file_count > 0)
        if not scene_ok:
            missing_scene_dirs.append(job["scene_id"])
        scene_summaries.append(
            {
                "scene_id": job["scene_id"],
                "scene_dir": _normalize(scene_dir),
                "mask_dir_exists": mask_dir.exists(),
                "feature_dir_exists": feature_dir.exists(),
                "mask_file_count": mask_file_count,
                "feature_file_count": feature_file_count,
            }
        )

    if feature_csv_path is None:
        candidates = sorted(results_root.rglob("sentinel2_features*.csv"))
        feature_csv_path = candidates[0] if candidates else None

    copied_feature_csv = None
    if feature_csv_path and copy_feature_to:
        copy_feature_to.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(feature_csv_path, copy_feature_to)
        copied_feature_csv = _normalize(copy_feature_to)

    return {
        "study_area": manifest_payload.get("study_area", "nanjing"),
        "job_count": len(jobs),
        "complete_scene_count": len(jobs) - len(missing_scene_dirs),
        "missing_scene_ids": missing_scene_dirs,
        "results_root": _normalize(results_root),
        "feature_csv_path": _normalize(feature_csv_path) if feature_csv_path else None,
        "copied_feature_csv": copied_feature_csv,
        "scenes": scene_summaries,
    }
