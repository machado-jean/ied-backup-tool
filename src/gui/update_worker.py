"""Worker-thread update check for the main window."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from src.core.update_checker import check_latest_release
from src.version import APP_VERSION


class UpdateCheckWorker(QObject):
    """Check GitHub Releases outside the GUI thread."""

    finished = Signal(object)
    failed = Signal(str)

    @Slot()
    def run(self) -> None:
        """Fetch and compare the latest public release."""

        try:
            self.finished.emit(check_latest_release(APP_VERSION))
        except Exception as exc:
            self.failed.emit(str(exc))
