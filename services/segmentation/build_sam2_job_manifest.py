from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_segmentation.pipeline import build_jobs_from_download_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a SAM-2 segmentation job manifest from a Sentinel-2 download plan.")
    parser.add_argument("--plan-json", type=Path, required=True)
    parser.add_argument("--raw-download-root", default="data/raw/sentinel2/downloads")
    parser.add_argument("--segmentation-root", default="data/processed/segmentation")
    parser.add_argument("--execution-mode", choices=["local-proxy", "remote-gpu"], default="remote-gpu")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("d:/4c/data/processed/segmentation/nanjing/sam2_job_manifest.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.plan_json.read_text(encoding="utf-8"))
    manifest = build_jobs_from_download_plan(
        payload,
        raw_download_root=args.raw_download_root,
        segmentation_root=args.segmentation_root,
        execution_mode=args.execution_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
