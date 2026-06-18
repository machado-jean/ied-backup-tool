"""Backup naming helpers shared by every project type."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from pathlib import Path

PROJECT_FILENAME_PATTERN = re.compile(r"^(?P<project>.+)_\d{8}_\d{4}$")


class BackupStage(str, Enum):
    """Workflow stage written into the generated backup filename."""

    DEV = "DEV"
    PRE_TAF = "PRE-TAF"
    TAF = "TAF"
    POS_TAF = "POS-TAF"
    PRE_TAC = "PRE-TAC"
    TAC = "TAC"
    POS_TAC = "POS-TAC"
    PRODUCAO = "PRODUCAO"
    CUSTOM = "CUSTOM"


def get_project_id(filename: str) -> str:
    """Infer a project identifier from an exported project filename."""

    stem = Path(filename).stem
    match = PROJECT_FILENAME_PATTERN.match(stem)
    project_id = (match.group("project") if match else stem.split("_", maxsplit=1)[0]).strip()
    if not project_id:
        raise ValueError(f"Identificador do projeto invalido: {filename}")
    return project_id


def get_file_timestamp(path: Path) -> datetime:
    """Return the file modification time used as the backup timestamp."""

    return datetime.fromtimestamp(path.stat().st_mtime)


def format_backup_timestamp(timestamp: datetime) -> str:
    """Format a timestamp in the canonical backup filename format."""

    return timestamp.strftime("%Y%m%d-%H%M")


def normalize_collaborator(collaborator: str) -> str:
    """Normalize collaborator names so they are stable in filenames."""

    normalized = collaborator.strip().upper().replace(" ", "-")
    if not normalized:
        raise ValueError("Colaborador nao pode ser vazio")
    return normalized


def build_backup_name(
    *,
    software_version: str,
    project_id: str,
    timestamp: datetime,
    collaborator: str,
    stage: BackupStage,
) -> str:
    """Build the standard backup filename from normalized metadata."""

    return "_".join(
        [
            software_version,
            project_id,
            format_backup_timestamp(timestamp),
            normalize_collaborator(collaborator),
            stage.value,
        ]
    ) + ".zip"
