"""Message builders used before backup execution starts."""

from __future__ import annotations

from src.core.backup_models import BackupStatus
from src.core.i18n import ui_text
from src.gui.backup_application_service import executable_backup_count
from src.gui.preview_table import source_files_text


def integrity_conflict_details(plans) -> str:
    """List planned files blocked by SHA conflicts."""

    return "\n".join(
        f"- {source_files_text(plan.source_files or (plan.source_file,))} "
        f"-> {plan.destination_path.name}"
        for plan in plans
        if plan.status == BackupStatus.SHA_CONFLICT
    )


def duplicate_problem_files(duplicate_plans) -> str:
    """List duplicate ATU files and which file will be kept."""

    return "\n".join(
        f"- {plan.source_file.name} (manter: {plan.keep_file.name})" for plan in duplicate_plans
    )


def execution_confirmation_message(summary, *, fix_duplicates: bool, language: str) -> str:
    """Build the final execution confirmation text."""

    return (
        f"{ui_text('files_to_process', language).format(count=executable_backup_count(summary))}\n"
        f"{ui_text('new', language)}: {summary.stored}\n"
        f"{ui_text('replaced_current', language)}: {summary.replaced_current}\n"
        f"{ui_text('archive_count', language)}: {summary.archived_history}\n"
        f"{ui_text('atu_corrections', language)}: "
        f"{summary.atu_duplicates if fix_duplicates else 0}\n"
        f"{ui_text('ignored', language)}: {summary.skipped_older}\n"
        f"{ui_text('continue_question', language)}"
    )
