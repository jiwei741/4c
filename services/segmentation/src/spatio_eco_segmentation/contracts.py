from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SegmentationJob:
    study_area: str
    asset_id: str
    model_variant: str
    input_path: str
    output_dir: str


@dataclass(frozen=True)
class FeatureExport:
    timestamp: str
    node_id: str
    vegetation_area_ratio: float
    ndvi_mean: float
    built_ratio: float
