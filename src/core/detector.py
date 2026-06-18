from __future__ import annotations

from pathlib import Path

from src.core.project_types.base import ProjectDetectionError
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE


class Dz5DetectionError(ProjectDetectionError):
    pass


def find_project_file(project_dir: Path) -> Path:
    try:
        return DEFAULT_PROJECT_TYPE.find_latest_file(project_dir)
    except ProjectDetectionError as exc:
        raise Dz5DetectionError(str(exc)) from exc


def find_project_files(project_dir: Path) -> list[Path]:
    try:
        return DEFAULT_PROJECT_TYPE.find_files(project_dir)
    except ProjectDetectionError as exc:
        raise Dz5DetectionError(str(exc)) from exc
