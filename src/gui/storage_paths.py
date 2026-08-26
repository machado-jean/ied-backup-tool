"""GUI prompts for ATU/HIS storage folder validation."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWidget

from src.core.i18n import ui_text
from src.core.path_validation import (
    StoragePathValidationError,
    create_missing_storage_paths,
    validate_storage_paths,
)
from src.gui.message_box import question_yes_no


def confirm_storage_paths_ready(
    *,
    parent: QWidget,
    atu_path: Path,
    his_path: Path,
    language: str,
) -> bool:
    """Validate ATU/HIS paths and ask before creating missing folders."""

    try:
        validation = validate_storage_paths(atu_path, his_path)
    except StoragePathValidationError as exc:
        QMessageBox.warning(
            parent,
            ui_text("storage_paths_invalid_title", language),
            str(exc),
        )
        return False

    if validation.nested_warning:
        answer = question_yes_no(
            parent,
            title=ui_text("storage_paths_nested_title", language),
            text=ui_text("storage_paths_nested_message", language).format(
                detail=validation.nested_warning,
            ),
            language=language,
            default_button=QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False

    if validation.synced_warnings:
        details = "\n".join(f"- {warning}" for warning in validation.synced_warnings)
        QMessageBox.warning(
            parent,
            ui_text("storage_paths_synced_title", language),
            ui_text("storage_paths_synced_message", language).format(details=details),
        )

    if not validation.missing_paths:
        return True

    paths = "\n".join(f"- {path}" for path in validation.missing_paths)
    answer = question_yes_no(
        parent,
        title=ui_text("storage_paths_missing_title", language),
        text=ui_text("storage_paths_missing_message", language).format(paths=paths),
        language=language,
        default_button=QMessageBox.StandardButton.Yes,
    )
    if answer != QMessageBox.StandardButton.Yes:
        return False

    try:
        create_missing_storage_paths(validation)
        validate_storage_paths(atu_path, his_path)
    except (OSError, StoragePathValidationError) as exc:
        QMessageBox.critical(
            parent,
            ui_text("storage_paths_invalid_title", language),
            ui_text("storage_paths_create_failed", language).format(error=exc),
        )
        return False

    return True
