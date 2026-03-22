from pathlib import Path
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import sys

from dotenv import dotenv_values


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    env = dotenv_values(project_root / ".env")
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        value = (env.get(key) or "").strip()
        if value:
            os.environ[key] = value

    username = env.get("COPERNICUS_USERNAME", "").strip()
    password = env.get("COPERNICUS_PASSWORD", "").strip()
    token_url = env.get("COPERNICUS_TOKEN_URL", "").strip()

    if not username or not password or not token_url:
        print("Missing Copernicus credentials in .env")
        return 1

    payload = urlencode(
        {
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": username,
            "password": password,
        }
    ).encode("utf-8")

    req = Request(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"Copernicus token request failed: {exc}")
        return 1

    access_token = body.get("access_token")
    expires_in = body.get("expires_in")
    if not access_token:
        print("No access_token in response")
        return 1

    print(f"Copernicus token OK, expires_in={expires_in}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
