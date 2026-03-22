from pathlib import Path
import subprocess

import requests


FILES = {
    "co2_mm_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv",
    "co2_annmean_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_gl.csv",
    "co2_gr_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_gr_gl.csv",
    "co2_trend_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv",
}


def download_file(session: requests.Session, url: str, output_path: Path) -> None:
    try:
        with session.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with output_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
        return
    except requests.RequestException:
        pass

    subprocess.run(
        [
            "curl.exe",
            "-L",
            "-A",
            "Mozilla/5.0",
            "-o",
            str(output_path),
            url,
        ],
        check=True,
    )


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "data" / "raw" / "noaa" / "co2"
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    for filename, url in FILES.items():
        output_path = output_dir / filename
        download_file(session, url, output_path)
        print(f"Saved {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
