"""Small file helpers for reading and writing workspace files."""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any


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


def list_directory(path: str) -> dict[str, Any]:
    """List all files and subdirectories at path."""

    try:
        target = Path(path)
        files = sorted(child.name for child in target.iterdir() if child.is_file())
        dirs = sorted(child.name for child in target.iterdir() if child.is_dir())
        return {"status": "success", "files": files, "dirs": dirs}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}


def delete_file(path: str) -> dict[str, str]:
    """Delete a file at path."""

    try:
        Path(path).unlink()
        return {"status": "success"}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}


def create_directory(path: str) -> dict[str, str]:
    """Create a directory and all intermediate directories."""

    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {"status": "success"}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}


def move_file(src: str, dest: str) -> dict[str, str]:
    """Move or rename a file from src to dest."""

    try:
        destination = Path(dest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dest)
        return {"status": "success"}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}
    except shutil.Error as exc:
        return {"status": "error", "error": str(exc)}


def get_file_tree(root: str, max_depth: int = 3) -> dict[str, Any]:
    """Recursively build a file tree from root up to max_depth."""

    def build_tree(path: Path, depth: int) -> dict[str, Any]:
        node: dict[str, Any] = {"name": path.name, "type": "directory", "children": []}
        if depth >= max_depth:
            return node
        for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
            if child.is_dir():
                node["children"].append(build_tree(child, depth + 1))
            else:
                node["children"].append({"name": child.name, "type": "file"})
        return node

    try:
        target = Path(root)
        if not target.exists():
            return {"status": "error", "error": f"Path does not exist: {root}"}
        if target.is_file():
            return {"status": "success", "tree": {"name": target.name, "type": "file"}}
        return {"status": "success", "tree": build_tree(target, 0)}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}
