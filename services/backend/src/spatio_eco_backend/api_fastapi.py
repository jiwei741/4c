from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover
    FastAPI = None
    HTTPException = None
    CORSMiddleware = None
    FASTAPI_AVAILABLE = False

from . import service


def _not_found(exc: KeyError) -> Any:
    if HTTPException is None:
        raise exc
    raise HTTPException(status_code=404, detail=str(exc)) from exc


def _bad_request(exc: ValueError) -> Any:
    if HTTPException is None:
        raise exc
    raise HTTPException(status_code=400, detail=str(exc)) from exc


def create_app() -> Any:
    if not FASTAPI_AVAILABLE:
        return None

    app = FastAPI(
        title="Spatio-Eco Backend",
        version="0.1.0",
        description="Platform API scaffold backed by current inference outputs.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health")
    def health() -> dict[str, Any]:
        return service.get_health()

    @app.get("/api/v1/dashboard")
    def dashboard() -> dict[str, Any]:
        return service.get_dashboard()

    @app.get("/api/v1/data-sources")
    def data_sources() -> dict[str, Any]:
        return service.get_data_sources()

    @app.get("/api/v1/admin/platform-status")
    def platform_status() -> dict[str, Any]:
        return service.get_platform_status()

    @app.get("/api/v1/admin/source-policy")
    def source_policy() -> dict[str, Any]:
        return service.get_source_policy()

    @app.post("/api/v1/admin/source-policy")
    def update_source_policy(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return service.set_source_policy(payload)
        except ValueError as exc:
            _bad_request(exc)

    @app.get("/api/v1/admin/segmentation-overview")
    def segmentation_overview() -> dict[str, Any]:
        return service.get_segmentation_overview()

    @app.get("/api/v1/architecture")
    def architecture() -> dict[str, Any]:
        return {"items": service.get_dashboard()["architecture"]}

    @app.get("/api/v1/study-area/grid-nodes")
    def grid_nodes() -> dict[str, Any]:
        return service.get_grid_nodes()

    @app.get("/api/v1/members")
    def members() -> dict[str, Any]:
        return {"items": service.get_dashboard()["members"]}

    @app.get("/api/v1/models")
    def models() -> dict[str, Any]:
        return {"items": service.list_models()}

    @app.get("/api/v1/models/{model_key}")
    def model_detail(model_key: str) -> dict[str, Any]:
        try:
            return service.get_model(model_key)
        except KeyError as exc:
            _not_found(exc)

    @app.get("/api/v1/predictions/latest")
    def latest_prediction(model_key: str | None = None) -> dict[str, Any]:
        try:
            return service.get_prediction_payload(model_key)
        except KeyError as exc:
            _not_found(exc)

    @app.get("/api/v1/map/predictions")
    def prediction_layer(model_key: str | None = None, horizon: str | None = None) -> dict[str, Any]:
        try:
            return service.get_prediction_layer(model_key, horizon)
        except KeyError as exc:
            _not_found(exc)

    @app.get("/api/v1/map/analytics")
    def prediction_analytics(
        model_key: str | None = None,
        horizon: str | None = None,
        compare_model_key: str | None = None,
    ) -> dict[str, Any]:
        try:
            return service.get_prediction_analytics(model_key, horizon, compare_model_key)
        except KeyError as exc:
            _not_found(exc)

    @app.get("/api/v1/scenarios/examples")
    def scenarios() -> dict[str, Any]:
        return {"items": service.list_scenarios()}

    @app.get("/api/v1/scenarios/examples/{scenario_key}")
    def scenario_detail(scenario_key: str) -> dict[str, Any]:
        try:
            return service.get_scenario_example(scenario_key)
        except KeyError as exc:
            _not_found(exc)

    @app.post("/api/v1/scenarios/run")
    def run_scenario(payload: dict[str, Any]) -> dict[str, Any]:
        return service.run_scenario(payload)

    return app
