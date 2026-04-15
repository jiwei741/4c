from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException

SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]
SRC_ROOT = SERVICE_ROOT / "src"
if str(SRC_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_inference.env_utils import load_env_from_file


API_ROOT = "https://appeears.earthdatacloud.nasa.gov/api"
NANJING_BBOX = {
    "west": 118.30,
    "south": 31.20,
    "east": 119.30,
    "north": 32.70,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Nanjing MOD17A2HGF.061 GPP GeoTIFFs via AppEEARS area task.")
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data/raw/gpp/nanjing/appeears_mod17a2hgf_061",
    )
    parser.add_argument("--poll-interval-seconds", type=int, default=30)
    parser.add_argument("--timeout-minutes", type=int, default=240)
    parser.add_argument("--task-name", default=None)
    parser.add_argument("--task-id", default=None, help="Reuse an existing AppEEARS task ID instead of submitting a new one.")
    parser.add_argument("--download-retries", type=int, default=6)
    parser.add_argument(
        "--layer-keywords",
        default="Gpp_500m",
        help="Comma-separated file name keywords to download from the AppEEARS bundle.",
    )
    parser.add_argument(
        "--include-support-files",
        action="store_true",
        help="Also download lookup/statistics/request metadata files from the bundle.",
    )
    return parser.parse_args()


def main() -> None:
    load_env_from_file(PROJECT_ROOT / ".env")
    args = parse_args()
    username = args.username or os.environ.get("EARTHDATA_USERNAME")
    password = args.password or os.environ.get("EARTHDATA_PASSWORD")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir = args.output_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    if args.task_id:
        task_id = args.task_id
        task_response = {"task_id": task_id, "reused": True}
    else:
        if not username or not password:
            raise RuntimeError(
                "missing Earthdata credentials. Set EARTHDATA_USERNAME and EARTHDATA_PASSWORD in .env or pass --username/--password."
            )

        token = login(username, password)
        task = build_area_task(args.start_year, args.end_year, args.task_name)
        request_path = metadata_dir / "appeears_request.json"
        request_path.write_text(json.dumps(task, indent=2), encoding="utf-8")
        task_response = submit_task(token, task)
        task_id = task_response["task_id"]
        (metadata_dir / "appeears_submit_response.json").write_text(json.dumps(task_response, indent=2), encoding="utf-8")

    if not args.task_id:
        token = login(username, password)
    else:
        if not username or not password:
            raise RuntimeError(
                "reusing a task ID still requires Earthdata credentials to query task status and download files."
            )
        token = login(username, password)

    final_task = wait_for_task(token, task_id, args.poll_interval_seconds, args.timeout_minutes)
    (metadata_dir / "appeears_task_final.json").write_text(json.dumps(final_task, indent=2), encoding="utf-8")

    bundle = list_bundle(token, task_id)
    (metadata_dir / "appeears_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    layer_keywords = [item.strip() for item in args.layer_keywords.split(",") if item.strip()]
    downloaded = download_bundle_files(
        token,
        task_id,
        bundle,
        args.output_dir,
        args.download_retries,
        layer_keywords,
        args.include_support_files,
    )

    summary = {
        "task_id": task_id,
        "task_status": final_task.get("status"),
        "output_dir": str(args.output_dir),
        "downloaded_files": downloaded,
    }
    (metadata_dir / "download_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def build_area_task(start_year: int, end_year: int, task_name: str | None) -> dict[str, object]:
    task_name = task_name or f"nanjing_mod17a2hgf_061_{start_year}_{end_year}"
    return {
        "task_type": "area",
        "task_name": task_name,
        "params": {
            "geo": bbox_to_feature_collection(),
            "dates": [
                {
                    "startDate": f"01-01-{start_year}",
                    "endDate": f"12-31-{end_year}",
                    "recurring": False,
                }
            ],
            "layers": [
                {
                    "product": "MOD17A2HGF.061",
                    "layer": "Gpp_500m",
                }
            ],
            "output": {
                "format": {
                    "type": "geotiff",
                    "filename_date": "calendar",
                },
                "projection": "geographic",
            },
        },
    }


def bbox_to_feature_collection() -> dict[str, object]:
    west = NANJING_BBOX["west"]
    south = NANJING_BBOX["south"]
    east = NANJING_BBOX["east"]
    north = NANJING_BBOX["north"]
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [west, south],
                            [west, north],
                            [east, north],
                            [east, south],
                            [west, south],
                        ]
                    ],
                },
                "properties": {"name": "nanjing_bbox"},
            }
        ],
    }


