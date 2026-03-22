from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
INFERENCE_ROOT = REPO_ROOT / "services" / "inference"
DOCS_ROOT = REPO_ROOT / "docs"
FEATURES_ROOT = REPO_ROOT / "data" / "processed" / "features" / "nanjing" / "quarterly"
INFERENCE_DATA_ROOT = REPO_ROOT / "data" / "processed" / "inference"
SEGMENTATION_ROOT = REPO_ROOT / "data" / "processed" / "segmentation" / "nanjing"
SEGMENTATION_REMOTE_BUNDLE_ROOT = SEGMENTATION_ROOT / "remote_bundle"
SEGMENTATION_REMOTE_IMPORT_SUMMARY_PATH = SEGMENTATION_ROOT / "remote_import_summary.json"
SEGMENTATION_JOB_MANIFEST_PATH = SEGMENTATION_ROOT / "sam2_job_manifest.json"

GRID_NODES_PATH = FEATURES_ROOT / "grid_nodes.csv"
SENTINEL2_PROXY_FEATURES_PATH = FEATURES_ROOT / "sentinel2_features.csv"
SENTINEL2_SAM2_FEATURES_PATH = FEATURES_ROOT / "sentinel2_features_from_sam2.csv"
ERA5_FEATURES_PATH = FEATURES_ROOT / "era5_features.csv"
EDGAR_FEATURES_PATH = FEATURES_ROOT / "edgar_features.csv"
LABELS_PATH = FEATURES_ROOT / "labels_qc_complete.csv"
BACKEND_RUNTIME_ROOT = REPO_ROOT / "services" / "backend" / "runtime"
SOURCE_POLICY_PATH = BACKEND_RUNTIME_ROOT / "source_policy.json"


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
        "layer": "Segmentation",
        "service": "services/segmentation",
        "owner": "Member B",
        "status": "remote_only",
        "current_scope": "Local manifest generation, remote bundle export, and result import pipeline are ready.",
        "next_fill": "Run real SAM-2 inference on a remote GPU server and export scene-level feature tables.",
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
        "current_scope": "Quarterly LSTM, ST-GNN, multi-step prediction, and scenario simulation are running.",
        "next_fill": "Switch to SAM-2 derived Sentinel-2 features once remote segmentation outputs are available.",
    },
    {
        "layer": "Backend",
        "service": "services/backend",
        "owner": "Member D",
        "status": "active",
        "current_scope": "Dashboard, map layers, scenario execution, and data source status APIs are working.",
        "next_fill": "Add more management endpoints and integrate remote segmentation result status.",
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
            "Enhanced scenario simulation",
        ],
        "remaining": [
            "Rebuild datasets after SAM-2 Sentinel-2 features arrive",
            "Prepare competition-grade experiments and interface notes",
        ],
    },
    {
        "member": "Member B",
        "role": "Remote sensing, SAM-2, land-cover features",
        "status": "pending_fill",
        "completed": [
            "Sentinel-2 catalog and quarterly proxy features are available",
            "Remote GPU execution boundary is defined",
        ],
        "remaining": [
            "Download raw Sentinel-2 products",
            "Run SAM-2 inference on remote GPU",
            "Export scene-level remote sensing feature tables",
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
            "Surface segmentation status and training-source switches",
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
    {"title": "Spatio-Eco Detailed Plan", "path": "Spatio-Eco_详细方案.md", "group": "core"},
    {"title": "Member AA Data Checklist", "path": "docs/02_成员AA模型训练数据补充清单.md", "group": "algorithm"},
    {"title": "Nanjing Quarterly Training Plan", "path": "docs/03_南京季度版训练接入方案.md", "group": "algorithm"},
    {"title": "Platform Boundaries", "path": "docs/12_平台框架与服务边界_2026-03-21.md", "group": "platform"},
    {"title": "Platform Integration Guide", "path": "docs/13_平台联调与启动说明_2026-03-21.md", "group": "platform"},
    {"title": "SAM-2 Remote Execution Guide", "path": "docs/14_SAM2远程执行与本地边界_2026-03-21.md", "group": "segmentation"},
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
