from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StreamTopic:
    name: str
    value_schema: str
    producer: str
    consumer: str


@dataclass(frozen=True)
class SinkBinding:
    sink_name: str
    target_table: str
    write_mode: str
