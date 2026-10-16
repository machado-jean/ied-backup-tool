"""Small QMessageBox helpers that respect the app language setting."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget

from src.core.i18n import ui_text


def ask_software_choice(
    parent: QWidget,
    *,
    project: str,
    existing: str,
    new: str,
    language: str,
) -> str:
    """Ask whether different software families coexist or replace one another."""

    message, keep_button, replace_button = create_software_choice_message_box(
        parent,
        project=project,
        existing=existing,
        new=new,
        language=language,
    )
    message.exec()
    clicked = message.clickedButton()
    if clicked is keep_button:
        return "keep"
    if clicked is replace_button:
        return "replace"
    return "cancel"


def create_software_choice_message_box(
    parent: QWidget,
    *,
    project: str,
    existing: str,
    new: str,
    language: str,
) -> tuple[QMessageBox, object, object]:
    """Build the cross-software decision dialog for execution or documentation."""

    message = QMessageBox(parent)
    message.setIcon(QMessageBox.Icon.Question)
    message.setWindowTitle(ui_text("software_choice_title", language))
    message.setText(
        ui_text("software_choice_message", language).format(
            project=project,
            existing=existing,
            new=new,
        )
    )
    keep_button = message.addButton(
        ui_text("software_choice_keep", language),
        QMessageBox.ButtonRole.AcceptRole,
    )
    replace_button = message.addButton(
        ui_text("software_choice_replace", language),
        QMessageBox.ButtonRole.DestructiveRole,
    )
    cancel_button = message.addButton(
        ui_text("cancel", language),
        QMessageBox.ButtonRole.RejectRole,
    )
    message.setDefaultButton(cancel_button)
    return message, keep_button, replace_button


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
