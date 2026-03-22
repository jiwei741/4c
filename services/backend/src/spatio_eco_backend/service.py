from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import (
    ARCHITECTURE_LAYERS,
    BACKEND_RUNTIME_ROOT,
    DEFAULT_MULTI_STEP_MODEL,
    DEFAULT_SINGLE_STEP_MODEL,
    DOC_REFERENCES,
    EDGAR_FEATURES_PATH,
    ERA5_FEATURES_PATH,
    EXAMPLE_SCENARIOS,
    GRID_NODES_PATH,
    LABELS_PATH,
    MEMBER_STATUS,
    MODEL_ARTIFACTS,
    SEGMENTATION_JOB_MANIFEST_PATH,
    SEGMENTATION_REMOTE_BUNDLE_ROOT,
    SEGMENTATION_REMOTE_IMPORT_SUMMARY_PATH,
    SENTINEL2_PROXY_FEATURES_PATH,
    SENTINEL2_SAM2_FEATURES_PATH,
    SOURCE_POLICY_PATH,
    STUDY_AREA,
)
from .inference_runner import run_live_scenario

SUPPORTED_SENTINEL2_SOURCE_KEYS = ("quarterly_proxy", "sam2_remote")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_or_none(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _file_size_mb(path: Path) -> float:
    return round(path.stat().st_size / (1024 * 1024), 3)


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def _csv_columns(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
    return [value for value in header if value]


def _path_status(path: Path, *, kind: str, owner: str, description: str) -> dict[str, Any]:
    exists = path.exists()
    payload = {
        "path": str(path),
        "exists": exists,
        "kind": kind,
        "owner": owner,
        "description": description,
    }
    if exists:
        payload["size_mb"] = _file_size_mb(path)
        if path.suffix.lower() == ".csv":
            payload["rows"] = _csv_row_count(path)
            payload["columns"] = _csv_columns(path)
    return payload


def _to_float_values(node_map: dict[str, Any]) -> list[float]:
    return [float(value) for value in node_map.values()]


def _top_nodes(node_map: dict[str, Any], *, limit: int = 5, absolute: bool = False) -> list[dict[str, float | str]]:
    keyed_items = []
    for node_id, value in node_map.items():
        numeric = float(value)
        keyed_items.append((str(node_id), abs(numeric) if absolute else numeric, numeric))
    keyed_items.sort(key=lambda item: item[1], reverse=True)
    return [{"node_id": node_id, "value": original} for node_id, _, original in keyed_items[:limit]]


def _stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "min": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def _percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = max(0.0, min(1.0, ratio)) * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _model_lookup(model_key: str) -> Any:
    for artifact in MODEL_ARTIFACTS:
        if artifact.key == model_key:
            return artifact
    raise KeyError(f"unknown model key: {model_key}")


def _grid_node_lookup() -> dict[str, dict[str, Any]]:
    with GRID_NODES_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return {
            row["node_id"]: {
                "node_id": row["node_id"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "max_lat": float(row["max_lat"]),
                "max_lon": float(row["max_lon"]),
                "min_lat": float(row["min_lat"]),
                "min_lon": float(row["min_lon"]),
            }
            for row in reader
        }


def _attach_coordinates(node_map: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _grid_node_lookup()
    features: list[dict[str, Any]] = []
    for node_id, value in node_map.items():
        if node_id not in nodes:
            continue
        features.append({**nodes[node_id], "value": float(value)})
    return features


def _prediction_horizons(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if "predictions_by_horizon" in payload:
        return payload["predictions_by_horizon"]
    if "predictions" in payload:
        horizon = payload.get("prediction_timestamp_to", "latest")
        return {horizon: payload["predictions"]}
    return {}


def summary_horizon(payload: dict[str, Any]) -> str:
    if payload.get("forecast_timestamps"):
        return payload["forecast_timestamps"][0]
    if payload.get("delta_by_horizon"):
        return next(iter(payload["delta_by_horizon"]))
    return "latest"


def _scenario_delta_map(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if "delta_by_horizon" in payload:
        horizon = summary_horizon(payload)
        return horizon, payload["delta_by_horizon"].get(horizon, {})
    if "delta" in payload:
        return payload.get("prediction_timestamp_to", "latest"), payload["delta"]
    return "latest", {}


def _scenario_summary(payload: dict[str, Any]) -> dict[str, Any]:
    horizon, delta_map = _scenario_delta_map(payload)
    values = [abs(value) for value in _to_float_values(delta_map)]
    return {
        "forecast_horizon": horizon,
        "changed_nodes": payload.get("changed_nodes", []),
        "feature_deltas": payload.get("feature_deltas", {}),
        "delta_summary": _stats(values),
        "top_impacts": _top_nodes(delta_map, absolute=True),
    }


def _latest_remote_bundle_dir() -> Path | None:
    if not SEGMENTATION_REMOTE_BUNDLE_ROOT.exists():
        return None
    candidates = [item for item in SEGMENTATION_REMOTE_BUNDLE_ROOT.iterdir() if item.is_dir()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item.name)[-1]


def _default_source_policy() -> dict[str, Any]:
    return {
        "mode": "auto",
        "preferred_source_key": None,
        "updated_at": None,
    }


def _read_source_policy() -> dict[str, Any]:
    payload = _default_source_policy()
    if SOURCE_POLICY_PATH.exists():
        try:
            raw = _load_json(SOURCE_POLICY_PATH)
        except json.JSONDecodeError:
            raw = {}
        mode = str(raw.get("mode", payload["mode"])).strip().lower()
        preferred = raw.get("preferred_source_key")
        if mode in {"auto", "manual"}:
            payload["mode"] = mode
        if preferred in SUPPORTED_SENTINEL2_SOURCE_KEYS:
            payload["preferred_source_key"] = preferred
        payload["updated_at"] = raw.get("updated_at")
    return payload


def _write_source_policy(mode: str, preferred_source_key: str | None) -> dict[str, Any]:
    BACKEND_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": mode,
        "preferred_source_key": preferred_source_key,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    SOURCE_POLICY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _sentinel2_source_items() -> list[dict[str, Any]]:
    sources = [
        {
            "key": "quarterly_proxy",
            "name": "Quarterly Proxy Features",
            "path": SENTINEL2_PROXY_FEATURES_PATH,
            "description": "Local quarterly Sentinel-2 proxy features that currently support training and platform demos.",
            "stage": "available",
        },
        {
            "key": "sam2_remote",
            "name": "Remote SAM-2 Features",
            "path": SENTINEL2_SAM2_FEATURES_PATH,
            "description": "Remote GPU generated SAM-2 feature table. This source becomes active automatically when the CSV is present.",
            "stage": "preferred_when_ready",
        },
    ]
    items: list[dict[str, Any]] = []
    for source in sources:
        rows = _csv_row_count(source["path"])
        available = source["path"].exists() and rows > 0
        items.append(
            {
                "key": source["key"],
                "name": source["name"],
                "path": str(source["path"]),
                "rows": rows,
                "exists": source["path"].exists(),
                "available": available,
                "stage": source["stage"],
                "description": source["description"],
            }
        )
    return items


def _effective_sentinel2_switch() -> dict[str, Any]:
    policy = _read_source_policy()
    items = _sentinel2_source_items()
    item_lookup = {item["key"]: item for item in items}

    auto_item = item_lookup["quarterly_proxy"]
    if item_lookup["sam2_remote"]["available"]:
        auto_item = item_lookup["sam2_remote"]

    effective_mode = "auto"
    effective_reason = "fallback_to_quarterly_proxy"
    active_item = auto_item

    if auto_item["key"] == "sam2_remote":
        effective_reason = "sam2_remote_ready"

    if policy["mode"] == "manual" and policy["preferred_source_key"] in item_lookup:
        preferred_item = item_lookup[policy["preferred_source_key"]]
        if preferred_item["available"]:
            active_item = preferred_item
            effective_mode = "manual"
            effective_reason = "manual_preference_applied"
        else:
            effective_mode = "auto_fallback"
            effective_reason = "manual_preference_unavailable"

    return {
        "policy": policy,
        "effective_mode": effective_mode,
        "effective_reason": effective_reason,
        "active_key": active_item["key"],
        "active_name": active_item["name"],
        "active_path": active_item["path"],
        "can_switch_to_sam2": item_lookup["sam2_remote"]["available"],
        "switch_rule": "Auto uses SAM-2 when available. Manual mode can pin quarterly_proxy or sam2_remote when the selected source is ready.",
        "items": items,
    }


def get_source_policy() -> dict[str, Any]:
    switch = _effective_sentinel2_switch()
    return {
        "policy": switch["policy"],
        "effective_mode": switch["effective_mode"],
        "effective_reason": switch["effective_reason"],
        "active_key": switch["active_key"],
        "active_name": switch["active_name"],
        "active_path": switch["active_path"],
        "can_switch_to_sam2": switch["can_switch_to_sam2"],
        "options": switch["items"],
    }


def set_source_policy(payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get("mode", "auto")).strip().lower()
    preferred = payload.get("preferred_source_key")

    if mode not in {"auto", "manual"}:
        raise ValueError("mode must be 'auto' or 'manual'")
    if mode == "manual" and preferred not in SUPPORTED_SENTINEL2_SOURCE_KEYS:
        raise ValueError("preferred_source_key must be one of quarterly_proxy or sam2_remote")
    if mode == "auto":
        preferred = None

    _write_source_policy(mode, preferred)
    return get_source_policy()


def get_segmentation_overview() -> dict[str, Any]:
    latest_bundle = _latest_remote_bundle_dir()
    latest_bundle_manifest = None
    if latest_bundle is not None and (latest_bundle / "sam2_job_manifest.json").exists():
        latest_bundle_manifest = _load_json(latest_bundle / "sam2_job_manifest.json")
    import_summary = _json_or_none(SEGMENTATION_REMOTE_IMPORT_SUMMARY_PATH) or {}

    job_count = int(latest_bundle_manifest.get("job_count", 0)) if latest_bundle_manifest else 0
    complete_scene_count = int(import_summary.get("complete_scene_count", 0))
    missing_scene_ids = list(import_summary.get("missing_scene_ids", []))
    completion_rate = 0.0
    if job_count > 0:
        completion_rate = round(complete_scene_count / job_count, 4)

    sam2_rows = _csv_row_count(SENTINEL2_SAM2_FEATURES_PATH)
    next_action = "export_remote_bundle"
    if latest_bundle_manifest and complete_scene_count == 0:
        next_action = "wait_for_remote_results"
    if complete_scene_count > 0:
        next_action = "import_remote_outputs"
    if sam2_rows > 0:
        next_action = "sam2_features_ready_for_training"

    return {
        "latest_bundle_dir": str(latest_bundle) if latest_bundle else None,
        "manifest": latest_bundle_manifest,
        "import_summary_path": str(SEGMENTATION_REMOTE_IMPORT_SUMMARY_PATH),
        "import_summary": import_summary or None,
        "job_manifest_path": str(SEGMENTATION_JOB_MANIFEST_PATH),
        "job_manifest_exists": SEGMENTATION_JOB_MANIFEST_PATH.exists() or latest_bundle_manifest is not None,
        "job_count": job_count,
        "complete_scene_count": complete_scene_count,
        "missing_scene_count": len(missing_scene_ids),
        "missing_scene_ids": missing_scene_ids,
        "completion_rate": completion_rate,
        "sam2_feature_rows": sam2_rows,
        "sam2_feature_path": str(SENTINEL2_SAM2_FEATURES_PATH),
        "sam2_feature_ready": sam2_rows > 0,
        "next_action": next_action,
    }


def get_data_sources() -> dict[str, Any]:
    sentinel2 = _effective_sentinel2_switch()
    segmentation_status = get_segmentation_overview()
    items = [
        {
            "key": "sentinel2",
            "name": "Sentinel-2 Features",
            "owner": "Member B",
            "required_for": ["segmentation", "training", "map_display"],
            "active_source": sentinel2["active_key"],
            "active_path": sentinel2["active_path"],
            "effective_mode": sentinel2["effective_mode"],
            "effective_reason": sentinel2["effective_reason"],
            "sources": sentinel2["items"],
        },
        {
            "key": "era5",
            "name": "ERA5 Quarterly Features",
            "owner": "Member C",
            "required_for": ["training", "inference"],
            **_path_status(
                ERA5_FEATURES_PATH,
                kind="csv",
                owner="Member C",
                description="Quarterly meteorological features already merged into the training set.",
            ),
        },
        {
            "key": "edgar",
            "name": "EDGAR Quarterly Features",
            "owner": "Member C",
            "required_for": ["training", "scenario"],
            **_path_status(
                EDGAR_FEATURES_PATH,
                kind="csv",
                owner="Member C",
                description="Quarterly emission proxy features already merged into ST-GNN training.",
            ),
        },
        {
            "key": "labels",
            "name": "GPP / Net Carbon Flux Labels",
            "owner": "Member A",
            "required_for": ["training", "evaluation"],
            **_path_status(
                LABELS_PATH,
                kind="csv",
                owner="Member A",
                description="Quality-filtered quarterly labels used for current model evaluation.",
            ),
        },
    ]
    return {
        "study_area": STUDY_AREA["name"],
        "sentinel2_switch": sentinel2,
        "segmentation_remote": segmentation_status,
        "items": items,
    }


def get_platform_status() -> dict[str, Any]:
    data_sources = get_data_sources()
    models = list_models()
    segmentation = data_sources["segmentation_remote"]

    service_counts = {
        "total": len(ARCHITECTURE_LAYERS),
        "active": sum(1 for item in ARCHITECTURE_LAYERS if item["status"] == "active"),
        "scaffolded": sum(1 for item in ARCHITECTURE_LAYERS if item["status"] == "scaffolded"),
        "pending_fill": sum(1 for item in ARCHITECTURE_LAYERS if item["status"] in {"pending_fill", "remote_only"}),
    }

    ready_data_count = sum(
        1
        for item in data_sources["items"]
        if item["key"] == "sentinel2"
        or item.get("exists")
    )

    model_leader = min(models, key=lambda item: float(item["metrics"]["rmse"]))
    recommendations = []
    if not data_sources["sentinel2_switch"]["can_switch_to_sam2"]:
        recommendations.append("Keep using quarterly_proxy until remote SAM-2 features are imported.")
    if segmentation["job_count"] > 0 and segmentation["complete_scene_count"] < segmentation["job_count"]:
        recommendations.append("Remote segmentation jobs are still incomplete. Wait for more scene outputs.")
    if segmentation["sam2_feature_ready"]:
        recommendations.append("SAM-2 feature CSV is ready. Rebuild training datasets when you want to switch inputs.")
    if not recommendations:
        recommendations.append("Platform data sources and artifacts are in a stable state.")

    return {
        "study_area": STUDY_AREA,
        "service_summary": service_counts,
        "data_summary": {
            "ready_data_count": ready_data_count,
            "tracked_data_count": len(data_sources["items"]),
            "active_sentinel2_source": data_sources["sentinel2_switch"]["active_key"],
            "effective_source_mode": data_sources["sentinel2_switch"]["effective_mode"],
        },
        "model_summary": {
            "count": len(models),
            "leader_key": model_leader["key"],
            "leader_name": model_leader["name"],
            "leader_rmse": model_leader["metrics"]["rmse"],
            "leader_mae": model_leader["metrics"]["mae"],
        },
        "segmentation_summary": {
            "job_count": segmentation["job_count"],
            "complete_scene_count": segmentation["complete_scene_count"],
            "completion_rate": segmentation["completion_rate"],
            "sam2_feature_ready": segmentation["sam2_feature_ready"],
            "next_action": segmentation["next_action"],
        },
        "source_policy": get_source_policy(),
        "recommendations": recommendations,
    }


def get_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "spatio-eco-backend",
        "mode": "file-backed-mvp",
        "study_area": STUDY_AREA["name"],
    }


def list_models() -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for artifact in MODEL_ARTIFACTS:
        metrics = _load_json(artifact.metrics_path)
        models.append(
            {
                "key": artifact.key,
                "name": artifact.name,
                "stage": artifact.stage,
                "owner": artifact.owner,
                "horizon": artifact.horizon,
                "output_dir": str(artifact.output_dir),
                "metrics": metrics["test_metrics"],
                "best_val_loss": metrics["best_val_loss"],
            }
        )
    return models


def get_model(model_key: str) -> dict[str, Any]:
    artifact = _model_lookup(model_key)
    metrics = _load_json(artifact.metrics_path)
    return {
        "key": artifact.key,
        "name": artifact.name,
        "stage": artifact.stage,
        "owner": artifact.owner,
        "horizon": artifact.horizon,
        "output_dir": str(artifact.output_dir),
        "metrics": metrics["test_metrics"],
        "best_val_loss": metrics["best_val_loss"],
        "normalization": metrics.get("normalization", {}),
        "target_transform": metrics.get("target_transform", {}),
        "prediction_constraints": metrics.get("prediction_constraints", {}),
        "dataset_path": str(artifact.dataset_path),
    }


def get_prediction_payload(model_key: str | None = None) -> dict[str, Any]:
    artifact = _model_lookup(model_key or DEFAULT_MULTI_STEP_MODEL)
    payload = _load_json(artifact.prediction_path)
    payload["model_key"] = artifact.key
    payload["model_name"] = artifact.name
    return payload


def get_prediction_summary(model_key: str | None = None) -> dict[str, Any]:
    payload = get_prediction_payload(model_key)
    horizons = _prediction_horizons(payload)
    summary: dict[str, Any] = {
        "model_key": payload["model_key"],
        "model_name": payload["model_name"],
        "target_name": payload["target_name"],
        "prediction_window": {
            "from": payload.get("prediction_timestamp_from"),
            "to": payload.get("prediction_timestamp_to"),
        },
        "forecast_timestamps": payload.get("forecast_timestamps", []),
        "by_horizon": {},
    }
    for horizon, node_map in horizons.items():
        values = _to_float_values(node_map)
        summary["by_horizon"][horizon] = {
            **_stats(values),
            "top_nodes": _top_nodes(node_map),
        }
    return summary


def get_grid_nodes() -> dict[str, Any]:
    items = list(_grid_node_lookup().values())
    return {
        "study_area": STUDY_AREA["name"],
        "count": len(items),
        "items": items,
    }


def get_prediction_layer(model_key: str | None = None, horizon: str | None = None) -> dict[str, Any]:
    payload = get_prediction_payload(model_key)
    horizons = _prediction_horizons(payload)
    if not horizons:
        raise KeyError("no prediction horizons available")
    default_horizon = payload.get("forecast_timestamps", [next(iter(horizons))])[0]
    selected_horizon = horizon or default_horizon
    if selected_horizon not in horizons:
        raise KeyError(f"unknown forecast horizon: {selected_horizon}")
    return {
        "model_key": payload["model_key"],
        "model_name": payload["model_name"],
        "target_name": payload["target_name"],
        "horizon": selected_horizon,
        "items": _attach_coordinates(horizons[selected_horizon]),
    }


def get_prediction_analytics(
    model_key: str | None = None,
    horizon: str | None = None,
    compare_model_key: str | None = None,
) -> dict[str, Any]:
    payload = get_prediction_payload(model_key)
    horizons = _prediction_horizons(payload)
    if not horizons:
        raise KeyError("no prediction horizons available")

    selected_horizon = horizon or payload.get("forecast_timestamps", [next(iter(horizons))])[0]
    if selected_horizon not in horizons:
        raise KeyError(f"unknown forecast horizon: {selected_horizon}")

    compare_model_key = compare_model_key or "lstm_multistep_baseline"
    compare_payload = None
    compare_map: dict[str, Any] = {}
    if compare_model_key != payload["model_key"]:
        try:
            compare_payload = get_prediction_payload(compare_model_key)
            compare_horizons = _prediction_horizons(compare_payload)
            compare_map = compare_horizons.get(selected_horizon, {})
        except KeyError:
            compare_payload = None
            compare_map = {}

    node_map = horizons[selected_horizon]
    items = _attach_coordinates(node_map)
    values = [float(item["value"]) for item in items]
    min_value = min(values) if values else 0.0
    max_value = max(values) if values else 0.0
    span = max(max_value - min_value, 1e-6)
    p50 = _percentile(values, 0.5)
    p75 = _percentile(values, 0.75)
    p90 = _percentile(values, 0.9)

    positive_gap_map: dict[str, float] = {}
    negative_gap_map: dict[str, float] = {}
    category_counts = {"stable": 0, "elevated": 0, "high": 0, "critical": 0}

    for item in items:
        value = float(item["value"])
        if value >= p90:
            risk_level = "critical"
        elif value >= p75:
            risk_level = "high"
        elif value >= p50:
            risk_level = "elevated"
        else:
            risk_level = "stable"
        category_counts[risk_level] += 1

        normalized_score = (value - min_value) / span
        comparison_gap = None
        if compare_map:
            comparison_gap = value - float(compare_map.get(item["node_id"], 0.0))
            if comparison_gap >= 0:
                positive_gap_map[item["node_id"]] = comparison_gap
            else:
                negative_gap_map[item["node_id"]] = comparison_gap

        item["risk_level"] = risk_level
        item["risk_score"] = round(normalized_score, 6)
        item["comparison_gap"] = comparison_gap

    analytics_summary = {
        "thresholds": {"p50": p50, "p75": p75, "p90": p90},
        "category_counts": category_counts,
        "top_hotspots": _top_nodes(node_map),
        "top_positive_gap": _top_nodes(positive_gap_map) if positive_gap_map else [],
        "top_negative_gap": _top_nodes(negative_gap_map, absolute=True) if negative_gap_map else [],
    }

    return {
        "model_key": payload["model_key"],
        "model_name": payload["model_name"],
        "compare_model_key": compare_payload["model_key"] if compare_payload else None,
        "compare_model_name": compare_payload["model_name"] if compare_payload else None,
        "horizon": selected_horizon,
        "items": items,
        "summary": analytics_summary,
    }


def list_scenarios() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for scenario_key, meta in EXAMPLE_SCENARIOS.items():
        payload = _load_json(meta["output_path"])
        summary = _scenario_summary(payload)
        items.append({"key": scenario_key, "name": meta["name"], **summary})
    return items


def get_scenario_example(scenario_key: str) -> dict[str, Any]:
    meta = EXAMPLE_SCENARIOS[scenario_key]
    input_payload = _load_json(meta["input_path"])
    output_payload = _load_json(meta["output_path"])
    horizon = summary_horizon(output_payload)
    delta_by_horizon = output_payload.get("delta_by_horizon", {})
    delta_map = delta_by_horizon.get(horizon, output_payload.get("delta", {}))
    return {
        "key": scenario_key,
        "name": meta["name"],
        "input": input_payload,
        "output": output_payload,
        "delta_layer": _attach_coordinates(delta_map),
        "summary": _scenario_summary(output_payload),
    }


def run_scenario(request_payload: dict[str, Any]) -> dict[str, Any]:
    model_key = str(request_payload.get("model_key") or DEFAULT_MULTI_STEP_MODEL)
    artifact = _model_lookup(model_key)

    if "scenario" in request_payload:
        scenario_payload = dict(request_payload["scenario"])
    elif "scenario_key" in request_payload:
        scenario_payload = get_scenario_example(str(request_payload["scenario_key"]))["input"]
    else:
        scenario_payload = {
            key: value
            for key, value in request_payload.items()
            if key
            in {
                "preset",
                "intensity",
                "node_ids",
                "node_indices",
                "graph_propagation",
                "temporal_profile",
                "feature_deltas",
            }
        }

    if not scenario_payload:
        scenario_payload = get_scenario_example("industrial_expansion_enhanced")["input"]

    execution = run_live_scenario(artifact, scenario_payload)
    result_payload = execution["result"]
    first_horizon = summary_horizon(result_payload)
    delta_by_horizon = result_payload.get("delta_by_horizon", {})
    delta_map = delta_by_horizon.get(first_horizon, result_payload.get("delta", {}))
    return {
        "status": "completed",
        "model_key": model_key,
        "model_name": artifact.name,
        "artifacts": {
            "checkpoint_path": str(artifact.checkpoint_path),
            "dataset_path": str(artifact.dataset_path),
            "request_path": execution["request_path"],
            "output_path": execution["output_path"],
            "runtime_dir": str(BACKEND_RUNTIME_ROOT / "scenarios"),
        },
        "scenario_request": scenario_payload,
        "result": result_payload,
        "summary": _scenario_summary(result_payload),
        "delta_layer": _attach_coordinates(delta_map),
    }


def get_dashboard() -> dict[str, Any]:
    data_sources = get_data_sources()
    platform_status = get_platform_status()
    return {
        "project": {
            "name": "Spatio-Eco",
            "subtitle": "Regional carbon-sink monitoring and forecasting platform",
            "phase": "Platform MVP",
            "study_area": STUDY_AREA,
            "sentinel2_feature_source": data_sources["sentinel2_switch"]["active_key"],
        },
        "architecture": list(ARCHITECTURE_LAYERS),
        "members": list(MEMBER_STATUS),
        "models": list_models(),
        "default_models": {
            "single_step": DEFAULT_SINGLE_STEP_MODEL,
            "multi_step": DEFAULT_MULTI_STEP_MODEL,
        },
        "prediction_preview": get_prediction_summary(DEFAULT_MULTI_STEP_MODEL),
        "business_preview": get_prediction_analytics(DEFAULT_MULTI_STEP_MODEL),
        "scenario_preview": get_scenario_example("industrial_expansion_enhanced"),
        "data_sources": data_sources,
        "management": platform_status,
        "docs": list(DOC_REFERENCES),
        "roadmap": [
            "Continue local work on backend, frontend, data ingestion, and inference.",
            "Keep real SAM-2 execution on a remote GPU server instead of this laptop.",
            "Switch the training source to sentinel2_features_from_sam2.csv once remote segmentation results are imported.",
            "Keep improving platform integration and competition demo views.",
        ],
    }
