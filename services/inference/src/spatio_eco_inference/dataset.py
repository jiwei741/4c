from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset


@dataclass
class DatasetBundle:
    x: np.ndarray
    y: np.ndarray
    adjacency: np.ndarray
    node_ids: list[str]
    feature_names: list[str]
    target_name: str
    timestamps: list[str]

    @property
    def num_timesteps(self) -> int:
        return int(self.x.shape[0])

    @property
    def num_nodes(self) -> int:
        return int(self.x.shape[1])

    @property
    def num_features(self) -> int:
        return int(self.x.shape[2])

    @property
    def target_dim(self) -> int:
        return int(self.y.shape[2])

    def metadata(self) -> dict[str, Any]:
        return {
            "num_timesteps": self.num_timesteps,
            "num_nodes": self.num_nodes,
            "num_features": self.num_features,
            "target_dim": self.target_dim,
            "node_ids": self.node_ids,
            "feature_names": self.feature_names,
            "target_name": self.target_name,
            "timestamps": self.timestamps,
        }


def load_dataset(path: str | Path) -> DatasetBundle:
    data_path = Path(path)
    data = np.load(data_path, allow_pickle=True)

    x = np.asarray(data["x"], dtype=np.float32)
    y = np.asarray(data["y"], dtype=np.float32)
    adjacency = np.asarray(data["adjacency"], dtype=np.float32)

    if x.ndim != 3:
        raise ValueError(f"x must have shape [T, N, F], got {x.shape}")
    if y.ndim == 2:
        y = y[..., None]
    if y.ndim != 3:
        raise ValueError(f"y must have shape [T, N, C], got {y.shape}")
    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError("adjacency must have shape [N, N]")
    if x.shape[0] != y.shape[0] or x.shape[1] != y.shape[1]:
        raise ValueError("x and y must align on T and N dimensions")
    if adjacency.shape[0] != x.shape[1]:
        raise ValueError("adjacency size must match node count")

    node_ids = _read_optional_list(data, "node_ids", x.shape[1], "grid")
    feature_names = _read_optional_list(data, "feature_names", x.shape[2], "feature")
    timestamps = _read_optional_list(data, "timestamps", x.shape[0], "t")
    target_name = str(data["target_name"][0]) if "target_name" in data else "target"

    return DatasetBundle(
        x=x,
        y=y,
        adjacency=adjacency,
        node_ids=node_ids,
        feature_names=feature_names,
        target_name=target_name,
        timestamps=timestamps,
    )


def _read_optional_list(
    data: Any,
    key: str,
    expected_length: int,
    prefix: str,
) -> list[str]:
    if key not in data:
        return [f"{prefix}_{index:02d}" for index in range(expected_length)]
    values = [str(item) for item in data[key].tolist()]
    if len(values) != expected_length:
        raise ValueError(f"{key} length mismatch: expected {expected_length}, got {len(values)}")
    return values


class WindowedGraphDataset(Dataset):
    def __init__(
        self,
        bundle: DatasetBundle,
        input_window: int,
        horizon: int,
        start_index: int,
        end_index: int,
    ) -> None:
        self.bundle = bundle
        self.input_window = int(input_window)
        self.horizon = int(horizon)
        self.indices = list(range(start_index, end_index))

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        start = self.indices[index]
        x = self.bundle.x[start : start + self.input_window]
        y = self.bundle.y[
            start + self.input_window : start + self.input_window + self.horizon
        ]
        return torch.from_numpy(x), torch.from_numpy(y)


class FeatureScaledDataset(Dataset):
    def __init__(self, base_dataset: Dataset, feature_mean: np.ndarray, feature_std: np.ndarray) -> None:
        self.base_dataset = base_dataset
        self.feature_mean = torch.as_tensor(feature_mean, dtype=torch.float32).view(1, 1, -1)
        self.feature_std = torch.as_tensor(feature_std, dtype=torch.float32).view(1, 1, -1)

    def __len__(self) -> int:
        return len(self.base_dataset)

    def __getitem__(self, index: int):
        item = self.base_dataset[index]
        inputs = normalize_features_tensor(item[0].to(dtype=torch.float32), self.feature_mean, self.feature_std)
        if len(item) == 2:
            return inputs, item[1]
        return (inputs, *item[1:])


