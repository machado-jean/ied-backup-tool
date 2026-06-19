"""Backup naming helpers shared by every project type."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from enum import Enum
from pathlib import Path

PROJECT_FILENAME_PATTERN = re.compile(r"^(?P<project>.+)_\d{8}_\d{4}$")
STAGE_ALLOWED_CHARS_PATTERN = re.compile(r"[^A-Z0-9-]+")


class BackupStage(str, Enum):
    """Workflow stage written into the generated backup filename."""

    DEV = "DEV"
    PRE_TAF = "PRE-TAF"
    TAF = "TAF"
    POS_TAF = "POS-TAF"
    PRE_TAC = "PRE-TAC"
    TAC = "TAC"
    POS_TAC = "POS-TAC"


def get_project_id(filename: str) -> str:
    """Infer a project identifier from an exported project filename."""

    stem = Path(filename).stem
    project_id = stem.split("_", maxsplit=1)[0].strip()
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


def normalize_stage(stage: BackupStage | str) -> str:
    """Normalize a stage/description while allowing it to be intentionally empty."""

    raw_stage = stage.value if isinstance(stage, BackupStage) else stage
    ascii_stage = unicodedata.normalize("NFKD", raw_stage).encode("ascii", "ignore").decode("ascii")
    normalized = ascii_stage.strip().upper().replace("_", "-")
    normalized = "-".join(normalized.split())
    normalized = STAGE_ALLOWED_CHARS_PATTERN.sub("-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized


def build_backup_name(
    *,
    software_version: str,
    project_id: str,
    timestamp: datetime,
    collaborator: str,
    stage: BackupStage | str,
) -> str:
    """Build the standard backup filename from normalized metadata."""

    return "_".join(
        [
            software_version,
            project_id,
            format_backup_timestamp(timestamp),
            normalize_collaborator(collaborator),
            normalize_stage(stage),
        ]
    ) + ".zip"
