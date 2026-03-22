from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from torch.utils.data import DataLoader

SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.config import load_config, resolve_output_dir
from spatio_eco_inference.dataset import (
    FeatureScaledDataset,
    TargetScaledDataset,
    TargetTransformedDataset,
    build_target_transform,
    build_window_splits,
    compute_feature_normalization,
    compute_target_normalization,
    load_dataset,
)
from spatio_eco_inference.training import (
    build_model,
    save_training_outputs,
    select_device,
    set_seed,
    train_model,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same experiment across multiple random seeds.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--seeds", nargs="+", required=True, type=int)
    parser.add_argument("--summary-output", type=Path)
    return parser.parse_args()


def run_single_seed(
    config: dict,
    dataset_path: Path,
    seed: int,
    device_name: str,
    output_dir: Path,
) -> dict[str, object]:
    bundle = load_dataset(dataset_path)
    set_seed(seed)
    device = select_device(device_name)

    input_window = int(config["data"]["input_window"])
    horizon = int(config["data"]["horizon"])
    batch_size = int(config["training"]["batch_size"])

    train_ds, val_ds, test_ds = build_window_splits(
        bundle=bundle,
        input_window=input_window,
        horizon=horizon,
        train_ratio=float(config["training"]["train_ratio"]),
        val_ratio=float(config["training"]["val_ratio"]),
    )

    normalization: dict[str, object] = {}
    if bool(config["training"].get("feature_normalization", False)):
        feature_mean, feature_std = compute_feature_normalization(train_ds)
        train_ds = FeatureScaledDataset(train_ds, feature_mean, feature_std)
        val_ds = FeatureScaledDataset(val_ds, feature_mean, feature_std)
        test_ds = FeatureScaledDataset(test_ds, feature_mean, feature_std)
        normalization["features"] = {
            "mean": feature_mean.tolist(),
            "std": feature_std.tolist(),
        }

    target_transform = build_target_transform(
        train_ds,
        config["training"].get("target_transform"),
    )
    train_ds = TargetTransformedDataset(train_ds, target_transform)
    val_ds = TargetTransformedDataset(val_ds, target_transform)
    test_ds = TargetTransformedDataset(test_ds, target_transform)

    target_scale_tensors = None
    if bool(config["training"].get("target_normalization", True)):
        target_mean, target_std = compute_target_normalization(train_ds)
        train_ds = TargetScaledDataset(train_ds, target_mean, target_std)
        val_ds = TargetScaledDataset(val_ds, target_mean, target_std)
        test_ds = TargetScaledDataset(test_ds, target_mean, target_std)
        normalization["target"] = {
            "mean": target_mean.tolist(),
            "std": target_std.tolist(),
        }
        target_scale_tensors = {
            "mean": train_ds.target_mean.to(device=device),
            "std": train_ds.target_std.to(device=device),
        }

    prediction_constraints = config["training"].get("prediction_constraints")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    model = build_model(
        config=config,
        input_dim=bundle.num_features,
        adjacency=bundle.adjacency,
    )
    result = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        training_config=config["training"],
        device=device,
        target_scale=target_scale_tensors,
        target_transform=target_transform,
        prediction_constraints=prediction_constraints,
    )
    checkpoint_path = save_training_outputs(
        output_dir=output_dir,
        config=config,
        dataset_meta=bundle.metadata(),
        result=result,
        normalization=normalization,
        target_transform=target_transform,
        prediction_constraints=prediction_constraints,
    )
    return {
        "seed": seed,
        "experiment_name": config["experiment_name"],
        "output_dir": str(output_dir),
        "checkpoint_path": str(checkpoint_path),
        "best_val_loss": result.best_val_loss,
        "test_metrics": result.test_metrics,
        "device": str(device),
    }


def summarize_runs(base_config: dict, runs: list[dict[str, object]]) -> dict[str, object]:
    maes = [float(run["test_metrics"]["mae"]) for run in runs]
    rmses = [float(run["test_metrics"]["rmse"]) for run in runs]
    best_run = min(runs, key=lambda run: float(run["test_metrics"]["rmse"]))
    return {
        "experiment_name": base_config["experiment_name"],
        "seeds": [int(run["seed"]) for run in runs],
        "num_runs": len(runs),
        "prediction_constraints": base_config["training"].get("prediction_constraints", {}),
        "aggregate": {
            "mae_mean": float(sum(maes) / len(maes)),
            "mae_std": float(_population_std(maes)),
            "mae_min": float(min(maes)),
            "mae_max": float(max(maes)),
            "rmse_mean": float(sum(rmses) / len(rmses)),
            "rmse_std": float(_population_std(rmses)),
            "rmse_min": float(min(rmses)),
            "rmse_max": float(max(rmses)),
        },
        "best_run_by_rmse": best_run,
        "runs": runs,
    }


def _population_std(values: list[float]) -> float:
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return variance ** 0.5


def main() -> None:
    args = parse_args()
    base_config = load_config(args.config)
    base_output_dir = resolve_output_dir(SERVICE_ROOT, base_config)
    device_name = str(base_config["training"]["device"])
    runs: list[dict[str, object]] = []

    for seed in args.seeds:
        config = copy.deepcopy(base_config)
        config["training"]["seed"] = int(seed)
        config["experiment_name"] = f'{base_config["experiment_name"]}_seed_{seed}'
        output_dir = base_output_dir / f"seed_{seed}"
        run_summary = run_single_seed(
            config=config,
            dataset_path=args.dataset,
            seed=seed,
            device_name=device_name,
            output_dir=output_dir,
        )
        runs.append(run_summary)

    summary = summarize_runs(base_config, runs)
    summary_output = args.summary_output or (base_output_dir / "multi_seed_summary.json")
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
