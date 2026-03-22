# Segmentation Service

## Scope

`services/segmentation` is the Member B workspace for the remote-sensing branch:

- Sentinel-2 scene level job planning
- SAM-2 segmentation task handoff
- scene masks and land-cover feature outputs
- handoff back to the local training and platform layers

At the moment this service does **not** run the real SAM-2 model yet. It supports:

- building a segmentation manifest from the Sentinel-2 download plan
- exporting a remote GPU execution bundle
- preparing the GPU server workspace
- importing remote outputs back into the local repo

## Current Boundary

Keep these parts local:

- `services/data_ingestion`
- `services/backend`
- `services/frontend`
- `services/inference`
- platform integration and scenario demos

Move only this part to the GPU server:

- real SAM-2 inference over Sentinel-2 SAFE products
- batch segmentation over historical scenes

## Local Commands

### 1. Build the job manifest

```powershell
cd services/segmentation
python build_sam2_job_manifest.py --plan-json d:\4c\data\raw\sentinel2\nanjing\catalog\sentinel2_download_plan_nanjing_2025-01-01_to_2025-01-31.json
```

### 2. Export a remote GPU bundle

```powershell
cd services/segmentation
python export_remote_sam2_bundle.py --plan-json d:\4c\data\raw\sentinel2\nanjing\catalog\sentinel2_download_plan_nanjing_2025-01-01_to_2025-01-31.json
```

### 3. Keep the current quarterly feature proxy available locally

```powershell
cd services/segmentation
python run_quarterly_feature_proxy.py
```

## GPU Server Commands

### 1. Prepare the directory layout on the server

```bash
cd services/segmentation
python prepare_remote_sam2_workspace.py --manifest /workspace/spatio-eco/data/processed/segmentation/nanjing/remote_bundle/<bundle>/sam2_job_manifest.json --server-workdir /workspace/spatio-eco
```

This only prepares directories and validates that the expected Sentinel-2 SAFE folders are present. The real SAM-2 runner still needs to be connected on the server.

## Import Back to Local

After the server finishes, copy the results back and run:

```powershell
cd services/segmentation
python import_remote_segmentation_results.py --manifest d:\4c\data\processed\segmentation\nanjing\remote_bundle\<bundle>\sam2_job_manifest.json --results-root d:\4c\data\processed\segmentation\nanjing
```

By default the merged feature CSV is copied to:

- `data/processed/features/nanjing/quarterly/sentinel2_features_from_sam2.csv`

## `uv` Environment

This service can also be isolated with `uv`:

```powershell
cd services/segmentation
uv sync
```
