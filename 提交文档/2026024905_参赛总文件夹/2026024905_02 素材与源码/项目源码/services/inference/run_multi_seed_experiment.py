from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.config import load_config
from spatio_eco_inference.experiment_runner import run_training_experiment, summarize_runs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same experiment across multiple random seeds.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--seeds", nargs="+", required=True, type=int)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--epochs", type=int)
    return parser.parse_args()


def resolve_path(root: Path, raw_path: Path | None, default_path: Path) -> Path:
    if raw_path is None:
        return default_path
    if raw_path.is_absolute():
        return raw_path
    return (root / raw_path).resolve()


def main() -> None:
    args = parse_args()
    base_config = load_config(args.config)
    default_output_root = (
        SERVICE_ROOT
        / "outputs"
        / "multi_seed"
        / str(base_config["experiment_name"])
    )
    base_output_dir = resolve_path(SERVICE_ROOT, args.output_root, default_output_root)
    base_output_dir.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []

    for seed in args.seeds:
        config = copy.deepcopy(base_config)
        config["training"]["seed"] = int(seed)
        if args.epochs is not None:
            config["training"]["epochs"] = int(args.epochs)
        config["experiment_name"] = f'{base_config["experiment_name"]}_seed_{seed}'
        output_dir = base_output_dir / f"seed_{seed}"
        config["output"]["dir"] = str(output_dir)
        run_summary = run_training_experiment(
            config=config,
            dataset_path=args.dataset,
            service_root=SERVICE_ROOT,
            output_dir=output_dir,
        )
        run_summary["seed"] = int(seed)
        runs.append(run_summary)

    summary = summarize_runs(base_config=base_config, runs=runs)
    summary_output = resolve_path(
        SERVICE_ROOT,
        args.summary_output,
        base_output_dir / "multi_seed_summary.json",
    )
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
