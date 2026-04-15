# Experiment Automation

This directory now includes two experiment automation entrypoints for the current quarterly Nanjing pipeline:

- `run_multi_seed_experiment.py`
- `run_adjacency_sweep.py`

## Multi-Seed

Run the same training config against one dataset across multiple random seeds and aggregate the results.

```powershell
cd D:\4c\services\inference
uv run --offline python run_multi_seed_experiment.py `
  --config configs/stgnn_gcn_lstm_quarterly_qc_edgar_hybrid_multistep.yaml `
  --dataset ..\..\data\processed\inference\nanjing_quarterly_qc_edgar_hybrid_v1.npz `
  --seeds 7 21 42 77 3407
```

Optional overrides:

```powershell
cd D:\4c\services\inference
uv run --offline python run_multi_seed_experiment.py `
  --config configs/stgnn_gcn_lstm_quarterly_qc_edgar_hybrid_multistep.yaml `
  --dataset ..\..\data\processed\inference\nanjing_quarterly_qc_edgar_hybrid_v1.npz `
  --seeds 7 21 42 `
  --epochs 80 `
  --output-root outputs\multi_seed\hybrid_multistep
```

Outputs:

- Per-seed training artifacts under the chosen output root
- `multi_seed_summary.json`

## Adjacency Sweep

Sweep adjacency parameters, rebuild the training dataset for each combination, retrain, and rank results.

Example: radius and `k` sweep for the current hybrid ST-GNN.

```powershell
cd D:\4c\services\inference
uv run --offline python run_adjacency_sweep.py `
  --dataset-config configs/nanjing_quarterly_dataset_qc_edgar_hybrid.yaml `
  --train-config configs/stgnn_gcn_lstm_quarterly_qc_edgar_hybrid_multistep.yaml `
  --set radius_km 12 15 18 `
  --set k 6 8 10 `
  --set wind_scale 0.45 0.55 0.65 `
  --set similarity_weight 0.35 0.45 0.55
```

Example: run every adjacency combination across multiple seeds.

```powershell
cd D:\4c\services\inference
uv run --offline python run_adjacency_sweep.py `
  --dataset-config configs/nanjing_quarterly_dataset_qc_edgar_hybrid.yaml `
  --train-config configs/stgnn_gcn_lstm_quarterly_qc_edgar_hybrid_multistep.yaml `
  --set radius_km 12 15 `
  --set k 6 8 `
  --set wind_scale 0.45 0.55 `
  --seeds 7 21 42
```

Useful flags:

- `--epochs 20`
- `--max-runs 3`
- `--dry-run`
- `--output-root outputs\adjacency_sweep\hybrid_multistep`
- `--summary-output outputs\adjacency_sweep\hybrid_multistep\summary.json`

Notes:

- `--set` values are parsed as YAML scalars or lists.
- For list-type adjacency fields such as `similarity_features`, quote the value:

```powershell
--set similarity_features "[vegetation_area_ratio, ndvi_mean, forest_ratio, built_ratio]"
```

Outputs:

- One folder per adjacency combination
- Rebuilt dataset NPZ and metadata per combination
- Training outputs per seed
- A ranked `sweep_summary.json`
