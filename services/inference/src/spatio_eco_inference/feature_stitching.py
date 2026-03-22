from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class GridNode:
    node_id: str
    latitude: float
    longitude: float


@dataclass
class FeatureSource:
    name: str
    path: str
    feature_columns: list[str]
    values: dict[tuple[str, str], list[float]]
    timestamps: set[str]


def build_training_arrays(
    config: dict[str, Any],
    service_root: Path,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, np.ndarray]:
    grid_nodes = load_grid_nodes(config["grid"], service_root)
    node_ids = [node.node_id for node in grid_nodes]

    sources_config = config["sources"]
    sources = [
        load_feature_source(source_name, source_config, service_root)
        for source_name, source_config in sources_config.items()
    ]
    labels = load_label_source(config["labels"], service_root)

    timestamp_mode = config.get("options", {}).get("timestamps", "intersection")
    timestamps = resolve_timestamps(sources, labels, timestamp_mode)
    feature_names = [column for source in sources for column in source.feature_columns]

    x = np.full(
        (len(timestamps), len(node_ids), len(feature_names)),
        np.nan,
        dtype=np.float32,
    )
    y = np.full((len(timestamps), len(node_ids), 1), np.nan, dtype=np.float32)

    timestamp_index = {value: idx for idx, value in enumerate(timestamps)}
    node_index = {node_id: idx for idx, node_id in enumerate(node_ids)}

    feature_offset = 0
    for source in sources:
        for (timestamp, node_id), values in source.values.items():
            if timestamp not in timestamp_index:
                continue
            if node_id not in node_index:
                raise KeyError(f"node_id {node_id} from {source.name} not found in grid table")
            t_idx = timestamp_index[timestamp]
            n_idx = node_index[node_id]
            width = len(values)
            x[t_idx, n_idx, feature_offset : feature_offset + width] = values
        feature_offset += len(source.feature_columns)

    target_column = labels["target_column"]
    for (timestamp, node_id), value in labels["values"].items():
        if timestamp not in timestamp_index:
            continue
        if node_id not in node_index:
            raise KeyError(f"node_id {node_id} from labels not found in grid table")
        y[timestamp_index[timestamp], node_index[node_id], 0] = value

    missing_strategy = config.get("options", {}).get("missing_value_strategy", "error")
    x = handle_missing_values(x, missing_strategy, "features")
    y = handle_missing_values(y, missing_strategy, "labels")

    adjacency = build_adjacency(grid_nodes, config["adjacency"], x, feature_names)
    metadata = {
        "study_area_name": config["study_area"]["name"],
        "timestamps": timestamps,
        "node_ids": node_ids,
        "feature_names": feature_names,
        "target_name": target_column,
        "source_names": [source.name for source in sources],
        "source_paths": {source.name: source.path for source in sources},
    }
    return metadata, x, y, adjacency


def write_training_dataset(
    metadata: dict[str, Any],
    x: np.ndarray,
    y: np.ndarray,
    adjacency: np.ndarray,
    output_path: Path,
    metadata_path: Path | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        x=x.astype(np.float32),
        y=y.astype(np.float32),
        adjacency=adjacency.astype(np.float32),
        timestamps=np.array(metadata["timestamps"]),
        node_ids=np.array(metadata["node_ids"]),
        feature_names=np.array(metadata["feature_names"]),
        target_name=np.array([metadata["target_name"]]),
    )

    if metadata_path is not None:
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def load_grid_nodes(config: dict[str, Any], service_root: Path) -> list[GridNode]:
    path = resolve_path(service_root, config["path"])
    rows = read_csv_rows(path)
    node_id_column = config["node_id_column"]
    lat_column = config["lat_column"]
    lon_column = config["lon_column"]

    nodes: list[GridNode] = []
    seen: set[str] = set()
    for row in rows:
        node_id = row[node_id_column].strip()
        if node_id in seen:
            raise ValueError(f"duplicate node_id in grid table: {node_id}")
        seen.add(node_id)
        nodes.append(
            GridNode(
                node_id=node_id,
                latitude=float(row[lat_column]),
                longitude=float(row[lon_column]),
            )
        )
    return nodes


def load_feature_source(
    source_name: str,
    config: dict[str, Any],
    service_root: Path,
) -> FeatureSource:
    path = resolve_source_path(service_root, config)
    rows = read_csv_rows(path)
    timestamp_column = config["timestamp_column"]
    node_id_column = config["node_id_column"]
    feature_columns = list(config["feature_columns"])

    values: dict[tuple[str, str], list[float]] = {}
    timestamps: set[str] = set()
    for row in rows:
        key = (row[timestamp_column].strip(), row[node_id_column].strip())
        if key in values:
            raise ValueError(f"duplicate record in {source_name}: {key}")
        values[key] = [float(row[column]) for column in feature_columns]
        timestamps.add(key[0])

    return FeatureSource(
        name=source_name,
        path=str(path),
        feature_columns=feature_columns,
        values=values,
        timestamps=timestamps,
    )


