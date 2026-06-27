"""Main Qt window for previewing and executing backup batches."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
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
from src.gui.resources import app_icon_path, language_flag_path
from src.gui.settings_window import SettingsWindow
from src.gui.storage_paths import confirm_storage_paths_ready
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


def configure_language_button(button: QPushButton) -> None:
    """Set a stable compact size for language flag buttons."""

    button.setFixedSize(44, 30)
    button.setIconSize(QSize(24, 17))
    button.setText("")


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
        self.pending_show_startup_instructions: bool | None = None

        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.setMinimumSize(920, 620)
        self._resize_to_available_screen()
        self._build_ui()
        self._load_manual_software_version(self._manual_version_project_type())
        QTimer.singleShot(0, self._run_startup_dialogs)
        self.refresh_preview()

    def _resize_to_available_screen(self) -> None:
        """Start wider on normal desktops while respecting the minimum size."""

        screen = QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        width = max(self.minimumWidth(), int(available.width() * 0.75))
        height = max(self.minimumHeight(), min(available.height(), 720))
        self.resize(width, height)

    def _build_ui(self) -> None:
        """Create the static layout used by the application."""

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        top = QHBoxLayout()
        self.project_dir_label = QLabel(str(self.project_dir))
        self.project_dir_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.language_button = QPushButton()
        configure_language_button(self.language_button)
        self.language_button.setToolTip(ui_text("language_tooltip", self.language))
        self.language_button.clicked.connect(self.toggle_language)
        self.refresh_button = QPushButton()
        self.refresh_button.clicked.connect(self.refresh_preview)
        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(self.open_settings)
        self.current_folder_title = QLabel()
        top.addWidget(self.current_folder_title)
        top.addWidget(self.project_dir_label, 1)
        top.addWidget(self.refresh_button)
        top.addWidget(self.settings_button)
        top.addWidget(self.language_button)
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

        self.type_checkboxes: dict[str, QCheckBox] = {}
        self.type_checkboxes_layout = QVBoxLayout()
        for project_type in PROJECT_TYPES:
            checkbox = QCheckBox()
            checkbox.setChecked(
                self.config is not None and project_type.key in self.config.project_types
            )
            checkbox.stateChanged.connect(self.on_project_type_selection_changed)
            self.type_checkboxes[project_type.key] = checkbox
            if getattr(project_type, "manual_version_required", False):
                self.software_version_label = QLabel()
                self.software_version_input = QLineEdit()
                self.software_version_input.setMaximumWidth(150)
                self.software_version_input.textChanged.connect(self.on_software_version_changed)
                version_row = QHBoxLayout()
                version_row.addWidget(checkbox)
                version_row.addStretch()
                version_row.addWidget(self.software_version_label)
                version_row.addWidget(self.software_version_input)
                self.type_checkboxes_layout.addLayout(version_row)
            else:
                self.type_checkboxes_layout.addWidget(checkbox)
        self.type_label = QLabel()
        form.addRow(self.type_label, self.type_checkboxes_layout)
        self._set_software_version_visible(False)

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

    def _run_startup_dialogs(self) -> None:
        """Show first-run guidance and then request settings when needed."""

        self._show_startup_instructions_if_needed()
        if not self.config:
            self.open_settings()

    def _show_startup_instructions_if_needed(self) -> None:
        """Show usage guidance unless the user opted out in config.json."""

        if self.config and not self.config.show_startup_instructions:
            return

        dialog = StartupInstructionsDialog(language=self.language, parent=self)
        dialog.exec()
        self._apply_startup_dialog_language(dialog.language)
        if not dialog.do_not_show_again:
            return

        if self.config:
            self.config = AppConfig(
                collaborator=self.config.collaborator,
                atu_path=self.config.atu_path,
                his_path=self.config.his_path,
                language=self.config.language,
                project_types=self.config.project_types,
                software_versions=self.config.software_versions,
                show_startup_instructions=False,
            )
            save_config(self.config_path, self.config)
        else:
            self.pending_show_startup_instructions = False

    def _apply_startup_dialog_language(self, language: str) -> None:
        """Apply the language selected in the startup instructions dialog."""

        if language == self.language:
            return

        self.language = language
        self._set_language_button_icon(self.language_button)
        if self.config:
            self.config = AppConfig(
                collaborator=self.config.collaborator,
                atu_path=self.config.atu_path,
                his_path=self.config.his_path,
                language=self.language,
                project_types=self.config.project_types,
                software_versions=self.config.software_versions,
                show_startup_instructions=self.config.show_startup_instructions,
            )
            save_config(self.config_path, self.config)
        self.retranslate_ui()

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
        if self.pending_show_startup_instructions is not None:
            self.config = AppConfig(
                collaborator=config.collaborator,
                atu_path=config.atu_path,
                his_path=config.his_path,
                language=config.language,
                project_types=config.project_types,
                software_versions=config.software_versions,
                show_startup_instructions=self.pending_show_startup_instructions,
            )
            save_config(self.config_path, self.config)
            self.pending_show_startup_instructions = None
        self.language = config.language
        self._set_language_button_icon(self.language_button)
        self._load_manual_software_version(self._manual_version_project_type())
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
        manual_project_type = self._manual_version_project_type(selected_project_types)
        self._set_software_version_visible(manual_project_type is not None)
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

        if manual_project_type is not None and not self._software_version_override():
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._clear_preview(
                ui_text("required_manual_software_version", self.language).format(
                    type=manual_project_type.label
                )
            )
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
                    software_version_overrides=self._software_version_overrides(),
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
            self._set_software_version_visible(manual_project_type is not None)
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

        if not confirm_storage_paths_ready(
            parent=self,
            atu_path=self.config.atu_path,
            his_path=self.config.his_path,
            language=self.language,
        ):
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
        self._load_manual_software_version(self._manual_version_project_type())
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
            software_versions=self.config.software_versions,
            show_startup_instructions=self.config.show_startup_instructions,
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

    def _manual_version_project_type(
        self,
        selected_project_types: list[ProjectType] | None = None,
    ) -> ProjectType | None:
        """Return the selected project type that requires a configured version."""

        if selected_project_types is None and not hasattr(self, "type_checkboxes"):
            return None
        for project_type in selected_project_types or self._selected_project_types():
            if getattr(project_type, "manual_version_required", False):
                return project_type
        return None

    def _load_manual_software_version(self, project_type: ProjectType | None) -> None:
        """Load the persisted manual software version into the input field."""

        if project_type is None:
            if self.software_version_input.text():
                self.software_version_input.blockSignals(True)
                self.software_version_input.clear()
                self.software_version_input.blockSignals(False)
            return
        if not self.config or project_type is None:
            return
        version = (self.config.software_versions or {}).get(project_type.key, "")
        if self.software_version_input.text() == version:
            return
        self.software_version_input.blockSignals(True)
        self.software_version_input.setText(version)
        self.software_version_input.blockSignals(False)

    def on_software_version_changed(self) -> None:
        """Persist manual software versions and refresh the current preview."""

        project_type = self._manual_version_project_type()
        if self.config and project_type is not None:
            software_versions = dict(self.config.software_versions or {})
            version = self.software_version_input.text().strip()
            if version:
                software_versions[project_type.key] = version
            else:
                software_versions.pop(project_type.key, None)
            self.config = AppConfig(
                collaborator=self.config.collaborator,
                atu_path=self.config.atu_path,
                his_path=self.config.his_path,
                language=self.config.language,
                project_types=self.config.project_types,
                software_versions=software_versions,
                show_startup_instructions=self.config.show_startup_instructions,
            )
            save_config(self.config_path, self.config)
        self.refresh_preview()

    def _software_version_overrides(self) -> dict[str, str]:
        """Return manual software versions keyed by project type."""

        software_versions = dict(self.config.software_versions or {}) if self.config else {}
        project_type = self._manual_version_project_type()
        version = self._software_version_override()
        if project_type is not None and version:
            software_versions[project_type.key] = version
        return software_versions

    def _set_software_version_visible(self, visible: bool) -> None:
        """Toggle the manual software version fallback controls."""

        project_type = self._manual_version_project_type()
        label_key = (
            "ingeteam_software_version"
            if project_type is not None and project_type.key == "ingeteam"
            else "software_version"
        )
        self.software_version_label.setText(ui_text(label_key, self.language))
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
        self._set_language_button_icon(self.language_button)
        if self.config:
            self.config = AppConfig(
                collaborator=self.config.collaborator,
                atu_path=self.config.atu_path,
                his_path=self.config.his_path,
                language=self.language,
                project_types=self.config.project_types,
                software_versions=self.config.software_versions,
                show_startup_instructions=self.config.show_startup_instructions,
            )
            save_config(self.config_path, self.config)
        self.retranslate_ui()
        if self.current_plans or self.atu_duplicate_plans:
            self._show_plans(self.current_plans, self.atu_duplicate_plans)

    def _set_language_button_icon(self, button: QPushButton) -> None:
        """Show the target-language flag icon on a language button."""

        button.setIcon(QIcon(str(language_flag_path(self.language))))

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
        self._set_language_button_icon(self.language_button)
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
        self._set_software_version_visible(self.software_version_input.isVisible())
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


class StartupInstructionsDialog(QDialog):
    """Instruction dialog shown when the application starts."""

    def __init__(self, *, language: str = DEFAULT_LANGUAGE, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self.do_not_show_again = False
        self.setMinimumWidth(700)

        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        self.language_button = QPushButton()
        configure_language_button(self.language_button)
        self.language_button.clicked.connect(self.toggle_language)
        header.addWidget(self.title_label, 1)
        header.addWidget(self.language_button)
        layout.addLayout(header)

        self.body_label = QLabel()
        self.body_label.setTextFormat(Qt.TextFormat.RichText)
        self.body_label.setWordWrap(True)
        self.body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.body_label)

        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self.accept)
        layout.addWidget(self.buttons)
        self.retranslate()

    def toggle_language(self) -> None:
        """Switch the instruction dialog language without closing it."""

        self.language = "en_US" if self.language == "pt_BR" else "pt_BR"
        self.retranslate()

    def retranslate(self) -> None:
        """Apply the current language to every instruction dialog label."""

        texts = self._texts(self.language)
        self.setWindowTitle(texts["title"])
        self.title_label.setText(f"<h2>{texts['title']}</h2>")
        self.body_label.setText(texts["body"])
        self.checkbox.setText(texts["do_not_show_again"])
        self.language_button.setIcon(QIcon(str(language_flag_path(self.language))))
        self.language_button.setToolTip(texts["language_tooltip"])

    def accept(self) -> None:
        """Store the opt-out state before closing the dialog."""

        self.do_not_show_again = self.checkbox.isChecked()
        super().accept()

    @staticmethod
    def _texts(language: str) -> dict[str, str]:
        """Return translated instruction dialog text."""

        if language == "en_US":
            return {
                "title": "Usage Instructions",
                "do_not_show_again": "Do not show again",
                "language_tooltip": "Language",
                "body": """
                <p>This executable must stay inside the folder that contains the
                working files for the substation, application, bay, or equipment
                that will be processed.</p>

                <p><b>Recommended structure:</b></p>
                <pre>Local folder/
