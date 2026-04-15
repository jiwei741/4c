from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.config import load_config, resolve_output_dir
from spatio_eco_inference.experiment_runner import run_training_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an inference model.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    output_dir = resolve_output_dir(SERVICE_ROOT, config)
    summary = run_training_experiment(
        config=config,
        dataset_path=args.dataset,
        service_root=SERVICE_ROOT,
        output_dir=output_dir,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
