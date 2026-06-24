"""INGETEAM project type implementation for efsPro and ITPro2 backups."""

from __future__ import annotations

from pathlib import Path

from src.core.naming import get_project_id, sanitize_filename_part
from src.core.project_types.base import BaseProjectType, ProjectVersionRequiredError


class IngeteamProjectType(BaseProjectType):
    """Project type adapter for INGETEAM `.efsPro` and `.ITPro2` backups.

    INGETEAM package formats expose several internal component versions, which
    makes automatic version selection ambiguous. The app therefore requires the
    user to provide the software version currently in use and stores it in the
    local configuration.
    """

    key = "ingeteam"
    label = "INGETEAM (.efsPro, .ITPro2)"
    extensions = (".efspro", ".itpro2")
    manual_version_required = True

    def get_project_id(self, project_file: Path) -> str:
        """Use the standard first-underscore policy to infer the project identifier."""

        return get_project_id(project_file.name)

    def get_software_version(
        self,
        project_file: Path,
        fallback_version: str | None = None,
    ) -> str:
        """Return the configured INGETEAM software version prefix."""

        if fallback_version:
            normalized = sanitize_filename_part(fallback_version)
            if normalized:
                if normalized.startswith("INGETEAM-"):
                    return normalized
                if normalized.startswith("V"):
                    return f"INGETEAM-{normalized}"
                return f"INGETEAM-V{normalized}"

        raise ProjectVersionRequiredError(
            project_type_label=self.label,
            project_file=project_file,
        )


INGETEAM_PROJECT_TYPE = IngeteamProjectType()
