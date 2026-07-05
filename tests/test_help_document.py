from __future__ import annotations

from src.gui.resources import help_document_path, help_document_url


def test_help_document_exists_with_core_sections() -> None:
    path = help_document_path()

    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert "## Limitacoes Conhecidas" in text
    assert "## Solucao de Problemas" in text
    assert "IEDS-BACKUP-INFO.txt" in text


def test_help_document_url_points_to_public_github_doc() -> None:
    assert help_document_url() == (
        "https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md"
    )
