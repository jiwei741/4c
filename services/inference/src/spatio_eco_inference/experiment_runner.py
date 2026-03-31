from __future__ import annotations

from pathlib import Path
from typing import Any

from torch.utils.data import DataLoader

from .config import resolve_output_dir
from .dataset import (
    FeatureScaledDataset,
    TargetScaledDataset,
    TargetTransformedDataset,
    build_target_transform,
    build_window_splits,
    compute_feature_normalization,
    compute_target_normalization,
    load_dataset,
)
from .training import (
    build_model,
    save_training_outputs,
    select_device,
    set_seed,
    train_model,
)


def run_training_experiment(
    *,
    config: dict[str, Any],
    dataset_path: str | Path,
    service_root: Path,
    output_dir: Path | None = None,
) -> dict[str, object]:
    bundle = load_dataset(dataset_path)

    set_seed(int(config["training"]["seed"]))
    device = select_device(str(config["training"]["device"]))

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

    resolved_output_dir = output_dir or resolve_output_dir(service_root, config)
    checkpoint_path = save_training_outputs(
        resolved_output_dir,
        config,
        bundle.metadata(),
        result,
        normalization,
        target_transform,
        prediction_constraints,
    )

    return {
        "experiment_name": config["experiment_name"],
        "output_dir": str(resolved_output_dir),
        "checkpoint_path": str(checkpoint_path),
        "best_val_loss": result.best_val_loss,
        "test_metrics": result.test_metrics,
        "device": str(device),
        "dataset_path": str(Path(dataset_path)),
    }


def summarize_runs(
    *,
    base_config: dict[str, Any],
    runs: list[dict[str, object]],
    metric_key: str = "rmse",
) -> dict[str, object]:
    if not runs:
        raise ValueError("runs must not be empty")

    maes = [float(run["test_metrics"]["mae"]) for run in runs]
    rmses = [float(run["test_metrics"]["rmse"]) for run in runs]
    best_run = min(runs, key=lambda run: float(run["test_metrics"][metric_key]))
    return {
        "experiment_name": base_config["experiment_name"],
        "seeds": [int(run["seed"]) for run in runs if "seed" in run],
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
