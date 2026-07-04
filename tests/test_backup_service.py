from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from src.core.backup_service import (
    execute_backup_plan,
    filter_current_and_newer_plans,
    fix_atu_duplicate_backups,
    plan_all_backups,
    plan_atu_duplicate_fixes,
    plan_grouped_backups,
    process_all_backups,
    summarize_results,
)
from src.core.naming import BackupStage
from src.core.project_types.registry import get_project_type
from src.core.zipper import BACKUP_INFO_FILENAME


def test_process_all_backups_versions_atu_and_his(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    first = create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    second = create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    third = create_dz5(project_dir / "SE-AAA_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert [result.source_file for result in results] == [first, second, third]
    assert [path.name for path in atu.glob("*.zip")] == [
        "DIGSI5-V10.00_SE-AAA_20260525-1809_COLABORADOR-EXEMPLO_DEV.zip"
    ]
    assert sorted(path.name for path in his.glob("*.zip")) == [
        "DIGSI5-V10.00_SE-AAA_20260525-1218_COLABORADOR-EXEMPLO_DEV.zip",
        "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_DEV.zip",
    ]
    assert first.exists()
    assert second.exists()
    assert third.exists()
    [current_backup] = list(atu.glob("*.zip"))
    with ZipFile(current_backup) as archive:
        assert BACKUP_INFO_FILENAME in archive.namelist()
        backup_info = archive.read(BACKUP_INFO_FILENAME).decode("utf-8")
        assert "IED Backup Manager - Backup Information" in backup_info
        assert "Software: DIGSI5-V10.00" in backup_info
        assert "Project: SE-AAA" in backup_info
        assert "Size:" in backup_info
        assert "SHA256:" in backup_info


def test_process_all_backups_skips_older_files_when_atu_has_newest(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-AAA_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))

    process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )
    second_run = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert [result.status for result in second_run] == [
        "skipped_older",
        "skipped_older",
        "already_current",
    ]
    assert len(list(atu.glob("*.zip"))) == 1
    assert len(list(his.glob("*.zip"))) == 2


