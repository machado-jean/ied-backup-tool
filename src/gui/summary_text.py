"""Presentation helpers for backup execution summaries."""

from __future__ import annotations

from src.core.i18n import ui_text


def format_summary_text(summary, language: str) -> str:
    """Format a human-readable summary for dialogs and logs."""

    return "\n".join(
        [
            ui_text("summary_total_line", language).format(total=summary.total),
            ui_text("summary_stored_line", language).format(count=summary.stored),
            ui_text("summary_replaced_line", language).format(count=summary.replaced_current),
            ui_text("summary_archived_line", language).format(count=summary.archived_history),
            ui_text("summary_atu_line", language).format(count=summary.atu_duplicates),
            ui_text("summary_sha_conflict_line", language).format(count=summary.sha_conflicts),
            ui_text("summary_skipped_line", language).format(count=summary.skipped_older),
            ui_text("summary_current_line", language).format(count=summary.already_current),
        ]
    )
