"""Shared backup status constants and data models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class BackupStatus(StrEnum):
    """Canonical status values shared by planning, execution, logs, and UI."""

    STORED = "stored"
    REPLACED_CURRENT = "replaced_current"
    ARCHIVED_HISTORY = "archived_history"
    ATU_DUPLICATE = "atu_duplicate"
    SHA_CONFLICT = "sha_conflict"
    SKIPPED_OLDER = "skipped_older"
    ALREADY_CURRENT = "already_current"


STATUS_STORED = BackupStatus.STORED
STATUS_REPLACED_CURRENT = BackupStatus.REPLACED_CURRENT
STATUS_ARCHIVED_HISTORY = BackupStatus.ARCHIVED_HISTORY
STATUS_ATU_DUPLICATE = BackupStatus.ATU_DUPLICATE
STATUS_SHA_CONFLICT = BackupStatus.SHA_CONFLICT
STATUS_SKIPPED_OLDER = BackupStatus.SKIPPED_OLDER
STATUS_ALREADY_CURRENT = BackupStatus.ALREADY_CURRENT

BackupStatusValue = BackupStatus | str


@dataclass(frozen=True)
class BackupResult:
    """Result of an executed backup operation."""

    source_file: Path
    backup_name: str
    final_path: Path
    status: BackupStatusValue = STATUS_STORED
    source_files: tuple[Path, ...] = ()


@dataclass(frozen=True)
class BackupPlan:
    """Dry-run description of what will happen to a project file."""

    source_file: Path
    backup_name: str
    destination_path: Path
    status: BackupStatusValue
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


@dataclass(frozen=True)
class AtuDuplicatePlan:
    """Dry-run description of an ATU duplicate correction."""

    source_file: Path
    backup_name: str
    destination_path: Path
    status: BackupStatusValue
    key: str
    keep_file: Path


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