def load_label_source(config: dict[str, Any], service_root: Path) -> dict[str, Any]:
    path = resolve_path(service_root, config["path"])
    rows = read_csv_rows(path)
    timestamp_column = config["timestamp_column"]
    node_id_column = config["node_id_column"]
    target_column = config["target_column"]

    values: dict[tuple[str, str], float] = {}
    timestamps: set[str] = set()
    for row in rows:
        key = (row[timestamp_column].strip(), row[node_id_column].strip())
        if key in values:
            raise ValueError(f"duplicate record in labels: {key}")
        values[key] = float(row[target_column])
        timestamps.add(key[0])

    return {
        "target_column": target_column,
        "values": values,
        "timestamps": timestamps,
    }


def resolve_timestamps(
    sources: list[FeatureSource],
    labels: dict[str, Any],
    mode: str,
) -> list[str]:
    all_sets = [source.timestamps for source in sources] + [labels["timestamps"]]
    if mode == "intersection":
        timestamps = set.intersection(*all_sets)
    elif mode == "union":
        timestamps = set.union(*all_sets)
    else:
        raise ValueError(f"unsupported timestamps mode: {mode}")
    return sorted(timestamps)


def handle_missing_values(array: np.ndarray, strategy: str, name: str) -> np.ndarray:
    if not np.isnan(array).any():
        return array
    if strategy == "zero":
        return np.nan_to_num(array, nan=0.0)
    missing_count = int(np.isnan(array).sum())
    raise ValueError(f"{name} tensor still contains {missing_count} missing values")


def build_adjacency(
    nodes: list[GridNode],
    config: dict[str, Any],
    x: np.ndarray | None = None,
    feature_names: list[str] | None = None,
) -> np.ndarray:
    method = config.get("method", "radius")
    num_nodes = len(nodes)
    adjacency = np.zeros((num_nodes, num_nodes), dtype=np.float32)

    if method == "radius":
        radius_km = float(config["radius_km"])
        for i, source in enumerate(nodes):
            for j, target in enumerate(nodes):
                if i == j:
                    continue
                if haversine_km(source.latitude, source.longitude, target.latitude, target.longitude) <= radius_km:
                    adjacency[i, j] = 1.0
            if adjacency[i].sum() == 0.0:
                nearest = nearest_neighbor_index(nodes, i)
                adjacency[i, nearest] = 1.0
    elif method == "knn":
        k = int(config["k"])
        for i, source in enumerate(nodes):
            distances = []
            for j, target in enumerate(nodes):
                if i == j:
                    continue
                distance = haversine_km(source.latitude, source.longitude, target.latitude, target.longitude)
                distances.append((distance, j))
            distances.sort(key=lambda item: item[0])
            for _, neighbor_index in distances[:k]:
                adjacency[i, neighbor_index] = 1.0
    elif method == "wind_radius":
        if x is None or feature_names is None:
            raise ValueError("wind_radius adjacency requires feature tensors and feature names")
        radius_km = float(config["radius_km"])
        base_weight = float(config.get("base_weight", 0.25))
        wind_scale = float(config.get("wind_scale", 0.75))
        distance_power = float(config.get("distance_power", 1.0))
        u_feature = str(config.get("u_feature", "u10_wind"))
        v_feature = str(config.get("v_feature", "v10_wind"))
        feature_index = {name: idx for idx, name in enumerate(feature_names)}
        if u_feature not in feature_index or v_feature not in feature_index:
            raise KeyError(f"wind_radius adjacency requires features {u_feature} and {v_feature}")
        mean_u = x[:, :, feature_index[u_feature]].mean(axis=0)
        mean_v = x[:, :, feature_index[v_feature]].mean(axis=0)

        for i, source in enumerate(nodes):
            for j, target in enumerate(nodes):
                if i == j:
                    continue
                distance = haversine_km(source.latitude, source.longitude, target.latitude, target.longitude)
                if distance > radius_km:
                    continue
                alignment = wind_alignment(
                    source.latitude,
                    source.longitude,
                    target.latitude,
                    target.longitude,
                    float(mean_u[i]),
                    float(mean_v[i]),
                )
                distance_weight = 1.0 / ((distance + 1.0) ** distance_power)
                adjacency[i, j] = distance_weight * (base_weight + wind_scale * alignment)
            if adjacency[i].sum() == 0.0:
                nearest = nearest_neighbor_index(nodes, i)
                distance = haversine_km(
                    nodes[i].latitude,
                    nodes[i].longitude,
                    nodes[nearest].latitude,
                    nodes[nearest].longitude,
                )
                adjacency[i, nearest] = 1.0 / ((distance + 1.0) ** distance_power)
    elif method == "hybrid_wind_knn":
        if x is None or feature_names is None:
            raise ValueError("hybrid_wind_knn adjacency requires feature tensors and feature names")
        radius_km = float(config["radius_km"])
        k = int(config["k"])
        base_weight = float(config.get("base_weight", 0.2))
        wind_scale = float(config.get("wind_scale", 0.5))
        similarity_weight = float(config.get("similarity_weight", 0.4))
        distance_power = float(config.get("distance_power", 1.0))
        u_feature = str(config.get("u_feature", "u10_wind"))
        v_feature = str(config.get("v_feature", "v10_wind"))
        similarity_features = list(config.get("similarity_features", []))
        feature_index = {name: idx for idx, name in enumerate(feature_names)}
        if u_feature not in feature_index or v_feature not in feature_index:
            raise KeyError(f"hybrid_wind_knn adjacency requires features {u_feature} and {v_feature}")
        missing_similarity = [name for name in similarity_features if name not in feature_index]
        if missing_similarity:
            raise KeyError(f"unknown similarity features: {missing_similarity}")

        mean_u = x[:, :, feature_index[u_feature]].mean(axis=0)
        mean_v = x[:, :, feature_index[v_feature]].mean(axis=0)
        similarity_matrix = build_similarity_matrix(x, feature_names, similarity_features)

        for i, source in enumerate(nodes):
            scores: list[tuple[float, int]] = []
            for j, target in enumerate(nodes):
                if i == j:
                    continue
                distance = haversine_km(source.latitude, source.longitude, target.latitude, target.longitude)
                if distance > radius_km:
                    continue
                alignment = wind_alignment(
                    source.latitude,
                    source.longitude,
                    target.latitude,
                    target.longitude,
                    float(mean_u[i]),
                    float(mean_v[i]),
                )
                distance_weight = 1.0 / ((distance + 1.0) ** distance_power)
                similarity = float(similarity_matrix[i, j])
                score = distance_weight * (base_weight + wind_scale * alignment) + similarity_weight * similarity
                scores.append((score, j))

            scores.sort(key=lambda item: item[0], reverse=True)
            for score, neighbor_index in scores[:k]:
                adjacency[i, neighbor_index] = score
            if adjacency[i].sum() == 0.0:
                nearest = nearest_neighbor_index(nodes, i)
                adjacency[i, nearest] = 1.0
    else:
        raise ValueError(f"unsupported adjacency method: {method}")

    if bool(config.get("symmetric", True)):
        adjacency = np.maximum(adjacency, adjacency.T)
    return adjacency


