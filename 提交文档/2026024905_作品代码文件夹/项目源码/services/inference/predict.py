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
from spatio_eco_inference.training import (
    apply_prediction_constraints_tensor,
    build_model,
    select_device,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one-step prediction from a trained checkpoint.")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
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

    input_window = int(config["data"]["input_window"])
    latest_inputs = latest_window(bundle, input_window).to(device=device, dtype=torch.float32)
    normalization = checkpoint.get("normalization", {})
    if "features" in normalization:
        feature_mean = torch.tensor(normalization["features"]["mean"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
        feature_std = torch.tensor(normalization["features"]["std"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
        latest_inputs = normalize_features_tensor(latest_inputs, feature_mean, feature_std)

    with torch.no_grad():
        predictions = model(latest_inputs)
        if "target" in normalization:
            target_mean = torch.tensor(normalization["target"]["mean"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
            target_std = torch.tensor(normalization["target"]["std"], dtype=torch.float32, device=device).view(1, 1, 1, -1)
            predictions = predictions * target_std + target_mean
        predictions = inverse_target_transform_tensor(
            predictions,
            checkpoint.get("target_transform"),
        )
        predictions = apply_prediction_constraints_tensor(
            predictions,
            checkpoint.get("prediction_constraints"),
        )
        predictions = predictions.cpu().numpy()[0, :, :, 0]

    forecast_timestamps = infer_forecast_timestamps(bundle.timestamps, predictions.shape[0])
    predictions_by_horizon = build_predictions_by_horizon(bundle.node_ids, forecast_timestamps, predictions)

    result = {
        "target_name": bundle.target_name,
        "prediction_timestamp_from": bundle.timestamps[-input_window],
        "prediction_timestamp_to": bundle.timestamps[-1],
        "forecast_timestamps": forecast_timestamps,
        "predictions_by_horizon": predictions_by_horizon,
    }
    if predictions.shape[0] == 1:
        first_key = forecast_timestamps[0]
        result["predictions"] = predictions_by_horizon[first_key]

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
