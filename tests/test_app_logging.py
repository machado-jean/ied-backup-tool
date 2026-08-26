from __future__ import annotations

from datetime import datetime

from src.core import app_logging


def test_daily_log_file_uses_local_app_data(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    log_file = app_logging.daily_log_file(datetime(2026, 8, 24, 10, 30))

    assert log_file == (
        tmp_path
        / "IED Backup Manager"
        / "logs"
        / "ied-backup-manager-2026-08-24.log"
    )


def test_setup_application_logging_creates_daily_log(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    log_file = app_logging.setup_application_logging("1.17.0")
    app_logging.get_logger("test").info("hello")

    assert log_file.exists()
    assert "Version: 1.17.0" in log_file.read_text(encoding="utf-8")
