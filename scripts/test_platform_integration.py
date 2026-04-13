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
    evidence_summary = fetch_json(f"{BACKEND}/api/v1/evidence/summary")
    data_sources = fetch_json(f"{BACKEND}/api/v1/data-sources")
    platform_status = fetch_json(f"{BACKEND}/api/v1/admin/platform-status")
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
    home_html = fetch_text(FRONTEND)
    workspace_html = fetch_text(f"{FRONTEND}/workspace")
    cases_html = fetch_text(f"{FRONTEND}/cases")
    evidence_html = fetch_text(f"{FRONTEND}/evidence")

    result = {
        "health": health,
        "dashboard_models": len(dashboard["models"]),
        "evidence_best_combo": evidence_summary["adjacency_sweep"]["best_combo_id"],
        "evidence_candidate_rmse_gain_percent": round(evidence_summary["candidate_upgrade"]["rmse_gain_percent"], 4),
        "sentinel2_active_source": data_sources["items"][0]["active_source"],
        "platform_leader": platform_status["model_summary"]["leader_key"],
        "analytics_hotspots": len(analytics["summary"]["top_hotspots"]),
        "prediction_items": len(prediction_layer["items"]),
        "scenario_status": scenario["status"],
        "scenario_changed_nodes": scenario["summary"]["changed_nodes"],
        "frontend_shell_ready": '<div id="app"></div>' in home_html,
        "frontend_routes_ready": {
            "home": '<div id="app"></div>' in home_html,
            "workspace": '<div id="app"></div>' in workspace_html,
            "cases": '<div id="app"></div>' in cases_html,
            "evidence": '<div id="app"></div>' in evidence_html,
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
