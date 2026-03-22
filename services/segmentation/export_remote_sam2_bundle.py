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
from spatio_eco_segmentation.remote_bundle import export_remote_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a SAM-2 remote execution bundle for a GPU server.")
    parser.add_argument("--plan-json", type=Path, required=True)
    parser.add_argument("--bundle-root", type=Path, default=Path("d:/4c/data/processed/segmentation/nanjing/remote_bundle"))
    parser.add_argument("--server-workdir", default="/workspace/spatio-eco")
    parser.add_argument("--raw-download-root", default="data/raw/sentinel2/downloads")
    parser.add_argument("--segmentation-root", default="data/processed/segmentation")
    parser.add_argument("--feature-output-csv", default="data/processed/features/nanjing/quarterly/sentinel2_features_from_sam2.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.plan_json.read_text(encoding="utf-8"))
    manifest = build_jobs_from_download_plan(
        payload,
        raw_download_root=args.raw_download_root,
        segmentation_root=args.segmentation_root,
        execution_mode="remote-gpu",
    )
    summary = export_remote_bundle(
        manifest,
        bundle_root=args.bundle_root,
        server_workdir=args.server_workdir,
        feature_output_csv=args.feature_output_csv,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
