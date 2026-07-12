from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path

from src.core.backup_service import process_all_backups
from src.core.naming import BackupStage
from src.core.project_types.ge_multilin import GE_MULTILIN_PROJECT_TYPE
from src.core.project_types.registry import get_project_type
from src.core.zipper import BACKUP_INFO_FILENAME


def test_ge_multilin_project_type_is_registered() -> None:
    assert get_project_type("ge_multilin") is GE_MULTILIN_PROJECT_TYPE
    assert GE_MULTILIN_PROJECT_TYPE.extensions == (".urs", ".urk")


def test_ge_multilin_finds_one_environment_backup_and_uses_folder_project(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "SE-LAGOS"
    _write_ge_sample(project_dir)

    files = GE_MULTILIN_PROJECT_TYPE.find_files(project_dir)

    assert len(files) == 1
    assert GE_MULTILIN_PROJECT_TYPE.get_project_id(files[0]) == "SE-LAGOS"
    assert GE_MULTILIN_PROJECT_TYPE.get_software_version(files[0]) == "GE-MULTILIN-V8.60"


def test_ge_multilin_includes_env_and_only_ied_folders(tmp_path: Path) -> None:
    project_dir = tmp_path / "SE-LAGOS"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    _write_ge_sample(project_dir)

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.TAF,
        project_type=GE_MULTILIN_PROJECT_TYPE,
    )

    assert [result.status for result in results] == ["stored"]
    [zip_path] = list(atu.glob("*.zip"))
    assert zip_path.name == (
        "GE-MULTILIN-V8.60_SE-LAGOS_20260721-1000_COLABORADOR-EXEMPLO_TAF.zip"
    )
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        assert BACKUP_INFO_FILENAME in names
        assert "SE-LAGOS - Enervista UR Environment.ENV" in names
        assert "IED-A/IED-A.urs" in names
        assert "IED-B/IED-B.urs" in names
        assert "IED-B/IED-B.cid" in names
        assert "IED-B/IED-B.icd" in names
        assert "RDPC1/RDPC1.cfg" not in names
        assert "SW1" not in names

        backup_info = archive.read(BACKUP_INFO_FILENAME).decode("utf-8")
        assert "GE Multilin IED Summary:" in backup_info
        assert "ENV file: SE-LAGOS - Enervista UR Environment.ENV" in backup_info
        assert "Environment Version: 300" in backup_info
        assert "Application Version: 840" in backup_info
        assert "- IED-A" in backup_info
        assert "IED/application version: V8.40" in backup_info
        assert "- IED-B" in backup_info
        assert "Developed with: GE UR Setup V8.61" in backup_info
        assert "IED-B/IED-B.urs" in backup_info


def test_ge_multilin_backup_works_without_env_and_with_only_urs(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "SE-AAA"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    ied = project_dir / "IED-A"
    ied.mkdir(parents=True)
    urs = ied / "IED-A.urs"
    urs.write_text(
        "HEADER,GEMULTILIN,5,C60-UE3,840,,01/01/2026 10:00:00\n",
        encoding="utf-8",
    )
    _set_mtime(urs, datetime(2026, 1, 1, 10, 0))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
        project_type=GE_MULTILIN_PROJECT_TYPE,
    )

    assert [result.status for result in results] == ["stored"]
    [zip_path] = list(atu.glob("*.zip"))
    assert zip_path.name == "GE-MULTILIN-V8.40_SE-AAA_20260101-1000_COLABORADOR-EXEMPLO_DEV.zip"
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.namelist() == [BACKUP_INFO_FILENAME, "IED-A.urs"]
        backup_info = archive.read(BACKUP_INFO_FILENAME).decode("utf-8")
        assert "ENV file: not found" in backup_info


def _write_ge_sample(project_dir: Path) -> None:
    project_dir.mkdir(parents=True)
    env = project_dir / "SE-LAGOS - Enervista UR Environment.ENV"
    env.write_text(
        "Environment Version, 300\n"
        "Application Version, 840\n",
        encoding="utf-8",
    )
    _set_mtime(env, datetime(2026, 7, 20, 9, 0))

    ied_a = project_dir / "IED-A"
    ied_a.mkdir()
    ied_a_urs = ied_a / "IED-A.urs"
    ied_a_urs.write_text(
        "HEADER,GEMULTILIN,5,C60-UE3,840,,01/01/2026 10:00:00\n",
        encoding="utf-8",
    )
    _set_mtime(ied_a_urs, datetime(2026, 7, 20, 10, 0))

    ied_b = project_dir / "IED-B"
    ied_b.mkdir()
    ied_b_urs = ied_b / "IED-B.urs"
    ied_b_urs.write_text(
        "HEADER,GEMULTILIN,5,T60-UEM,860,,01/01/2026 11:00:00\n",
        encoding="utf-8",
    )
    _set_mtime(ied_b_urs, datetime(2026, 7, 21, 9, 0))
    cid = ied_b / "IED-B.cid"
    cid.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!--Created by GE Digital Energy UR Setup 8.61 on Mon Jul 21 10:00:00 2025-->\n"
        '<Header id="T60-UEM_8.60" version="0" revision="" toolID="ICDGenerator"/>',
        encoding="utf-8",
    )
    _set_mtime(cid, datetime(2026, 7, 21, 10, 0))
    icd = ied_b / "IED-B.icd"
    icd.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!--Created by GE Digital Energy UR Setup 8.50 on Thu Feb 22 16:56:00 2024-->\n"
        '<Header id="T60-UEM_8.40" version="0" revision="" toolID="ICDGenerator"/>',
        encoding="utf-8",
    )
    _set_mtime(icd, datetime(2026, 7, 21, 9, 30))

    rdpc = project_dir / "RDPC1"
    rdpc.mkdir()
    (rdpc / "RDPC1.cfg").write_text("config_version = 2\n", encoding="utf-8")
    (project_dir / "SW1").write_text("!version 6\n", encoding="utf-8")


def _set_mtime(path: Path, timestamp: datetime) -> None:
    seconds = timestamp.timestamp()
    os.utime(path, (seconds, seconds))
