"""High-level backup planning and execution service.

This module contains the project-type-agnostic business rules. Project-specific
logic, such as file extension and software/version extraction, is injected
through the `ProjectType` interface.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.core.naming import (
    BackupStage,
    build_backup_name,
    get_file_timestamp,
)
from src.core.project_types.base import ProjectType
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE
from src.core.storage import (
    BackupFileInfo,
    find_atu_duplicates,
    find_backup_by_identity,
    find_current_backup,
    fix_atu_duplicates,
    parse_backup_filename,
    update_storage,
)
from src.core.zipper import create_backup_zip

STATUS_STORED = "stored"
STATUS_REPLACED_CURRENT = "replaced_current"
STATUS_ARCHIVED_HISTORY = "archived_history"
STATUS_ATU_DUPLICATE = "atu_duplicate"
STATUS_SKIPPED_OLDER = "skipped_older"
STATUS_ALREADY_CURRENT = "already_current"
StageValue = BackupStage | str


@dataclass(frozen=True)
class BackupResult:
    """Result of an executed backup operation."""

    source_file: Path
    backup_name: str
    final_path: Path
    status: str = STATUS_STORED


@dataclass(frozen=True)
class BackupPlan:
    """Dry-run description of what will happen to a project file."""

    source_file: Path
    backup_name: str
    destination_path: Path
    status: str
    software: str
    project: str
    timestamp_text: str
    collaborator: str
    stage: str
    project_type_key: str
    project_type_label: str
    current_backup: Path | None = None
    history_path: Path | None = None


@dataclass(frozen=True)
class BackupSummary:
    """Aggregated counters used by the CLI, GUI, and final dialogs."""

    total: int
    stored: int
    replaced_current: int
    archived_history: int
    atu_duplicates: int
    skipped_older: int
    already_current: int


def summarize_results(
    results: list[BackupResult] | list[BackupPlan] | list[AtuDuplicatePlan],
) -> BackupSummary:
    """Count result statuses in a presentation-friendly structure."""

    statuses = [result.status for result in results]
    return BackupSummary(
        total=len(results),
        stored=statuses.count(STATUS_STORED),
        replaced_current=statuses.count(STATUS_REPLACED_CURRENT),
        archived_history=statuses.count(STATUS_ARCHIVED_HISTORY),
        atu_duplicates=statuses.count(STATUS_ATU_DUPLICATE),
        skipped_older=statuses.count(STATUS_SKIPPED_OLDER),
        already_current=statuses.count(STATUS_ALREADY_CURRENT),
    )


@dataclass(frozen=True)
class AtuDuplicatePlan:
    """Dry-run description of an ATU duplicate correction."""

    source_file: Path
    backup_name: str
    destination_path: Path
    status: str
    key: str
    keep_file: Path


def process_latest_backup(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
) -> BackupResult:
    """Process only the newest file for the selected project type."""

    return process_backup_file(
        project_file=project_type.find_latest_file(project_dir),
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
    )


def process_all_backups(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
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
        virtual_current=virtual_current,
    ):
        if plan.status in {STATUS_SKIPPED_OLDER, STATUS_ALREADY_CURRENT}:
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=plan.destination_path,
                    status=plan.status,
                )
            )
            continue

        if plan.status == STATUS_ARCHIVED_HISTORY:
            final_path = archive_history_backup(
                project_file=plan.source_file,
                backup_name=plan.backup_name,
                his_path=his_path,
            )
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=final_path,
                    status=plan.status,
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
        )
        results.append(
            BackupResult(
                source_file=result.source_file,
                backup_name=result.backup_name,
                final_path=result.final_path,
                status=plan.status,
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
) -> list[BackupResult]:
    """Execute a previously computed list of plans."""

    results = []
    for plan in plans:
        if plan.status in {STATUS_SKIPPED_OLDER, STATUS_ALREADY_CURRENT}:
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=plan.destination_path,
                    status=plan.status,
                )
            )
            continue

        if plan.status == STATUS_ARCHIVED_HISTORY:
            final_path = archive_history_backup(
                project_file=plan.source_file,
                backup_name=plan.backup_name,
                his_path=his_path,
            )
            results.append(
                BackupResult(
                    source_file=plan.source_file,
                    backup_name=plan.backup_name,
                    final_path=final_path,
                    status=plan.status,
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
        )
        results.append(
            BackupResult(
                source_file=result.source_file,
                backup_name=result.backup_name,
                final_path=result.final_path,
                status=plan.status,
            )
        )
    return results


def plan_atu_duplicate_fixes(*, atu_path: Path, his_path: Path) -> list[AtuDuplicatePlan]:
    """Describe ATU duplicate corrections without moving files."""

    return [
        AtuDuplicatePlan(
            source_file=duplicate.duplicate.path,
            backup_name=duplicate.duplicate.path.name,
            destination_path=duplicate.history_path,
            status=STATUS_ATU_DUPLICATE,
            key=duplicate.key,
            keep_file=duplicate.keep.path,
        )
        for duplicate in find_atu_duplicates(atu_path, his_path)
    ]


def fix_atu_duplicate_backups(*, atu_path: Path, his_path: Path) -> list[AtuDuplicatePlan]:
    """Move older duplicate ATU files to HIS and return the planned actions."""

    plans = plan_atu_duplicate_fixes(atu_path=atu_path, his_path=his_path)
    fix_atu_duplicates(atu_path, his_path)
    return plans


def plan_latest_backup(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
) -> BackupPlan:
    """Plan only the newest file for the selected project type."""

    return plan_backup_file(
        project_file=project_type.find_latest_file(project_dir),
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
    )


def plan_all_backups(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    virtual_current: dict[str, Path] | None = None,
) -> list[BackupPlan]:
    """Build an ordered plan for every supported project file."""

    plans = []
    current_by_key = virtual_current if virtual_current is not None else {}
    for project_file in project_type.find_files(project_dir):
        plan = plan_backup_file(
            project_file=project_file,
            atu_path=atu_path,
            his_path=his_path,
            collaborator=collaborator,
            stage=stage,
            project_type=project_type,
            current_override=current_by_key,
        )
        plans.append(plan)

        planned_info = parse_backup_filename(Path(plan.backup_name))
        if plan.status in {STATUS_STORED, STATUS_REPLACED_CURRENT, STATUS_ALREADY_CURRENT}:
            current_by_key[planned_info.key] = plan.destination_path

    return plans


def filter_current_and_newer_plans(plans: list[BackupPlan]) -> list[BackupPlan]:
    """Keep only the current backup and newer files from a full chronological plan."""

    return [
        plan
        for plan in plans
        if plan.status
        in {
            STATUS_ALREADY_CURRENT,
            STATUS_STORED,
            STATUS_REPLACED_CURRENT,
        }
    ]


def process_backup_file(
    *,
    project_file: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
) -> BackupResult:
    """Create a staged zip and move it into ATU/HIS using the storage rules."""

    plan = plan_backup_file(
        project_file=project_file,
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
    )

    with tempfile.TemporaryDirectory(prefix="ied-backup-") as staging:
        staged_zip = create_backup_zip(project_file, plan.backup_name, output_dir=Path(staging))
        final_path = update_storage(
            new_backup=staged_zip,
            atu_path=atu_path,
            his_path=his_path,
        )

    return BackupResult(
        source_file=project_file,
        backup_name=plan.backup_name,
        final_path=final_path,
        status=plan.status,
    )


def plan_backup_file(
    *,
    project_file: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    current_override: dict[str, Path] | None = None,
) -> BackupPlan:
    """Plan how a single project file should interact with ATU and HIS."""

    backup_name = build_project_backup_name(
        project_file=project_file,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
    )
    planned_info = parse_backup_filename(Path(backup_name))
    current = _find_current_for_plan(
        atu_path=atu_path,
        planned_key=planned_info.key,
        current_override=current_override,
    )
    destination = atu_path / backup_name

    if current and current.timestamp > planned_info.timestamp:
        history_path = find_backup_by_identity(his_path, planned_info.identity)
        if history_path is None:
            # Older files missing from HIS are archived without touching ATU.
            history_path = his_path / backup_name
            return BackupPlan(
                source_file=project_file,
                backup_name=backup_name,
                destination_path=history_path,
                status=STATUS_ARCHIVED_HISTORY,
                software=planned_info.software,
                project=planned_info.project,
                timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
                collaborator=planned_info.collaborator,
                stage=planned_info.stage,
                project_type_key=project_type.key,
                project_type_label=project_type.label,
                current_backup=current.path,
                history_path=history_path,
            )

        return BackupPlan(
            source_file=project_file,
            backup_name=backup_name,
            destination_path=current.path,
            status=STATUS_SKIPPED_OLDER,
            software=planned_info.software,
            project=planned_info.project,
            timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_key=project_type.key,
            project_type_label=project_type.label,
            current_backup=current.path,
        )

    if current and current.identity == planned_info.identity:
        # Collaborator/stage differences do not create a new technical backup.
        return BackupPlan(
            source_file=project_file,
            backup_name=backup_name,
            destination_path=current.path,
            status=STATUS_ALREADY_CURRENT,
            software=planned_info.software,
            project=planned_info.project,
            timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_key=project_type.key,
            project_type_label=project_type.label,
            current_backup=current.path,
        )

    if current:
        # A newer file replaces the current ATU backup and sends the old one to HIS.
        return BackupPlan(
            source_file=project_file,
            backup_name=backup_name,
            destination_path=destination,
            status=STATUS_REPLACED_CURRENT,
            software=planned_info.software,
            project=planned_info.project,
            timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_key=project_type.key,
            project_type_label=project_type.label,
            current_backup=current.path,
            history_path=his_path / current.path.name,
        )

    return BackupPlan(
        source_file=project_file,
        backup_name=backup_name,
        destination_path=destination,
        status=STATUS_STORED,
        software=planned_info.software,
        project=planned_info.project,
        timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
        collaborator=planned_info.collaborator,
        stage=planned_info.stage,
        project_type_key=project_type.key,
        project_type_label=project_type.label,
    )


def archive_history_backup(*, project_file: Path, backup_name: str, his_path: Path) -> Path:
    """Create a missing historical backup directly in HIS."""

    his_path.mkdir(parents=True, exist_ok=True)
    planned_info = parse_backup_filename(Path(backup_name))
    existing = find_backup_by_identity(his_path, planned_info.identity)
    if existing is not None:
        return existing
    destination = his_path / backup_name
    if destination.exists():
        return destination
    return create_backup_zip(project_file, backup_name, output_dir=his_path)


def _find_current_for_plan(
    *,
    atu_path: Path,
    planned_key: str,
    current_override: dict[str, Path] | None,
) -> BackupFileInfo | None:
    """Read the current backup from a virtual batch state or from ATU."""

    if current_override and planned_key in current_override:
        return parse_backup_filename(current_override[planned_key])
    return find_current_backup(atu_path, planned_key)


def build_project_backup_name(
    *,
    project_file: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
) -> str:
    """Build a backup filename using the selected project type adapter."""

    project_id = project_type.get_project_id(project_file)
    version = project_type.get_software_version(project_file)
    timestamp = get_file_timestamp(project_file)
    return build_backup_name(
        software_version=version,
        project_id=project_id,
        timestamp=timestamp,
        collaborator=collaborator,
        stage=stage,
    )
