"""Registry of project types available to the CLI and GUI."""

from __future__ import annotations

from src.core.project_types.base import ProjectType
from src.core.project_types.digsi import DIGSI_PROJECT_TYPE

PROJECT_TYPES: tuple[ProjectType, ...] = (DIGSI_PROJECT_TYPE,)
DEFAULT_PROJECT_TYPE = DIGSI_PROJECT_TYPE


def get_project_type(key: str) -> ProjectType:
    """Return a registered project type by key."""

    for project_type in PROJECT_TYPES:
        if project_type.key == key:
            return project_type
    raise ValueError(f"Tipo de projeto nao suportado: {key}")
