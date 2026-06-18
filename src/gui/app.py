from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IED Backup Manager GUI")
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Pasta processada pela GUI. Uso principal: testes em desenvolvimento.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = QApplication(sys.argv)
    app.setApplicationName("IED Backup Manager")
    window = MainWindow(project_dir=args.project_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
