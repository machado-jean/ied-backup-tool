from pathlib import Path

import pytest

from src.config.config_manager import AppConfig, ConfigError, parse_config, save_config


def test_parse_config_normalizes_collaborator() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
        }
    )

    assert config.collaborator == "COLABORADOR-EXEMPLO"
    assert config.atu_path == Path("C:/BKP/ATU")
    assert config.his_path == Path("C:/BKP/HIS")
    assert config.language == "pt_BR"


def test_parse_config_accepts_language() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "language": "en_US",
        }
    )

    assert config.language == "en_US"


def test_parse_config_accepts_project_types() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "project_types": ["digsi5", "sel"],
        }
    )

    assert config.project_types == ("digsi5", "sel")


def test_parse_config_accepts_software_versions() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "software_versions": {"ingeteam": "5.5.4", "empty": " "},
        }
    )

    assert config.software_versions == {"ingeteam": "5.5.4"}


def test_parse_config_accepts_startup_instruction_preference() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "show_startup_instructions": False,
        }
    )

    assert config.show_startup_instructions is False


def test_parse_config_accepts_history_cleanup_preferences() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "history_cleanup": {
                "retention_days": 45,
            },
        }
    )

    assert config.history_cleanup.retention_days == 45


def test_parse_config_defaults_invalid_history_cleanup_preferences() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "history_cleanup": {
                "retention_days": "30",
            },
        }
    )

    assert config.history_cleanup.retention_days == 30


def test_parse_config_accepts_zero_retention_to_disable_cleanup() -> None:
    config = parse_config(
        {
            "colaborador": "Colaborador Exemplo",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "history_cleanup": {
                "retention_days": 0,
            },
        }
    )

    assert config.history_cleanup.retention_days == 0


def test_save_config_writes_history_cleanup_retention_only(tmp_path: Path) -> None:
    path = tmp_path / "config.json"

    save_config(
        path,
        AppConfig(
            collaborator="COLABORADOR",
            atu_path=tmp_path / "ATU",
            his_path=tmp_path / "HIS",
        ),
    )

    text = path.read_text(encoding="utf-8")

    assert '"history_cleanup"' in text
    assert '"retention_days": 30' in text


def test_parse_config_requires_paths() -> None:
    with pytest.raises(ConfigError, match="his_path"):
        parse_config({"colaborador": "Colaborador Exemplo", "atu_path": "C:/BKP/ATU"})