def nearest_neighbor_index(nodes: list[GridNode], source_index: int) -> int:
    source = nodes[source_index]
    distances = []
    for target_index, target in enumerate(nodes):
        if target_index == source_index:
            continue
        distance = haversine_km(source.latitude, source.longitude, target.latitude, target.longitude)
        distances.append((distance, target_index))
    distances.sort(key=lambda item: item[0])
    return distances[0][1]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2.0) ** 2
    )
    return 2.0 * radius * math.asin(math.sqrt(a))


def wind_alignment(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    u_wind: float,
    v_wind: float,
) -> float:
    east_km = (lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2.0)) * 111.32
    north_km = (lat2 - lat1) * 110.57
    target_norm = math.sqrt(east_km * east_km + north_km * north_km)
    wind_norm = math.sqrt(u_wind * u_wind + v_wind * v_wind)
    if target_norm < 1e-6 or wind_norm < 1e-6:
        return 0.5
    direction_dot = (east_km / target_norm) * (u_wind / wind_norm) + (north_km / target_norm) * (v_wind / wind_norm)
    return max(0.0, direction_dot)


def build_similarity_matrix(
    x: np.ndarray,
    feature_names: list[str],
    similarity_features: list[str],
) -> np.ndarray:
    num_nodes = x.shape[1]
    if not similarity_features:
        return np.zeros((num_nodes, num_nodes), dtype=np.float32)

    feature_index = {name: idx for idx, name in enumerate(feature_names)}
    stacked = np.stack([x[:, :, feature_index[name]].mean(axis=0) for name in similarity_features], axis=1)
    mean = stacked.mean(axis=0, keepdims=True)
    std = stacked.std(axis=0, keepdims=True)
    std = np.where(std < 1e-6, 1.0, std)
    normalized = (stacked - mean) / std

    similarity = np.zeros((num_nodes, num_nodes), dtype=np.float32)
    for i in range(num_nodes):
        diffs = np.abs(normalized[i][None, :] - normalized)
        similarity[i] = np.exp(-diffs.mean(axis=1))
    np.fill_diagonal(similarity, 0.0)
    return similarity


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def resolve_source_path(service_root: Path, config: dict[str, Any]) -> Path:
    if "path_candidates" in config:
        candidates = [resolve_path(service_root, raw_path) for raw_path in config["path_candidates"]]
        for candidate in candidates:
            if candidate.exists() and csv_has_rows(candidate):
                return candidate
        if candidates:
            return candidates[-1]
    return resolve_path(service_root, config["path"])


def csv_has_rows(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return next(reader, None) is not None


def resolve_path(service_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (service_root / path).resolve()
