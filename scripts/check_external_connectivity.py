from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values


TARGETS = [
    "https://identity.dataspace.copernicus.eu",
    "https://sh.dataspace.copernicus.eu",
    "https://eodata.dataspace.copernicus.eu",
    "https://cds.climate.copernicus.eu",
    "https://appeears.earthdatacloud.nasa.gov",
]


def load_env(project_root: Path) -> dict[str, str]:
    env = dotenv_values(project_root / ".env")
    return {key: (value or "").strip() for key, value in env.items()}


def apply_network_env(env: dict[str, str]) -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        value = env.get(key, "")
        if value:
            os.environ[key] = value


def check_socket(hostname: str, port: int = 443) -> dict[str, Any]:
    try:
        with socket.create_connection((hostname, port), timeout=8):
            return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_https(url: str) -> dict[str, Any]:
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        return {
            "ok": True,
            "status_code": response.status_code,
            "final_url": response.url,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    env = load_env(project_root)
    apply_network_env(env)

    proxy_summary = {
        key: bool(env.get(key, ""))
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE")
    }

    report: dict[str, Any] = {
        "proxy_configured": proxy_summary,
        "targets": [],
    }

    for url in TARGETS:
        hostname = url.split("//", 1)[1]
        report["targets"].append(
            {
                "url": url,
                "socket_check": check_socket(hostname),
                "https_check": check_https(url),
            }
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
