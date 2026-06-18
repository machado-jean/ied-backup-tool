from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from pathlib import Path

PROJECT_FILENAME_PATTERN = re.compile(r"^(?P<project>.+)_\d{8}_\d{4}$")


class BackupStage(str, Enum):
    DEV = "DEV"
    PRE_TAF = "PRE-TAF"
    POS_TAF = "POS-TAF"
    PRE_TAC = "PRE-TAC"
    POS_TAC = "POS-TAC"
    PRODUCAO = "PRODUCAO"
    CUSTOM = "CUSTOM"


def get_project_id(filename: str) -> str:
    stem = Path(filename).stem
    match = PROJECT_FILENAME_PATTERN.match(stem)
    project_id = (match.group("project") if match else stem.split("_", maxsplit=1)[0]).strip()
    if not project_id:
        raise ValueError(f"Identificador do projeto invalido: {filename}")
    return project_id


def get_file_timestamp(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def format_backup_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime("%Y%m%d-%H%M")


def normalize_collaborator(collaborator: str) -> str:
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
    return "_".join(
        [
            software_version,
            project_id,
            format_backup_timestamp(timestamp),
            normalize_collaborator(collaborator),
            stage.value,
        ]
    ) + ".zip"
