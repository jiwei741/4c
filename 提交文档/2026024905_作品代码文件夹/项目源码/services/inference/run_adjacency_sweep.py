from __future__ import annotations

import argparse
import copy
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import yaml

SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.config import load_config
from spatio_eco_inference.experiment_runner import run_training_experiment, summarize_runs
from spatio_eco_inference.feature_stitching import build_training_arrays, write_training_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep adjacency parameters, rebuild datasets, retrain models, and summarize results.",
    )
    parser.add_argument("--dataset-config", required=True, type=Path)
    parser.add_argument("--train-config", required=True, type=Path)
    parser.add_argument(
        "--set",
        dest="parameter_sets",
        action="append",
        nargs="+",
        metavar=("KEY", "VALUE"),
        help="Adjacency key followed by one or more YAML values. Repeat this flag for multiple keys.",
    )
    parser.add_argument("--seeds", nargs="+", type=int, help="Optional seeds to run for every adjacency combination.")
    parser.add_argument("--epochs", type=int, help="Optional training epoch override for all runs.")
    parser.add_argument("--output-root", type=Path, help="Optional root directory for sweep artifacts.")
    parser.add_argument("--summary-output", type=Path, help="Optional path for the sweep summary JSON.")
    parser.add_argument("--max-runs", type=int, help="Optional limit on the number of adjacency combinations to execute.")
    parser.add_argument("--dry-run", action="store_true", help="Only print planned combinations without building or training.")
    return parser.parse_args()


def resolve_path(root: Path, raw_path: Path | None, default_path: Path) -> Path:
    if raw_path is None:
        return default_path
    if raw_path.is_absolute():
        return raw_path
    return (root / raw_path).resolve()


def parse_parameter_grid(raw_sets: list[list[str]] | None) -> dict[str, list[Any]]:
    if not raw_sets:
        raise ValueError("at least one --set KEY VALUE... pair is required for adjacency sweep")

    grid: dict[str, list[Any]] = {}
    for raw_set in raw_sets:
        if len(raw_set) < 2:
            raise ValueError("each --set entry must provide a key and at least one value")
        key = str(raw_set[0])
        if key in grid:
            raise ValueError(f"duplicate adjacency sweep key: {key}")
        grid[key] = [yaml.safe_load(value) for value in raw_set[1:]]
    return grid


def build_parameter_combinations(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid.keys())
    value_lists = [grid[key] for key in keys]
    combinations: list[dict[str, Any]] = []
    for values in itertools.product(*value_lists):
        combinations.append({key: value for key, value in zip(keys, values, strict=True)})
    return combinations


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def build_dataset_artifacts(dataset_config: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    dataset_dir = output_dir / "dataset"
    dataset_path = dataset_dir / "training_dataset.npz"
    metadata_path = dataset_dir / "training_dataset.meta.json"

    dataset_config["output"]["path"] = str(dataset_path)
    dataset_config["output"]["metadata_path"] = str(metadata_path)

    metadata, x, y, adjacency = build_training_arrays(dataset_config, SERVICE_ROOT)
    write_training_dataset(metadata, x, y, adjacency, dataset_path, metadata_path)
    return dataset_path, metadata_path


def main() -> None:
    args = parse_args()
    dataset_base = load_config(args.dataset_config)
    train_base = load_config(args.train_config)
    parameter_grid = parse_parameter_grid(args.parameter_sets)
    combinations = build_parameter_combinations(parameter_grid)

    if args.max_runs is not None:
        combinations = combinations[: max(0, int(args.max_runs))]

    default_output_root = (
        SERVICE_ROOT
        / "outputs"
        / "adjacency_sweep"
        / f'{train_base["experiment_name"]}__{dataset_base["study_area"]["name"]}'
    )
    output_root = resolve_path(SERVICE_ROOT, args.output_root, default_output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    summary_output = resolve_path(
        SERVICE_ROOT,
        args.summary_output,
        output_root / "sweep_summary.json",
    )

    plan = {
        "dataset_config": str(args.dataset_config),
        "train_config": str(args.train_config),
        "num_combinations": len(combinations),
        "parameter_grid": parameter_grid,
        "output_root": str(output_root),
    }
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    if args.dry_run:
        return

    results: list[dict[str, Any]] = []
    seeds = [int(seed) for seed in args.seeds] if args.seeds else None

    for index, parameters in enumerate(combinations, start=1):
        combo_id = f"combo_{index:03d}"
        combo_root = output_root / combo_id
        combo_root.mkdir(parents=True, exist_ok=True)

        dataset_config = copy.deepcopy(dataset_base)
        dataset_config["adjacency"].update(parameters)
        dataset_path, metadata_path = build_dataset_artifacts(dataset_config, combo_root)
        write_yaml(combo_root / "configs" / "dataset_config.yaml", dataset_config)

        training_runs: list[dict[str, object]] = []
        seeds_to_run = seeds or [int(train_base["training"]["seed"])]

        for seed in seeds_to_run:
            train_config = copy.deepcopy(train_base)
            train_config["training"]["seed"] = int(seed)
            if args.epochs is not None:
                train_config["training"]["epochs"] = int(args.epochs)

            train_output_dir = combo_root / "training" / f"seed_{seed}"
            train_output_dir.mkdir(parents=True, exist_ok=True)
            train_config["output"]["dir"] = str(train_output_dir)
            train_config["experiment_name"] = f'{train_base["experiment_name"]}__{combo_id}__seed_{seed}'

            run_summary = run_training_experiment(
                config=train_config,
                dataset_path=dataset_path,
                service_root=SERVICE_ROOT,
                output_dir=train_output_dir,
            )
            run_summary["seed"] = int(seed)
            training_runs.append(run_summary)
            write_yaml(train_output_dir / "train_config.yaml", train_config)

        if len(training_runs) == 1:
            entry = {
                "combo_id": combo_id,
                "adjacency": parameters,
                "dataset_path": str(dataset_path),
                "dataset_metadata_path": str(metadata_path),
                "result": training_runs[0],
            }
        else:
            combo_train_base = copy.deepcopy(train_base)
            combo_train_base["experiment_name"] = f'{train_base["experiment_name"]}__{combo_id}'
            entry = {
                "combo_id": combo_id,
                "adjacency": parameters,
                "dataset_path": str(dataset_path),
                "dataset_metadata_path": str(metadata_path),
                "aggregate": summarize_runs(base_config=combo_train_base, runs=training_runs),
            }
        results.append(entry)

    ranked = sorted(results, key=ranking_key)
    summary = {
        "dataset_config": str(args.dataset_config),
        "train_config": str(args.train_config),
        "parameter_grid": parameter_grid,
        "num_combinations": len(results),
        "ranked_results": ranked,
        "best_result": ranked[0] if ranked else None,
    }
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def ranking_key(entry: dict[str, Any]) -> float:
    if "aggregate" in entry:
        return float(entry["aggregate"]["aggregate"]["rmse_mean"])
    return float(entry["result"]["test_metrics"]["rmse"])


if __name__ == "__main__":
    main()
