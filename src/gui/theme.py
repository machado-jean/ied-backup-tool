"""Application-wide light and dark theme helpers."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QPushButton, QStyleFactory

ThemeName = Literal["light", "dark"]


def normalize_theme(value: object) -> ThemeName | None:
    """Return a supported explicit theme or ``None`` for system behavior."""

    return value if value in {"light", "dark"} else None


def effective_theme(app: QApplication, preference: ThemeName | None) -> ThemeName:
    """Resolve an optional preference against the current system/Qt palette."""

    if preference is not None:
        return preference
    color_scheme = app.styleHints().colorScheme()
    if color_scheme == Qt.ColorScheme.Dark:
        return "dark"
    if color_scheme == Qt.ColorScheme.Light:
        return "light"
    return "dark" if app.palette().window().color().lightness() < 128 else "light"


def apply_theme(app: QApplication, preference: ThemeName | None) -> ThemeName:
    """Apply the palette and control contrast for the resolved application theme."""

    resolved = effective_theme(app, preference)
    if preference is not None:
        app.setPalette(_palette(resolved))
    app.setStyleSheet(_style_sheet(resolved))
    return resolved


def configure_theme_button(button: QPushButton) -> None:
    """Give the theme toggle the same compact footprint as the language button."""

    button.setFixedSize(44, 30)
    font = button.font()
    font.setPointSize(14)
    button.setFont(font)


def set_theme_button_state(button: QPushButton, current_theme: ThemeName) -> None:
    """Show the theme the button will activate when clicked."""

    button.setText("☾" if current_theme == "light" else "☀")


class ThemedComboBox(QComboBox):
    """Combo box that finishes styling Qt's native popup after it is created."""

    def showPopup(self) -> None:
        super().showPopup()
        configure_combo_popup(self)


def configure_combo_popup(combo: QComboBox) -> None:
    """Give Qt's separate combo popup window a visible native frame."""

    popup = combo.view().window()
    if not isinstance(popup, QFrame):
        return
    if not popup.property("themeFusionStyle"):
        popup_style = QStyleFactory.create("Fusion")
        if popup_style is not None:
            popup_style.setParent(popup)
            popup.setStyle(popup_style)
            popup.setProperty("themeFusionStyle", True)
    popup.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
    popup.setLineWidth(1)
    palette = popup.palette()
    is_dark = combo.palette().base().color().lightness() < 128
    palette.setColor(
        QPalette.ColorRole.WindowText,
        QColor("#8b949e" if is_dark else "#7f8c99"),
    )
    popup.setPalette(palette)
    popup_layout = popup.layout()
    if popup_layout is not None:
        popup_layout.setContentsMargins(1, 1, 1, 1)
        popup_layout.activate()
    popup.update()


def alert_color(theme: ThemeName) -> str:
    """Return an alert red with sufficient contrast for the active theme."""

    return "#d1242f" if theme == "light" else "#ff7b72"


def _palette(theme: ThemeName) -> QPalette:
    """Build an accessible palette for the requested explicit theme."""

    palette = QPalette()
    colors = (
        {
            "window": "#edf1f5",
            "window_text": "#1f2328",
            "base": "#ffffff",
            "alternate": "#f3f6f9",
            "button": "#f8fafc",
            "button_text": "#1f2328",
            "muted": "#66707b",
            "highlight": "#0969da",
            "highlighted_text": "#ffffff",
            "link": "#0969da",
            "light": "#ffffff",
            "mid": "#aeb6bf",
            "dark": "#69727d",
            "shadow": "#343a40",
        }
        if theme == "light"
        else {
            "window": "#202328",
            "window_text": "#e6e9ed",
            "base": "#15171a",
            "alternate": "#272b31",
            "button": "#2b3037",
            "button_text": "#e6e9ed",
            "muted": "#aab2bd",
            "highlight": "#478be6",
            "highlighted_text": "#ffffff",
            "link": "#77b7ff",
            "light": "#464d57",
            "mid": "#555d68",
            "dark": "#111316",
            "shadow": "#090a0c",
        }
    )
    roles = {
        QPalette.ColorRole.Window: colors["window"],
        QPalette.ColorRole.WindowText: colors["window_text"],
        QPalette.ColorRole.Base: colors["base"],
        QPalette.ColorRole.AlternateBase: colors["alternate"],
        QPalette.ColorRole.ToolTipBase: colors["base"],
        QPalette.ColorRole.ToolTipText: colors["window_text"],
        QPalette.ColorRole.Text: colors["window_text"],
        QPalette.ColorRole.Button: colors["button"],
        QPalette.ColorRole.ButtonText: colors["button_text"],
        QPalette.ColorRole.BrightText: "#ff6b6b",
        QPalette.ColorRole.Link: colors["link"],
        QPalette.ColorRole.LinkVisited: colors["link"],
        QPalette.ColorRole.Highlight: colors["highlight"],
        QPalette.ColorRole.HighlightedText: colors["highlighted_text"],
        QPalette.ColorRole.PlaceholderText: colors["muted"],
        QPalette.ColorRole.Light: colors["light"],
        QPalette.ColorRole.Midlight: colors["mid"],
        QPalette.ColorRole.Mid: colors["mid"],
        QPalette.ColorRole.Dark: colors["dark"],
        QPalette.ColorRole.Shadow: colors["shadow"],
    }
    for role, color in roles.items():
        palette.setColor(role, QColor(color))
    return palette


