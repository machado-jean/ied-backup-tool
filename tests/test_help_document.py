from __future__ import annotations

from src.gui.resources import help_document_path, help_document_url


def test_help_document_exists_with_core_sections() -> None:
    path = help_document_path()
    english_path = path.with_name("HELP.en.md")

    assert path.exists()
    assert english_path.exists()

    text = path.read_text(encoding="utf-8")
    assert "## Limitações Conhecidas" in text
    assert "## Solução de Problemas" in text
    assert "IEDS-BACKUP-INFO.txt" in text

    english_text = english_path.read_text(encoding="utf-8")
    assert "## Known Limitations" in english_text
    assert "## Troubleshooting" in english_text
    assert "IEDS-BACKUP-INFO.txt" in english_text


def test_help_document_url_points_to_public_github_doc() -> None:
    assert help_document_url("pt_BR") == (
        "https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md"
    )
    assert help_document_url("en_US") == (
        "https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.en.md"
    )
    assert help_document_url("unknown") == (
        "https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md"
    )
