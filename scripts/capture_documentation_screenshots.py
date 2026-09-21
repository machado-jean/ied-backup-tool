"""Capture reproducible GUI screenshots using only sanitized public examples."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget

from src.gui.history_cleanup_window import HistoryCleanupWindow
from src.gui.main_window import MainWindow
from src.gui.resources import app_icon_path
from src.gui.settings_window import SettingsWindow
from src.gui.startup_instructions import StartupInstructionsDialog
from src.version import APP_NAME, APP_VERSION


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture documentation screenshots from a sanitized demo workspace."
    )
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/images"))
    return parser.parse_args()


def wait_until(app: QApplication, predicate, *, timeout_seconds: float = 15.0) -> None:
    """Process Qt events until a screenshot prerequisite becomes true."""

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        app.processEvents()
        if predicate():
            return
        time.sleep(0.02)
    raise TimeoutError("Timed out while preparing a documentation screenshot")


def capture(app: QApplication, widget: QWidget, path: Path) -> None:
    """Capture one complete Qt window and save it as a PNG."""

    widget.show()
    app.processEvents()
    screen = widget.screen() or app.primaryScreen()
    if screen is None:
        raise RuntimeError("No screen is available for screenshot capture")
    pixmap = screen.grabWindow(int(widget.winId()))
    path.parent.mkdir(parents=True, exist_ok=True)
    if pixmap.isNull() or not pixmap.save(str(path), "PNG"):
        raise RuntimeError(f"Could not save screenshot: {path}")


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()
    output_dir = args.output_dir.resolve()
    config_path = project_dir / "config.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"Sanitized config not found: {config_path}")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setWindowIcon(QIcon(str(app_icon_path())))

    # Documentation capture must stay deterministic and avoid network activity.
    MainWindow.schedule_update_check = lambda self: None  # type: ignore[method-assign]
    window = MainWindow(project_dir=project_dir, auto_startup_dialogs=False)
    window.resize(1600, 900)
    window.stage_input.setCurrentIndex(1)
    window.refresh_preview()
    window.show()
    try:
        wait_until(
            app,
            lambda: window.preview_thread is None
            and not window.preview_refresh_timer.isActive()
            and bool(window.current_plans),
        )
    except TimeoutError:
        thread_running = bool(window.preview_thread and window.preview_thread.isRunning())
        raise RuntimeError(
            "Preview did not become ready: "
            f"thread_running={thread_running}, "
            f"timer_active={window.preview_refresh_timer.isActive()}, "
            f"plans={len(window.current_plans)}, "
            f"log={window.log_output.toPlainText()!r}"
        ) from None
    capture(app, window, output_dir / "pt-main-window-preview.png")

    settings = SettingsWindow(
        config_path=config_path,
        config=window.config,
        language="pt_BR",
        theme=window.theme_preference,
        parent=window,
    )
    settings.resize(760, settings.sizeHint().height())
    capture(app, settings, output_dir / "pt-settings-window.png")
    settings.close()

    if window.config is None:
        raise RuntimeError("The sanitized configuration was not loaded")
    cleanup = HistoryCleanupWindow(
        config_path=config_path,
        config=window.config,
        language="pt_BR",
        parent=window,
    )
    cleanup.resize(1180, 620)
    capture(app, cleanup, output_dir / "pt-history-cleanup.png")
    cleanup.close()

    instructions = StartupInstructionsDialog(language="pt_BR", parent=window)
    instructions.resize(780, min(900, instructions.sizeHint().height()))
    capture(app, instructions, output_dir / "pt-startup-instructions.png")
    instructions.close()

    window.toggle_theme()
    app.processEvents()
    capture(app, window, output_dir / "pt-main-window-light.png")

    window.toggle_language()
    app.processEvents()
    capture(app, window, output_dir / "en-main-window-preview.png")

    window.close()
    QCoreApplication.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
