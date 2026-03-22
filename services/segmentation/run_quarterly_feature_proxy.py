from __future__ import annotations

import sys
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SERVICE_ROOT.parents[1]
INFERENCE_SCRIPT = REPO_ROOT / "services" / "inference" / "prepare_nanjing_quarterly_remote_sensing.py"


if __name__ == "__main__":
    raise SystemExit(__import__("subprocess").run([sys.executable, str(INFERENCE_SCRIPT)], cwd=str(REPO_ROOT)).returncode)
