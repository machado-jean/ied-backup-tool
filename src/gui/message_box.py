"""Small QMessageBox helpers that respect the app language setting."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget

from src.core.i18n import ui_text


def question_yes_no(
    parent: QWidget,
    *,
    title: str,
    text: str,
    language: str,
    default_button: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
) -> QMessageBox.StandardButton:
    """Ask a Yes/No question with button labels translated by the app."""

    message = QMessageBox(parent)
    message.setIcon(QMessageBox.Icon.Question)
    message.setWindowTitle(title)
    message.setText(text)
    message.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    message.setDefaultButton(default_button)
    translate_yes_no_buttons(message, language)
    return QMessageBox.StandardButton(message.exec())


def translate_yes_no_buttons(message: QMessageBox, language: str) -> None:
    """Apply app translations to existing Yes/No buttons."""

    yes_button = message.button(QMessageBox.StandardButton.Yes)
    no_button = message.button(QMessageBox.StandardButton.No)
    if yes_button is not None:
        yes_button.setText(ui_text("yes", language))
    if no_button is not None:
        no_button.setText(ui_text("no", language))
