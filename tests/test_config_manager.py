from pathlib import Path

import pytest

from src.config.config_manager import ConfigError, parse_config


def test_parse_config_normalizes_collaborator() -> None:
    config = parse_config(
        {
            "colaborador": "Jean Carlos Machado",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
        }
    )

    assert config.collaborator == "JEAN-CARLOS-MACHADO"
    assert config.atu_path == Path("C:/BKP/ATU")
    assert config.his_path == Path("C:/BKP/HIS")
    assert config.language == "pt_BR"


def test_parse_config_accepts_language() -> None:
    config = parse_config(
        {
            "colaborador": "Jean",
            "atu_path": "C:/BKP/ATU",
            "his_path": "C:/BKP/HIS",
            "language": "en_US",
        }
    )

    assert config.language == "en_US"


def test_parse_config_requires_paths() -> None:
    with pytest.raises(ConfigError, match="his_path"):
        parse_config({"colaborador": "Jean", "atu_path": "C:/BKP/ATU"})
