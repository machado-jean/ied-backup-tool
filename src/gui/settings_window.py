"""Settings dialog used to create and edit the local config.json file."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.config.config_manager import AppConfig, HistoryCleanupConfig, save_config
from src.core.i18n import DEFAULT_LANGUAGE, ui_text
from src.gui.storage_paths import confirm_storage_paths_ready


class SettingsWindow(QDialog):
    """Modal dialog for collaborator, ATU path, and HIS path configuration."""

    saved = Signal(AppConfig)

    def __init__(
        self,
        *,
        config_path: Path,
        config: AppConfig | None,
        language: str = DEFAULT_LANGUAGE,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.config_path = config_path
        self.config = config
        self.language = language
        self.setWindowTitle(ui_text("settings", self.language))
        self.setMinimumWidth(560)

        self.first_name_input = QLineEdit(config.collaborator_first_name if config else "")
        self.last_name_input = QLineEdit(config.collaborator_last_name if config else "")
        self.atu_input = QLineEdit(str(config.atu_path) if config else "")
        self.his_input = QLineEdit(str(config.his_path) if config else "")

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow(ui_text("first_name", self.language), self.first_name_input)
        form.addRow(ui_text("last_name", self.language), self.last_name_input)
        form.addRow(ui_text("atu_folder", self.language), self._path_row(self.atu_input))
        form.addRow(ui_text("his_folder", self.language), self._path_row(self.his_input))
        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()
        save_button = QPushButton(ui_text("save", self.language))
        cancel_button = QPushButton(ui_text("cancel", self.language))
        save_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

    def _path_row(self, line_edit: QLineEdit) -> QHBoxLayout:
        """Build a path input row with a folder picker button."""

        row = QHBoxLayout()
        browse_button = QPushButton(ui_text("select", self.language))
        browse_button.clicked.connect(lambda: self.select_folder(line_edit))
        row.addWidget(line_edit)
        row.addWidget(browse_button)
        return row

    def select_folder(self, line_edit: QLineEdit) -> None:
        """Open a native folder picker and write the result into an input."""

        folder = QFileDialog.getExistingDirectory(
            self,
            ui_text("select_folder_title", self.language),
            line_edit.text(),
        )
        if folder:
            line_edit.setText(folder)

    def save(self) -> None:
        """Validate fields, persist config.json, and notify the main window."""

        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        atu_path = self.atu_input.text().strip()
        his_path = self.his_input.text().strip()

        missing = []
        if not first_name:
            missing.append(ui_text("first_name", self.language))
        if not last_name:
            missing.append(ui_text("last_name", self.language))
        if not atu_path:
            missing.append(ui_text("atu_folder", self.language))
        if not his_path:
            missing.append(ui_text("his_folder", self.language))
        if missing:
            QMessageBox.warning(
                self,
                ui_text("required_fields", self.language),
                ui_text("fill_fields", self.language) + ": " + ", ".join(missing),
            )
            return

        atu = Path(atu_path)
        his = Path(his_path)
        if not confirm_storage_paths_ready(
            parent=self,
            atu_path=atu,
            his_path=his,
            language=self.language,
        ):
            return

        config = AppConfig(
            collaborator=f"{first_name} {last_name}",
            collaborator_first_name=first_name,
            collaborator_last_name=last_name,
            atu_path=atu,
            his_path=his,
            language=self.config.language if self.config else self.language,
            project_types=self.config.project_types if self.config else (),
            software_versions=self.config.software_versions if self.config else {},
            show_startup_instructions=(
                self.config.show_startup_instructions if self.config else True
            ),
            history_cleanup=(
                self.config.history_cleanup if self.config else HistoryCleanupConfig()
            ),
        )
        save_config(self.config_path, config)
        self.saved.emit(config)
        self.accept()
