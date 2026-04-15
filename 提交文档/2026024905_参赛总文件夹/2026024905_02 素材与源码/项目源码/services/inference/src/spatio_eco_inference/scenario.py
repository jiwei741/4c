from __future__ import annotations

import math
from typing import Any

import torch

from .dataset import DatasetBundle


SCENARIO_PRESETS: dict[str, dict[str, float]] = {
    "industrial_expansion": {
        "edgar_emission": 3.0,
        "built_ratio": 0.08,
        "vegetation_area_ratio": -0.06,
        "ndvi_mean": -0.04,
        "land_surface_temperature": 1.2,
    },
    "greening_restoration": {
        "edgar_emission": -1.5,
        "built_ratio": -0.04,
        "vegetation_area_ratio": 0.07,
        "ndvi_mean": 0.05,
        "land_surface_temperature": -0.8,
    },
}


def resolve_node_indices(bundle: DatasetBundle, scenario: dict[str, Any]) -> list[int]:
    if "node_indices" in scenario:
        return [int(index) for index in scenario["node_indices"]]

    node_ids = scenario.get("node_ids", [])
    node_lookup = {node_id: idx for idx, node_id in enumerate(bundle.node_ids)}
    missing = [node_id for node_id in node_ids if node_id not in node_lookup]
    if missing:
        raise KeyError(f"unknown node ids: {missing}")
    return [node_lookup[node_id] for node_id in node_ids]


def apply_feature_deltas(
    bundle: DatasetBundle,
    input_window: torch.Tensor,
    scenario: dict[str, Any],
) -> torch.Tensor:
    feature_lookup = {name: idx for idx, name in enumerate(bundle.feature_names)}
    feature_deltas = resolve_feature_deltas(bundle, scenario)
    node_weights = resolve_node_weights(bundle, scenario)
    temporal_weights = resolve_temporal_weights(input_window.size(1), scenario)

    modified = input_window.clone()
    for feature_name, delta in feature_deltas.items():
        if feature_name not in feature_lookup:
            raise KeyError(f"unknown feature name: {feature_name}")
        feature_index = feature_lookup[feature_name]
        delta_value = float(delta)
        for time_index, time_weight in enumerate(temporal_weights.tolist()):
            if abs(time_weight) < 1e-8:
                continue
            modified[:, time_index, :, feature_index] += delta_value * time_weight * node_weights

    return modified


def resolve_feature_deltas(bundle: DatasetBundle, scenario: dict[str, Any]) -> dict[str, float]:
    feature_deltas = dict(scenario.get("feature_deltas", {}))
    preset_name = str(scenario.get("preset", "")).strip().lower()
    intensity = float(scenario.get("intensity", 1.0))

    if preset_name:
        if preset_name not in SCENARIO_PRESETS:
            raise KeyError(f"unknown scenario preset: {preset_name}")
        for feature_name, delta in SCENARIO_PRESETS[preset_name].items():
            feature_deltas.setdefault(feature_name, delta * intensity)

    available_features = set(bundle.feature_names)
    return {
        feature_name: float(delta)
        for feature_name, delta in feature_deltas.items()
        if feature_name in available_features
    }


def resolve_node_weights(bundle: DatasetBundle, scenario: dict[str, Any]) -> torch.Tensor:
    node_indices = resolve_node_indices(bundle, scenario)
    weights = torch.zeros(bundle.num_nodes, dtype=torch.float32)
    weights[node_indices] = 1.0

    propagation = scenario.get("graph_propagation")
    if not propagation:
        return weights

    hops = int(propagation.get("hops", 1))
    attenuation = float(propagation.get("attenuation", 0.6))
    blend_mode = str(propagation.get("blend_mode", "max")).lower()
    adjacency = torch.as_tensor(bundle.adjacency, dtype=torch.float32)
    degree = adjacency.sum(dim=1, keepdim=True).clamp(min=1e-6)
    transition = adjacency / degree

    accumulated = weights.clone()
    frontier = weights.clone()
    for hop in range(1, hops + 1):
        frontier = torch.matmul(frontier.unsqueeze(0), transition).squeeze(0)
        weighted_frontier = frontier * (attenuation ** hop)
        if blend_mode == "sum":
            accumulated = accumulated + weighted_frontier
        else:
            accumulated = torch.maximum(accumulated, weighted_frontier)

    return torch.clamp(accumulated, min=0.0, max=1.0)


def resolve_temporal_weights(num_steps: int, scenario: dict[str, Any]) -> torch.Tensor:
    if bool(scenario.get("apply_to_all_timesteps", False)):
        return torch.ones(num_steps, dtype=torch.float32)

    profile = scenario.get("temporal_profile")
    if not profile:
        weights = torch.zeros(num_steps, dtype=torch.float32)
        weights[-1] = 1.0
        return weights

    mode = str(profile.get("mode", "last")).lower()
    if mode == "last":
        weights = torch.zeros(num_steps, dtype=torch.float32)
        weights[-1] = 1.0
        return weights
    if mode == "uniform":
        return torch.ones(num_steps, dtype=torch.float32)
    if mode == "linear":
        start_weight = float(profile.get("start_weight", 0.4))
        end_weight = float(profile.get("end_weight", 1.0))
        return torch.linspace(start_weight, end_weight, steps=num_steps, dtype=torch.float32)
    if mode == "exp":
        start_weight = float(profile.get("start_weight", 0.25))
        end_weight = float(profile.get("end_weight", 1.0))
        weights = []
        for index in range(num_steps):
            alpha = (index + 1) / max(num_steps, 1)
            weight = start_weight * math.exp(math.log(end_weight / max(start_weight, 1e-6)) * alpha)
            weights.append(weight)
        return torch.tensor(weights, dtype=torch.float32)
    raise ValueError(f"unsupported temporal_profile mode: {mode}")
