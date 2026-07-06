"""Main Qt window for previewing and executing backup batches."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
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
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from src.config.config_manager import AppConfig, load_config, save_config
from src.core.backup_service import (
    AtuDuplicatePlan,
    BackupPlan,
    BackupResult,
    summarize_results,
)
from src.core.i18n import DEFAULT_LANGUAGE, message_label, status_label, ui_text
from src.core.naming import BackupStage, normalize_stage
from src.core.project_types.base import ProjectType, ProjectVersionRequiredError
from src.core.project_types.registry import PROJECT_TYPES, get_project_type
from src.gui.backup_application_service import (
    PreviewRequest,
    PreviewValidationCode,
    PreviewValidationError,
    build_preview,
    manual_version_project_type,
    summarize_preview,
)
from src.gui.backup_confirmation import (
    duplicate_problem_files,
    execution_confirmation_message,
    integrity_conflict_details,
)
from src.gui.backup_worker import BackupExecutionWorker, BackupProgressEvent
from src.gui.language_button import configure_language_button
from src.gui.preview_table import populate_preview_table, source_files_text
from src.gui.resources import app_icon_path, help_document_url, language_flag_path, repository_url
from src.gui.runtime import get_runtime_project_dir
from src.gui.settings_window import SettingsWindow
from src.gui.startup_instructions import StartupInstructionsDialog
from src.gui.storage_paths import confirm_storage_paths_ready
from src.gui.summary_text import format_summary_text
from src.gui.update_worker import UpdateCheckWorker
from src.version import APP_DISPLAY_NAME

MANUAL_STAGE_DATA = "__manual_stage__"

class MainWindow(QMainWindow):
    """Main GUI controller for configuration, preview, execution, and logs."""

    def __init__(
        self,
        *,
        project_dir: Path | None = None,
        auto_startup_dialogs: bool = True,
    ) -> None:
        super().__init__()
        self.project_dir = (project_dir or get_runtime_project_dir()).resolve()
        self.config_path = self.project_dir / "config.json"
        self.config = self._load_config()
        self.current_plans: list[BackupPlan] = []
        self.atu_duplicate_plans: list[AtuDuplicatePlan] = []
        self.language = self.config.language if self.config else DEFAULT_LANGUAGE
        self.pending_show_startup_instructions: bool | None = None
        self.backup_thread: QThread | None = None
        self.backup_worker: BackupExecutionWorker | None = None
        self.update_thread: QThread | None = None
        self.update_worker: UpdateCheckWorker | None = None
        self.latest_release_url: str | None = None
        self.progress_dialog: QProgressDialog | None = None
        self.cancel_requested = False

        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.setMinimumSize(920, 620)
        self._resize_to_available_screen()
        self._build_ui()
        self._load_manual_software_version(self._manual_version_project_type())
        if auto_startup_dialogs:
            self.schedule_startup_dialogs()
        self.refresh_preview()
        self.schedule_update_check()

    def schedule_startup_dialogs(self) -> None:
        """Open startup dialogs after the window has entered the event loop."""

        QTimer.singleShot(0, self._run_startup_dialogs)

    def schedule_update_check(self) -> None:
        """Check for new public releases shortly after startup."""

        QTimer.singleShot(750, self._start_update_check)

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
        self.help_button = QPushButton()
        self.help_button.clicked.connect(self.open_help_document)
        self.current_folder_title = QLabel()
        top.addWidget(self.current_folder_title)
        top.addWidget(self.project_dir_label, 1)
        top.addWidget(self.refresh_button)
        top.addWidget(self.settings_button)
        top.addWidget(self.help_button)
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

        footer = QHBoxLayout()
        self.update_available_label = QLabel()
        self.update_available_label.setTextFormat(Qt.TextFormat.RichText)
        self.update_available_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.update_available_label.linkActivated.connect(self.open_latest_release)
        self.update_available_label.setVisible(False)
        footer.addWidget(self.update_available_label)
        footer.addStretch()
        self.license_button = QPushButton("©")
        self.license_button.setFlat(True)
        self.license_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.license_button.setFixedSize(28, 24)
        self.license_button.clicked.connect(self.show_license_notice)
        footer.addWidget(self.license_button)
        layout.addLayout(footer)

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
            ("sha_conflicts", "sha_conflicts"),
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
            lambda: self.open_folder(
                self.config.atu_path if self.config else None,
                "atu_folder",
            )
        )
        self.open_his_button.clicked.connect(
            lambda: self.open_folder(
                self.config.his_path if self.config else None,
                "his_folder",
            )
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

    def open_help_document(self) -> None:
        """Open the public user help document with the system default browser."""

        url = help_document_url()
        if not QDesktopServices.openUrl(QUrl(url)):
            QMessageBox.warning(
                self,
                ui_text("help", self.language),
                ui_text("help_open_failed", self.language).format(url=url),
            )

    def _start_update_check(self) -> None:
        """Start the background update checker if one is not already running."""

        if self.update_thread is not None:
            return

        self.update_thread = QThread(self)
        self.update_worker = UpdateCheckWorker()
        self.update_worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self._on_update_check_finished)
        self.update_worker.failed.connect(self._on_update_check_failed)
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.failed.connect(self.update_thread.quit)
        self.update_thread.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self._clear_update_worker)
        self.update_thread.start()

    def _on_update_check_finished(self, result) -> None:
        """Show the update notice only when a newer release exists."""

        if not result.update_available:
            self.latest_release_url = None
            self.update_available_label.setVisible(False)
            return

        self.latest_release_url = result.release_url
        self.update_available_label.setText(
            f'<a href="{result.release_url}" style="color:#d92d20; '
            f'text-decoration:none; font-weight:600;">'
            f'{ui_text("update_available", self.language)}</a>'
        )
        self.update_available_label.setToolTip(
            ui_text("update_available_tooltip", self.language).format(
                version=result.latest_version
            )
        )
        self.update_available_label.setVisible(True)

    def _on_update_check_failed(self, _message: str) -> None:
        """Keep startup quiet when update checks fail."""

        self.latest_release_url = None
        self.update_available_label.setVisible(False)

    def _clear_update_worker(self) -> None:
        """Release update worker/thread references after completion."""

        self.update_thread = None
        self.update_worker = None

    def open_latest_release(self, url: str | None = None) -> None:
        """Open the latest release URL in the default browser."""

        target = url or self.latest_release_url
        if target:
            QDesktopServices.openUrl(QUrl(target))

    def show_license_notice(self) -> None:
        """Show a compact copyright and license notice."""

        dialog = QDialog(self)
        dialog.setWindowTitle(ui_text("license", self.language))
        layout = QVBoxLayout(dialog)
        label = QLabel(
            ui_text("license_message", self.language).format(url=repository_url())
        )
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        layout.addWidget(label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
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

        selected_project_types = self._selected_project_types()
        manual_project_type = self._manual_version_project_type(selected_project_types)
        self._set_software_version_visible(manual_project_type is not None)

        try:
            preview = build_preview(
                PreviewRequest(
                    project_dir=self.project_dir,
                    config=self.config,
                    selected_project_types=selected_project_types,
                    selected_stage=self._selected_stage(),
                    latest_only=self.latest_only_checkbox.isChecked(),
                    software_version_override=self._software_version_override(),
                    software_version_overrides=self._software_version_overrides(),
                )
            )
            self.current_plans = preview.plans
            self.atu_duplicate_plans = preview.duplicate_plans
            self._set_software_version_visible(preview.manual_project_type is not None)
        except PreviewValidationError as exc:
            self.current_plans = []
            self.atu_duplicate_plans = []
            self._set_software_version_visible(exc.project_type is not None)
            if exc.code == PreviewValidationCode.REQUIRED_MANUAL_SOFTWARE_VERSION:
                self._clear_preview(
                    ui_text("required_manual_software_version", self.language).format(
                        type=exc.project_type.label if exc.project_type else ""
                    )
                )
            else:
                self._clear_preview(ui_text(exc.code.value, self.language))
            return
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
        summary = summarize_preview(self.current_plans, self.atu_duplicate_plans)
        if summary.sha_conflicts:
            QMessageBox.warning(
                self,
                ui_text("integrity_conflicts_title", self.language),
                ui_text("integrity_conflicts_found", self.language).format(
                    details=integrity_conflict_details(self.current_plans)
                ),
            )
            return
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
            answer = QMessageBox.question(
                self,
                ui_text("duplicates_title", self.language),
                f"{ui_text('duplicate_files_found', self.language)}\n\n"
                f"{duplicate_problem_files(self.atu_duplicate_plans)}\n\n"
                f"{ui_text('duplicates_question', self.language)}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            fix_duplicates = answer == QMessageBox.StandardButton.Yes

        answer = QMessageBox.question(
            self,
            ui_text("confirm_execution", self.language),
            execution_confirmation_message(
                summary,
                fix_duplicates=fix_duplicates,
                language=self.language,
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._start_backup_worker(fix_duplicates)

    def _start_backup_worker(
        self,
        fix_duplicates: bool,
    ) -> None:
        """Start backup execution in a worker thread."""

        if not self.config:
            return

        plans = self.current_plans
        self.cancel_requested = False
        self.progress_dialog = QProgressDialog(
            ui_text("progress_starting", self.language),
            ui_text("cancel", self.language),
            0,
            1000,
            self,
        )
        self.progress_dialog.setWindowTitle(ui_text("progress_title", self.language))
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setValue(0)
        progress_bar = self.progress_dialog.findChild(QProgressBar)
        if progress_bar:
            progress_bar.setTextVisible(False)
        self.progress_dialog.canceled.connect(self._request_backup_cancel)

        self.generate_button.setEnabled(False)
        self.backup_thread = QThread(self)
        self.backup_worker = BackupExecutionWorker(
            plans=plans,
            atu_duplicate_plans=self.atu_duplicate_plans,
            atu_path=self.config.atu_path,
            his_path=self.config.his_path,
            fix_duplicates=fix_duplicates,
        )
        self.backup_worker.moveToThread(self.backup_thread)
        self.backup_thread.started.connect(self.backup_worker.run)
        self.backup_worker.progress.connect(self._on_backup_progress)
        self.backup_worker.finished.connect(self._on_backup_finished)
        self.backup_worker.failed.connect(self._on_backup_failed)
        self.backup_worker.finished.connect(self.backup_thread.quit)
        self.backup_worker.failed.connect(self.backup_thread.quit)
        self.backup_thread.finished.connect(self.backup_worker.deleteLater)
        self.backup_thread.finished.connect(self._clear_backup_worker)
        self.backup_thread.start()

    def _request_backup_cancel(self) -> None:
        """Ask the worker to stop before the next file starts."""

        self.cancel_requested = True
        if self.backup_worker:
            self.backup_worker.request_cancel()
        if self.progress_dialog:
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.setLabelText(ui_text("progress_cancel_requested", self.language))
            self.progress_dialog.show()

    def _on_backup_progress(self, event: BackupProgressEvent) -> None:
        """Update the progress dialog from a worker progress event."""

        if not self.progress_dialog:
            return

        percent = (
            100
            if event.total_bytes <= 0
            else min(100, int(event.current_bytes * 100 / event.total_bytes))
        )
        self.progress_dialog.setValue(percent * 10)
        if event.is_duplicate_fix:
            text = ui_text("progress_fixing_atu_detail", self.language).format(
                phase=ui_text(f"progress_phase_{event.phase}", self.language),
                percent=percent,
            )
        else:
            text = ui_text("progress_processing_file", self.language).format(
                index=event.index,
                total=event.total,
                file=event.file_text,
                phase=ui_text(f"progress_phase_{event.phase}", self.language),
                percent=percent,
            )
        if self.cancel_requested:
            text = f"{text}\n\n{ui_text('progress_cancel_pending', self.language)}"
        self.progress_dialog.setLabelText(text)

    def _on_backup_finished(
        self,
        duplicate_results: list[AtuDuplicatePlan],
        results: list[BackupResult],
        canceled: bool,
    ) -> None:
        """Handle successful or canceled worker completion."""

        self._close_progress_dialog(ui_text("progress_finished", self.language))
        self.generate_button.setEnabled(True)
        self._write_execution_log(duplicate_results, results)
        summary = summarize_results([*results, *duplicate_results])
        if canceled:
            title = ui_text("backup_canceled_title", self.language)
            body = (
                ui_text("backup_canceled_message", self.language).format(
                    completed=len(results) + len(duplicate_results)
                )
                + "\n\n"
                + format_summary_text(summary, self.language)
            )
        else:
            title = ui_text("backup_processed_title", self.language)
            body = format_summary_text(summary, self.language)
        QMessageBox.information(self, title, body)
        self.refresh_preview()

    def _on_backup_failed(self, message: str) -> None:
        """Handle worker failure."""

        self._close_progress_dialog("")
        self.generate_button.setEnabled(True)
        QMessageBox.critical(self, ui_text("backup_failed", self.language), message)
        self.log_output.appendPlainText(f"{ui_text('error_prefix', self.language)}: {message}")

    def _write_execution_log(
        self,
        duplicate_results: list[AtuDuplicatePlan],
        results: list[BackupResult],
    ) -> None:
        """Write the execution result log and summary."""

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
                f"{source_files_text(result.source_files or (result.source_file,))} "
                f"-> {result.final_path.name} "
                f"[{status_label(result.status, self.language)}]"
            )
        summary = summarize_results([*results, *duplicate_results])
        self.log_output.appendPlainText(
            f"{ui_text('completed_at', self.language)} {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        self.log_output.appendPlainText(format_summary_text(summary, self.language))

    def _close_progress_dialog(self, final_text: str) -> None:
        """Close the progress dialog after worker completion."""

        if not self.progress_dialog:
            return
        if final_text:
            self.progress_dialog.setLabelText(final_text)
            self.progress_dialog.setValue(1000)
        self.progress_dialog.blockSignals(True)
        self.progress_dialog.close()
        self.progress_dialog = None

    def _clear_backup_worker(self) -> None:
        """Release worker/thread references after the thread stops."""

        self.backup_thread = None
        self.backup_worker = None

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
        populate_preview_table(
            self.preview_table,
            plans=plans,
            duplicate_plans=duplicate_plans,
            language=self.language,
        )
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
                f"{source_files_text(plan.source_files or (plan.source_file,))} "
                f"-> {plan.destination_path.name} "
                f"[{status_label(plan.status, self.language)}]"
            )

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
        return manual_version_project_type(selected_project_types or self._selected_project_types())

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
        self.summary_labels["sha_conflicts"].setText(str(summary.sha_conflicts))
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
        self.help_button.setText(ui_text("help", self.language))
        self.license_button.setToolTip(ui_text("license_tooltip", self.language))
        self.license_button.setStyleSheet(
            "QPushButton { border: none; padding: 0; font-weight: 600; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        if self.update_available_label.isVisible() and self.latest_release_url:
            self.update_available_label.setText(
                f'<a href="{self.latest_release_url}" style="color:#d92d20; '
                f'text-decoration:none; font-weight:600;">'
                f'{ui_text("update_available", self.language)}</a>'
            )
        self.summary_group.setTitle(ui_text("summary", self.language))
        self.preview_group.setTitle(ui_text("preview", self.language))
        self.action_group.setTitle(ui_text("execution", self.language))
        self.log_output.setPlaceholderText(ui_text("preview", self.language))
        self.preview_table.setHorizontalHeaderLabels(
            [
                ui_text("action", self.language),
                ui_text("file", self.language),
                ui_text("project", self.language),
                ui_text("version", self.language),
                ui_text("timestamp", self.language),
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

    def open_folder(self, folder: Path | None, label_key: str) -> None:
        """Open a configured folder, asking before recreating missing paths."""

        if not folder:
            return

        label = ui_text(label_key, self.language)
        target = folder.expanduser().resolve(strict=False)
        if target.exists() and not target.is_dir():
            QMessageBox.warning(
                self,
                ui_text("storage_paths_invalid_title", self.language),
                ui_text("storage_folder_not_directory", self.language).format(
                    label=label,
                    path=target,
                ),
            )
            return

        if not target.exists():
            answer = QMessageBox.question(
                self,
                ui_text("storage_folder_missing_title", self.language),
                ui_text("storage_folder_missing_message", self.language).format(
                    label=label,
                    path=target,
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                QMessageBox.critical(
                    self,
                    ui_text("storage_paths_invalid_title", self.language),
                    ui_text("storage_paths_create_failed", self.language).format(error=exc),
                )
                return

        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(target))):
            QMessageBox.warning(
                self,
                ui_text("storage_paths_invalid_title", self.language),
                ui_text("storage_folder_open_failed", self.language).format(path=target),
            )