def test_process_all_backups_archives_missing_history_when_atu_has_newest(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-AAA_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))
    current = atu / "DIGSI5-V10.00_SE-AAA_20260525-1809_COLABORADOR-EXEMPLO_DEV.zip"
    current.write_text("current", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert [result.status for result in results] == [
        "archived_history",
        "archived_history",
        "already_current",
    ]
    assert [path.name for path in atu.glob("*.zip")] == [current.name]
    assert sorted(path.name for path in his.glob("*.zip")) == [
        "DIGSI5-V10.00_SE-AAA_20260525-1218_COLABORADOR-EXEMPLO_DEV.zip",
        "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_DEV.zip",
    ]


def test_process_all_backups_does_not_archive_when_same_identity_exists_in_his(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()
    his.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    current = atu / "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_TAC.zip"
    current.write_text("current", encoding="utf-8")
    existing_history = his / "DIGSI5-V10.00_SE-AAA_20260525-1218_OUTRO-COLABORADOR_DEV.zip"
    existing_history.write_text("history", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.TAC,
    )

    assert [result.status for result in results] == ["skipped_older"]
    assert len(list(his.glob("*.zip"))) == 1
    assert existing_history.read_text(encoding="utf-8") == "history"


def test_process_all_backups_treats_same_identity_in_atu_as_current(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    current = atu / "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_DEV.zip"
    current.write_text("current", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.TAC,
    )

    assert [result.status for result in results] == ["already_current"]
    assert [path.name for path in atu.glob("*.zip")] == [current.name]
    assert not his.exists()


def test_plan_all_backups_flags_same_identity_with_different_sha(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    timestamp = datetime(2026, 5, 25, 17, 19)
    source = create_dz5_with_content(
        project_dir / "SE-AAA_20260525_1719.dz5",
        timestamp,
        "original content",
    )

    process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )
    current_backup = next(atu.glob("*.zip"))
    create_dz5_with_content(source, timestamp, "changed content")

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="OUTRO-COLABORADOR",
        stage=BackupStage.TAF,
    )
    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="OUTRO-COLABORADOR",
        stage=BackupStage.TAF,
    )

    assert [plan.status for plan in plans] == ["sha_conflict"]
    assert plans[0].destination_path == current_backup
    assert summarize_results(plans).sha_conflicts == 1
    assert [result.status for result in results] == ["sha_conflict"]
    assert [path.name for path in atu.glob("*.zip")] == [current_backup.name]
    assert not list(his.glob("*.zip"))


def test_plan_all_backups_flags_same_identity_history_with_different_sha(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    timestamp = datetime(2026, 5, 25, 17, 19)
    source = create_dz5_with_content(
        project_dir / "SE-AAA_20260525_1719.dz5",
        timestamp,
        "original content",
    )

    process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )
    current_backup = next(atu.glob("*.zip"))
    his.mkdir(exist_ok=True)
    history_backup = his / current_backup.name
    current_backup.replace(history_backup)
    create_dz5_with_content(source, timestamp, "changed content")

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert [plan.status for plan in plans] == ["sha_conflict"]
    assert plans[0].destination_path == history_backup
    assert not list(atu.glob("*.zip"))


def test_process_all_backups_allows_newer_backup_with_any_stage(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))
    current = atu / "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_POS-TAC.zip"
    current.write_text("current", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert [result.status for result in results] == ["replaced_current"]
    assert (his / current.name).exists()
    assert [path.name for path in atu.glob("*.zip")] == [
        "DIGSI5-V10.00_SE-AAA_20260525-1809_COLABORADOR-EXEMPLO_DEV.zip"
    ]


def test_plan_and_fix_atu_duplicate_backups(tmp_path: Path) -> None:
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    atu.mkdir()
    older = atu / "DIGSI5-V10.00_SE-AAA_20260525-1218_COLABORADOR-EXEMPLO_DEV.zip"
    newer = atu / "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_DEV.zip"
    older.write_text("older", encoding="utf-8")
    newer.write_text("newer", encoding="utf-8")

    plans = plan_atu_duplicate_fixes(atu_path=atu, his_path=his)

    assert len(plans) == 1
    assert plans[0].source_file == older
    assert plans[0].keep_file == newer
    assert plans[0].destination_path == his / older.name
    assert summarize_results(plans).atu_duplicates == 1

    fixed = fix_atu_duplicate_backups(atu_path=atu, his_path=his)

    assert len(fixed) == 1
    assert not older.exists()
    assert newer.exists()
    assert (his / older.name).read_text(encoding="utf-8") == "older"


def test_process_all_backups_keeps_one_current_per_project(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-BBB_20260526_1133.dz5", datetime(2026, 5, 26, 11, 33))
    create_dz5(project_dir / "SE-BBB_20260526_1512.dz5", datetime(2026, 5, 26, 15, 12))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert summarize_results(results).replaced_current == 2
    assert sorted(path.name for path in atu.glob("*.zip")) == [
        "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_DEV.zip",
        "DIGSI5-V10.00_SE-BBB_20260526-1512_COLABORADOR-EXEMPLO_DEV.zip",
    ]
    assert sorted(path.name for path in his.glob("*.zip")) == [
        "DIGSI5-V10.00_SE-AAA_20260525-1218_COLABORADOR-EXEMPLO_DEV.zip",
        "DIGSI5-V10.00_SE-BBB_20260526-1133_COLABORADOR-EXEMPLO_DEV.zip",
    ]


def test_filter_current_and_newer_plans_omits_previous_history(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-AAA_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))
    current = atu / "DIGSI5-V10.00_SE-AAA_20260525-1719_COLABORADOR-EXEMPLO_DEV.zip"
    current.write_text("current", encoding="utf-8")

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )
    filtered = filter_current_and_newer_plans(plans)

    assert [plan.source_file.name for plan in filtered] == [
        "SE-AAA_20260525_1719.dz5",
        "SE-AAA_20260525_1809.dz5",
    ]
    assert [plan.status for plan in filtered] == ["already_current", "replaced_current"]


