from __future__ import annotations

import json
import urllib.error
import urllib.request


BACKEND = "http://127.0.0.1:8000"
FRONTEND = "http://127.0.0.1:4173"


def fetch_json(url: str, data: bytes | None = None) -> dict:
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def main() -> int:
    health = fetch_json(f"{BACKEND}/api/v1/health")
    dashboard = fetch_json(f"{BACKEND}/api/v1/dashboard")
    data_sources = fetch_json(f"{BACKEND}/api/v1/data-sources")
    platform_status = fetch_json(f"{BACKEND}/api/v1/admin/platform-status")
    source_policy = fetch_json(f"{BACKEND}/api/v1/admin/source-policy")
    analytics = fetch_json(f"{BACKEND}/api/v1/map/analytics")
    prediction_layer = fetch_json(f"{BACKEND}/api/v1/map/predictions")
    scenario = fetch_json(
        f"{BACKEND}/api/v1/scenarios/run",
        data=json.dumps(
            {
                "model_key": "stgnn_multistep_hybrid",
                "scenario_key": "industrial_expansion_enhanced",
            }
        ).encode("utf-8"),
    )
    html = fetch_text(FRONTEND)
    models_html = fetch_text(f"{FRONTEND}/models.html")
    operations_html = fetch_text(f"{FRONTEND}/operations.html")
    research_html = fetch_text(f"{FRONTEND}/research.html")

    result = {
        "health": health,
        "dashboard_models": len(dashboard["models"]),
        "sentinel2_active_source": data_sources["sentinel2_switch"]["active_key"],
        "segmentation_job_manifest_exists": data_sources["segmentation_remote"]["job_manifest_exists"],
        "platform_leader": platform_status["model_summary"]["leader_key"],
        "source_policy_mode": source_policy["policy"]["mode"],
        "analytics_hotspots": len(analytics["summary"]["top_hotspots"]),
        "prediction_items": len(prediction_layer["items"]),
        "scenario_status": scenario["status"],
        "scenario_changed_nodes": scenario["summary"]["changed_nodes"],
        "frontend_contains_title": "Spatio-Eco Platform" in html,
        "frontend_pages_ready": {
            "overview": "Spatio-Eco Platform" in html,
            "models": "Spatio-Eco Platform" in models_html,
            "operations": "Spatio-Eco Platform" in operations_html,
            "research": "Spatio-Eco Platform" in research_html,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise
