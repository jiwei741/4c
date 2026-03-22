from pathlib import Path

import requests
from dotenv import dotenv_values


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    env = dotenv_values(project_root / ".env")

    token_resp = requests.post(
        env.get("COPERNICUS_TOKEN_URL", ""),
        data={
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": env.get("COPERNICUS_USERNAME", ""),
            "password": env.get("COPERNICUS_PASSWORD", ""),
        },
        timeout=30,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json()["access_token"]

    response = requests.post(
        "https://s3-keys-manager.cloudferro.com/api/user/credentials",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()

    print("access_id=" + body["access_id"])
    print("secret=" + body["secret"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
