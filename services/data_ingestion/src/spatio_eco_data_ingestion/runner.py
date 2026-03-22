from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values


NETWORK_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "REQUESTS_CA_BUNDLE",
    "SSL_CERT_FILE",
)

def run_python_script(script_path: Path, args: list[str], *, cwd: Path) -> int:
    command = [sys.executable, str(script_path), *args]
    child_env = os.environ.copy()
    env_path = cwd / ".env"
    if env_path.exists():
        dotenv = dotenv_values(env_path)
        for key in NETWORK_ENV_KEYS:
            value = (dotenv.get(key) or "").strip()
            if value:
                child_env[key] = value
    completed = subprocess.run(command, cwd=str(cwd), env=child_env, check=False)
    return int(completed.returncode)
