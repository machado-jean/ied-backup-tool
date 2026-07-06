"""High-level backup planning and execution service.

This module contains the project-type-agnostic business rules. Project-specific
logic, such as file extension and software/version extraction, is injected
through the `ProjectType` interface.
"""

from __future__ import annotations

from pathlib import Path

from src.core.backup_duplicates import fix_atu_duplicate_backups, plan_atu_duplicate_fixes
from src.core.backup_executor import (
    BackupCanceledError,
    archive_history_backup,
    execute_backup_plan,
)
from src.core.backup_models import (
    STATUS_ALREADY_CURRENT,
    STATUS_ARCHIVED_HISTORY,
    STATUS_ATU_DUPLICATE,
    STATUS_REPLACED_CURRENT,
    STATUS_SHA_CONFLICT,
    STATUS_SKIPPED_OLDER,
    STATUS_STORED,
    AtuDuplicatePlan,
    BackupPlan,
    BackupResult,
    BackupStatus,
    BackupSummary,
    summarize_results,
)
from src.core.backup_planner import (
    StageValue,
    build_project_backup_name,
    filter_current_and_newer_plans,
    plan_all_backups,
    plan_backup_file,
    plan_grouped_backups,
    plan_latest_backup,
)
from src.core.progress import CancellationCallback, ProgressCallback
from src.core.project_types.base import ProjectType
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE

__all__ = [
    "STATUS_ALREADY_CURRENT",
    "STATUS_ARCHIVED_HISTORY",
    "STATUS_ATU_DUPLICATE",
    "STATUS_REPLACED_CURRENT",
    "STATUS_SHA_CONFLICT",
    "STATUS_SKIPPED_OLDER",
    "STATUS_STORED",
    "AtuDuplicatePlan",
    "BackupCanceledError",
    "BackupPlan",
    "BackupResult",
    "BackupSummary",
    "BackupStatus",
    "archive_history_backup",
    "build_project_backup_name",
    "execute_backup_plan",
    "filter_current_and_newer_plans",
    "fix_atu_duplicate_backups",
    "plan_all_backups",
    "plan_atu_duplicate_fixes",
    "plan_backup_file",
    "plan_grouped_backups",
    "plan_latest_backup",
    "process_all_backups",
    "process_backup_file",
    "process_backup_plans",
    "process_latest_backup",
    "summarize_results",
]


def process_latest_backup(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    software_version_override: str | None = None,
) -> BackupResult:
    """Process only the newest file for the selected project type."""

    return process_backup_file(
        project_file=project_type.find_latest_file(project_dir),
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
        software_version_override=software_version_override,
    )


def process_all_backups(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    software_version_override: str | None = None,
) -> list[BackupResult]:
    """Plan and process all supported files in chronological order."""

    results = []
    virtual_current: dict[str, Path] = {}
    for plan in plan_all_backups(
        project_dir=project_dir,
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
        software_version_override=software_version_override,
        virtual_current=virtual_current,
    ):
        if plan.status in {STATUS_SKIPPED_OLDER, STATUS_ALREADY_CURRENT, STATUS_SHA_CONFLICT}:
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=plan.destination_path,
                    status=plan.status,
                    source_files=plan.source_files,
                )
            )
            continue

        if plan.status == STATUS_ARCHIVED_HISTORY:
            final_path = archive_history_backup(
                project_file=plan.source_file,
                backup_name=plan.backup_name,
                his_path=his_path,
                project_type=project_type,
                source_files=plan.source_files,
                backup_info_text=plan.backup_info_text,
            )
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=final_path,
                    status=plan.status,
                    source_files=plan.source_files,
                )
            )
            continue

        result = process_backup_file(
            project_file=plan.source_file,
            atu_path=atu_path,
            his_path=his_path,
            collaborator=collaborator,
            stage=stage,
            project_type=project_type,
            software_version_override=software_version_override,
        )
        results.append(
            BackupResult(
                source_file=result.source_file,
                backup_name=result.backup_name,
                final_path=result.final_path,
                status=plan.status,
                source_files=result.source_files,
            )
        )
    return results


def process_backup_plans(
    *,
    plans: list[BackupPlan],
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    software_version_override: str | None = None,
) -> list[BackupResult]:
    """Execute a previously computed list of plans."""

    results = []
    for plan in plans:
        if plan.status in {STATUS_SKIPPED_OLDER, STATUS_ALREADY_CURRENT, STATUS_SHA_CONFLICT}:
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=plan.destination_path,
                    status=plan.status,
                    source_files=plan.source_files,
                )
            )
            continue

        if plan.status == STATUS_ARCHIVED_HISTORY:
            final_path = archive_history_backup(
                project_file=plan.source_file,
                backup_name=plan.backup_name,
                his_path=his_path,
                project_type=project_type,
                source_files=plan.source_files,
                backup_info_text=plan.backup_info_text,
            )
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=final_path,
                    status=plan.status,
                    source_files=plan.source_files,
                )
            )
            continue

        result = process_backup_file(
            project_file=plan.source_file,
            atu_path=atu_path,
            his_path=his_path,
            collaborator=collaborator,
            stage=stage,
            project_type=project_type,
            software_version_override=software_version_override,
        )
        results.append(
            BackupResult(
                source_file=result.source_file,
                backup_name=result.backup_name,
                final_path=result.final_path,
                status=plan.status,
                source_files=result.source_files,
            )
        )
    return results


def process_backup_file(
    *,
    project_file: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    software_version_override: str | None = None,
    progress_callback: ProgressCallback | None = None,
    cancellation_callback: CancellationCallback | None = None,
) -> BackupResult:
    """Create a staged zip and move it into ATU/HIS using the storage rules."""

    plan = plan_backup_file(
        project_file=project_file,
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
        software_version_override=software_version_override,
    )
    return execute_backup_plan(
        plan=plan,
        atu_path=atu_path,
        his_path=his_path,
        progress_callback=progress_callback,
        cancellation_callback=cancellation_callback,
    )



