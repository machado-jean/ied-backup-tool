"""Main Qt window for previewing and executing backup batches."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.config.config_manager import AppConfig, load_config, save_config
from src.core.backup_service import (
    AtuDuplicatePlan,
    BackupPlan,
    BackupResult,
    execute_backup_plan,
    filter_current_and_newer_plans,
    fix_atu_duplicate_backups,
    plan_all_backups,
    plan_atu_duplicate_fixes,
    plan_grouped_backups,
    summarize_results,
)
from src.core.i18n import DEFAULT_LANGUAGE, message_label, status_label, ui_text
from src.core.naming import BackupStage, normalize_stage
from src.core.project_types.base import ProjectType, ProjectVersionRequiredError
from src.core.project_types.registry import PROJECT_TYPES, get_project_type
from src.gui.resources import app_icon_path
from src.gui.settings_window import SettingsWindow
from src.version import APP_DISPLAY_NAME

STATUS_COLORS = {
    "stored": QColor("#1f7a3f"),
    "replaced_current": QColor("#1c5d99"),
    "archived_history": QColor("#7a4f00"),
    "atu_duplicate": QColor("#9a5b00"),
    "skipped_older": QColor("#666666"),
    "already_current": QColor("#2f6f73"),
}
MANUAL_STAGE_DATA = "__manual_stage__"


class MainWindow(QMainWindow):
    """Main GUI controller for configuration, preview, execution, and logs."""

    def __init__(self, *, project_dir: Path | None = None) -> None:
        super().__init__()
        self.project_dir = (project_dir or get_runtime_project_dir()).resolve()
        self.config_path = self.project_dir / "config.json"
        self.config = self._load_config()
        self.current_plans: list[BackupPlan] = []
        self.atu_duplicate_plans: list[AtuDuplicatePlan] = []
        self.language = self.config.language if self.config else DEFAULT_LANGUAGE

        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.setMinimumSize(920, 620)
        self._build_ui()
        if not self.config:
            QTimer.singleShot(0, self.open_settings)
        self.refresh_preview()

    def _build_ui(self) -> None:
        """Create the static layout used by the application."""

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        top = QHBoxLayout()
        self.project_dir_label = QLabel(str(self.project_dir))
        self.project_dir_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.language_button = QPushButton(self._language_flag())
        self.language_button.setFixedWidth(44)
        self.language_button.setToolTip(ui_text("language_tooltip", self.language))
        self.language_button.clicked.connect(self.toggle_language)
        self.refresh_button = QPushButton()
        self.refresh_button.clicked.connect(self.refresh_preview)
        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(self.open_settings)
        self.current_folder_title = QLabel()
        top.addWidget(self.current_folder_title)
        top.addWidget(self.project_dir_label, 1)
        top.addWidget(self.language_button)
        top.addWidget(self.refresh_button)
        top.addWidget(self.settings_button)
        layout.addLayout(top)

        layout.addWidget(self._build_summary_group())

        content = QHBoxLayout()
        content.addWidget(self._build_preview_group(), 3)
        content.addWidget(self._build_action_group(), 1)
        layout.addLayout(content, 2)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumBlockCount(300)
        layout.addWidget(self.log_output, 1)

        self.setCentralWidget(root)
        self.retranslate_ui()

    def _build_preview_group(self) -> QGroupBox:
        """Create the table that shows the planned batch actions."""

        self.preview_group = QGroupBox()
        layout = QVBoxLayout(self.preview_group)
        self.preview_table = QTableWidget(0, 6)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.preview_table)
        return self.preview_group

    def _build_summary_group(self) -> QGroupBox:
        """Create the numeric summary displayed above the preview table."""

        self.summary_group = QGroupBox()
        layout = QHBoxLayout(self.summary_group)
        self.summary_labels: dict[str, QLabel] = {}
        self.summary_title_labels: dict[str, QLabel] = {}
        items = [
            ("total", "total"),
            ("new", "stored"),
            ("replaced_current", "replaced_current"),
            ("archive_count", "archived_history"),
            ("atu_corrections", "atu_duplicates"),
            ("ignored", "skipped_older"),
            ("already_current", "already_current"),
        ]
        for title_key, key in items:
            value = QLabel("0")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value.setMinimumWidth(80)
            value.setStyleSheet("font-size: 20px; font-weight: 600;")
            title = QLabel()
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box = QVBoxLayout()
            box.addWidget(value)
            box.addWidget(title)
            layout.addLayout(box)
            self.summary_labels[key] = value
            self.summary_title_labels[title_key] = title
        return self.summary_group

    def _build_action_group(self) -> QGroupBox:
        """Create stage, project type, mode, and execution controls."""

        self.action_group = QGroupBox()
        layout = QVBoxLayout(self.action_group)

        form = QFormLayout()
        self.action_form = form
        self.stage_input = QComboBox()
        self.stage_input.addItem("", None)
        for stage in BackupStage:
            self.stage_input.addItem(stage.value, stage.value)
        self.stage_input.addItem("", MANUAL_STAGE_DATA)
        self.stage_input.currentIndexChanged.connect(self.on_stage_selection_changed)
        self.stage_label = QLabel()
        form.addRow(self.stage_label, self.stage_input)

        self.stage_description_label = QLabel()
        self.stage_description_input = QLineEdit()
        self.stage_description_input.textChanged.connect(self.refresh_preview)
        form.addRow(self.stage_description_label, self.stage_description_input)
        self._set_stage_description_visible(False)

        self.software_version_label = QLabel()
        self.software_version_input = QLineEdit()
        self.software_version_input.textChanged.connect(self.refresh_preview)
        form.addRow(self.software_version_label, self.software_version_input)
        self._set_software_version_visible(False)

        self.type_checkboxes: dict[str, QCheckBox] = {}
        self.type_checkboxes_layout = QVBoxLayout()
        for project_type in PROJECT_TYPES:
            checkbox = QCheckBox()
            checkbox.setChecked(
                self.config is not None and project_type.key in self.config.project_types
            )
            checkbox.stateChanged.connect(self.on_project_type_selection_changed)
            self.type_checkboxes[project_type.key] = checkbox
            self.type_checkboxes_layout.addWidget(checkbox)
        self.type_label = QLabel()
        form.addRow(self.type_label, self.type_checkboxes_layout)

        self.latest_only_checkbox = QCheckBox()
        self.latest_only_checkbox.setChecked(False)
        self.latest_only_checkbox.stateChanged.connect(self.refresh_preview)
        self.mode_label = QLabel()
        form.addRow(self.mode_label, self.latest_only_checkbox)
        layout.addLayout(form)

        self.generate_button = QPushButton()
        self.generate_button.clicked.connect(self.generate_backup)
        layout.addWidget(self.generate_button)
        open_buttons = QHBoxLayout()
        self.open_atu_button = QPushButton()
        self.open_his_button = QPushButton()
        self.open_atu_button.clicked.connect(
            lambda: self.open_folder(self.config.atu_path if self.config else None)
        )
        self.open_his_button.clicked.connect(
            lambda: self.open_folder(self.config.his_path if self.config else None)
        )
        open_buttons.addWidget(self.open_atu_button)
        open_buttons.addWidget(self.open_his_button)
        layout.addLayout(open_buttons)
        layout.addStretch()
        return self.action_group

    def _load_config(self) -> AppConfig | None:
        """Load config.json from the runtime folder when it exists."""

        if not self.config_path.exists():
            return None
        try:
            return load_config(self.config_path)
        except Exception as exc:
            QMessageBox.warning(self, ui_text("settings_invalid", self.language), str(exc))
            return None

    def open_settings(self) -> None:
        """Open the settings dialog and refresh the preview after saving."""

        dialog = SettingsWindow(
            config_path=self.config_path,
            config=self.config,
            language=self.language,
            parent=self,
        )
        dialog.saved.connect(self.on_settings_saved)
        dialog.exec()

    def on_settings_saved(self, config: AppConfig) -> None:
        """Update in-memory configuration after the settings dialog saves."""

        self.config = config
        self.language = config.language
        self.language_button.setText(self._language_flag())
        self.retranslate_ui()
        self.refresh_preview()

    def refresh_preview(self) -> None:
        """Rebuild the batch preview using the current config and selected filters."""

        if not self.config:
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._clear_preview(ui_text("required_config", self.language))
            return

        selected_project_types = self._selected_project_types()
        if not selected_project_types:
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._clear_preview(ui_text("required_type", self.language))
            return

        selected_stage = self._selected_stage()
        if selected_stage is None:
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._clear_preview(ui_text("required_stage", self.language))
            return

        try:
            self.atu_duplicate_plans = plan_atu_duplicate_fixes(
                atu_path=self.config.atu_path,
                his_path=self.config.his_path,
            )
            plans: list[BackupPlan] = []
            if len(selected_project_types) > 1:
                plans = plan_grouped_backups(
                    project_dir=self.project_dir,
                    atu_path=self.config.atu_path,
                    his_path=self.config.his_path,
                    collaborator=self.config.collaborator,
                    stage=selected_stage,
                    project_types=selected_project_types,
                    software_version_override=self._software_version_override(),
                )
            else:
                for project_type in selected_project_types:
                    plans.extend(
                        plan_all_backups(
                            project_dir=self.project_dir,
                            atu_path=self.config.atu_path,
                            his_path=self.config.his_path,
                            collaborator=self.config.collaborator,
                            stage=selected_stage,
                            project_type=project_type,
                            software_version_override=self._software_version_override(),
                        )
                    )
            self.current_plans = (
                filter_current_and_newer_plans(plans)
                if self.latest_only_checkbox.isChecked()
                else plans
            )
            self._set_software_version_visible(False)
        except ProjectVersionRequiredError as exc:
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._set_software_version_visible(True)
            self._clear_preview(
                ui_text("required_software_version", self.language).format(
                    file=exc.project_file.name
                )
            )
            return
        except Exception as exc:
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._clear_preview(str(exc))
            return

        self._show_plans(self.current_plans, self.atu_duplicate_plans)

    def generate_backup(self) -> None:
        """Confirm and execute the currently planned backup batch."""

        if not self.config:
            QMessageBox.warning(
                self,
                ui_text("settings_pending", self.language),
                ui_text("settings_required", self.language),
            )
            return

        if not self.current_plans:
            self.refresh_preview()
            if not self.current_plans:
                return
        summary = summarize_results([*self.current_plans, *self.atu_duplicate_plans])
        executable_count = summary.stored + summary.replaced_current + summary.archived_history
        if executable_count == 0 and summary.atu_duplicates == 0:
            QMessageBox.information(
                self,
                ui_text("nothing_to_execute", self.language),
                ui_text("no_new_backups", self.language),
            )
            return

        fix_duplicates = False
        if summary.atu_duplicates:
            problem_files = "\n".join(
                f"- {plan.source_file.name} (manter: {plan.keep_file.name})"
                for plan in self.atu_duplicate_plans
            )
            answer = QMessageBox.question(
                self,
                ui_text("duplicates_title", self.language),
                f"{ui_text('duplicate_files_found', self.language)}\n\n"
                f"{problem_files}\n\n"
                f"{ui_text('duplicates_question', self.language)}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            fix_duplicates = answer == QMessageBox.StandardButton.Yes

        message = (
            f"{ui_text('files_to_process', self.language).format(count=executable_count)}\n"
            f"{ui_text('new', self.language)}: {summary.stored}\n"
            f"{ui_text('replaced_current', self.language)}: {summary.replaced_current}\n"
            f"{ui_text('archive_count', self.language)}: {summary.archived_history}\n"
            f"{ui_text('atu_corrections', self.language)}: "
            f"{summary.atu_duplicates if fix_duplicates else 0}\n"
            f"{ui_text('ignored', self.language)}: {summary.skipped_older}\n"
            f"{ui_text('continue_question', self.language)}"
        )
        answer = QMessageBox.question(
            self,
            ui_text("confirm_execution", self.language),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            duplicate_results, results = self._run_backup_with_progress(fix_duplicates)
        except Exception as exc:
            QMessageBox.critical(self, ui_text("backup_failed", self.language), str(exc))
            self.log_output.appendPlainText(f"{ui_text('error_prefix', self.language)}: {exc}")
            return

        self.log_output.clear()
        for result in duplicate_results:
            self.log_output.appendPlainText(
                f"{message_label('executed', self.language)}: "
                f"{result.source_file.name} -> {result.destination_path.name} "
                f"[{status_label(result.status, self.language)}]"
            )
        for result in results:
            self.log_output.appendPlainText(
                f"{message_label('executed', self.language)}: "
                f"{self._source_files_text(result.source_files or (result.source_file,))} "
                f"-> {result.final_path.name} "
                f"[{status_label(result.status, self.language)}]"
            )
        summary = summarize_results([*results, *duplicate_results])
        self.log_output.appendPlainText(
            f"{ui_text('completed_at', self.language)} {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        self.log_output.appendPlainText(self._summary_text(summary))
        QMessageBox.information(
            self,
            ui_text("backup_processed_title", self.language),
            self._summary_text(summary),
        )
        self.refresh_preview()

    def _run_backup_with_progress(
        self,
        fix_duplicates: bool,
    ) -> tuple[list[AtuDuplicatePlan], list[BackupResult]]:
        """Execute plans while keeping the UI responsive with a progress dialog."""

        if not self.config:
            return [], []

        plans = self.current_plans
        total_steps = len(plans) + (1 if fix_duplicates else 0)
        progress = QProgressDialog(
            ui_text("progress_starting", self.language),
            None,
            0,
            max(total_steps, 1),
            self,
        )
        progress.setWindowTitle(ui_text("progress_title", self.language))
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setValue(0)

        self.generate_button.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()
        try:
            step = 0
            duplicate_results: list[AtuDuplicatePlan] = []
            if fix_duplicates:
                progress.setLabelText(ui_text("progress_fixing_atu", self.language))
                QApplication.processEvents()
                duplicate_results = fix_atu_duplicate_backups(
                    atu_path=self.config.atu_path,
                    his_path=self.config.his_path,
                )
                step += 1
                progress.setValue(step)
                QApplication.processEvents()

            results: list[BackupResult] = []
            for plan in plans:
                progress.setLabelText(
                    ui_text("progress_processing_file", self.language).format(
                        file=self._source_files_text(plan.source_files or (plan.source_file,))
                    )
                )
                QApplication.processEvents()
                results.append(self._process_plan(plan))
                step += 1
                progress.setValue(step)
                QApplication.processEvents()

            progress.setLabelText(ui_text("progress_finished", self.language))
            progress.setValue(max(total_steps, 1))
            QApplication.processEvents()
            return duplicate_results, results
        finally:
            QApplication.restoreOverrideCursor()
            self.generate_button.setEnabled(True)
            progress.close()

    def _process_plan(self, plan: BackupPlan) -> BackupResult:
        """Execute one plan using the project type captured during preview."""

        if not self.config:
            raise RuntimeError(ui_text("settings_required", self.language))

        return execute_backup_plan(
            plan=plan,
            atu_path=self.config.atu_path,
            his_path=self.config.his_path,
        )

    def _show_plans(
        self,
        plans: list[BackupPlan],
        duplicate_plans: list[AtuDuplicatePlan],
    ) -> None:
        """Display plans in the preview table, counters, and text log."""

        if not plans and not duplicate_plans:
            self._clear_preview(ui_text("no_project_files_found", self.language))
            return
        executable_count = sum(
            plan.status in {"stored", "replaced_current", "archived_history"} for plan in plans
        )
        self.generate_button.setEnabled(executable_count > 0 or bool(duplicate_plans))
        summary = summarize_results([*plans, *duplicate_plans])
        self._set_summary(summary)
        self._populate_table(plans, duplicate_plans)
        self.log_output.clear()
        self.log_output.appendPlainText(ui_text("preview_note", self.language))
        for plan in duplicate_plans:
            self.log_output.appendPlainText(
                f"{message_label('problematic', self.language)}: "
                f"{plan.source_file.name} -> {plan.destination_path.name} "
                f"[{status_label(plan.status, self.language)}]"
            )
        for plan in plans:
            self.log_output.appendPlainText(
                f"{message_label('planned', self.language)}: "
                f"{self._source_files_text(plan.source_files or (plan.source_file,))} "
                f"-> {plan.destination_path.name} "
                f"[{status_label(plan.status, self.language)}]"
            )

    def _populate_table(
        self,
        plans: list[BackupPlan],
        duplicate_plans: list[AtuDuplicatePlan],
    ) -> None:
        """Write preview rows to the table widget."""

        rows = [*duplicate_plans, *plans]
        self.preview_table.setRowCount(len(rows))
        for row, plan in enumerate(rows):
            if isinstance(plan, AtuDuplicatePlan):
                project = plan.key
                software = "-"
                timestamp = "-"
            else:
                project = plan.project
                software = plan.software
                timestamp = plan.timestamp_text
            values = [
                self._source_files_text(plan.source_files or (plan.source_file,)),
                project,
                software,
                timestamp,
                status_label(plan.status, self.language),
                str(plan.destination_path),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {1, 2, 3, 4}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == 4 and plan.status in STATUS_COLORS:
                    item.setForeground(STATUS_COLORS[plan.status])
                self.preview_table.setItem(row, column, item)
        self.preview_table.resizeColumnsToContents()

    def _clear_preview(self, message: str) -> None:
        """Reset preview state and show a blocking message in the log area."""

        self.generate_button.setEnabled(False)
        self.log_output.clear()
        self.preview_table.setRowCount(0)
        self._set_summary_empty()
        self.log_output.appendPlainText(message)

    def _selected_project_types(self) -> list[ProjectType]:
        """Return project types selected in the checkbox list."""

        return [
            get_project_type(key)
            for key, checkbox in self.type_checkboxes.items()
            if checkbox.isChecked()
        ]

    def on_project_type_selection_changed(self) -> None:
        """Persist selected project types and refresh the batch preview."""

        self._save_selected_project_types()
        self.refresh_preview()

    def _save_selected_project_types(self) -> None:
        """Store the current project type checkbox state in config.json."""

        if not self.config:
            return
        self.config = AppConfig(
            collaborator=self.config.collaborator,
            atu_path=self.config.atu_path,
            his_path=self.config.his_path,
            language=self.config.language,
            project_types=tuple(
                key for key, checkbox in self.type_checkboxes.items() if checkbox.isChecked()
            ),
        )
        save_config(self.config_path, self.config)

    def _selected_stage(self) -> str | None:
        """Return selected fixed stage or normalized free description."""

        data = self.stage_input.currentData()
        if data is None:
            return None
        if data == MANUAL_STAGE_DATA:
            return normalize_stage(self.stage_description_input.text())
        return str(data)

    def on_stage_selection_changed(self) -> None:
        """Show the free stage field only for the manual description option."""

        self._set_stage_description_visible(self.stage_input.currentData() == MANUAL_STAGE_DATA)
        self.refresh_preview()

    def _set_stage_description_visible(self, visible: bool) -> None:
        """Toggle the optional stage description controls."""

        self.stage_description_label.setVisible(visible)
        self.stage_description_input.setVisible(visible)

    def _software_version_override(self) -> str | None:
        """Return the optional manual software version used as detection fallback."""

        version = self.software_version_input.text().strip()
        return version or None

    def _set_software_version_visible(self, visible: bool) -> None:
        """Toggle the manual software version fallback controls."""

        self.software_version_label.setVisible(visible)
        self.software_version_input.setVisible(visible)

    def _source_files_text(self, files: tuple[Path, ...]) -> str:
        """Format one or more source files for preview, logs, and progress text."""

        if len(files) <= 1:
            return files[0].name if files else "-"
        return f"{files[0].name} + {len(files) - 1}"

    def _summary_text(self, summary) -> str:
        """Format a human-readable summary for dialogs and logs."""

        return "\n".join(
            [
                ui_text("summary_total_line", self.language).format(total=summary.total),
                ui_text("summary_stored_line", self.language).format(count=summary.stored),
                ui_text("summary_replaced_line", self.language).format(
                    count=summary.replaced_current
                ),
                ui_text("summary_archived_line", self.language).format(
                    count=summary.archived_history
                ),
                ui_text("summary_atu_line", self.language).format(count=summary.atu_duplicates),
                ui_text("summary_skipped_line", self.language).format(
                    count=summary.skipped_older
                ),
                ui_text("summary_current_line", self.language).format(
                    count=summary.already_current
                ),
            ]
        )

    def toggle_language(self) -> None:
        """Switch UI language and persist the preference when config exists."""

        self.language = "en_US" if self.language == "pt_BR" else "pt_BR"
        self.language_button.setText(self._language_flag())
        if self.config:
            self.config = AppConfig(
                collaborator=self.config.collaborator,
                atu_path=self.config.atu_path,
                his_path=self.config.his_path,
                language=self.language,
                project_types=self.config.project_types,
            )
            save_config(self.config_path, self.config)
        self.retranslate_ui()
        if self.current_plans or self.atu_duplicate_plans:
            self._show_plans(self.current_plans, self.atu_duplicate_plans)

    def _language_flag(self) -> str:
        """Return the flag shown in the language toggle button."""

        return "🇺🇸" if self.language == "en_US" else "🇧🇷"

    def _set_summary(self, summary) -> None:
        """Update the numeric summary strip."""

        self.summary_labels["total"].setText(str(summary.total))
        self.summary_labels["stored"].setText(str(summary.stored))
        self.summary_labels["replaced_current"].setText(str(summary.replaced_current))
        self.summary_labels["archived_history"].setText(str(summary.archived_history))
        self.summary_labels["atu_duplicates"].setText(str(summary.atu_duplicates))
        self.summary_labels["skipped_older"].setText(str(summary.skipped_older))
        self.summary_labels["already_current"].setText(str(summary.already_current))

    def _set_summary_empty(self) -> None:
        """Reset all summary counters to zero."""

        for label in self.summary_labels.values():
            label.setText("0")

    def retranslate_ui(self) -> None:
        """Apply the current language to visible labels and buttons."""

        self.current_folder_title.setText(ui_text("current_folder", self.language))
        self.language_button.setToolTip(ui_text("language_tooltip", self.language))
        self.refresh_button.setText(ui_text("refresh", self.language))
        self.settings_button.setText(ui_text("settings", self.language))
        self.summary_group.setTitle(ui_text("summary", self.language))
        self.preview_group.setTitle(ui_text("preview", self.language))
        self.action_group.setTitle(ui_text("execution", self.language))
        self.log_output.setPlaceholderText(ui_text("preview", self.language))
        self.preview_table.setHorizontalHeaderLabels(
            [
                ui_text("file", self.language),
                ui_text("project", self.language),
                ui_text("version", self.language),
                ui_text("timestamp", self.language),
                ui_text("action", self.language),
                ui_text("destination", self.language),
            ]
        )
        for title_key, label in self.summary_title_labels.items():
            label.setText(ui_text(title_key, self.language))
        self.stage_label.setText(ui_text("stage", self.language))
        self.stage_description_label.setText(ui_text("stage_description", self.language))
        self.stage_description_input.setPlaceholderText(
            ui_text("stage_description_placeholder", self.language)
        )
        self.software_version_label.setText(ui_text("software_version", self.language))
        self.software_version_input.setPlaceholderText(
            ui_text("software_version_placeholder", self.language)
        )
        manual_index = self.stage_input.count() - 1
        self.stage_input.setItemText(
            manual_index,
            ui_text("stage_description_option", self.language),
        )
        self.type_label.setText(ui_text("type", self.language))
        self.mode_label.setText(ui_text("mode", self.language))
        for project_type in PROJECT_TYPES:
            self.type_checkboxes[project_type.key].setText(project_type.label)
        self.latest_only_checkbox.setText(ui_text("process_from_current", self.language))
        self.generate_button.setText(ui_text("generate_backups", self.language))
        self.open_atu_button.setText(ui_text("open_atu", self.language))
        self.open_his_button.setText(ui_text("open_his", self.language))

    def open_folder(self, folder: Path | None) -> None:
        """Create and open a configured folder in Windows Explorer."""

        if not folder:
            return
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder.resolve())))


def get_runtime_project_dir() -> Path:
    """Return the executable folder in production or cwd during development."""

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()
