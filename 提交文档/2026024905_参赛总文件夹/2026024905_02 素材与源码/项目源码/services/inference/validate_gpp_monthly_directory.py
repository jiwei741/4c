from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PATTERN = re.compile(r"^map_(\d{4})(\d{2})\.tif$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate monthly GPP GeoTIFF naming and coverage.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("d:/4c/data/raw/gpp/nanjing/monthly"),
    )
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("d:/4c/data/raw/gpp/nanjing/monthly/validation.summary.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    expected = [f"{year}{month:02d}" for year in range(args.start_year, args.end_year + 1) for month in range(1, 13)]
    existing = {}
    invalid = []

    if not args.input_dir.exists():
        raise FileNotFoundError(f"directory does not exist: {args.input_dir}")

    for path in sorted(args.input_dir.iterdir()):
        if path.is_dir():
            continue
        if path.suffix.lower() not in {".tif", ".tiff"}:
            continue
        match = PATTERN.match(path.name)
        if not match:
            invalid.append(path.name)
            continue
        existing[match.group(1) + match.group(2)] = path.name

    missing = [item for item in expected if item not in existing]
    summary = {
        "input_dir": str(args.input_dir),
        "expected_count": len(expected),
        "existing_count": len(existing),
        "missing": missing,
        "invalid_filenames": invalid,
        "valid": not missing and not invalid,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