def test_plan_all_backups_does_not_create_atu_or_his(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-AAA_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
    )

    assert [plan.status for plan in plans] == ["stored", "replaced_current"]
    assert plans[1].history_path == his / plans[0].backup_name
    assert not atu.exists()
    assert not his.exists()


def test_grouped_backups_package_selected_types_by_substation(tmp_path: Path) -> None:
    project_dir = tmp_path / "IED-DES"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    timestamp = datetime(2026, 6, 19, 12, 30)

    create_dz5(project_dir / "SE-AAA_20260619_1200.dz5", datetime(2026, 6, 19, 12, 0))
    dz5 = create_dz5(project_dir / "SE-AAA_20260619_1230.dz5", timestamp)
    rdb = project_dir / "SE-AAA.rdb"
    scd = project_dir / "SE-AAA.scd"
    rdb.write_text("Saved with Main Shell Version: 7.5.3.10", encoding="utf-8")
    scd.write_text(
        '<Header id="ESD_AAA" version="388" revision="1.0" '
        'toolID="AcSELerator Architect 2.4.2.34" />',
        encoding="utf-8",
    )
    os.utime(rdb, (timestamp.timestamp(), timestamp.timestamp()))
    os.utime(scd, (timestamp.timestamp(), timestamp.timestamp()))

    plans = plan_grouped_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.TAF,
        project_types=[get_project_type("digsi5"), get_project_type("sel")],
    )

    assert len(plans) == 1
    assert plans[0].backup_name == (
        "IED-PACK_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip"
    )
    assert plans[0].software == "DIGSI5-V10.00 + QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34"
    assert plans[0].source_files == (dz5, rdb, scd)

    result = execute_backup_plan(plan=plans[0], atu_path=atu, his_path=his)

    assert result.status == "stored"
    [zip_path] = list(atu.glob("*.zip"))
    with ZipFile(zip_path) as archive:
        assert archive.namelist() == [
            BACKUP_INFO_FILENAME,
            "SE-AAA_20260619_1230.dz5",
            "SE-AAA.rdb",
            "SE-AAA.scd",
        ]
        backup_info = archive.read(BACKUP_INFO_FILENAME).decode("utf-8")
        assert "IED Backup Manager - Backup Information" in backup_info
        assert "Software: DIGSI5-V10.00 + QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34" in backup_info
        assert "DIGSI 5 (.dz5): DIGSI5-V10.00 (SE-AAA_20260619_1230.dz5)" in backup_info
        assert "SEL (.rdb): QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34 (SE-AAA.rdb)" in backup_info
        assert "Size:" in backup_info
        assert "SHA256:" in backup_info
        assert "SE-AAA_20260619_1200.dz5" not in backup_info


def test_grouped_backups_uses_individual_name_when_only_one_type_exists(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "IED-DES"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    timestamp = datetime(2026, 6, 19, 12, 30)
    rdb = project_dir / "SE-AAA.rdb"
    rdb.write_text("Saved with Main Shell Version: 7.5.3.10", encoding="utf-8")
    os.utime(rdb, (timestamp.timestamp(), timestamp.timestamp()))

    plans = plan_grouped_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.TAF,
        project_types=[get_project_type("digsi5"), get_project_type("sel")],
    )

    assert len(plans) == 1
    assert plans[0].backup_name == (
        "QUICKSET-V7.5.3.10_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip"
    )
    assert plans[0].backup_info_text is not None
    assert "QUICKSET-V7.5.3.10" in plans[0].backup_info_text


def create_dz5(path: Path, mtime: datetime) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr(f"{path.stem}.dp5v100", "DIGSI project")
    timestamp = mtime.timestamp()
    os.utime(path, (timestamp, timestamp))
    return path


def create_dz5_with_content(path: Path, mtime: datetime, content: str) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr(f"{path.stem}.dp5v100", content)
    timestamp = mtime.timestamp()
    os.utime(path, (timestamp, timestamp))
    return path


