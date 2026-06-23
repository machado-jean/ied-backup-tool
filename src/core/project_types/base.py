"""Contracts and shared helpers for supported IED project types."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ProjectType(Protocol):
    """Interface implemented by each software/IED family supported by the app."""

    key: str
    label: str
    extensions: tuple[str, ...]

    def find_files(self, project_dir: Path) -> list[Path]:
        """Return supported project files sorted from oldest to newest."""

    def get_project_id(self, project_file: Path) -> str:
        """Return the project identifier used in the backup name."""

    def get_software_version(
        self,
        project_file: Path,
        fallback_version: str | None = None,
    ) -> str:
        """Return the software/version prefix used in the backup name."""

    def get_related_files(self, project_file: Path) -> list[Path]:
        """Return every source file that must be included in the backup zip."""


class ProjectDetectionError(RuntimeError):
    pass


class ProjectVersionRequiredError(ProjectDetectionError):
    """Raised when a project type needs a manual software version fallback."""

    def __init__(self, *, project_type_label: str, project_file: Path) -> None:
        self.project_type_label = project_type_label
        self.project_file = project_file
        super().__init__(
            f"Nao foi possivel detectar a versao de {project_file.name}. "
            "Informe a versao do software."
        )


class BaseProjectType:
    """Base implementation for extension-based project file discovery."""

    key: str
    label: str
    extensions: tuple[str, ...]

    def find_files(self, project_dir: Path) -> list[Path]:
        """Find supported files and sort them chronologically for batch processing."""

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
        """Return the newest supported file in a project folder."""

        return self.find_files(project_dir)[-1]

    def get_related_files(self, project_file: Path) -> list[Path]:
        """Return only the primary file for single-file project types."""

        return [project_file]
