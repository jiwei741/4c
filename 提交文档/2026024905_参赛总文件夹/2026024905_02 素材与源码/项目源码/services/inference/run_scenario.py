from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.dataset import (
    infer_forecast_timestamps,
    latest_window,
    load_dataset,
    normalize_features_tensor,
)
from spatio_eco_inference.dataset import inverse_target_transform_tensor
from spatio_eco_inference.scenario import (
    apply_feature_deltas,
    resolve_feature_deltas,
    resolve_node_indices,
)
from spatio_eco_inference.training import (
    apply_prediction_constraints_tensor,
    build_model,
    select_device,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a scenario inference from a trained checkpoint.")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    config = checkpoint["config"]
    device = select_device(str(config["training"]["device"]))

    bundle = load_dataset(args.dataset)
    model = build_model(config=config, input_dim=bundle.num_features, adjacency=bundle.adjacency)
    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)
    model.eval()

    scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
    resolved_feature_deltas = resolve_feature_deltas(bundle, scenario)
    window = latest_window(bundle, int(config["data"]["input_window"]))
    modified_window = apply_feature_deltas(bundle, window, scenario)
    normalization = checkpoint.get("normalization", {})
    baseline_window = window.to(device=device, dtype=torch.float32)
    scenario_window = modified_window.to(device=device, dtype=torch.float32)
    if "features" in normalization:
        feature_mean = torch.tensor(normalization["features"]["mean"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
        feature_std = torch.tensor(normalization["features"]["std"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
        baseline_window = normalize_features_tensor(baseline_window, feature_mean, feature_std)
        scenario_window = normalize_features_tensor(scenario_window, feature_mean, feature_std)

    with torch.no_grad():
        baseline = model(baseline_window)
        scenario_pred = model(scenario_window)
        if "target" in normalization:
            target_mean = torch.tensor(normalization["target"]["mean"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
            target_std = torch.tensor(normalization["target"]["std"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
            baseline = baseline * target_std + target_mean
            scenario_pred = scenario_pred * target_std + target_mean
        target_transform = checkpoint.get("target_transform")
        baseline = inverse_target_transform_tensor(baseline, target_transform)
        scenario_pred = inverse_target_transform_tensor(scenario_pred, target_transform)
        prediction_constraints = checkpoint.get("prediction_constraints")
        baseline = apply_prediction_constraints_tensor(baseline, prediction_constraints)
        scenario_pred = apply_prediction_constraints_tensor(scenario_pred, prediction_constraints)
        baseline = baseline.cpu().numpy()[0, :, :, 0]
        scenario_pred = scenario_pred.cpu().numpy()[0, :, :, 0]

    changed_indices = resolve_node_indices(bundle, scenario)
    forecast_timestamps = infer_forecast_timestamps(bundle.timestamps, baseline.shape[0])
    baseline_by_horizon = build_predictions_by_horizon(bundle.node_ids, forecast_timestamps, baseline)
    scenario_by_horizon = build_predictions_by_horizon(bundle.node_ids, forecast_timestamps, scenario_pred)
    delta_by_horizon = build_predictions_by_horizon(bundle.node_ids, forecast_timestamps, scenario_pred - baseline)
    result = {
        "target_name": bundle.target_name,
        "changed_nodes": [bundle.node_ids[index] for index in changed_indices],
        "feature_deltas": resolved_feature_deltas,
        "forecast_timestamps": forecast_timestamps,
        "baseline_by_horizon": baseline_by_horizon,
        "scenario_by_horizon": scenario_by_horizon,
        "delta_by_horizon": delta_by_horizon,
    }
    if baseline.shape[0] == 1:
        first_key = forecast_timestamps[0]
        result["baseline"] = baseline_by_horizon[first_key]
        result["scenario"] = scenario_by_horizon[first_key]
        result["delta"] = delta_by_horizon[first_key]

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


def build_predictions_by_horizon(
    node_ids: list[str],
    forecast_timestamps: list[str],
    predictions: np.ndarray,
) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for horizon_index, forecast_timestamp in enumerate(forecast_timestamps):
        output[forecast_timestamp] = {
            node_id: float(value)
            for node_id, value in zip(node_ids, predictions[horizon_index], strict=True)
        }
    return output


if __name__ == "__main__":
    main()
