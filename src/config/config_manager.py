from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.i18n import DEFAULT_LANGUAGE


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class AppConfig:
    collaborator: str
    atu_path: Path
    his_path: Path
    language: str = DEFAULT_LANGUAGE


def load_config(path: Path) -> AppConfig:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "colaborador": config.collaborator,
        "atu_path": str(config.atu_path),
        "his_path": str(config.his_path),
        "language": config.language,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_config(raw: dict[str, Any]) -> AppConfig:
    collaborator = _required_str(raw, "colaborador")
    atu_path = Path(_required_str(raw, "atu_path"))
    his_path = Path(_required_str(raw, "his_path"))
    language = raw.get("language", DEFAULT_LANGUAGE)
    if not isinstance(language, str) or language not in {"pt_BR", "en_US"}:
        language = DEFAULT_LANGUAGE

    return AppConfig(
        collaborator=collaborator.strip().upper().replace(" ", "-"),
        atu_path=atu_path,
        his_path=his_path,
        language=language,
    )


def _required_str(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Campo obrigatorio ausente ou invalido: {key}")
    return value
