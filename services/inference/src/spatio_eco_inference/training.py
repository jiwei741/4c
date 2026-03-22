from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from .dataset import denormalize_targets_tensor, inverse_target_transform_tensor
from .models import GraphTemporalNet, LSTMBaseline


@dataclass
class TrainingResult:
    history: list[dict[str, float]]
    best_val_loss: float
    best_model_state: dict[str, torch.Tensor]
    test_metrics: dict[str, float]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def select_device(device_name: str) -> torch.device:
    if device_name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_name)


def build_model(
    config: dict[str, Any],
    input_dim: int,
    adjacency: np.ndarray,
) -> nn.Module:
    model_config = config["model"]
    data_config = config["data"]
    horizon = int(data_config["horizon"])
    target_dim = int(data_config["target_dim"])
    model_name = model_config["name"]

    if model_name == "lstm_baseline":
        return LSTMBaseline(
            input_dim=input_dim,
            hidden_dim=int(model_config["hidden_dim"]),
            num_layers=int(model_config["lstm_layers"]),
            dropout=float(model_config["dropout"]),
            horizon=horizon,
            target_dim=target_dim,
        )

    if model_name == "stgnn_gcn_lstm":
        adjacency_tensor = torch.tensor(adjacency, dtype=torch.float32)
        return GraphTemporalNet(
            input_dim=input_dim,
            graph_hidden_dim=int(model_config["graph_hidden_dim"]),
            temporal_hidden_dim=int(model_config["temporal_hidden_dim"]),
            num_layers=int(model_config["lstm_layers"]),
            dropout=float(model_config["dropout"]),
            horizon=horizon,
            target_dim=target_dim,
            adjacency=adjacency_tensor,
        )

    raise ValueError(f"unsupported model name: {model_name}")


def compute_metrics(predictions: torch.Tensor, targets: torch.Tensor) -> dict[str, float]:
    errors = predictions - targets
    mae = torch.mean(torch.abs(errors)).item()
    rmse = torch.sqrt(torch.mean(errors ** 2)).item()
    return {"mae": float(mae), "rmse": float(rmse)}


def apply_prediction_constraints_tensor(
    predictions: torch.Tensor,
    constraints: dict[str, Any] | None,
) -> torch.Tensor:
    if constraints is None:
        return predictions
    constrained = predictions
    if "min_value" in constraints and constraints["min_value"] is not None:
        constrained = torch.clamp_min(constrained, float(constraints["min_value"]))
    if "max_value" in constraints and constraints["max_value"] is not None:
        constrained = torch.clamp_max(constrained, float(constraints["max_value"]))
    return constrained


def run_epoch(
    model: nn.Module,
    data_loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
    target_scale: dict[str, torch.Tensor] | None = None,
    target_transform: dict[str, Any] | None = None,
    prediction_constraints: dict[str, Any] | None = None,
) -> tuple[float, dict[str, float]]:
    is_train = optimizer is not None
    model.train(mode=is_train)
    total_loss = 0.0
    total_items = 0
    batch_metrics: list[dict[str, float]] = []

    for batch in data_loader:
        if len(batch) == 2:
            inputs, targets = batch
            raw_targets = targets
        else:
            inputs, targets, raw_targets = batch
        inputs = inputs.to(device=device, dtype=torch.float32)
        targets = targets.to(device=device, dtype=torch.float32)
        raw_targets = raw_targets.to(device=device, dtype=torch.float32)

        if is_train:
            optimizer.zero_grad()

        predictions = model(inputs)
        loss = criterion(predictions, targets)

        if is_train:
            loss.backward()
            optimizer.step()

        batch_size = inputs.size(0)
        total_loss += loss.item() * batch_size
        total_items += batch_size
        metric_predictions = predictions.detach()
        if target_scale is not None:
            metric_predictions = denormalize_targets_tensor(
                metric_predictions,
                target_scale["mean"],
                target_scale["std"],
            )
        metric_predictions = inverse_target_transform_tensor(metric_predictions, target_transform)
        metric_predictions = apply_prediction_constraints_tensor(metric_predictions, prediction_constraints)
        batch_metrics.append(compute_metrics(metric_predictions, raw_targets.detach()))

    mean_metrics = {
        "mae": float(np.mean([item["mae"] for item in batch_metrics])),
        "rmse": float(np.mean([item["rmse"] for item in batch_metrics])),
    }
    return total_loss / max(total_items, 1), mean_metrics


def train_model(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    val_loader: torch.utils.data.DataLoader,
    test_loader: torch.utils.data.DataLoader,
    training_config: dict[str, Any],
    device: torch.device,
    target_scale: dict[str, torch.Tensor] | None = None,
    target_transform: dict[str, Any] | None = None,
    prediction_constraints: dict[str, Any] | None = None,
) -> TrainingResult:
    model = model.to(device)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(training_config["learning_rate"]),
        weight_decay=float(training_config["weight_decay"]),
    )
    criterion = nn.MSELoss()

    history: list[dict[str, float]] = []
    best_val_loss = float("inf")
    best_state: dict[str, torch.Tensor] | None = None

    for epoch in range(1, int(training_config["epochs"]) + 1):
        train_loss, train_metrics = run_epoch(
            model,
            train_loader,
            criterion,
            device,
            optimizer,
            target_scale,
            target_transform,
            prediction_constraints,
        )
        val_loss, val_metrics = run_epoch(
            model,
            val_loader,
            criterion,
            device,
            None,
            target_scale,
            target_transform,
            prediction_constraints,
        )

        record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "train_mae": train_metrics["mae"],
            "train_rmse": train_metrics["rmse"],
            "val_mae": val_metrics["mae"],
            "val_rmse": val_metrics["rmse"],
        }
        history.append(record)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }

    if best_state is None:
        raise RuntimeError("training did not produce a best checkpoint")

    model.load_state_dict(best_state)
    _, test_metrics = run_epoch(
        model,
        test_loader,
        criterion,
        device,
        None,
        target_scale,
        target_transform,
        prediction_constraints,
    )
    return TrainingResult(
        history=history,
        best_val_loss=best_val_loss,
        best_model_state=best_state,
        test_metrics=test_metrics,
    )


def save_training_outputs(
    output_dir: Path,
    config: dict[str, Any],
    dataset_meta: dict[str, Any],
    result: TrainingResult,
    normalization: dict[str, Any] | None = None,
    target_transform: dict[str, Any] | None = None,
    prediction_constraints: dict[str, Any] | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "best.pt"
    torch.save(
        {
            "config": config,
            "dataset_meta": dataset_meta,
            "model_state": result.best_model_state,
            "best_val_loss": result.best_val_loss,
            "test_metrics": result.test_metrics,
            "normalization": normalization or {},
            "target_transform": target_transform or {"name": "identity"},
            "prediction_constraints": prediction_constraints or {},
        },
        checkpoint_path,
    )

    with (output_dir / "history.json").open("w", encoding="utf-8") as handle:
        json.dump(result.history, handle, indent=2)
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "best_val_loss": result.best_val_loss,
                "test_metrics": result.test_metrics,
                "normalization": normalization or {},
                "target_transform": target_transform or {"name": "identity"},
                "prediction_constraints": prediction_constraints or {},
            },
            handle,
            indent=2,
        )
    with (output_dir / "dataset_meta.json").open("w", encoding="utf-8") as handle:
        json.dump(dataset_meta, handle, indent=2)

    return checkpoint_path
