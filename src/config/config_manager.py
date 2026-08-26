"""Load and save the user configuration stored next to the executable."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.i18n import DEFAULT_LANGUAGE
from src.core.naming import (
    compact_collaborator_name,
    format_collaborator_name,
    normalize_person_name_part,
)


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class HistoryCleanupConfig:
    """User preferences for controlled HIS cleanup."""

    retention_days: int = 30


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings required to generate backups."""

    collaborator: str
    atu_path: Path
    his_path: Path
    collaborator_first_name: str = ""
    collaborator_last_name: str = ""
    language: str = DEFAULT_LANGUAGE
    project_types: tuple[str, ...] = ()
    software_versions: dict[str, str] | None = None
    show_startup_instructions: bool = True
    history_cleanup: HistoryCleanupConfig = HistoryCleanupConfig()

    def __post_init__(self) -> None:
        """Keep legacy collaborator input and split name fields synchronized."""

        first_name = normalize_person_name_part(self.collaborator_first_name)
        last_name = normalize_person_name_part(self.collaborator_last_name)
        if not first_name and not last_name:
            first_name, last_name = split_collaborator_name(self.collaborator)
        collaborator = format_collaborator_name(first_name, last_name)
        object.__setattr__(self, "collaborator_first_name", first_name)
        object.__setattr__(self, "collaborator_last_name", last_name)
        object.__setattr__(self, "collaborator", collaborator)


def load_config(path: Path) -> AppConfig:
    """Read and validate a JSON configuration file."""

    if not path.exists():
        raise ConfigError(
            f"Arquivo de configuracao nao encontrado: {path}. "
            "Crie o config.json antes de executar o backup."
        )

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Arquivo de configuracao invalido: {path}") from exc

    return parse_config(raw)


def save_config(path: Path, config: AppConfig) -> None:
    """Persist the current GUI configuration in a portable JSON format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "nome": config.collaborator_first_name,
        "sobrenome": config.collaborator_last_name,
        "colaborador": config.collaborator,
        "atu_path": str(config.atu_path),
        "his_path": str(config.his_path),
        "language": config.language,
        "project_types": list(config.project_types),
        "software_versions": config.software_versions or {},
        "show_startup_instructions": config.show_startup_instructions,
        "history_cleanup": {
            "retention_days": config.history_cleanup.retention_days,
        },
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_config(raw: dict[str, Any]) -> AppConfig:
    """Convert raw JSON data into a normalized application configuration."""

    first_name, last_name = _read_collaborator_fields(raw)
    atu_path = Path(_required_str(raw, "atu_path"))
    his_path = Path(_required_str(raw, "his_path"))
    language = raw.get("language", DEFAULT_LANGUAGE)
    if not isinstance(language, str) or language not in {"pt_BR", "en_US"}:
        language = DEFAULT_LANGUAGE
    project_types = raw.get("project_types", [])
    if not isinstance(project_types, list):
        project_types = []
    software_versions = raw.get("software_versions", {})
    if not isinstance(software_versions, dict):
        software_versions = {}
    show_startup_instructions = raw.get("show_startup_instructions", True)
    if not isinstance(show_startup_instructions, bool):
        show_startup_instructions = True
    history_cleanup = _parse_history_cleanup(raw.get("history_cleanup", {}))

    return AppConfig(
        collaborator=format_collaborator_name(first_name, last_name),
        collaborator_first_name=first_name,
        collaborator_last_name=last_name,
        atu_path=atu_path,
        his_path=his_path,
        language=language,
        project_types=tuple(item for item in project_types if isinstance(item, str)),
        software_versions={
            key: value.strip()
            for key, value in software_versions.items()
            if isinstance(key, str) and isinstance(value, str) and value.strip()
        },
        show_startup_instructions=show_startup_instructions,
        history_cleanup=history_cleanup,
    )


def split_collaborator_name(collaborator: str) -> tuple[str, str]:
    """Split legacy collaborator text into first and last name fields."""

    compacted = compact_collaborator_name(collaborator)
    parts = compacted.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


def _read_collaborator_fields(raw: dict[str, Any]) -> tuple[str, str]:
    """Read current name fields or migrate the legacy collaborator field."""

    first_name = raw.get("nome")
    last_name = raw.get("sobrenome")
    if isinstance(first_name, str) and first_name.strip():
        return (
            normalize_person_name_part(first_name),
            normalize_person_name_part(last_name if isinstance(last_name, str) else ""),
        )

    collaborator = _required_str(raw, "colaborador")
    return split_collaborator_name(collaborator)


def _required_str(raw: dict[str, Any], key: str) -> str:
    """Return a required non-empty string field from the raw config payload."""

    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Campo obrigatorio ausente ou invalido: {key}")
    return value


def _parse_history_cleanup(raw: Any) -> HistoryCleanupConfig:
    """Normalize optional HIS cleanup preferences from config.json."""

    if not isinstance(raw, dict):
        return HistoryCleanupConfig()

    retention_days = raw.get("retention_days", 30)
    if not isinstance(retention_days, int) or isinstance(retention_days, bool):
        retention_days = 30
    retention_days = max(0, min(retention_days, 3650))

    return HistoryCleanupConfig(retention_days=retention_days)
