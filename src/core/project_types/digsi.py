"""DIGSI 5 project type implementation."""

from __future__ import annotations

from pathlib import Path

from src.core.digsi import extract_digsi_version
from src.core.naming import get_project_id
from src.core.project_types.base import BaseProjectType


class DigsiProjectType(BaseProjectType):
    """Project type adapter for Siemens DIGSI 5 `.dz5` files."""

    key = "digsi5"
    label = "DIGSI 5 (.dz5)"
    extensions = (".dz5",)

    def get_project_id(self, project_file: Path) -> str:
        """Use the standard DIGSI export filename to infer the project identifier."""

        return get_project_id(project_file.name)

    def get_software_version(self, project_file: Path) -> str:
        """Inspect the `.dz5` archive and return the DIGSI version prefix."""

        return extract_digsi_version(project_file)


DIGSI_PROJECT_TYPE = DigsiProjectType()
