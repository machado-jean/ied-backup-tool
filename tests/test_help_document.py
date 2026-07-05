from __future__ import annotations

from src.gui.resources import help_document_path


def test_help_document_exists_with_core_sections() -> None:
    path = help_document_path()

    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert "## Limitacoes Conhecidas" in text
    assert "## Solucao de Problemas" in text
    assert "IEDS-BACKUP-INFO.txt" in text
