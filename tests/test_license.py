from __future__ import annotations

from pathlib import Path

from src.gui.resources import repository_url


def test_license_file_documents_non_commercial_terms() -> None:
    text = Path("LICENSE").read_text(encoding="utf-8")

    assert "IED Backup Manager Non-Commercial License" in text
    assert "Copyright (c) 2026 Jean Carlos Machado" in text
    assert "Commercial use is not permitted" in text


def test_repository_url_points_to_public_project() -> None:
    assert repository_url() == "https://github.com/machado-jean/ied-backup-tool"
