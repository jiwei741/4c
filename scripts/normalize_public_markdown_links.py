from __future__ import annotations

import os
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_PREFIXES = (
    "/d:/4c/",
    "d:/4c/",
    "/D:/4c/",
    "D:/4c/",
)
PUBLIC_EXCLUDED_PREFIXES = (
    ".env",
    "data/raw/",
    "data/processed/segmentation/",
    "logs/",
    "external/",
    "remote_sensing_output/",
    "remote_sensing_output_ver.03.20/",
    "services/backend/runtime/",
)
SCAN_ROOTS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs",
    REPO_ROOT / "services",
)
MARKDOWN_LINK = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<target>/?[A-Za-z]:/[^)]+)\)")


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file() and root.suffix.lower() == ".md":
            files.append(root)
            continue
        if root.is_dir():
            for path in root.rglob("*.md"):
                if any(part in {".venv", "__pycache__"} for part in path.parts):
                    continue
                files.append(path)
    return files


def repo_relative_target(target: str) -> Path | None:
    normalized = target.replace("\\", "/")
    for prefix in LOCAL_PREFIXES:
        if normalized.startswith(prefix):
            return Path(normalized[len(prefix) :])
    return None


def should_publish_as_link(repo_relative: Path) -> bool:
    posix_path = repo_relative.as_posix()
    if any(posix_path == prefix or posix_path.startswith(prefix) for prefix in PUBLIC_EXCLUDED_PREFIXES):
        return False
    return (REPO_ROOT / repo_relative).exists()


def replacement_for(file_path: Path, label: str, target: str) -> str:
    repo_relative = repo_relative_target(target)
    if repo_relative is None:
        return f"[{label}]({target})"

    repo_relative_posix = repo_relative.as_posix()
    if not should_publish_as_link(repo_relative):
        return f"{label} (`{repo_relative_posix}`)"

    relative = os.path.relpath(REPO_ROOT / repo_relative, file_path.parent).replace("\\", "/")
    return f"[{label}]({relative})"


def normalize_file(file_path: Path) -> bool:
    original = file_path.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        return replacement_for(file_path, match.group("label"), match.group("target"))

    updated = MARKDOWN_LINK.sub(replace, original)
    if updated == original:
        return False

    file_path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for file_path in iter_markdown_files():
        if normalize_file(file_path):
            changed += 1
            print(f"updated: {file_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"done: {changed} files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
