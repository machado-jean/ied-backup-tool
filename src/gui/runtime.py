"""Runtime path helpers for development and packaged execution."""

from __future__ import annotations

import sys
from pathlib import Path


def get_runtime_project_dir() -> Path:
    """Return the executable folder in production or cwd during development."""

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()