└─ SE, ETD, bay, or equipment folder/
   ├─ IED Backup Manager.exe
   ├─ config.json
   ├─ SE-XXX_GENERIC-COMMENT_20260622_1350.dz5
   ├─ ETD-YYY_GENERIC-COMMENT_20260612_0350.dz5
   ├─ ETD-YYY_OTHER-COMMENT.rdb
   └─ other working files</pre>

                <p><b>File naming rules:</b></p>
                <ul>
                  <li>The SE, ETD, bay, or equipment name must come before the
                  first underscore <code>"_"</code>.</li>
                  <li>Use hyphen <code>"-"</code> to separate text inside the SE,
                  ETD, bay, or equipment name.</li>
                  <li>All text after the first underscore <code>"_"</code> is treated
                  as a user comment and will not be used to identify the backup.</li>
                  <li>The backup will be grouped by the text before the first
                  underscore <code>"_"</code>.</li>
                </ul>

                <p><b>Example 1 - Siemens backup</b></p>
                <p>Input file:</p>
                <pre>SE-XXX_GENERIC-COMMENT_20260622_1350.dz5</pre>
                <p>Output:</p>
                <pre>DIGSIn-Vmmm_SE-XXX_YYYYMMDD-HHMM_COLLABORATOR_STAGE.zip</pre>
                <p><code>DIGSIn</code> represents the DIGSI family, for example
                <code>DIGSI5</code>, and <code>Vmmm</code> represents the detected
                version, for example <code>V10.00</code>.</p>

                <p><b>Example 2 - Multiple IEDs from the same SE</b></p>
                <p>Input files:</p>
                <pre>ETD-YYY_GENERIC-COMMENT_20260612_0350.dz5