def build_window_splits(
    bundle: DatasetBundle,
    input_window: int,
    horizon: int,
    train_ratio: float,
    val_ratio: float,
) -> tuple[WindowedGraphDataset, WindowedGraphDataset, WindowedGraphDataset]:
    total_windows, train_end, val_end = compute_split_indices(
        bundle.num_timesteps,
        input_window,
        horizon,
        train_ratio,
        val_ratio,
    )

    train_ds = WindowedGraphDataset(bundle, input_window, horizon, 0, train_end)
    val_ds = WindowedGraphDataset(bundle, input_window, horizon, train_end, val_end)
    test_ds = WindowedGraphDataset(bundle, input_window, horizon, val_end, total_windows)
    return train_ds, val_ds, test_ds


def compute_split_indices(
    num_timesteps: int,
    input_window: int,
    horizon: int,
    train_ratio: float,
    val_ratio: float,
) -> tuple[int, int, int]:
    total_windows = num_timesteps - input_window - horizon + 1
    if total_windows < 3:
        raise ValueError("dataset is too short for the requested input_window and horizon")

    train_end = max(1, int(total_windows * train_ratio))
    val_end = max(train_end + 1, int(total_windows * (train_ratio + val_ratio)))
    val_end = min(val_end, total_windows - 1)
    return total_windows, train_end, val_end


class TargetScaledDataset(Dataset):
    def __init__(self, base_dataset: Dataset, target_mean: np.ndarray, target_std: np.ndarray) -> None:
        self.base_dataset = base_dataset
        self.target_mean = torch.as_tensor(target_mean, dtype=torch.float32).view(1, 1, -1)
        self.target_std = torch.as_tensor(target_std, dtype=torch.float32).view(1, 1, -1)

    def __len__(self) -> int:
        return len(self.base_dataset)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        item = self.base_dataset[index]
        if len(item) == 2:
            inputs, targets = item
            raw_targets = targets
        else:
            inputs, targets, raw_targets = item
        scaled_targets = normalize_targets_tensor(targets.to(dtype=torch.float32), self.target_mean, self.target_std)
        return inputs, scaled_targets, raw_targets.to(dtype=torch.float32)


class TargetTransformedDataset(Dataset):
    def __init__(self, base_dataset: Dataset, target_transform: dict[str, Any]) -> None:
        self.base_dataset = base_dataset
        self.target_transform = dict(target_transform)

    def __len__(self) -> int:
        return len(self.base_dataset)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        inputs, raw_targets = self.base_dataset[index]
        transformed_targets = apply_target_transform_tensor(
            raw_targets.to(dtype=torch.float32),
            self.target_transform,
        )
        return inputs, transformed_targets, raw_targets.to(dtype=torch.float32)


def compute_target_normalization(dataset: Dataset) -> tuple[np.ndarray, np.ndarray]:
    targets = [dataset[index][1].numpy() for index in range(len(dataset))]
    stacked = np.concatenate(targets, axis=0)
    mean = stacked.mean(axis=(0, 1), keepdims=False).astype(np.float32)
    std = stacked.std(axis=(0, 1), keepdims=False).astype(np.float32)
    std = np.where(std < 1e-6, 1.0, std)
    return mean, std


