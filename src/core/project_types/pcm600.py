"""ABB PCM600 project type implementation."""

from __future__ import annotations

from pathlib import Path

from src.core.naming import get_project_id
from src.core.pcm600 import extract_pcm600_version
from src.core.project_types.base import BaseProjectType


class Pcm600ProjectType(BaseProjectType):
    """Project type adapter for ABB PCM600 project package files."""

    key = "pcm600"
    label = "ABB PCM600 (.pcmp, .apcmp)"
    extensions = (".pcmp", ".apcmp")

    def get_project_id(self, project_file: Path) -> str:
        """Use the standard first-underscore policy to infer the project identifier."""

        return get_project_id(project_file.name)

    def get_software_version(
        self,
        project_file: Path,
        fallback_version: str | None = None,
    ) -> str:
        """Inspect the PCM600 package and return the PCM600 version prefix."""

        return extract_pcm600_version(project_file)


PCM600_PROJECT_TYPE = Pcm600ProjectType()
