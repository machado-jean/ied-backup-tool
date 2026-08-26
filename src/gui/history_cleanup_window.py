"""Dialog for previewing and executing controlled HIS cleanup."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.config.config_manager import AppConfig, HistoryCleanupConfig, save_config
from src.core.history_cleanup import (
    HistoryCleanupCandidate,
    execute_history_cleanup,
    plan_history_cleanup,
)
from src.core.i18n import DEFAULT_LANGUAGE, ui_text
from src.core.naming import format_backup_timestamp
from src.gui.message_box import question_yes_no


class HistoryCleanupWindow(QDialog):
    """Preview and confirm deletion candidates from the HIS folder."""

    saved = Signal(AppConfig)

    def __init__(
        self,
        *,
        config_path: Path,
        config: AppConfig,
        language: str = DEFAULT_LANGUAGE,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.config_path = config_path
        self.config = config
        self.language = language
        self.candidates: list[HistoryCleanupCandidate] = []
        self.setWindowTitle(ui_text("history_cleanup", self.language))
        self.setMinimumSize(980, 520)
        self._build_ui()
        self.refresh_plan()

    def _build_ui(self) -> None:
        """Create cleanup controls, summary, and candidate table."""

        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel(ui_text("history_cleanup_retention_days", self.language)))
        self.retention_input = QSpinBox()
        self.retention_input.setRange(0, 3650)
        self.retention_input.setValue(self.config.history_cleanup.retention_days)
        self.retention_input.valueChanged.connect(self._save_preferences)
        controls.addWidget(self.retention_input)
        controls.addStretch()
        self.refresh_button = QPushButton(ui_text("history_cleanup_refresh", self.language))
        self.refresh_button.clicked.connect(self.refresh_plan)
        controls.addWidget(self.refresh_button)
        layout.addLayout(controls)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            [
                ui_text("action", self.language),
                ui_text("file", self.language),
                ui_text("project", self.language),
                ui_text("stage", self.language),
                ui_text("timestamp", self.language),
                ui_text("history_cleanup_age", self.language),
                ui_text("history_cleanup_size", self.language),
                ui_text("history_cleanup_reason", self.language),
            ]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        self.select_all_button = QPushButton(ui_text("history_cleanup_select_all", self.language))
        self.select_all_button.clicked.connect(self._check_all_candidates)
        self.clean_button = QPushButton(ui_text("history_cleanup_delete_selected", self.language))
        self.clean_button.clicked.connect(self.delete_selected)
        close_button = QPushButton(ui_text("close", self.language))
        close_button.clicked.connect(self.accept)
        buttons.addWidget(self.select_all_button)
        buttons.addStretch()
        buttons.addWidget(self.clean_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    def refresh_plan(self) -> None:
        """Recalculate cleanup candidates from the current HIS folder."""

        self._save_preferences()
        plan = plan_history_cleanup(
            self.config.his_path,
            retention_days=self.config.history_cleanup.retention_days,
        )
        self.candidates = plan.candidates
        self.summary_label.setText(
            ui_text("history_cleanup_summary", self.language).format(
                total=plan.total_his_files,
                candidates=len(plan.candidates),
                total_size=_format_size(plan.total_his_size_bytes),
                candidate_size=_format_size(plan.candidate_size_bytes),
            )
        )
        self._populate_table()

    def delete_selected(self) -> None:
        """Delete selected candidates after explicit confirmation."""

        selected_candidates = self._selected_candidates()
        if not selected_candidates:
            QMessageBox.information(
                self,
                ui_text("history_cleanup", self.language),
                ui_text("history_cleanup_select_required", self.language),
            )
            return

        answer = question_yes_no(
            self,
            title=ui_text("history_cleanup_confirm_title", self.language),
            text=ui_text("history_cleanup_confirm_message", self.language).format(
                count=len(selected_candidates),
                size=_format_size(sum(candidate.size_bytes for candidate in selected_candidates)),
            ),
            language=self.language,
            default_button=QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            removed = execute_history_cleanup(selected_candidates)
        except OSError as exc:
            QMessageBox.critical(
                self,
                ui_text("history_cleanup_failed_title", self.language),
                str(exc),
            )
            self.refresh_plan()
            return

        QMessageBox.information(
            self,
            ui_text("history_cleanup_done_title", self.language),
            ui_text("history_cleanup_done_message", self.language).format(count=len(removed)),
        )
        self.refresh_plan()

    def _populate_table(self) -> None:
        """Render cleanup candidates in the preview table."""

        self.table.setRowCount(0)
        for row, candidate in enumerate(self.candidates):
            self.table.insertRow(row)
            values = [
                "",
                candidate.path.name,
                candidate.info.project,
                candidate.info.stage or "-",
                format_backup_timestamp(candidate.info.timestamp),
                str(candidate.age_days),
                _format_size(candidate.size_bytes),
                candidate.reason,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, row)
                    item.setFlags(
                        Qt.ItemFlag.ItemIsEnabled
                        | Qt.ItemFlag.ItemIsUserCheckable
                        | Qt.ItemFlag.ItemIsSelectable
                    )
                    item.setCheckState(Qt.CheckState.Unchecked)
                self.table.setItem(row, column, item)
        self.clean_button.setEnabled(bool(self.candidates))
        self.select_all_button.setEnabled(bool(self.candidates))
        self.table.resizeColumnsToContents()

    def _selected_candidates(self) -> list[HistoryCleanupCandidate]:
        """Return candidates checked by the user."""

        rows = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                rows.append(row)
        return [self.candidates[row] for row in rows if row < len(self.candidates)]

    def _check_all_candidates(self) -> None:
        """Mark every visible cleanup candidate."""

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)

    def _save_preferences(self) -> None:
        """Persist cleanup preferences while preserving the remaining config."""

        cleanup = HistoryCleanupConfig(retention_days=self.retention_input.value())
        if cleanup == self.config.history_cleanup:
            return
        self.config = AppConfig(
            collaborator=self.config.collaborator,
            atu_path=self.config.atu_path,
            his_path=self.config.his_path,
            language=self.config.language,
            project_types=self.config.project_types,
            software_versions=self.config.software_versions,
            show_startup_instructions=self.config.show_startup_instructions,
            history_cleanup=cleanup,
        )
        save_config(self.config_path, self.config)
        self.saved.emit(self.config)


def _format_size(size_bytes: int) -> str:
    """Format bytes for compact table display."""

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
