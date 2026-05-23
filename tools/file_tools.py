"""Small file helpers for reading and writing workspace files."""

from __future__ import annotations

from pathlib import Path


def read_file(path: str) -> str:
    """Read a UTF-8 text file with a clear error on failure."""

    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Could not read file {path}: {exc}") from exc


def write_file(path: str, content: str) -> bool:
    """Write a UTF-8 text file with a clear error on failure."""

    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return True
    except OSError as exc:
        raise RuntimeError(f"Could not write file {path}: {exc}") from exc
