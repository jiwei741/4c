from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.config import load_config
from spatio_eco_inference.feature_stitching import build_training_arrays, write_training_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a training NPZ from real feature tables.")
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    output_path = resolve_output_path(config["output"]["path"])
    metadata_path = resolve_output_path(config["output"].get("metadata_path"))

    metadata, x, y, adjacency = build_training_arrays(config, SERVICE_ROOT)
    write_training_dataset(metadata, x, y, adjacency, output_path, metadata_path)

    summary = {
        "output_path": str(output_path),
        "metadata_path": str(metadata_path) if metadata_path else None,
        "shape": {
            "x": list(x.shape),
            "y": list(y.shape),
            "adjacency": list(adjacency.shape),
        },
        "feature_names": metadata["feature_names"],
        "target_name": metadata["target_name"],
        "num_timestamps": len(metadata["timestamps"]),
        "num_nodes": len(metadata["node_ids"]),
    }
    print(json.dumps(summary, indent=2))


def resolve_output_path(raw_path: str | None) -> Path | None:
    if raw_path is None:
        return None
    path = Path(raw_path)
    if not path.is_absolute():
        path = (SERVICE_ROOT / path).resolve()
    return path


if __name__ == "__main__":
    main()
