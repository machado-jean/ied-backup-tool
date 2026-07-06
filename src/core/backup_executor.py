"""Execution helpers for already planned backup operations."""

from __future__ import annotations

import tempfile
from pathlib import Path

from src.core.backup_metadata import build_backup_info_text
from src.core.backup_models import (
    STATUS_ALREADY_CURRENT,
    STATUS_ARCHIVED_HISTORY,
    STATUS_SHA_CONFLICT,
    STATUS_SKIPPED_OLDER,
    BackupPlan,
    BackupResult,
)
from src.core.progress import CancellationCallback, ProgressCallback
from src.core.project_types.base import ProjectType
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE
from src.core.storage import (
    find_backup_by_identity,
    parse_backup_filename,
    place_staged_backup,
    update_storage,
)
from src.core.zipper import create_backup_zip


class BackupCanceledError(RuntimeError):
    """Raised when execution is canceled before publishing a staged backup."""


def execute_backup_plan(
    *,
    plan: BackupPlan,
    atu_path: Path,
    his_path: Path,
    progress_callback: ProgressCallback | None = None,
    cancellation_callback: CancellationCallback | None = None,
) -> BackupResult:
    """Execute a previously computed plan without recalculating its metadata."""

    if plan.status in {STATUS_SKIPPED_OLDER, STATUS_ALREADY_CURRENT, STATUS_SHA_CONFLICT}:
        return BackupResult(
            source_file=plan.source_file,
            backup_name=plan.backup_name,
            final_path=plan.destination_path,
            status=plan.status,
            source_files=plan.source_files,
        )

    if plan.status == STATUS_ARCHIVED_HISTORY:
        final_path = archive_history_backup(
            project_file=plan.source_file,
            backup_name=plan.backup_name,
            his_path=his_path,
            source_files=plan.source_files,
            backup_info_text=plan.backup_info_text,
            progress_callback=progress_callback,
            cancellation_callback=cancellation_callback,
        )
        return BackupResult(
            source_file=plan.source_file,
            backup_name=plan.backup_name,
            final_path=final_path,
            status=plan.status,
            source_files=plan.source_files,
        )

    with tempfile.TemporaryDirectory(prefix="ied-backup-") as staging:
        staged_zip = create_backup_zip(
            plan.source_files or (plan.source_file,),
            plan.backup_name,
            output_dir=Path(staging),
            backup_info_text=plan.backup_info_text,
            progress_callback=progress_callback,
        )
        _raise_if_canceled(cancellation_callback)
        final_path = update_storage(
            new_backup=staged_zip,
            atu_path=atu_path,
            his_path=his_path,
            progress_callback=progress_callback,
        )

    return BackupResult(
        source_file=plan.source_file,
        backup_name=plan.backup_name,
        final_path=final_path,
        status=plan.status,
        source_files=plan.source_files,
    )


def archive_history_backup(
    *,
    project_file: Path,
    backup_name: str,
    his_path: Path,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    source_files: tuple[Path, ...] | None = None,
    backup_info_text: str | None = None,
    progress_callback: ProgressCallback | None = None,
    cancellation_callback: CancellationCallback | None = None,
) -> Path:
    """Create a missing historical backup directly in HIS."""

    his_path.mkdir(parents=True, exist_ok=True)
    planned_info = parse_backup_filename(Path(backup_name))
    existing = find_backup_by_identity(his_path, planned_info.identity)
    if existing is not None:
        return existing
    destination = his_path / backup_name
    if destination.exists():
        return destination
    files_to_zip = source_files or tuple(project_type.get_related_files(project_file))
    if backup_info_text is None:
        backup_info_text = build_backup_info_text(
            backup_name=backup_name,
            project=planned_info.project,
            software=planned_info.software,
            timestamp=planned_info.timestamp,
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_label=project_type.label,
            source_file=project_file,
            source_files=list(files_to_zip),
            detected_versions=None,
        )
    with tempfile.TemporaryDirectory(prefix="ied-backup-history-") as staging:
        staged_zip = create_backup_zip(
            files_to_zip,
            backup_name,
            output_dir=Path(staging),
            backup_info_text=backup_info_text,
            progress_callback=progress_callback,
        )
        _raise_if_canceled(cancellation_callback)
        return place_staged_backup(
            staged_zip,
            destination,
            progress_callback=progress_callback,
        )


def _raise_if_canceled(cancellation_callback: CancellationCallback | None) -> None:
    """Stop after staging ZIP creation and before publishing to ATU/HIS."""

    if cancellation_callback and cancellation_callback():
        raise BackupCanceledError("Backup cancelado antes da copia final.")
