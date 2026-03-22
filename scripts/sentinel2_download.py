import argparse
import os
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from dotenv import dotenv_values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Sentinel-2 SAFE product files via CDSE S3 access."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--s3-uri", help="Example: s3://EODATA/Sentinel-2/MSI/L2A/...SAFE")
    source.add_argument("--plan-json", help="Download from a generated Sentinel-2 plan JSON")
    parser.add_argument("--priority", type=int, default=1, help="Used with --plan-json")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--target-name", default=None)
    return parser.parse_args()


def load_env(project_root: Path) -> dict[str, str]:
    env = dotenv_values(project_root / ".env")
    return {key: (value or "").strip() for key, value in env.items()}


def apply_network_env(env: dict[str, str]) -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        value = env.get(key, "")
        if value:
            os.environ[key] = value


def resolve_download_source(args: argparse.Namespace) -> tuple[str, str]:
    if args.s3_uri:
        target_name = args.target_name or Path(args.s3_uri.rstrip("/")).name
        return args.s3_uri, target_name

    plan_path = Path(args.plan_json)
    import json

    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    for item in payload["downloads"]:
        if int(item["priority"]) == args.priority:
            return item["remote_uri"], args.target_name or item["scene_id"]
    raise ValueError(f"Priority {args.priority} not found in {plan_path}")


def build_s3_resource(env: dict[str, str]):
    access_key = env.get("CDSE_S3_ACCESS_KEY", "")
    secret_key = env.get("CDSE_S3_SECRET_KEY", "")
    endpoint_url = env.get("CDSE_S3_ENDPOINT_URL", "https://eodata.dataspace.copernicus.eu")
    region_name = env.get("CDSE_S3_REGION", "default")

    if not access_key or not secret_key:
        raise RuntimeError("Missing CDSE_S3_ACCESS_KEY or CDSE_S3_SECRET_KEY in .env")

    return boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
        config=Config(signature_version="s3v4"),
    )


def parse_s3_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    if parsed.scheme != "s3":
        raise ValueError(f"Unsupported S3 URI: {uri}")
    bucket = parsed.netloc.lower()
    prefix = parsed.path.lstrip("/")
    if prefix and not prefix.endswith("/"):
        prefix = f"{prefix}/"
    return bucket, prefix


def download_prefix(bucket, prefix: str, output_root: Path) -> int:
    count = 0
    for obj in bucket.objects.filter(Prefix=prefix):
        key = obj.key
        if key.endswith("/"):
            continue
        relative_path = key[len(prefix):] if key.startswith(prefix) else Path(key).name
        target_path = output_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        bucket.download_file(key, str(target_path))
        count += 1
    return count


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    env = load_env(project_root)
    apply_network_env(env)

    s3_uri, target_name = resolve_download_source(args)
    bucket_name, prefix = parse_s3_uri(s3_uri)
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else project_root / "data" / "raw" / "sentinel2" / "downloads" / target_name
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    s3 = build_s3_resource(env)
    bucket = s3.Bucket(bucket_name)
    downloaded = download_prefix(bucket, prefix, output_dir)
    if downloaded == 0:
        raise FileNotFoundError(f"No objects found for {s3_uri}")

    print(f"Downloaded {downloaded} objects to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
