from pathlib import Path

from src.core.detector import find_project_file


def test_find_project_file_detects_single_dz5(tmp_path: Path) -> None:
    project = tmp_path / "SE-CTU_20260612_1736.dz5"
    project.write_text("content", encoding="utf-8")

    assert find_project_file(tmp_path) == project


def test_find_project_file_selects_latest_dz5(tmp_path: Path) -> None:
    older = tmp_path / "A.dz5"
    newer = tmp_path / "B.dz5"
    older.write_text("a", encoding="utf-8")
    newer.write_text("b", encoding="utf-8")

    older_mtime = 1_780_000_000
    newer_mtime = 1_780_010_000
    older.touch()
    newer.touch()
    import os

    os.utime(older, (older_mtime, older_mtime))
    os.utime(newer, (newer_mtime, newer_mtime))

    assert find_project_file(tmp_path) == newer
