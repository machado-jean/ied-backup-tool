"""Preview-table rendering helpers."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from src.core.backup_service import AtuDuplicatePlan, BackupPlan
from src.core.i18n import status_label

STATUS_COLORS = {
    "stored": QColor("#1f7a3f"),
    "replaced_current": QColor("#1c5d99"),
    "archived_history": QColor("#7a4f00"),
    "atu_duplicate": QColor("#9a5b00"),
    "sha_conflict": QColor("#b42318"),
    "skipped_older": QColor("#666666"),
    "already_current": QColor("#2f6f73"),
}


def source_files_text(files: tuple[Path, ...]) -> str:
    """Format one or more source files for preview, logs, and progress text."""

    if len(files) <= 1:
        return files[0].name if files else "-"
    return f"{files[0].name} + {len(files) - 1}"


def populate_preview_table(
    table: QTableWidget,
    *,
    plans: list[BackupPlan],
    duplicate_plans: list[AtuDuplicatePlan],
    language: str,
) -> None:
    """Write backup and duplicate-fix plans to the preview table."""

    rows = [*duplicate_plans, *plans]
    table.setRowCount(len(rows))
    for row, plan in enumerate(rows):
        values = _row_values(plan, language)
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 5:
                item.setToolTip(str(plan.destination_path))
            if column in {0, 2, 3, 4}:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if column == 0 and plan.status in STATUS_COLORS:
                item.setForeground(STATUS_COLORS[plan.status])
            table.setItem(row, column, item)
    table.resizeColumnsToContents()


def _row_values(plan: BackupPlan | AtuDuplicatePlan, language: str) -> list[str]:
    """Return display values in the configured preview-table column order."""

    if isinstance(plan, AtuDuplicatePlan):
        project = plan.key
        software = "-"
        timestamp = "-"
        file_text = plan.source_file.name
    else:
        project = plan.project
        software = plan.software
        timestamp = plan.timestamp_text
        file_text = source_files_text(plan.source_files or (plan.source_file,))

    return [
        status_label(plan.status, language),
        file_text,
        project,
        software,
        timestamp,
        destination_display_text(plan.destination_path),
    ]


def destination_display_text(destination_path: Path) -> str:
    """Format destination for compact preview display while preserving the file name."""

    parent_name = destination_path.parent.name
    if parent_name.upper().endswith("ATU"):
        return f"ATU\\{destination_path.name}"
    if parent_name.upper().endswith("HIS"):
        return f"HIS\\{destination_path.name}"
    return destination_path.name
