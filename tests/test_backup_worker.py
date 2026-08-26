from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from src.core.backup_service import plan_all_backups
from src.core.naming import BackupStage
from src.gui.backup_worker import BackupExecutionWorker


def test_backup_worker_cancels_before_first_file(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR EXEMPLO",
        stage=BackupStage.DEV,
    )
    finished = []
    worker = BackupExecutionWorker(
        plans=plans,
        atu_duplicate_plans=[],
        atu_path=atu,
        his_path=his,
        fix_duplicates=False,
    )
    worker.finished.connect(lambda duplicates, results, canceled: finished.append(canceled))

    worker.request_cancel()
    worker.run()

    assert finished == [True]
    assert not atu.exists()
    assert not his.exists()


def test_backup_worker_cancel_during_zip_does_not_publish_backup(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    create_dz5(project_dir / "SE-AAA_20260525_1218.dz5", datetime(2026, 5, 25, 12, 18))

    plans = plan_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="COLABORADOR EXEMPLO",
        stage=BackupStage.DEV,
    )
    finished = []
    progress_events = []
    worker = BackupExecutionWorker(
        plans=plans,
        atu_duplicate_plans=[],
        atu_path=atu,
        his_path=his,
        fix_duplicates=False,
    )
    worker.finished.connect(
        lambda duplicates, results, canceled: finished.append((len(results), canceled))
    )

    def cancel_during_zip(event) -> None:
        progress_events.append(event.phase)
        if event.phase == "zip":
            worker.request_cancel()

    worker.progress.connect(cancel_during_zip)

    worker.run()

    assert "zip" in progress_events
    assert finished == [(0, True)]
    assert not atu.exists()
    assert not his.exists()


def create_dz5(path: Path, mtime: datetime) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr(f"{path.stem}.dp5v100", "DIGSI project")
    timestamp = mtime.timestamp()
    os.utime(path, (timestamp, timestamp))
    return path
