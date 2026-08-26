"""GUI entry point for the packaged Windows application."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen

from src.core.app_logging import get_logger, setup_application_logging
from src.core.i18n import DEFAULT_LANGUAGE, ui_text
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


def create_splash_screen(app: QApplication, *, language: str = DEFAULT_LANGUAGE) -> QSplashScreen:
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
    painter.drawText(42, 148, ui_text("splash_loading", language))

    painter.setPen(QColor(accent))
    painter.drawLine(42, 172, 418, 172)

    status_font = QFont()
    status_font.setPointSize(9)
    painter.setFont(status_font)
    painter.setPen(muted)
    painter.drawText(42, 202, ui_text("splash_preparing_interface", language))
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

    log_file = setup_application_logging(APP_VERSION)
    logger = get_logger("startup")
    qInstallMessageHandler(_qt_message_handler)
    try:
        return _run_app()
    except Exception as exc:
        logger.exception("Fatal application error")
        _show_fatal_error(exc, log_file)
        return 1


def _run_app() -> int:
    """Run the Qt event loop after diagnostics are ready."""

    logger = get_logger("startup")
    logger.info("Parsing arguments")
    args = parse_args()
    language = _startup_language(args.project_dir or Path.cwd())
    logger.info("Creating QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setWindowIcon(QIcon(str(app_icon_path())))

    logger.info("Showing splash screen")
    splash = create_splash_screen(app, language=language)
    splash.show()
    splash.showMessage(
        ui_text("splash_loading_modules", language),
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        app.palette().windowText().color(),
    )
    app.processEvents()

    logger.info("Importing main window")
    from src.gui.main_window import MainWindow

    splash.showMessage(
        ui_text("splash_reading_settings", language),
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        app.palette().windowText().color(),
    )
    app.processEvents()

    logger.info("Creating main window")
    window = MainWindow(project_dir=args.project_dir, auto_startup_dialogs=False)
    splash.showMessage(
        ui_text("splash_opening_application", window.language),
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        app.palette().windowText().color(),
    )
    app.processEvents()
    logger.info("Showing main window")
    window.show()
    close_splash_screen(splash, window)
    app.processEvents()
    logger.info("Scheduling startup dialogs")
    window.schedule_startup_dialogs()
    logger.info("Entering Qt event loop")
    return app.exec()


def _qt_message_handler(mode, _context, message: str) -> None:
    """Forward Qt runtime messages to the daily log."""

    level = logging.WARNING
    if "critical" in str(mode).lower() or "fatal" in str(mode).lower():
        level = logging.ERROR
    get_logger("qt").log(level, message)


def _show_fatal_error(exc: Exception, log_file: Path) -> None:
    """Show a last-resort startup error dialog when possible."""

    try:
        app = QApplication.instance() or QApplication(sys.argv)
        language = _startup_language(Path.cwd())
        QMessageBox.critical(
            None,
            "IED Backup Manager",
            ui_text("fatal_startup_error", language).format(
                error=exc,
                log_file=log_file,
            ),
        )
        app.processEvents()
    except Exception:
        get_logger("startup").exception("Could not show fatal error dialog")


def _startup_language(project_dir: Path) -> str:
    """Read the saved language before the main window/config loader is available."""

    config_path = project_dir / "config.json"
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_LANGUAGE
    language = raw.get("language")
    if language in {"pt_BR", "en_US"}:
        return language
    return DEFAULT_LANGUAGE


if __name__ == "__main__":
    raise SystemExit(main())