def _style_sheet(theme: ThemeName) -> str:
    """Return identical widget metrics with colors selected for each theme."""

    colors = (
        {
            "border": "#aeb9c5",
            "field": "#ffffff",
            "focus": "#0969da",
            "header": "#e1e7ee",
            "section_border": "#b9c3ce",
            "button": "#f8fafc",
            "button_border": "#a7b3bf",
            "button_hover": "#e5ebf1",
            "button_hover_border": "#8793a0",
            "button_pressed": "#d5dbe2",
            "disabled_text": "#8c959f",
            "disabled_button": "#f3f4f6",
            "disabled_border": "#d0d6dd",
            "text": "#1f2328",
            "selection": "#0969da",
            "selected_text": "#ffffff",
            "tooltip": "#ffffff",
        }
        if theme == "light"
        else {
            "border": "#69727d",
            "field": "#15171a",
            "focus": "#478be6",
            "header": "#2d333b",
            "section_border": "#444c56",
            "button": "#2b3037",
            "button_border": "#4b535d",
            "button_hover": "#363c44",
            "button_hover_border": "#717b87",
            "button_pressed": "#20242a",
            "disabled_text": "#737b85",
            "disabled_button": "#25292f",
            "disabled_border": "#3b424b",
            "text": "#e6e9ed",
            "selection": "#478be6",
            "selected_text": "#ffffff",
            "tooltip": "#25292f",
        }
    )
    return _STYLE_SHEET_TEMPLATE.format(**colors)


_STYLE_SHEET_TEMPLATE = """
QGroupBox {{
    border: 1px solid {border};
    border-radius: 5px;
    margin-top: 7px;
    padding-top: 7px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
}}
QTableView, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox {{
    background-color: {field};
    border: 1px solid {border};
    border-radius: 4px;
}}
QTableView:focus, QPlainTextEdit:focus, QLineEdit:focus,
QComboBox:focus, QSpinBox:focus {{
    border-color: {focus};
}}
QComboBox {{
    padding-left: 8px;
}}
QComboBox QAbstractItemView {{
    color: {text};
    background-color: {field};
    border: none;
    outline: 0;
    padding: 2px;
    selection-color: {selected_text};
    selection-background-color: {selection};
}}
QComboBox QAbstractItemView::item {{
    min-height: 24px;
    padding: 3px 8px;
}}
QComboBox QAbstractItemView::item:selected {{
    color: {selected_text};
    background-color: {selection};
}}
QHeaderView::section {{
    background-color: {header};
    border: none;
    border-right: 1px solid {section_border};
    border-bottom: 1px solid {section_border};
    padding: 5px;
}}
QPushButton {{
    background-color: {button};
    border: 1px solid {button_border};
    border-radius: 4px;
    padding: 4px 10px;
}}
QPushButton:hover {{
    background-color: {button_hover};
    border-color: {button_hover_border};
}}
QPushButton:pressed {{
    background-color: {button_pressed};
}}
QPushButton:disabled {{
    color: {disabled_text};
    background-color: {disabled_button};
    border-color: {disabled_border};
}}
QProgressBar {{
    color: {text};
    background-color: {field};
    border: 1px solid {border};
    border-radius: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {selection};
    border-radius: 3px;
}}
QToolTip {{
    color: {text};
    background-color: {tooltip};
    border: 1px solid {border};
    padding: 4px;
}}
"""
