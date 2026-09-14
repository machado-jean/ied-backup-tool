from __future__ import annotations

import os
import subprocess
import sys
import textwrap


def test_update_worker_process_exits_cleanly() -> None:
    probe = textwrap.dedent(
        """
        import tempfile
        import time
        from pathlib import Path

        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        from src.core.update_checker import UpdateCheckResult
        from src.gui import update_worker as update_worker_module
        from src.gui.main_window import MainWindow

        def fake_check_latest_release(_version):
            time.sleep(0.05)
            return UpdateCheckResult(
                current_version="1.17.0",
                latest_version="1.17.0",
                release_url="https://example.invalid/release",
                release_page_url="https://example.invalid/release/notes",
                update_available=False,
            )

        update_worker_module.check_latest_release = fake_check_latest_release
        MainWindow.refresh_preview = lambda self: None
        MainWindow.schedule_update_check = lambda self: None

        app = QApplication([])
        project_dir = Path(tempfile.mkdtemp(prefix="ied-worker-lifecycle-"))
        window = MainWindow(project_dir=project_dir, auto_startup_dialogs=False)
        window._start_update_check()
        thread = window.update_thread
        thread.finished.connect(app.quit)
        QTimer.singleShot(2_000, lambda: app.exit(2))

        exit_code = app.exec()
        app.processEvents()
        assert window.update_thread is None
        assert window.update_worker is None
        raise SystemExit(exit_code)
        """
    )
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"

    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        timeout=10,
        env=environment,
        check=False,
    )

    assert result.returncode == 0, result.stderr
