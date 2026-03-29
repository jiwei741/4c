from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass
class GridRecord:
    node_id: str
    latitude: float
    longitude: float
    extra: dict[str, str]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def normalize_node_id(raw_value: str) -> str:
    value = str(raw_value).strip()
    if value.endswith(".0"):
        value = value[:-2]
    return value


def normalize_quarter_label(raw_value: str) -> str:
    value = str(raw_value).strip()
    if "_Q" in value:
        year_str, quarter_str = value.split("_Q", 1)
        return f"{int(year_str):04d}-Q{int(quarter_str)}"
    if "-Q" in value:
        year_str, quarter_str = value.split("-Q", 1)
        return f"{int(year_str):04d}-Q{int(quarter_str)}"
    return value


def load_grid_records(path: Path) -> list[GridRecord]:
    rows = read_csv_rows(path)
    records: list[GridRecord] = []
    for row in rows:
        node_id = normalize_node_id(row["node_id"])
        extra = {key: value for key, value in row.items() if key not in {"node_id", "latitude", "longitude"}}
        records.append(
            GridRecord(
                node_id=node_id,
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                extra=extra,
            )
        )
    records.sort(key=lambda item: int(item.node_id))
    return records


def parse_date_like(text: str) -> tuple[int, int]:
    value = normalize_quarter_label(text)
    if "-Q" in value:
        year_str, quarter_str = value.split("-Q", 1)
        month = (int(quarter_str) - 1) * 3 + 1
        return int(year_str), month

    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y/%m", "%Y-%m", "%Y%m"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.year, parsed.month
        except ValueError:
            continue

    if re.fullmatch(r"\d{4}", value):
        return int(value), 1

    raise ValueError(f"unsupported date format: {text}")


def to_quarter_label(year: int, month: int) -> str:
    quarter = (month - 1) // 3 + 1
    return f"{year}-Q{quarter}"


def quarter_sort_key(label: str) -> tuple[int, int]:
    normalized = normalize_quarter_label(label)
    year_str, quarter_str = normalized.split("-Q", 1)
    return int(year_str), int(quarter_str)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2.0) ** 2
    )
    return 2.0 * radius * math.asin(math.sqrt(a))


def sort_node_ids(node_ids: Iterable[str]) -> list[str]:
    return sorted({normalize_node_id(item) for item in node_ids}, key=lambda value: int(value))
