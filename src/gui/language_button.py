"""Shared helpers for compact language flag buttons."""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton


def configure_language_button(button: QPushButton) -> None:
    """Set a stable compact size for language flag buttons."""

    button.setFixedSize(44, 30)
    button.setIconSize(QSize(24, 17))
    button.setText("")
