from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from src.core.backup_service import (
    filter_current_and_newer_plans,
    fix_atu_duplicate_backups,
    plan_all_backups,
    plan_atu_duplicate_fixes,
    process_all_backups,
    summarize_results,
)
from src.core.naming import BackupStage


def test_process_all_backups_versions_atu_and_his(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    first = create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    second = create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    third = create_dz5(project_dir / "SE-GVM_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )

    assert [result.source_file for result in results] == [first, second, third]
    assert [path.name for path in atu.glob("*.zip")] == [
        "DIGSI-V100_SE-GVM_20260525-1809_JEAN-CARLOS-MACHADO_DEV.zip"
    ]
    assert sorted(path.name for path in his.glob("*.zip")) == [
        "DIGSI-V100_SE-GVM_20260525-1218_JEAN-CARLOS-MACHADO_DEV.zip",
        "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_DEV.zip",
    ]
    assert first.exists()
    assert second.exists()
    assert third.exists()


def test_process_all_backups_skips_older_files_when_atu_has_newest(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-GVM_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))

    process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )
    second_run = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
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

    create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-GVM_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))
    current = atu / "DIGSI-V100_SE-GVM_20260525-1809_JEAN-CARLOS-MACHADO_DEV.zip"
    current.write_text("current", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )

    assert [result.status for result in results] == [
        "archived_history",
        "archived_history",
        "already_current",
    ]
    assert [path.name for path in atu.glob("*.zip")] == [current.name]
    assert sorted(path.name for path in his.glob("*.zip")) == [
        "DIGSI-V100_SE-GVM_20260525-1218_JEAN-CARLOS-MACHADO_DEV.zip",
        "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_DEV.zip",
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

    create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    current = atu / "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_TAC.zip"
    current.write_text("current", encoding="utf-8")
    existing_history = his / "DIGSI-V100_SE-GVM_20260525-1218_OUTRO-COLABORADOR_DEV.zip"
    existing_history.write_text("history", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
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

    create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    current = atu / "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_DEV.zip"
    current.write_text("current", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.TAC,
    )

    assert [result.status for result in results] == ["already_current"]
    assert [path.name for path in atu.glob("*.zip")] == [current.name]
    assert not his.exists()


def test_process_all_backups_allows_newer_backup_with_any_stage(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()

    create_dz5(project_dir / "SE-GVM_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))
    current = atu / "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_POS-TAC.zip"
    current.write_text("current", encoding="utf-8")

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )

    assert [result.status for result in results] == ["replaced_current"]
    assert (his / current.name).exists()
    assert [path.name for path in atu.glob("*.zip")] == [
        "DIGSI-V100_SE-GVM_20260525-1809_JEAN-CARLOS-MACHADO_DEV.zip"
    ]


def test_plan_and_fix_atu_duplicate_backups(tmp_path: Path) -> None:
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    atu.mkdir()
    older = atu / "DIGSI-V100_SE-GVM_20260525-1218_JEAN-CARLOS-MACHADO_DEV.zip"
    newer = atu / "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_DEV.zip"
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

    create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-CTU_20260526_1133.dz5", datetime(2026, 5, 26, 11, 33))
    create_dz5(project_dir / "SE-CTU_20260526_1512.dz5", datetime(2026, 5, 26, 15, 12))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )

    assert summarize_results(results).replaced_current == 2
    assert sorted(path.name for path in atu.glob("*.zip")) == [
        "DIGSI-V100_SE-CTU_20260526-1512_JEAN-CARLOS-MACHADO_DEV.zip",
        "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_DEV.zip",
    ]
    assert sorted(path.name for path in his.glob("*.zip")) == [
        "DIGSI-V100_SE-CTU_20260526-1133_JEAN-CARLOS-MACHADO_DEV.zip",
        "DIGSI-V100_SE-GVM_20260525-1218_JEAN-CARLOS-MACHADO_DEV.zip",
    ]


def test_filter_current_and_newer_plans_omits_previous_history(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    atu.mkdir()

    create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))
    create_dz5(project_dir / "SE-GVM_20260525_1809.dz5", datetime(2026, 5, 25, 18, 9))
    current = atu / "DIGSI-V100_SE-GVM_20260525-1719_JEAN-CARLOS-MACHADO_DEV.zip"
    current.write_text("current", encoding="utf-8")

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )
    filtered = filter_current_and_newer_plans(plans)

    assert [plan.source_file.name for plan in filtered] == [
        "SE-GVM_20260525_1719.dz5",
        "SE-GVM_20260525_1809.dz5",
    ]
    assert [plan.status for plan in filtered] == ["already_current", "replaced_current"]


def test_plan_all_backups_does_not_create_atu_or_his(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()

    create_dz5(project_dir / "SE-GVM_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))
    create_dz5(project_dir / "SE-GVM_20260525_1719.dz5", datetime(2026, 5, 25, 17, 19))

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.DEV,
    )

    assert [plan.status for plan in plans] == ["stored", "replaced_current"]
    assert plans[1].history_path == his / plans[0].backup_name
    assert not atu.exists()
    assert not his.exists()


def create_dz5(path: Path, mtime: datetime) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr(f"{path.stem}.dp5v100", "DIGSI project")
    timestamp = mtime.timestamp()
    os.utime(path, (timestamp, timestamp))
    return path
