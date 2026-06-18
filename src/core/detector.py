"""Backward-compatible DIGSI file detection helpers.

New code should prefer `src.core.project_types`, but these functions remain so
older CLI/tests can keep using the original DIGSI-focused names.
"""

from __future__ import annotations

from pathlib import Path

from src.core.project_types.base import ProjectDetectionError
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE


class Dz5DetectionError(ProjectDetectionError):
    pass


def find_project_file(project_dir: Path) -> Path:
    """Return the latest default project file."""

    try:
        return DEFAULT_PROJECT_TYPE.find_latest_file(project_dir)
    except ProjectDetectionError as exc:
        raise Dz5DetectionError(str(exc)) from exc


def find_project_files(project_dir: Path) -> list[Path]:
    """Return default project files from oldest to newest."""

    try:
        return DEFAULT_PROJECT_TYPE.find_files(project_dir)
    except ProjectDetectionError as exc:
        raise Dz5DetectionError(str(exc)) from exc
