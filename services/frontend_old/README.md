# Frontend Service

`services/frontend` is the current platform presentation layer for Member E.

## Current Scope

- Show project status, model metrics, prediction summaries, and scenario results
- Render the Nanjing study area in a Cesium-first layout
- Provide business map modes for forecast, hotspot, model-gap, and scenario-delta views
- Provide a Sentinel-2 source policy panel that is ready for future SAM-2 feature return
- Call the backend directly for live dashboard and scenario data
- Fallback to local mock data if the backend is not running

## Current Behavior

- Loads `GET /api/v1/dashboard` first
- Loads `GET /api/v1/predictions/latest` and `GET /api/v1/map/predictions`
- Loads `GET /api/v1/map/analytics`
- Loads `GET /api/v1/admin/platform-status`
- Loads `GET /api/v1/admin/source-policy`
- Loads `GET /api/v1/admin/segmentation-overview`
- Calls `POST /api/v1/scenarios/run` for real scenario execution
- Calls `POST /api/v1/admin/source-policy` to reserve or switch Sentinel-2 feature sources
- Uses the Cesium CDN when it is reachable
- Falls back to a static panel view if Cesium is unavailable

## Run

```powershell
cd services/frontend
python -m http.server 4173
```

Open:

- `http://127.0.0.1:4173`

## Current UI Blocks

- Hero and metric strip
- Cesium map workspace
- Business map modes: forecast, hotspot, model gap, scenario delta
- Sentinel-2 source policy switch panel
- Remote segmentation status panel
- Hotspot watchlist
- Scenario simulation form
- Platform management overview
- Model registry
- Prediction summary
- Architecture, members, docs, and roadmap sections

## Next Fill

- Upgrade point/rectangle layers into richer business overlays
- Add more answer-defense views and storytelling panels
- Connect real SAM-2 grid features after remote GPU outputs are imported
