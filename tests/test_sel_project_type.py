from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from src.core.backup_service import process_all_backups
from src.core.naming import BackupStage
from src.core.project_types.base import ProjectVersionRequiredError
from src.core.project_types.registry import get_project_type
from src.core.project_types.sel import SEL_PROJECT_TYPE


def test_sel_project_type_is_registered() -> None:
    assert get_project_type("sel") is SEL_PROJECT_TYPE
    assert SEL_PROJECT_TYPE.extensions == (".rdb",)


def test_sel_backup_includes_same_stem_architect_file(tmp_path: Path) -> None:
    project_dir = tmp_path / "IED-DES"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    rdb = project_dir / "SE-SEL_DEV_01_20260619_0013.rdb"
    scd = project_dir / "SE-SEL_DEV_01_20260619_0013.scd"
    rdb.write_text(
        "Saved with Main Shell Version: 7.5.2.3\n"
        "Saved with Main Shell Version: 7.5.3.10\n",
        encoding="utf-8",
    )
    scd.write_text(
        '<Header id="ESD_PDO" version="388" revision="1.0" '
        'toolID="AcSELerator Architect 2.4.2.34" />',
        encoding="utf-8",
    )
    timestamp = datetime(2026, 6, 19, 0, 13).timestamp()
    os.utime(rdb, (timestamp, timestamp))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.TAF,
        project_type=SEL_PROJECT_TYPE,
    )

    assert [result.status for result in results] == ["stored"]
    [zip_path] = list(atu.glob("*.zip"))
    assert zip_path.name == (
        "SEL-QS7.5.3.10-AA2.4.2.34_SE-SEL_20260619-0013_"
        "JEAN-CARLOS-MACHADO_TAF.zip"
    )
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.namelist() == [
            "SE-SEL_DEV_01_20260619_0013.rdb",
            "SE-SEL_DEV_01_20260619_0013.scd",
        ]


def test_sel_version_fallback_is_used_when_quickset_is_missing(tmp_path: Path) -> None:
    project_dir = tmp_path / "IED-DES"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    rdb = project_dir / "SE-SEL_20260619_0013.rdb"
    rdb.write_text("old sel file", encoding="utf-8")
    timestamp = datetime(2026, 6, 19, 0, 13).timestamp()
    os.utime(rdb, (timestamp, timestamp))

    process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
        project_type=SEL_PROJECT_TYPE,
        software_version_override="7.5.2.3",
    )

    assert [path.name for path in atu.glob("*.zip")] == [
        "SEL-V7.5.2.3_SE-SEL_20260619-0013_JEAN-CARLOS-MACHADO_DEV.zip"
    ]


def test_sel_requires_manual_version_when_quickset_is_missing(tmp_path: Path) -> None:
    project_dir = tmp_path / "IED-DES"
    project_dir.mkdir()
    (project_dir / "SE-SEL_20260619_0013.rdb").write_text("old sel file", encoding="utf-8")

    with pytest.raises(ProjectVersionRequiredError):
        SEL_PROJECT_TYPE.get_software_version(project_dir / "SE-SEL_20260619_0013.rdb")
