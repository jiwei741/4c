from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import BACKEND_RUNTIME_ROOT, INFERENCE_ROOT, ModelArtifact


def _resolve_python_candidates() -> list[str]:
    candidates: list[str] = []
    explicit = os.getenv("INFERENCE_PYTHON_EXECUTABLE", "").strip()
    if explicit:
        candidates.append(explicit)

    inference_venv = INFERENCE_ROOT / ".venv" / "Scripts" / "python.exe"
    if inference_venv.exists():
        candidates.append(str(inference_venv))

    candidates.append(sys.executable)
    candidates.append("python")

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            deduped.append(candidate)
    return deduped


def run_live_scenario(artifact: ModelArtifact, scenario_payload: dict[str, Any]) -> dict[str, Any]:
    runtime_dir = BACKEND_RUNTIME_ROOT / "scenarios"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + uuid4().hex[:8]
    request_path = runtime_dir / f"scenario_request_{run_id}.json"
    output_path = runtime_dir / f"scenario_result_{run_id}.json"
    request_path.write_text(json.dumps(scenario_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    command_tail = [
        str(INFERENCE_ROOT / "run_scenario.py"),
        "--checkpoint",
        str(artifact.checkpoint_path),
        "--dataset",
        str(artifact.dataset_path),
        "--scenario",
        str(request_path),
        "--output",
        str(output_path),
    ]

    failures: list[dict[str, str]] = []
    for python_executable in _resolve_python_candidates():
        try:
            completed = subprocess.run(
                [python_executable, *command_tail],
                cwd=str(INFERENCE_ROOT),
                capture_output=True,
                text=True,
                timeout=600,
                check=True,
            )
        except Exception as exc:  # pragma: no cover
            failures.append({"python": python_executable, "error": str(exc)})
            continue

        result_payload = json.loads(output_path.read_text(encoding="utf-8"))
        return {
            "run_id": run_id,
            "python_executable": python_executable,
            "request_path": str(request_path),
            "output_path": str(output_path),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "result": result_payload,
        }

    raise RuntimeError(
        "failed to execute services/inference/run_scenario.py with available Python interpreters: "
        + json.dumps(failures, ensure_ascii=False)
    )
