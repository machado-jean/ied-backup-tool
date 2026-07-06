"""Qt-independent application service used by the main backup window."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from src.config.config_manager import AppConfig
from src.core.backup_service import (
    AtuDuplicatePlan,
    BackupPlan,
    BackupSummary,
    filter_current_and_newer_plans,
    plan_all_backups,
    plan_atu_duplicate_fixes,
    plan_grouped_backups,
    summarize_results,
)
from src.core.project_types.base import ProjectType


class PreviewValidationCode(StrEnum):
    """Reasons why a preview cannot be built from the current UI state."""

    REQUIRED_CONFIG = "required_config"
    REQUIRED_TYPE = "required_type"
    REQUIRED_STAGE = "required_stage"
    REQUIRED_MANUAL_SOFTWARE_VERSION = "required_manual_software_version"


class PreviewValidationError(ValueError):
    """Raised when preview inputs are incomplete before planning starts."""

    def __init__(
        self,
        code: PreviewValidationCode,
        *,
        project_type: ProjectType | None = None,
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.project_type = project_type


@dataclass(frozen=True)
class PreviewRequest:
    """Input data needed to plan the current preview batch."""

    project_dir: Path
    config: AppConfig | None
    selected_project_types: list[ProjectType]
    selected_stage: str | None
    latest_only: bool
    software_version_override: str | None
    software_version_overrides: dict[str, str]


@dataclass(frozen=True)
class PreviewResult:
    """Planned backup preview and derived state for the main window."""

    plans: list[BackupPlan]
    duplicate_plans: list[AtuDuplicatePlan]
    manual_project_type: ProjectType | None


def manual_version_project_type(project_types: list[ProjectType]) -> ProjectType | None:
    """Return the selected project type that requires a configured version."""

    for project_type in project_types:
        if getattr(project_type, "manual_version_required", False):
            return project_type
    return None


def build_preview(request: PreviewRequest) -> PreviewResult:
    """Build all preview plans from validated application inputs."""

    if request.config is None:
        raise PreviewValidationError(PreviewValidationCode.REQUIRED_CONFIG)
    if not request.selected_project_types:
        raise PreviewValidationError(PreviewValidationCode.REQUIRED_TYPE)
    if request.selected_stage is None:
        raise PreviewValidationError(PreviewValidationCode.REQUIRED_STAGE)

    manual_project_type = manual_version_project_type(request.selected_project_types)
    if manual_project_type is not None and not request.software_version_override:
        raise PreviewValidationError(
            PreviewValidationCode.REQUIRED_MANUAL_SOFTWARE_VERSION,
            project_type=manual_project_type,
        )

    duplicate_plans = plan_atu_duplicate_fixes(
        atu_path=request.config.atu_path,
        his_path=request.config.his_path,
    )
    plans: list[BackupPlan] = []
    if len(request.selected_project_types) > 1:
        plans = plan_grouped_backups(
            project_dir=request.project_dir,
            atu_path=request.config.atu_path,
            his_path=request.config.his_path,
            collaborator=request.config.collaborator,
            stage=request.selected_stage,
            project_types=request.selected_project_types,
            software_version_override=request.software_version_override,
            software_version_overrides=request.software_version_overrides,
        )
    else:
        for project_type in request.selected_project_types:
            plans.extend(
                plan_all_backups(
                    project_dir=request.project_dir,
                    atu_path=request.config.atu_path,
                    his_path=request.config.his_path,
                    collaborator=request.config.collaborator,
                    stage=request.selected_stage,
                    project_type=project_type,
                    software_version_override=request.software_version_override,
                )
            )

    if request.latest_only:
        plans = filter_current_and_newer_plans(plans)

    return PreviewResult(
        plans=plans,
        duplicate_plans=duplicate_plans,
        manual_project_type=manual_project_type,
    )


def summarize_preview(
    plans: list[BackupPlan],
    duplicate_plans: list[AtuDuplicatePlan],
) -> BackupSummary:
    """Return summary counters for a planned preview."""

    return summarize_results([*plans, *duplicate_plans])


def executable_backup_count(summary: BackupSummary) -> int:
    """Count backup plans that will create/archive/replace files."""

    return summary.stored + summary.replaced_current + summary.archived_history
