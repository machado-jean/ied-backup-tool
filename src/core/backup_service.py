"""High-level backup planning and execution service.

This module contains the project-type-agnostic business rules. Project-specific
logic, such as file extension and software/version extraction, is injected
through the `ProjectType` interface.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.core.hashing import calculate_sha256
from src.core.integrity import has_sha256_conflict
from src.core.naming import (
    BackupStage,
    build_backup_name,
    get_file_timestamp,
)
from src.core.project_types.base import ProjectDetectionError, ProjectType
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
STATUS_SHA_CONFLICT = "sha_conflict"
STATUS_SKIPPED_OLDER = "skipped_older"
STATUS_ALREADY_CURRENT = "already_current"
StageValue = BackupStage | str
GROUPED_PROJECT_TYPE_KEY = "ied-package"
GROUPED_PROJECT_TYPE_LABEL = "Pacote por SE"
GROUPED_SOFTWARE_PREFIX = "IED-PACK"


@dataclass(frozen=True)
class BackupResult:
    """Result of an executed backup operation."""

    source_file: Path
    backup_name: str
    final_path: Path
    status: str = STATUS_STORED
    source_files: tuple[Path, ...] = ()


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
    source_files: tuple[Path, ...] = ()
    backup_info_text: str | None = None


@dataclass(frozen=True)
class BackupSummary:
    """Aggregated counters used by the CLI, GUI, and final dialogs."""

    total: int
    stored: int
    replaced_current: int
    archived_history: int
    atu_duplicates: int
    sha_conflicts: int
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
        sha_conflicts=statuses.count(STATUS_SHA_CONFLICT),
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


def plan_grouped_backups(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_types: list[ProjectType],
    software_version_override: str | None = None,
    software_version_overrides: dict[str, str] | None = None,
    virtual_current: dict[str, Path] | None = None,
) -> list[BackupPlan]:
    """Build one backup package per substation using all selected project types."""

    grouped_sources: dict[str, list[tuple[ProjectType, Path, tuple[Path, ...], str]]] = {}
    for project_type in project_types:
        try:
            project_files = project_type.find_files(project_dir)
        except ProjectDetectionError:
            continue

        latest_by_project: dict[str, Path] = {}
        for project_file in project_files:
            project = project_type.get_project_id(project_file)
            current = latest_by_project.get(project)
            if current is None or get_file_timestamp(project_file) > get_file_timestamp(current):
                latest_by_project[project] = project_file

        for project, project_file in latest_by_project.items():
            version = project_type.get_software_version(
                project_file,
                _software_version_override_for(
                    project_type,
                    software_version_override,
                    software_version_overrides,
                ),
            )
            source_files = tuple(project_type.get_related_files(project_file))
            grouped_sources.setdefault(project, []).append(
                (project_type, project_file, source_files, version)
            )

    plans = []
    current_by_key = virtual_current if virtual_current is not None else {}
    for project, entries in sorted(grouped_sources.items()):
        if len(entries) == 1:
            project_type, project_file, _, _ = entries[0]
            plan = plan_backup_file(
                project_file=project_file,
                atu_path=atu_path,
                his_path=his_path,
                collaborator=collaborator,
                stage=stage,
                project_type=project_type,
                software_version_override=_software_version_override_for(
                    project_type,
                    software_version_override,
                    software_version_overrides,
                ),
                current_override=current_by_key,
            )
            plans.append(plan)
            planned_info = parse_backup_filename(Path(plan.backup_name))
            if plan.status in {STATUS_STORED, STATUS_REPLACED_CURRENT, STATUS_ALREADY_CURRENT}:
                current_by_key[planned_info.key] = plan.destination_path
            continue

        source_files = _unique_paths(path for _, _, files, _ in entries for path in files)
        primary_files = [project_file for _, project_file, _, _ in entries]
        versions = _unique_text(version for _, _, _, version in entries)
        timestamp = max(get_file_timestamp(path) for path in source_files)
        backup_name = build_backup_name(
            software_version=GROUPED_SOFTWARE_PREFIX,
            project_id=project,
            timestamp=timestamp,
            collaborator=collaborator,
            stage=stage,
        )
        plan = _plan_backup_name(
            source_file=max(primary_files, key=get_file_timestamp),
            source_files=tuple(source_files),
            backup_name=backup_name,
            atu_path=atu_path,
            his_path=his_path,
            current_override=current_by_key,
            software_display=" + ".join(versions),
            project_type_key=GROUPED_PROJECT_TYPE_KEY,
            project_type_label=GROUPED_PROJECT_TYPE_LABEL,
            detected_versions=[
                (project_type.label, version, project_file)
                for project_type, project_file, _, version in entries
            ],
        )
        plans.append(plan)

        planned_info = parse_backup_filename(Path(plan.backup_name))
        if plan.status in {STATUS_STORED, STATUS_REPLACED_CURRENT, STATUS_ALREADY_CURRENT}:
            current_by_key[planned_info.key] = plan.destination_path

    return sorted(plans, key=lambda plan: (plan.project, plan.timestamp_text))


def execute_backup_plan(*, plan: BackupPlan, atu_path: Path, his_path: Path) -> BackupResult:
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
        )
        final_path = update_storage(
            new_backup=staged_zip,
            atu_path=atu_path,
            his_path=his_path,
        )

    return BackupResult(
        source_file=plan.source_file,
        backup_name=plan.backup_name,
        final_path=final_path,
        status=plan.status,
        source_files=plan.source_files,
    )


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
    software_version_override: str | None = None,
) -> BackupPlan:
    """Plan only the newest file for the selected project type."""

    return plan_backup_file(
        project_file=project_type.find_latest_file(project_dir),
        atu_path=atu_path,
        his_path=his_path,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
        software_version_override=software_version_override,
    )


def plan_all_backups(
    *,
    project_dir: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    software_version_override: str | None = None,
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
            software_version_override=software_version_override,
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
            STATUS_SHA_CONFLICT,
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
    software_version_override: str | None = None,
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

    if plan.status in {STATUS_SKIPPED_OLDER, STATUS_ALREADY_CURRENT, STATUS_SHA_CONFLICT}:
        return BackupResult(
            source_file=project_file,
            backup_name=plan.backup_name,
            final_path=plan.destination_path,
            status=plan.status,
            source_files=plan.source_files,
        )

    with tempfile.TemporaryDirectory(prefix="ied-backup-") as staging:
        staged_zip = create_backup_zip(
            plan.source_files,
            plan.backup_name,
            output_dir=Path(staging),
            backup_info_text=plan.backup_info_text,
        )
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
        source_files=plan.source_files,
    )


def plan_backup_file(
    *,
    project_file: Path,
    atu_path: Path,
    his_path: Path,
    collaborator: str,
    stage: StageValue,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    software_version_override: str | None = None,
    current_override: dict[str, Path] | None = None,
) -> BackupPlan:
    """Plan how a single project file should interact with ATU and HIS."""

    backup_name = build_project_backup_name(
        project_file=project_file,
        collaborator=collaborator,
        stage=stage,
        project_type=project_type,
        software_version_override=software_version_override,
    )
    source_files = tuple(project_type.get_related_files(project_file))
    return _plan_backup_name(
        source_file=project_file,
        source_files=source_files,
        backup_name=backup_name,
        atu_path=atu_path,
        his_path=his_path,
        current_override=current_override,
        software_display=None,
        project_type_key=project_type.key,
        project_type_label=project_type.label,
    )


def _plan_backup_name(
    *,
    source_file: Path,
    source_files: tuple[Path, ...],
    backup_name: str,
    atu_path: Path,
    his_path: Path,
    current_override: dict[str, Path] | None,
    software_display: str | None,
    project_type_key: str,
    project_type_label: str,
    detected_versions: list[tuple[str, str, Path]] | None = None,
) -> BackupPlan:
    """Plan storage behavior for an already built backup filename."""

    planned_info = parse_backup_filename(Path(backup_name))
    current = _find_current_for_plan(
        atu_path=atu_path,
        planned_key=planned_info.key,
        current_override=current_override,
    )
    destination = atu_path / backup_name
    software = software_display or planned_info.software
    backup_info_text = _build_backup_info_text(
        backup_name=backup_name,
        project=planned_info.project,
        software=software,
        timestamp=planned_info.timestamp,
        collaborator=planned_info.collaborator,
        stage=planned_info.stage,
        project_type_label=project_type_label,
        source_file=source_file,
        source_files=list(source_files),
        detected_versions=detected_versions,
    )

    history_identity_path = find_backup_by_identity(his_path, planned_info.identity)

    if (
        history_identity_path
        and (current is None or current.identity != planned_info.identity)
        and has_sha256_conflict(source_files, history_identity_path)
    ):
        return _build_plan(
            source_file=source_file,
            backup_name=backup_name,
            destination_path=history_identity_path,
            status=STATUS_SHA_CONFLICT,
            software=software,
            planned_info=planned_info,
            project_type_key=project_type_key,
            project_type_label=project_type_label,
            current_backup=current.path if current else None,
            source_files=source_files,
            backup_info_text=backup_info_text,
        )

    if current and current.timestamp > planned_info.timestamp:
        if history_identity_path and has_sha256_conflict(source_files, history_identity_path):
            return _build_plan(
                source_file=source_file,
                backup_name=backup_name,
                destination_path=history_identity_path,
                status=STATUS_SHA_CONFLICT,
                software=software,
                planned_info=planned_info,
                project_type_key=project_type_key,
                project_type_label=project_type_label,
                current_backup=current.path,
                source_files=source_files,
                backup_info_text=backup_info_text,
            )
        history_path = find_backup_by_identity(his_path, planned_info.identity)
        if history_path is None:
            # Older files missing from HIS are archived without touching ATU.
            history_path = his_path / backup_name
            return BackupPlan(
                source_file=source_file,
                backup_name=backup_name,
                destination_path=history_path,
                status=STATUS_ARCHIVED_HISTORY,
                software=software,
                project=planned_info.project,
                timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
                collaborator=planned_info.collaborator,
                stage=planned_info.stage,
                project_type_key=project_type_key,
                project_type_label=project_type_label,
                current_backup=current.path,
                history_path=history_path,
                source_files=source_files,
                backup_info_text=backup_info_text,
            )

        return BackupPlan(
            source_file=source_file,
            backup_name=backup_name,
            destination_path=current.path,
            status=STATUS_SKIPPED_OLDER,
            software=software,
            project=planned_info.project,
            timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_key=project_type_key,
            project_type_label=project_type_label,
            current_backup=current.path,
            source_files=source_files,
            backup_info_text=backup_info_text,
        )

    if current and current.identity == planned_info.identity:
        if has_sha256_conflict(source_files, current.path):
            return _build_plan(
                source_file=source_file,
                backup_name=backup_name,
                destination_path=current.path,
                status=STATUS_SHA_CONFLICT,
                software=software,
                planned_info=planned_info,
                project_type_key=project_type_key,
                project_type_label=project_type_label,
                current_backup=current.path,
                source_files=source_files,
                backup_info_text=backup_info_text,
            )
        # Collaborator/stage differences do not create a new technical backup.
        return BackupPlan(
            source_file=source_file,
            backup_name=backup_name,
            destination_path=current.path,
            status=STATUS_ALREADY_CURRENT,
            software=software,
            project=planned_info.project,
            timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_key=project_type_key,
            project_type_label=project_type_label,
            current_backup=current.path,
            source_files=source_files,
            backup_info_text=backup_info_text,
        )

    if current:
        # A newer file replaces the current ATU backup and sends the old one to HIS.
        return BackupPlan(
            source_file=source_file,
            backup_name=backup_name,
            destination_path=destination,
            status=STATUS_REPLACED_CURRENT,
            software=software,
            project=planned_info.project,
            timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
            collaborator=planned_info.collaborator,
            stage=planned_info.stage,
            project_type_key=project_type_key,
            project_type_label=project_type_label,
            current_backup=current.path,
            history_path=his_path / current.path.name,
            source_files=source_files,
            backup_info_text=backup_info_text,
        )

    return BackupPlan(
        source_file=source_file,
        backup_name=backup_name,
        destination_path=destination,
        status=STATUS_STORED,
        software=software,
        project=planned_info.project,
        timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
        collaborator=planned_info.collaborator,
        stage=planned_info.stage,
        project_type_key=project_type_key,
        project_type_label=project_type_label,
        source_files=source_files,
        backup_info_text=backup_info_text,
    )


def _build_plan(
    *,
    source_file: Path,
    backup_name: str,
    destination_path: Path,
    status: str,
    software: str,
    planned_info: BackupFileInfo,
    project_type_key: str,
    project_type_label: str,
    current_backup: Path | None = None,
    history_path: Path | None = None,
    source_files: tuple[Path, ...] = (),
    backup_info_text: str | None = None,
) -> BackupPlan:
    """Create a plan from parsed filename metadata."""

    return BackupPlan(
        source_file=source_file,
        backup_name=backup_name,
        destination_path=destination_path,
        status=status,
        software=software,
        project=planned_info.project,
        timestamp_text=planned_info.timestamp.strftime("%Y%m%d-%H%M"),
        collaborator=planned_info.collaborator,
        stage=planned_info.stage,
        project_type_key=project_type_key,
        project_type_label=project_type_label,
        current_backup=current_backup,
        history_path=history_path,
        source_files=source_files,
        backup_info_text=backup_info_text,
    )


def archive_history_backup(
    *,
    project_file: Path,
    backup_name: str,
    his_path: Path,
    project_type: ProjectType = DEFAULT_PROJECT_TYPE,
    source_files: tuple[Path, ...] | None = None,
    backup_info_text: str | None = None,
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
        planned_info = parse_backup_filename(Path(backup_name))
        backup_info_text = _build_backup_info_text(
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
    return create_backup_zip(
        files_to_zip,
        backup_name,
        output_dir=his_path,
        backup_info_text=backup_info_text,
    )


def _unique_paths(paths) -> list[Path]:
    """Return paths without duplicates while preserving discovery order."""

    seen = set()
    unique = []
    for path in paths:
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _unique_text(values) -> list[str]:
    """Return non-empty text values without duplicates while preserving order."""

    seen = set()
    unique = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def _software_version_override_for(
    project_type: ProjectType,
    fallback: str | None,
    overrides: dict[str, str] | None,
) -> str | None:
    """Return a manual version scoped to the project type when available."""

    if overrides and project_type.key in overrides:
        return overrides[project_type.key]
    return fallback


def _build_backup_info_text(
    *,
    backup_name: str,
    project: str,
    software: str,
    timestamp,
    collaborator: str,
    stage: StageValue,
    project_type_label: str,
    source_file: Path,
    source_files: list[Path],
    detected_versions: list[tuple[str, str, Path]] | None,
) -> str:
    """Build a human-readable metadata file included in every backup zip."""

    stage_text = stage.value if isinstance(stage, BackupStage) else str(stage)
    versions = detected_versions or [(project_type_label, software, source_file)]
    lines = [
        "IED Backup Manager - Backup Information",
        "",
        f"Backup: {backup_name}",
        f"Project: {project}",
        f"Software: {software}",
        f"Timestamp: {timestamp.strftime('%Y%m%d-%H%M')}",
        f"Collaborator: {collaborator}",
        f"Stage: {stage_text}",
        "",
        "Detected versions:",
    ]
    for label, version, project_file in versions:
        lines.append(f"- {label}: {version} ({project_file.name})")

    lines.extend(["", "Included files:"])
    for path in source_files:
        lines.append(
            f"- {path.name}",
        )
        lines.append(
            f"  Modified: {get_file_timestamp(path).strftime('%Y%m%d-%H%M')}",
        )
        lines.append(f"  Size: {path.stat().st_size} bytes")
        lines.append(f"  SHA256: {calculate_sha256(path)}")

    return "\n".join(lines) + "\n"


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
    software_version_override: str | None = None,
) -> str:
    """Build a backup filename using the selected project type adapter."""

    project_id = project_type.get_project_id(project_file)
    version = project_type.get_software_version(project_file, software_version_override)
    timestamp = get_file_timestamp(project_file)
    return build_backup_name(
        software_version=version,
        project_id=project_id,
        timestamp=timestamp,
        collaborator=collaborator,
        stage=stage,
    )

