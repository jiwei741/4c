# Backend Service

`services/backend` is the current platform aggregation service for Member D.

## Current Scope

- Expose the trained model outputs produced by `services/inference`
- Provide dashboard, map layer, scenario, and data-source status APIs
- Bridge the frontend to local inference artifacts before the full database stack is ready

## Available APIs

- `GET /api/v1/health`
- `GET /api/v1/dashboard`
- `GET /api/v1/data-sources`
- `GET /api/v1/admin/platform-status`
- `GET /api/v1/admin/source-policy`
- `POST /api/v1/admin/source-policy`
- `GET /api/v1/admin/segmentation-overview`
- `GET /api/v1/architecture`
- `GET /api/v1/study-area/grid-nodes`
- `GET /api/v1/members`
- `GET /api/v1/models`
- `GET /api/v1/models/{model_key}`
- `GET /api/v1/predictions/latest?model_key=...`
- `GET /api/v1/map/predictions?model_key=...&horizon=...`
- `GET /api/v1/map/analytics?model_key=...&horizon=...&compare_model_key=...`
- `GET /api/v1/scenarios/examples`
- `GET /api/v1/scenarios/examples/{scenario_key}`
- `POST /api/v1/scenarios/run`

## Current Data Sources

This MVP reads files directly instead of querying PostGIS:

- `services/inference/outputs/*/metrics.json`
- `services/inference/outputs/*/latest_prediction.json`
- `services/inference/outputs/*/enhanced_scenario.json`
- `services/inference/examples/*.json`
- `data/processed/features/nanjing/quarterly/*.csv`
- `data/processed/segmentation/nanjing/remote_import_summary.json`
- `services/backend/runtime/source_policy.json`

## Run

Fallback mode with the Python standard library:

```powershell
cd services/backend
python app.py
```

Isolated mode with `uv`:

```powershell
cd services/backend
uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

If backend and inference use different Python environments, set this in the repo root `.env`:

```text
INFERENCE_PYTHON_EXECUTABLE=
```

Then `POST /api/v1/scenarios/run` will use that interpreter to execute [run_scenario.py](../inference/run_scenario.py).

## Next Fill

- Expand management APIs only after database-backed state is introduced
- Surface remote SAM-2 import progress at scene level when files arrive
- Replace file-backed reads with database-backed queries
- Wire in real streaming and segmentation outputs as they become available
