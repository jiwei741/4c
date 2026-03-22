from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_segmentation.remote_bundle import summarize_remote_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and import remote SAM-2 outputs back into the local workspace.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--feature-csv", type=Path, default=None)
    parser.add_argument(
        "--copy-feature-to",
        type=Path,
        default=Path("d:/4c/data/processed/features/nanjing/quarterly/sentinel2_features_from_sam2.csv"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("d:/4c/data/processed/segmentation/nanjing/remote_import_summary.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    summary = summarize_remote_results(
        payload,
        results_root=args.results_root,
        feature_csv_path=args.feature_csv,
        copy_feature_to=args.copy_feature_to,
    )
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
