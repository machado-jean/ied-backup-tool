from __future__ import annotations

from datetime import datetime
from pathlib import Path

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


def test_unclean_session_is_offered_on_next_start(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(app_logging.sys, "argv", [str(tmp_path / "IED_Backup_Manager.exe")])

    app_logging.setup_application_logging("1.17.1")
    app_logging.touch_application_session()
    app_logging.setup_application_logging("1.17.1")

    incident = app_logging.pending_previous_session()
    assert incident is not None
    assert Path(incident.executable).name == "IED_Backup_Manager.exe"
    app_logging.resolve_pending_incident()
    app_logging.mark_application_session_clean(0)


def test_clean_session_is_not_reported_as_incident(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    app_logging.setup_application_logging("1.17.1")
    app_logging.mark_application_session_clean(0)
    app_logging.setup_application_logging("1.17.1")

    assert app_logging.pending_previous_session() is None
    app_logging.mark_application_session_clean(0)


def test_windows_event_parser_keeps_only_matching_executable() -> None:
    incident = app_logging.PreviousSessionIncident(
        session_id="session",
        started_at="2026-09-11T20:21:30+00:00",
        last_seen_at="2026-09-11T20:21:40+00:00",
        executable=r"C:\Projects\IED_Backup_Manager.exe",
        pid=123,
    )
    xml = rb"""
    <Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
      <System>
        <Provider Name='Application Error'/><EventID>1000</EventID>
        <TimeCreated SystemTime='2026-09-11T20:21:40.000Z'/>
      </System>
      <EventData>
        <Data Name='AppName'>IED_Backup_Manager.exe</Data>
        <Data Name='ModuleName'>ucrtbase.dll</Data>
        <Data Name='ExceptionCode'>c0000409</Data>
        <Data Name='AppPath'>C:\Projects\IED_Backup_Manager.exe</Data>
        <Data Name='IntegratorReportId'>report-id</Data>
      </EventData>
    </Event>
    <Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
      <System><Provider Name='Application Error'/><EventID>1000</EventID></System>
      <EventData><Data Name='AppName'>Other.exe</Data></EventData>
    </Event>
    """

    events = app_logging._parse_windows_events(xml, incident)

    assert len(events) == 1
    assert events[0].module == "ucrtbase.dll"
    assert events[0].exception_code == "c0000409"
    assert events[0].report_id == "report-id"
