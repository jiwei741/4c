from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


SERVICE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_ROOT.parents[1]

SECTOR_URLS = {
    "ENE": "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/EDGAR_2025_GHG/CO2/ENE/ENE_emi_nc.zip",
    "IND": "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/EDGAR_2025_GHG/CO2/IND/IND_emi_nc.zip",
    "PRO_FFF": "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/EDGAR_2025_GHG/CO2/PRO_FFF/PRO_FFF_emi_nc.zip",
    "CHE": "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/EDGAR_2025_GHG/CO2/CHE/CHE_emi_nc.zip",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download EDGAR 2025 CO2 annual sector gridmaps for the Nanjing quarterly training pipeline."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data/raw/edgar/nanjing",
    )
    parser.add_argument(
        "--sectors",
        nargs="+",
        default=["ENE", "IND", "PRO_FFF", "CHE"],
        help="Sector codes to download.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload files even if they already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "release": "EDGAR_2025_GHG",
        "substance": "CO2",
        "output_dir": str(output_dir),
        "downloads": {},
    }

    for sector in args.sectors:
        if sector not in SECTOR_URLS:
            raise ValueError(f"unsupported EDGAR sector: {sector}")
        url = SECTOR_URLS[sector]
        target = output_dir / Path(url).name
        if target.exists() and not args.force:
            summary["downloads"][sector] = {
                "status": "cached",
                "path": str(target),
                "size_bytes": target.stat().st_size,
                "url": url,
            }
            continue
        download_file(url, target)
        summary["downloads"][sector] = {
            "status": "downloaded",
            "path": str(target),
            "size_bytes": target.stat().st_size,
            "url": url,
        }

    summary_path = output_dir / "download.summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def download_file(url: str, target: Path) -> None:
    with requests.get(url, stream=True, timeout=180) as response:
        response.raise_for_status()
        with target.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


if __name__ == "__main__":
    main()
