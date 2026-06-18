from pathlib import Path

import pytest

from src.core.zipper import BackupZipError, create_backup_zip


def test_create_backup_zip_reports_unreadable_source(tmp_path: Path) -> None:
    missing = tmp_path / "missing.dz5"

    with pytest.raises(BackupZipError, match="Nao foi possivel ler"):
        create_backup_zip(missing, "backup.zip", output_dir=tmp_path / "out")
