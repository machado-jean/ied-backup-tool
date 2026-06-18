from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ProjectType(Protocol):
    key: str
    label: str
    extensions: tuple[str, ...]

    def find_files(self, project_dir: Path) -> list[Path]:
        """Return supported project files sorted from oldest to newest."""

    def get_project_id(self, project_file: Path) -> str:
        """Return the project identifier used in the backup name."""

    def get_software_version(self, project_file: Path) -> str:
        """Return the software/version prefix used in the backup name."""


class ProjectDetectionError(RuntimeError):
    pass


class BaseProjectType:
    key: str
    label: str
    extensions: tuple[str, ...]

    def find_files(self, project_dir: Path) -> list[Path]:
        if not project_dir.exists() or not project_dir.is_dir():
            raise ProjectDetectionError(f"Pasta do projeto invalida: {project_dir}")

        matches = [
            path
            for path in project_dir.iterdir()
            if path.is_file() and path.suffix.lower() in self.extensions
        ]

        if not matches:
            extensions = ", ".join(self.extensions)
            raise ProjectDetectionError(
                f"Nenhum arquivo {self.label} encontrado em: {project_dir} ({extensions})"
            )

        return sorted(matches, key=lambda path: (path.stat().st_mtime, path.name))

    def find_latest_file(self, project_dir: Path) -> Path:
        return self.find_files(project_dir)[-1]
