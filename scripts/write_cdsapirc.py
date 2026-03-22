from pathlib import Path
import sys

from dotenv import dotenv_values


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    env_path = project_root / ".env"
    if not env_path.exists():
        print(f".env not found: {env_path}")
        return 1

    env = dotenv_values(env_path)
    cds_url = env.get("CDSAPI_URL", "").strip()
    cds_key = env.get("CDSAPI_KEY", "").strip()

    if not cds_url or not cds_key:
        print("CDSAPI_URL or CDSAPI_KEY is missing in .env")
        return 1

    target = Path.home() / ".cdsapirc"
    target.write_text(
        f"url: {cds_url}\nkey: {cds_key}\n",
        encoding="utf-8",
    )
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
