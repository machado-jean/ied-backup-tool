from pathlib import Path

import pytest

from src.core.zipper import BackupZipError, create_backup_zip


def test_create_backup_zip_reports_unreadable_source(tmp_path: Path) -> None:
    missing = tmp_path / "missing.dz5"

    with pytest.raises(BackupZipError, match="Nao foi possivel ler"):
        create_backup_zip(missing, "backup.zip", output_dir=tmp_path / "out")


def test_create_backup_zip_reports_byte_progress(tmp_path: Path) -> None:
    source = tmp_path / "project.dz5"
    source.write_bytes(b"a" * 2048)
    events = []

    create_backup_zip(
        source,
        "backup.zip",
        output_dir=tmp_path / "out",
        progress_callback=lambda phase, current, total: events.append((phase, current, total)),
    )

    assert events
    assert events[0] == ("zip", 0, 2048)
    assert events[-1] == ("zip", 2048, 2048)
