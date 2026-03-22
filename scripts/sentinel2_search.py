import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values


CATALOG_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search Sentinel-2 L2A products via Copernicus Sentinel Hub Catalog API."
    )
    parser.add_argument("--area-name", required=True)
    parser.add_argument("--north", type=float, required=True)
    parser.add_argument("--west", type=float, required=True)
    parser.add_argument("--south", type=float, required=True)
    parser.add_argument("--east", type=float, required=True)
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--cloud-cover-max", type=float, default=20.0)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def load_env(project_root: Path) -> dict[str, str]:
    env = dotenv_values(project_root / ".env")
    return {key: (value or "").strip() for key, value in env.items()}


def apply_network_env(env: dict[str, str]) -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        value = env.get(key, "")
        if value:
            os.environ[key] = value


def fetch_access_token(env: dict[str, str]) -> str:
    payload = {
        "client_id": "cdse-public",
        "grant_type": "password",
        "username": env.get("COPERNICUS_USERNAME", ""),
        "password": env.get("COPERNICUS_PASSWORD", ""),
    }
    token_url = env.get("COPERNICUS_TOKEN_URL", "")
    if not token_url or not payload["username"] or not payload["password"]:
        raise RuntimeError("Missing Copernicus credentials in .env")

    response = requests.post(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    access_token = body.get("access_token")
    if not access_token:
        raise RuntimeError("No access_token returned by Copernicus token endpoint")
    return access_token


def build_body(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "collections": ["sentinel-2-l2a"],
        "datetime": f"{args.start_date}T00:00:00Z/{args.end_date}T23:59:59Z",
        "bbox": [args.west, args.south, args.east, args.north],
        "limit": max(args.top * 3, args.top),
    }


def normalize_feature(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties", {})
    assets = feature.get("assets", {})
    data_asset = assets.get("data", {})
    return {
        "id": feature.get("id"),
        "collection": feature.get("collection"),
        "datetime": props.get("datetime"),
        "platform": props.get("platform"),
        "constellation": props.get("constellation"),
        "cloud_cover": props.get("eo:cloud_cover"),
        "epsg": props.get("proj:epsg"),
        "bbox": feature.get("bbox"),
        "geometry": feature.get("geometry"),
        "s3_href": data_asset.get("href"),
        "self_href": next(
            (link.get("href") for link in feature.get("links", []) if link.get("rel") == "self"),
            None,
        ),
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "id",
        "collection",
        "datetime",
        "platform",
        "constellation",
        "cloud_cover",
        "epsg",
        "s3_href",
        "self_href",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def search_products(env: dict[str, str], args: argparse.Namespace) -> list[dict[str, Any]]:
    token = fetch_access_token(env)
    response = requests.post(
        CATALOG_API_URL,
        headers={"Authorization": f"Bearer {token}"},
        json=build_body(args),
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    features = payload.get("features", [])

    normalized = [normalize_feature(feature) for feature in features]
    filtered = [
        row
        for row in normalized
        if row.get("cloud_cover") is not None and row["cloud_cover"] <= args.cloud_cover_max
    ]
    filtered.sort(
        key=lambda row: (
            row.get("cloud_cover") if row.get("cloud_cover") is not None else 9999,
            row.get("datetime") or "",
        )
    )
    return filtered[: args.top]


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    env = load_env(project_root)
    apply_network_env(env)

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else project_root / "data" / "raw" / "sentinel2" / args.area_name / "catalog"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    stamp = f"{args.start_date}_to_{args.end_date}"
    json_path = output_dir / f"sentinel2_{args.area_name}_{stamp}.json"
    csv_path = output_dir / f"sentinel2_{args.area_name}_{stamp}.csv"

    products = search_products(env, args)
    payload = {
        "area_name": args.area_name,
        "bbox": {
            "north": args.north,
            "west": args.west,
            "south": args.south,
            "east": args.east,
        },
        "start_date": args.start_date,
        "end_date": args.end_date,
        "cloud_cover_max": args.cloud_cover_max,
        "count": len(products),
        "products": products,
    }

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(products, csv_path)

    print(f"Saved {len(products)} products")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