ETD-YYY_OTHER-COMMENT.rdb</pre>
                <p>Output:</p>
                <pre>IED-PACK_ETD-YYY_YYYYMMDD-HHMM_COLLABORATOR_STAGE.zip</pre>
                <p>The ZIP will include <code>IEDS-BACKUP-INFO.txt</code> with
                versions and included file details.</p>

                <p>Before generating backups, check the <b>Project</b> column in the
                batch preview.</p>
                """,
            }

        return {
            "title": "Instruções de uso",
            "do_not_show_again": "Não exibir novamente",
            "language_tooltip": "Idioma",
            "body": """
            <p>Este executável deve ficar dentro da pasta que contém os arquivos
            de trabalho da subestação, aplicação ou vãos/equipamentos que serão
            processados.</p>

            <p><b>Estrutura recomendada:</b></p>
            <pre>Pasta local/
└─ Pasta da SE, ETD, vão ou equipamento/
   ├─ IED Backup Manager.exe
   ├─ config.json
   ├─ SE-XXX_COMENTARIO-GENERICO_20260622_1350.dz5
   ├─ ETD-YYY_COMENTARIO-GENERICO_20260612_0350.dz5
   ├─ ETD-YYY_OUTRO-COMENTARIO.rdb
   └─ outros arquivos de trabalho</pre>

            <p><b>Regras para nome dos arquivos:</b></p>
            <ul>
              <li>O nome da SE, ETD, vão ou equipamento deve vir antes do primeiro
              sublinhado <code>"_"</code>.</li>
              <li>Use hífen <code>"-"</code> para separar textos dentro do nome da SE,
              ETD, vão ou equipamento.</li>
              <li>Todo texto depois do primeiro sublinhado <code>"_"</code> é tratado
              como comentário do usuário e não será usado para identificar o backup.</li>
              <li>O backup será agrupado pelo trecho antes do primeiro sublinhado
              <code>"_"</code>.</li>
            </ul>

            <p><b>Exemplo 1 - Backup Siemens</b></p>
            <p>Arquivo de entrada:</p>
            <pre>SE-XXX_COMENTARIO-GENERICO_20260622_1350.dz5</pre>
            <p>Saída:</p>
            <pre>DIGSIn-Vmmm_SE-XXX_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip</pre>
            <p>Onde <code>DIGSIn</code> representa a família do DIGSI, por exemplo
            <code>DIGSI5</code>, e <code>Vmmm</code> representa a versão detectada,
            por exemplo <code>V10.00</code>.</p>

            <p><b>Exemplo 2 - Múltiplos IEDs da mesma SE</b></p>
            <p>Arquivos de entrada:</p>
            <pre>ETD-YYY_COMENTARIO-GENERICO_20260612_0350.dz5
ETD-YYY_OUTRO-COMENTARIO.rdb</pre>
            <p>Saída:</p>
            <pre>IED-PACK_ETD-YYY_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip</pre>
            <p>Dentro do ZIP haverá o arquivo <code>IEDS-BACKUP-INFO.txt</code> com
            versões e detalhes dos arquivos incluídos.</p>

            <p>Antes de gerar backups, confira a coluna <b>Projeto</b> na prévia do lote.</p>
            """,
        }


def get_runtime_project_dir() -> Path:
    """Return the executable folder in production or cwd during development."""

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()
