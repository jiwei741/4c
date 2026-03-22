from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare directory layout for remote SAM-2 execution on a GPU server.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--server-workdir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])
    plan_rows = []

    for job in jobs:
        input_safe_dir = args.server_workdir / Path(job["input_safe_dir"])
        mask_dir = args.server_workdir / Path(job["output_mask_dir"])
        feature_dir = args.server_workdir / Path(job["output_feature_dir"])
        mask_dir.mkdir(parents=True, exist_ok=True)
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_rows.append(
            {
                "scene_id": job["scene_id"],
                "input_safe_dir": str(input_safe_dir).replace("\\", "/"),
                "output_mask_dir": str(mask_dir).replace("\\", "/"),
                "output_feature_dir": str(feature_dir).replace("\\", "/"),
                "input_exists": input_safe_dir.exists(),
            }
        )

    output_path = args.output or (args.manifest.parent / "server_job_plan.json")
    result = {
        "study_area": payload.get("study_area", "nanjing"),
        "job_count": len(plan_rows),
        "server_workdir": str(args.server_workdir).replace("\\", "/"),
        "jobs": plan_rows,
        "note": "This script only prepares directories and validates inputs. Connect the real SAM-2 runner on the server.",
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
