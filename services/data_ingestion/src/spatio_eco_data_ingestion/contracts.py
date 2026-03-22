from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Cadence = Literal["daily", "5-day", "8-day", "monthly", "quarterly", "yearly"]


@dataclass(frozen=True)
class SourceSpec:
    name: str
    source_type: str
    cadence: Cadence
    raw_dir: str
    output_format: str


@dataclass(frozen=True)
class IngestionPlan:
    study_area: str
    start_date: str
    end_date: str
    sources: tuple[SourceSpec, ...]
