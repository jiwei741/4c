from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
INFERENCE_ROOT = REPO_ROOT / "services" / "inference"
DOCS_ROOT = REPO_ROOT / "docs"
FEATURES_ROOT = REPO_ROOT / "data" / "processed" / "features" / "nanjing" / "quarterly"
INFERENCE_DATA_ROOT = REPO_ROOT / "data" / "processed" / "inference"

GRID_NODES_PATH = FEATURES_ROOT / "grid_nodes.csv"
SENTINEL2_FEATURES_PATH = FEATURES_ROOT / "sentinel2_features.csv"
ERA5_FEATURES_PATH = FEATURES_ROOT / "era5_features.csv"
EDGAR_FEATURES_PATH = FEATURES_ROOT / "edgar_features.csv"
LABELS_PATH = FEATURES_ROOT / "labels_qc_complete.csv"
BACKEND_RUNTIME_ROOT = REPO_ROOT / "services" / "backend" / "runtime"


@dataclass(frozen=True)
class ModelArtifact:
    key: str
    name: str
    stage: str
    owner: str
    horizon: str
    metrics_path: Path
    prediction_path: Path
    output_dir: Path
    checkpoint_path: Path
    dataset_path: Path


MODEL_ARTIFACTS = (
    ModelArtifact(
        key="stgnn_single_step_hybrid",
        name="ST-GNN Single-Step",
        stage="default_single_step",
        owner="Member A",
        horizon="single_step",
        metrics_path=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm" / "metrics.json",
        prediction_path=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm" / "latest_prediction.json",
        output_dir=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm",
        checkpoint_path=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm" / "best.pt",
        dataset_path=INFERENCE_DATA_ROOT / "nanjing_quarterly_qc_edgar_hybrid_v1.npz",
    ),
    ModelArtifact(
        key="stgnn_multistep_hybrid",
        name="ST-GNN Multi-Step",
        stage="default_multi_step",
        owner="Member A",
        horizon="multi_step",
        metrics_path=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep" / "metrics.json",
        prediction_path=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep" / "latest_prediction.json",
        output_dir=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep",
        checkpoint_path=INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep" / "best.pt",
        dataset_path=INFERENCE_DATA_ROOT / "nanjing_quarterly_qc_edgar_hybrid_v1.npz",
    ),
    ModelArtifact(
        key="lstm_multistep_baseline",
        name="LSTM Multi-Step Baseline",
        stage="baseline",
        owner="Member A",
        horizon="multi_step",
        metrics_path=INFERENCE_ROOT / "outputs" / "lstm_baseline_nanjing_quarterly_qc_edgar_multistep" / "metrics.json",
        prediction_path=INFERENCE_ROOT / "outputs" / "lstm_baseline_nanjing_quarterly_qc_edgar_multistep" / "latest_prediction.json",
        output_dir=INFERENCE_ROOT / "outputs" / "lstm_baseline_nanjing_quarterly_qc_edgar_multistep",
        checkpoint_path=INFERENCE_ROOT / "outputs" / "lstm_baseline_nanjing_quarterly_qc_edgar_multistep" / "best.pt",
        dataset_path=INFERENCE_DATA_ROOT / "nanjing_quarterly_qc_edgar_v1.npz",
    ),
)

DEFAULT_SINGLE_STEP_MODEL = "stgnn_single_step_hybrid"
DEFAULT_MULTI_STEP_MODEL = "stgnn_multistep_hybrid"

STUDY_AREA = {
    "name": "Nanjing",
    "node_count": 309,
    "time_granularity": "quarterly",
    "time_range": ["2020-Q1", "2024-Q4"],
    "current_target": "net_carbon_flux",
    "status": "Quarterly training MVP ready",
}