def login(username: str, password: str) -> str:
    response = requests.post(f"{API_ROOT}/login", auth=(username, password), timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["token"]


def submit_task(token: str, task: dict[str, object]) -> dict[str, object]:
    response = requests.post(
        f"{API_ROOT}/task",
        json=task,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and "task_id" in data:
        return data
    location = response.headers.get("Location", "")
    task_id = location.rstrip("/").split("/")[-1] if location else None
    if not task_id:
        raise RuntimeError(f"cannot determine task_id from response: {data}")
    return {"task_id": task_id, "raw": data}


def wait_for_task(token: str, task_id: str, poll_interval_seconds: int, timeout_minutes: int) -> dict[str, object]:
    deadline = time.time() + timeout_minutes * 60
    last_response: dict[str, object] | None = None
    while time.time() < deadline:
        response = requests.get(
            f"{API_ROOT}/task/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and data:
            data = data[0]
        if not isinstance(data, dict):
            raise RuntimeError(f"unexpected task response: {data}")
        last_response = data
        status = str(data.get("status", "")).lower()
        if status == "done":
            return data
        if status in {"error", "failed", "deleted"}:
            raise RuntimeError(f"AppEEARS task {task_id} ended with status={status}: {json.dumps(data, ensure_ascii=False)}")
        print(json.dumps({"task_id": task_id, "status": status or "unknown"}, ensure_ascii=False))
        time.sleep(poll_interval_seconds)
    raise TimeoutError(f"timed out waiting for task {task_id}; last response: {last_response}")


def list_bundle(token: str, task_id: str) -> dict[str, object]:
    response = requests.get(
        f"{API_ROOT}/bundle/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"unexpected bundle response: {data}")
    return data


def download_bundle_files(
    token: str,
    task_id: str,
    bundle: dict[str, object],
    output_dir: Path,
    download_retries: int,
    layer_keywords: list[str],
    include_support_files: bool,
) -> list[str]:
    files = bundle.get("files", [])
    if not isinstance(files, list):
        raise RuntimeError(f"bundle.files is not a list: {bundle}")
    downloaded: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        file_id = item.get("file_id")
        file_name = item.get("file_name") or str(file_id)
        file_type = item.get("file_type")
        if not file_id:
            continue
        if not should_download_file(file_name, file_type, layer_keywords, include_support_files):
            continue
        destination = output_dir / file_name
        if destination.exists() and destination.stat().st_size > 0:
            downloaded.append(str(destination))
            continue
        downloaded.append(str(download_bundle_file(token, task_id, file_id, file_name, output_dir, download_retries)))
    return downloaded


def download_bundle_file(
    token: str,
    task_id: str,
    file_id: str,
    fallback_name: str,
    output_dir: Path,
    download_retries: int,
) -> Path:
    last_error: Exception | None = None
    for attempt in range(1, download_retries + 1):
        try:
            response = requests.get(
                f"{API_ROOT}/bundle/{task_id}/{file_id}",
                headers={"Authorization": f"Bearer {token}"},
                allow_redirects=True,
                stream=True,
                timeout=300,
            )
            response.raise_for_status()
            filename = resolve_filename(response, fallback_name)
            destination = output_dir / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
            return destination
        except RequestException as exc:
            last_error = exc
            print(json.dumps({"file_id": file_id, "attempt": attempt, "status": "retry", "error": str(exc)}, ensure_ascii=False))
            time.sleep(min(5 * attempt, 30))
    raise RuntimeError(f"failed to download file_id={file_id} after {download_retries} attempts: {last_error}")


def should_download_file(
    file_name: str,
    file_type: str | None,
    layer_keywords: list[str],
    include_support_files: bool,
) -> bool:
    if file_type == "tif":
        return any(keyword in file_name for keyword in layer_keywords)
    if include_support_files and file_type in {"csv", "json", "txt", "xml"}:
        return True
    return False


def resolve_filename(response: requests.Response, fallback_name: str) -> str:
    content_disposition = response.headers.get("Content-Disposition", "")
    for token in content_disposition.split(";"):
        token = token.strip()
        if token.startswith("filename="):
            return token.split("=", 1)[1].strip('"')
    if response.url:
        name = Path(urlparse(response.url).path).name
        if name:
            return name
    return fallback_name


if __name__ == "__main__":
    main()
