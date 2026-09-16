from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.core import app_logging


def _write_session(
    root: Path,
    *,
    session_id: str,
    executable: Path,
    pid: int,
    last_seen: datetime,
    process_executable: str = r"C:\Python\python.exe",
    process_started_at: str = "2026-09-15T12:00:00+00:00",
    clean_exit: bool = False,
) -> Path:
    marker = root / "IED Backup Manager" / "logs" / "sessions" / f"{session_id}.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps(
            {
                "session_id": session_id,
                "started_at": "2026-09-15T12:00:00+00:00",
                "last_seen_at": last_seen.isoformat(),
                "executable": str(executable),
                "pid": pid,
                "process_executable": process_executable,
                "process_started_at": process_started_at,
                "clean_exit": clean_exit,
            }
        ),
        encoding="utf-8",
    )
    return marker


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
    assert "session=" in log_file.read_text(encoding="utf-8")
    app_logging.mark_application_session_clean(0)


def test_unclean_session_is_offered_on_next_start(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    executable = tmp_path / "project" / "IED_Backup_Manager.exe"
    monkeypatch.setattr(app_logging.sys, "argv", [str(executable)])
    monkeypatch.setattr(app_logging, "_running_process_identity", lambda _pid: None)
    marker = _write_session(
        tmp_path,
        session_id="crashed",
        executable=executable,
        pid=98765,
        last_seen=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    app_logging.setup_application_logging("1.17.1")

    incident = app_logging.pending_previous_session()
    assert incident is not None
    assert Path(incident.executable).name == "IED_Backup_Manager.exe"
    assert Path(incident.marker_path) == marker
    app_logging.resolve_pending_incident()
    assert not marker.exists()
    app_logging.mark_application_session_clean(0)


def test_clean_session_is_not_reported_as_incident(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(app_logging, "_running_process_identity", lambda _pid: None)

    app_logging.setup_application_logging("1.17.1")
    marker = app_logging._current_session_path
    assert marker is not None and marker.exists()
    app_logging.mark_application_session_clean(0)
    assert not marker.exists()
    app_logging.setup_application_logging("1.17.1")

    assert app_logging.pending_previous_session() is None
    app_logging.mark_application_session_clean(0)


def test_active_session_and_other_executable_path_do_not_raise_alert(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    current_executable = tmp_path / "CTU" / "IED_Backup_Manager.exe"
    other_executable = tmp_path / "release" / "IED_Backup_Manager.exe"
    monkeypatch.setattr(app_logging.sys, "argv", [str(current_executable)])
    now = datetime.now(timezone.utc)
    active = _write_session(
        tmp_path,
        session_id="active",
        executable=current_executable,
        pid=456,
        last_seen=now,
    )
    other = _write_session(
        tmp_path,
        session_id="other-path",
        executable=other_executable,
        pid=789,
        last_seen=now,
    )

    def process_identity(pid: int):
        if pid == 456:
            return r"C:\Python\python.exe", "2026-09-15T12:00:00+00:00"
        return None

    monkeypatch.setattr(app_logging, "_running_process_identity", process_identity)
    app_logging.setup_application_logging("1.17.2")

    assert app_logging.pending_previous_session() is None
    assert active.exists()
    assert other.exists()
    app_logging.mark_application_session_clean(0)


def test_session_cleanup_applies_retention_and_per_path_limit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    executable = tmp_path / "CTU" / "IED_Backup_Manager.exe"
    monkeypatch.setattr(app_logging.sys, "argv", [str(executable)])
    monkeypatch.setattr(app_logging, "_running_process_identity", lambda _pid: None)
    now = datetime.now(timezone.utc)
    expired = _write_session(
        tmp_path,
        session_id="expired",
        executable=executable,
        pid=1,
        last_seen=now - timedelta(days=31),
    )
    for index in range(22):
        _write_session(
            tmp_path,
            session_id=f"pending-{index:02d}",
            executable=executable,
            pid=1000 + index,
            last_seen=now - timedelta(minutes=index),
        )

    app_logging.setup_application_logging("1.17.2")

    markers = list(app_logging.session_dir().glob("*.json"))
    assert not expired.exists()
    assert len(markers) == app_logging.MAX_PENDING_SESSIONS_PER_EXECUTABLE + 1
    assert app_logging.pending_previous_session() is not None
    assert app_logging.pending_previous_session().session_id == "pending-00"
    app_logging.resolve_pending_incident()
    app_logging.mark_application_session_clean(0)


def test_legacy_shared_markers_are_retired(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(app_logging, "_running_process_identity", lambda _pid: None)
    log_directory = tmp_path / "IED Backup Manager" / "logs"
    log_directory.mkdir(parents=True)
    legacy_state = log_directory / app_logging.LEGACY_SESSION_STATE_NAME
    legacy_pending = log_directory / app_logging.LEGACY_PENDING_INCIDENT_NAME
    legacy_state.write_text("{}", encoding="utf-8")
    legacy_pending.write_text("{}", encoding="utf-8")

    app_logging.setup_application_logging("1.17.2")

    assert not legacy_state.exists()
    assert not legacy_pending.exists()
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