ARCHITECTURE_LAYERS = (
    {
        "layer": "Data Ingestion",
        "service": "services/data_ingestion",
        "owner": "Member B / Member C",
        "status": "scaffolded",
        "current_scope": "Download and preprocessing entry points are in place for Sentinel-2, ERA5, EDGAR, NOAA, and GPP.",
        "next_fill": "Continue with Sentinel-2 raw download orchestration and database import scripts.",
    },
    {
        "layer": "Remote Sensing Features",
        "service": "services/inference",
        "owner": "Member A / Member B",
        "status": "active",
        "current_scope": "High-precision quarterly Sentinel-2 land-cover features have been normalized into the local training set.",
        "next_fill": "Continue quarterly feature QA and expand scenario-aware feature engineering when needed.",
    },
    {
        "layer": "Streaming",
        "service": "services/streaming",
        "owner": "Member C",
        "status": "scaffolded",
        "current_scope": "Kafka and Flink boundaries are prepared with placeholder workflows.",
        "next_fill": "Connect download, segmentation, and feature updates into real topics and sinks.",
    },
    {
        "layer": "Inference",
        "service": "services/inference",
        "owner": "Member A",
        "status": "active",
        "current_scope": "Quarterly LSTM, ST-GNN, multi-step prediction, and scenario simulation are running on the refined Sentinel-2 feature set.",
        "next_fill": "Keep iterating on competition-grade experiments and feature selection.",
    },
    {
        "layer": "Backend",
        "service": "services/backend",
        "owner": "Member D",
        "status": "active",
        "current_scope": "Dashboard, map layers, scenario execution, and data source status APIs are working.",
        "next_fill": "Keep polishing training artifact visibility and operational status summaries.",
    },
    {
        "layer": "Frontend",
        "service": "services/frontend",
        "owner": "Member E",
        "status": "active",
        "current_scope": "Cesium page skeleton, model panels, and scenario forms are wired to backend APIs.",
        "next_fill": "Improve business dashboards, grid layers, and demo-grade presentation views.",
    },
)

MEMBER_STATUS = (
    {
        "member": "Member A",
        "role": "Algorithms and model training",
        "status": "active",
        "completed": [
            "Quarterly training dataset pipeline",
            "LSTM baseline",
            "ST-GNN with EDGAR and stronger graph structure",
            "Multi-step prediction",
            "Refined Sentinel-2 quarterly retraining pipeline",
            "Enhanced scenario simulation",
        ],
        "remaining": [
            "Prepare competition-grade experiments and interface notes",
        ],
    },
    {
        "member": "Member B",
        "role": "Remote sensing and land-cover features",
        "status": "active",
        "completed": [
            "Sentinel-2 catalog and quarterly proxy features are available",
            "High-precision quarterly feature package is available locally",
        ],
        "remaining": [
            "Download raw Sentinel-2 products",
            "Continue land-cover QA and source documentation",
            "Support future feature engineering for scenario simulation",
        ],
    },
    {
        "member": "Member C",
        "role": "Streaming and spatial database",
        "status": "pending_fill",
        "completed": [
            "PostGIS and streaming boundaries are scaffolded",
        ],
        "remaining": [
            "Kafka and Flink integration",
            "Result ingestion and subscription updates",
            "Database runtime scripts",
        ],
    },
    {
        "member": "Member D",
        "role": "Backend APIs",
        "status": "active",
        "completed": [
            "Platform API skeleton",
            "Model result aggregation",
            "Live scenario invocation",
        ],
        "remaining": [
            "Add management APIs",
            "Surface retraining metadata and dataset provenance",
        ],
    },
    {
        "member": "Member E",
        "role": "Frontend and platform presentation",
        "status": "active",
        "completed": [
            "Platform page skeleton",
            "Cesium integration",
            "Scenario form integration",
        ],
        "remaining": [
            "Improve map layers and status panels",
            "Polish competition demo views",
        ],
    },
)

DOC_REFERENCES = (
    {"title": "Spatio-Eco Detailed Plan", "path": "Spatio-Eco_璇︾粏鏂规.md", "group": "core"},
    {"title": "Member AA Data Checklist", "path": "docs/02_鎴愬憳AA妯″瀷璁粌鏁版嵁琛ュ厖娓呭崟.md", "group": "algorithm"},
    {"title": "Nanjing Quarterly Training Plan", "path": "docs/03_鍗椾含瀛ｅ害鐗堣缁冩帴鍏ユ柟妗?md", "group": "algorithm"},
    {"title": "Platform Boundaries", "path": "docs/12_骞冲彴妗嗘灦涓庢湇鍔¤竟鐣宊2026-03-21.md", "group": "platform"},
    {"title": "Platform Integration Guide", "path": "docs/13_骞冲彴鑱旇皟涓庡惎鍔ㄨ鏄巁2026-03-21.md", "group": "platform"},
)

EXAMPLE_SCENARIOS = {
    "industrial_expansion_enhanced": {
        "name": "Industrial Expansion Enhanced",
        "input_path": INFERENCE_ROOT / "examples" / "nanjing_industrial_expansion_enhanced.json",
        "output_path": INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm" / "enhanced_scenario.json",
    },
    "industrial_expansion_simple": {
        "name": "Industrial Expansion Basic",
        "input_path": INFERENCE_ROOT / "examples" / "nanjing_qc_edgar_scenario.json",
        "output_path": INFERENCE_ROOT / "outputs" / "stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm" / "simple_scenario.json",
    },
}
