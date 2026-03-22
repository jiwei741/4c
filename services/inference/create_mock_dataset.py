from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def build_grid_adjacency(rows: int, cols: int) -> np.ndarray:
    num_nodes = rows * cols
    adjacency = np.zeros((num_nodes, num_nodes), dtype=np.float32)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for row in range(rows):
        for col in range(cols):
            node = row * cols + col
            for d_row, d_col in directions:
                n_row = row + d_row
                n_col = col + d_col
                if 0 <= n_row < rows and 0 <= n_col < cols:
                    neighbor = n_row * cols + n_col
                    adjacency[node, neighbor] = 1.0
    return adjacency


def generate_mock_dataset(
    output_path: Path,
    timesteps: int,
    rows: int,
    cols: int,
    seed: int,
) -> None:
    rng = np.random.default_rng(seed)
    num_nodes = rows * cols
    num_features = 7
    adjacency = build_grid_adjacency(rows, cols)

    time_index = np.arange(timesteps, dtype=np.float32)
    seasonal = np.sin(2.0 * np.pi * time_index / 12.0)

    vegetation_base = rng.uniform(0.35, 0.85, size=num_nodes)
    ndvi_base = rng.uniform(0.4, 0.8, size=num_nodes)
    temperature_base = rng.uniform(18.0, 33.0, size=num_nodes)
    emission_base = rng.uniform(3.0, 18.0, size=num_nodes)
    wind_u_base = rng.uniform(-2.0, 2.0, size=num_nodes)
    wind_v_base = rng.uniform(-2.0, 2.0, size=num_nodes)
    precipitation_base = rng.uniform(10.0, 60.0, size=num_nodes)

    x = np.zeros((timesteps, num_nodes, num_features), dtype=np.float32)
    y = np.zeros((timesteps, num_nodes, 1), dtype=np.float32)

    normalized_adjacency = adjacency / np.maximum(adjacency.sum(axis=1, keepdims=True), 1.0)

    for t in range(timesteps):
        x[t, :, 0] = vegetation_base + 0.10 * seasonal[t] + rng.normal(0, 0.02, size=num_nodes)
        x[t, :, 1] = ndvi_base + 0.08 * seasonal[t] + rng.normal(0, 0.02, size=num_nodes)
        x[t, :, 2] = temperature_base - 4.0 * seasonal[t] + rng.normal(0, 0.6, size=num_nodes)
        x[t, :, 3] = emission_base + 1.5 * (1.0 - seasonal[t]) + rng.normal(0, 0.4, size=num_nodes)
        x[t, :, 4] = wind_u_base + rng.normal(0, 0.2, size=num_nodes)
        x[t, :, 5] = wind_v_base + rng.normal(0, 0.2, size=num_nodes)
        x[t, :, 6] = precipitation_base + 5.0 * seasonal[t] + rng.normal(0, 1.0, size=num_nodes)

        neighbor_emission = normalized_adjacency @ x[t, :, 3]
        neighbor_vegetation = normalized_adjacency @ x[t, :, 0]
        y[t, :, 0] = (
            12.0 * x[t, :, 0]
            + 20.0 * x[t, :, 1]
            - 0.7 * x[t, :, 2]
            - 2.8 * x[t, :, 3]
            - 0.12 * neighbor_emission
            + 3.0 * neighbor_vegetation
            + 0.03 * x[t, :, 6]
            + rng.normal(0, 0.6, size=num_nodes)
        )

    node_ids = np.array([f"grid_{index:02d}" for index in range(num_nodes)])
    feature_names = np.array(
        [
            "vegetation_area_ratio",
            "ndvi_mean",
            "land_surface_temperature",
            "edgar_emission",
            "u10_wind",
            "v10_wind",
            "precipitation",
        ]
    )
    timestamps = np.array(_build_month_strings(2023, 1, timesteps))
    target_name = np.array(["net_carbon_flux"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        x=x,
        y=y,
        adjacency=adjacency,
        node_ids=node_ids,
        feature_names=feature_names,
        timestamps=timestamps,
        target_name=target_name,
    )


def _build_month_strings(start_year: int, start_month: int, count: int) -> list[str]:
    values: list[str] = []
    month_index = start_month - 1
    for offset in range(count):
        current = month_index + offset
        year = start_year + current // 12
        month = current % 12 + 1
        values.append(f"{year}-{month:02d}")
    return values


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a mock graph time-series dataset.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data/processed/inference/mock/nanjing_mock_v1.npz",
    )
    parser.add_argument("--timesteps", type=int, default=36)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_mock_dataset(
        output_path=args.output,
        timesteps=args.timesteps,
        rows=args.rows,
        cols=args.cols,
        seed=args.seed,
    )
    print(f"mock dataset saved to {args.output}")


if __name__ == "__main__":
    main()
