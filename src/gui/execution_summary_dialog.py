"""Polished execution summary dialog for completed backup batches."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.core.backup_models import BackupSummary
from src.core.i18n import ui_text


def show_execution_summary_dialog(
    parent,
    *,
    title: str,
    summary: BackupSummary,
    language: str,
    canceled_message: str | None = None,
    cleanup_message: str | None = None,
    cleanup_action=None,
) -> None:
    """Show a compact summary that hides zero-value operational counters."""

    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumWidth(420)

    layout = QVBoxLayout(dialog)
    layout.setSpacing(12)

    heading = QLabel(title)
    heading.setStyleSheet("font-size: 16px; font-weight: 700;")
    layout.addWidget(heading)

    if canceled_message:
        message = QLabel(canceled_message)
        message.setWordWrap(True)
        layout.addWidget(message)

    for label, value in _summary_rows(summary, language):
        layout.addWidget(_metric_row(label, value))

    if cleanup_message:
        layout.addWidget(_separator())
        cleanup = QLabel(cleanup_message)
        cleanup.setWordWrap(True)
        cleanup.setStyleSheet("font-weight: 600; color: #d92d20;")
        layout.addWidget(cleanup)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    if cleanup_message and cleanup_action:
        cleanup_button = QPushButton(ui_text("history_cleanup", language))
        buttons.addButton(cleanup_button, QDialogButtonBox.ButtonRole.ActionRole)
        cleanup_button.clicked.connect(dialog.accept)
        cleanup_button.clicked.connect(cleanup_action)
    buttons.accepted.connect(dialog.accept)
    layout.addWidget(buttons)
    dialog.exec()


def _summary_rows(summary: BackupSummary, language: str) -> list[tuple[str, int]]:
    """Return non-zero summary rows, keeping total as the first row."""

    rows = [(ui_text("summary_total_title", language), summary.total)]
    optional_rows = [
        (ui_text("summary_stored_title", language), summary.stored),
        (ui_text("summary_replaced_title", language), summary.replaced_current),
        (ui_text("summary_archived_title", language), summary.archived_history),
        (ui_text("summary_atu_title", language), summary.atu_duplicates),
        (ui_text("summary_sha_conflict_title", language), summary.sha_conflicts),
        (ui_text("summary_skipped_title", language), summary.skipped_older),
        (ui_text("summary_current_title", language), summary.already_current),
    ]
    rows.extend((label, value) for label, value in optional_rows if value)
    return rows


def _metric_row(label_text: str, value: int) -> QFrame:
    """Build a stable metric row for the summary dialog."""

    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet("QFrame { border-radius: 4px; padding: 4px; }")
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(10, 6, 10, 6)
    label = QLabel(label_text)
    value_label = QLabel(str(value))
    value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    value_label.setMinimumWidth(48)
    value_label.setStyleSheet("font-size: 18px; font-weight: 700;")
    layout.addWidget(label, 1)
    layout.addWidget(value_label)
    return frame


def _separator() -> QFrame:
    """Return a horizontal separator between summary and advisories."""

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line
