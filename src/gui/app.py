"""GUI entry point for the packaged Windows application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
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


def main() -> int:
    """Start the Qt application and show the main window."""

    args = parse_args()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setWindowIcon(QIcon(str(app_icon_path())))
    window = MainWindow(project_dir=args.project_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
