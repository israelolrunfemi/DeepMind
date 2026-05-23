"""Validated pip package installation helper."""

from __future__ import annotations

import re
import subprocess
import sys


PACKAGE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*([=<>!~]=?[A-Za-z0-9_.!*+-]+)?$")


def install_package(name: str) -> bool:
    """Install a package with pip after validating the package specifier."""

    if not PACKAGE_PATTERN.fullmatch(name):
        return False

    try:
        completed = subprocess.run(
            [sys.executable, "-m", "pip", "install", name],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False

    return completed.returncode == 0
