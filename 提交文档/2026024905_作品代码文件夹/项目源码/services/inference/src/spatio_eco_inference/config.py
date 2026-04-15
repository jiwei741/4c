from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_output_dir(service_root: Path, config: dict[str, Any]) -> Path:
    output_dir = Path(config["output"]["dir"])
    if not output_dir.is_absolute():
        output_dir = service_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
