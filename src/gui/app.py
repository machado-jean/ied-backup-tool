"""GUI entry point for the packaged Windows application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from src.gui.resources import app_icon_path
from src.version import APP_NAME, APP_VERSION


def parse_args() -> argparse.Namespace:
    """Parse development-only GUI arguments."""

    parser = argparse.ArgumentParser(description="IED Backup Manager GUI")
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Pasta processada pela GUI. Uso principal: testes em desenvolvimento.",
    )
    return parser.parse_args()


def create_splash_screen(app: QApplication) -> QSplashScreen:
    """Create a compact startup splash that follows the active Qt palette."""

    pixmap = QPixmap(460, 240)
    palette = app.palette()
    background = palette.window().color()
    foreground = palette.windowText().color()
    muted = QColor(foreground)
    muted.setAlpha(165)
    accent = QColor("#d8b23f")

    pixmap.fill(background)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    icon = QPixmap(str(app_icon_path())).scaled(
        56,
        56,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    painter.drawPixmap(42, 44, icon)

    title_font = QFont()
    title_font.setPointSize(18)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.setPen(foreground)
    painter.drawText(118, 62, APP_NAME)

    version_font = QFont()
    version_font.setPointSize(10)
    painter.setFont(version_font)
    painter.setPen(muted)
    painter.drawText(120, 88, f"v{APP_VERSION}")

    loading_font = QFont()
    loading_font.setPointSize(11)
    loading_font.setBold(True)
    painter.setFont(loading_font)
    painter.setPen(foreground)
    painter.drawText(42, 148, "Carregando...")

    painter.setPen(QColor(accent))
    painter.drawLine(42, 172, 418, 172)

    status_font = QFont()
    status_font.setPointSize(9)
    painter.setFont(status_font)
    painter.setPen(muted)
    painter.drawText(42, 202, "Preparando interface")
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash


def close_splash_screen(splash: QSplashScreen, window) -> None:
    """Close the splash reliably after the main window has been shown."""

    splash.hide()
    splash.close()
    splash.deleteLater()


def main() -> int:
    """Start the Qt application and show the main window."""

    args = parse_args()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setWindowIcon(QIcon(str(app_icon_path())))

    splash = create_splash_screen(app)
    splash.show()
    splash.showMessage(
        "Carregando módulos...",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        app.palette().windowText().color(),
    )
    app.processEvents()

    from src.gui.main_window import MainWindow

    splash.showMessage(
        "Lendo configurações...",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        app.palette().windowText().color(),
    )
    app.processEvents()

    window = MainWindow(project_dir=args.project_dir, auto_startup_dialogs=False)
    splash.showMessage(
        "Abrindo aplicação...",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        app.palette().windowText().color(),
    )
    app.processEvents()
    window.show()
    close_splash_screen(splash, window)
    app.processEvents()
    window.schedule_startup_dialogs()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