def normalize_targets_tensor(targets: torch.Tensor, mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    return (targets - mean) / std


def denormalize_targets_tensor(targets: torch.Tensor, mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    return targets * std + mean


def compute_feature_normalization(dataset: Dataset) -> tuple[np.ndarray, np.ndarray]:
    inputs = [dataset[index][0].numpy() for index in range(len(dataset))]
    stacked = np.concatenate(inputs, axis=0)
    mean = stacked.mean(axis=(0, 1), keepdims=False).astype(np.float32)
    std = stacked.std(axis=(0, 1), keepdims=False).astype(np.float32)
    std = np.where(std < 1e-6, 1.0, std)
    return mean, std


def normalize_features_tensor(features: torch.Tensor, mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    return (features - mean) / std


def build_target_transform(
    dataset: Dataset,
    config: dict[str, Any] | None,
) -> dict[str, Any]:
    transform_config = dict(config or {})
    name = str(transform_config.get("name", "identity")).strip().lower()
    if name == "identity":
        return {"name": "identity"}

    targets = [dataset[index][1].numpy() for index in range(len(dataset))]
    stacked = np.concatenate(targets, axis=0)

    if name == "log1p":
        min_value = float(stacked.min())
        if min_value < -1e-6:
            raise ValueError(f"log1p target transform requires non-negative targets, got min={min_value}")
        return {"name": "log1p"}

    if name == "quantile_clip":
        upper_quantile = float(transform_config.get("upper_quantile", 0.99))
        if upper_quantile <= 0.0 or upper_quantile > 1.0:
            raise ValueError("target_transform.upper_quantile must be in (0, 1]")
        clip_max = float(np.quantile(stacked, upper_quantile))
        return {
            "name": "quantile_clip",
            "upper_quantile": upper_quantile,
            "clip_max": clip_max,
        }

    raise ValueError(f"unsupported target transform: {name}")


def apply_target_transform_tensor(targets: torch.Tensor, transform: dict[str, Any] | None) -> torch.Tensor:
    if transform is None:
        return targets
    name = str(transform.get("name", "identity")).lower()
    if name == "identity":
        return targets
    if name == "log1p":
        return torch.log1p(torch.clamp_min(targets, 0.0))
    if name == "quantile_clip":
        clip_max = float(transform["clip_max"])
        return torch.clamp(targets, min=0.0, max=clip_max)
    raise ValueError(f"unsupported target transform: {name}")


def inverse_target_transform_tensor(targets: torch.Tensor, transform: dict[str, Any] | None) -> torch.Tensor:
    if transform is None:
        return targets
    name = str(transform.get("name", "identity")).lower()
    if name == "identity":
        return targets
    if name == "log1p":
        return torch.expm1(targets)
    if name == "quantile_clip":
        return targets
    raise ValueError(f"unsupported target transform: {name}")


def latest_window(bundle: DatasetBundle, input_window: int) -> torch.Tensor:
    x = bundle.x[-input_window:]
    return torch.from_numpy(x).unsqueeze(0)


def infer_forecast_timestamps(history_timestamps: list[str], horizon: int) -> list[str]:
    if horizon <= 0:
        return []
    if not history_timestamps:
        return [f"t+{step}" for step in range(1, horizon + 1)]

    last_timestamp = history_timestamps[-1]
    quarter_match = re.fullmatch(r"(\d{4})-Q([1-4])", last_timestamp)
    if quarter_match:
        year = int(quarter_match.group(1))
        quarter = int(quarter_match.group(2))
        result = []
        for step in range(1, horizon + 1):
            raw_quarter = quarter + step
            next_year = year + (raw_quarter - 1) // 4
            next_quarter = ((raw_quarter - 1) % 4) + 1
            result.append(f"{next_year:04d}-Q{next_quarter}")
        return result

    month_match = re.fullmatch(r"(\d{4})-(\d{2})", last_timestamp)
    if month_match:
        year = int(month_match.group(1))
        month = int(month_match.group(2))
        result = []
        for step in range(1, horizon + 1):
            raw_month = month + step
            next_year = year + (raw_month - 1) // 12
            next_month = ((raw_month - 1) % 12) + 1
            result.append(f"{next_year:04d}-{next_month:02d}")
        return result

    year_match = re.fullmatch(r"(\d{4})", last_timestamp)
    if year_match:
        year = int(year_match.group(1))
        return [f"{year + step:04d}" for step in range(1, horizon + 1)]

    return [f"t+{step}" for step in range(1, horizon + 1)]
