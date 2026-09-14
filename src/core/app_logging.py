"""Application logging setup for startup and crash diagnostics."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOGGER_NAME = "ied_backup_manager"
LOG_DIR_NAME = "IED Backup Manager"
SESSION_STATE_NAME = "session-state.json"
PENDING_INCIDENT_NAME = "pending-incident.json"
CRASH_EVENT_WINDOW = timedelta(minutes=2)


@dataclass(frozen=True)
class PreviousSessionIncident:
    """Minimal local state left by an execution that did not exit cleanly."""

    session_id: str
    started_at: str
    last_seen_at: str
    executable: str
    pid: int


@dataclass(frozen=True)
class WindowsCrashDiagnostic:
    """Sanitized fields copied from a matching Windows Application event."""

    timestamp: str
    event_id: int
    provider: str
    application: str
    module: str
    exception_code: str
    report_id: str


_current_session: dict[str, object] | None = None
_pending_incident: PreviousSessionIncident | None = None


def setup_application_logging(app_version: str) -> Path:
    """Configure daily local logging and global exception hooks."""

    log_file = daily_log_file()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
        force=True,
    )
    logger = get_logger("startup")
    logger.info("Application logging started")
    logger.info("Version: %s", app_version)
    logger.info("Executable: %s", Path(sys.argv[0]).resolve(strict=False))
    logger.info("Python: %s", sys.version.replace("\n", " "))
    logger.info("Packaged executable: %s", bool(getattr(sys, "frozen", False)))
    _install_exception_hooks()
    _start_session_tracking(logger)
    return log_file


def daily_log_file(today: datetime | None = None) -> Path:
    """Return the daily log path under LOCALAPPDATA."""

    current = today or datetime.now()
    return log_dir() / f"ied-backup-manager-{current:%Y-%m-%d}.log"


def log_dir() -> Path:
    """Return the application log directory."""

    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return base / LOG_DIR_NAME / "logs"


def pending_previous_session() -> PreviousSessionIncident | None:
    """Return an unresolved abnormal previous session, when one exists."""

    return _pending_incident


def touch_application_session() -> None:
    """Refresh the current session heartbeat used to narrow a later event query."""

    if _current_session is None:
        return
    _current_session["last_seen_at"] = _utc_now_text()
    _write_json(session_state_file(), _current_session)


def mark_application_session_clean(exit_code: int) -> None:
    """Record a normal Qt event-loop return for the current session."""

    if _current_session is None:
        return
    _current_session["clean_exit"] = True
    _current_session["exit_code"] = exit_code
    _current_session["ended_at"] = _utc_now_text()
    _current_session["last_seen_at"] = _current_session["ended_at"]
    _write_json(session_state_file(), _current_session)


def resolve_pending_incident() -> None:
    """Mark the pending incident as handled, whether consent was granted or denied."""

    global _pending_incident
    _pending_incident = None
    try:
        pending_incident_file().unlink(missing_ok=True)
    except OSError:
        get_logger("diagnostics").exception("Could not remove pending incident marker")


def collect_windows_crash_diagnostics(
    incident: PreviousSessionIncident,
) -> list[WindowsCrashDiagnostic]:
    """Read matching Windows events in a narrow interval after explicit consent."""

    if sys.platform != "win32":
        return []
    center = _parse_utc(incident.last_seen_at)
    start = center - CRASH_EVENT_WINDOW
    end = center + CRASH_EVENT_WINDOW
    query = (
        "*[System[(EventID=1000 or EventID=1001) and "
        f"TimeCreated[@SystemTime>='{_event_time(start)}' and "
        f"@SystemTime<='{_event_time(end)}']]]"
    )
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        [
            "wevtutil.exe",
            "qe",
            "Application",
            f"/q:{query}",
            "/f:xml",
            "/rd:true",
            "/c:50",
        ],
        capture_output=True,
        timeout=5,
        creationflags=creation_flags,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise RuntimeError(detail or f"wevtutil exited with code {result.returncode}")
    return _parse_windows_events(result.stdout, incident)


def append_windows_crash_diagnostics(
    incident: PreviousSessionIncident,
    events: list[WindowsCrashDiagnostic],
) -> None:
    """Append the user-approved, sanitized Windows event fields to the app log."""

    logger = get_logger("diagnostics")
    logger.warning(
        "Previous application session ended unexpectedly: session=%s, "
        "started=%s, last_seen=%s, executable=%s, pid=%s",
        incident.session_id,
        incident.started_at,
        incident.last_seen_at,
        incident.executable,
        incident.pid,
    )
    if not events:
        logger.warning("No matching Windows crash events found in the approved time window")
        return
    for event in events:
        logger.warning(
            "Windows crash event: time=%s, event_id=%s, provider=%s, "
            "application=%s, module=%s, exception=%s, report_id=%s",
            event.timestamp,
            event.event_id,
            event.provider,
            event.application,
            event.module,
            event.exception_code,
            event.report_id,
        )


def session_state_file() -> Path:
    """Return the per-user current-session marker path."""

    return log_dir() / SESSION_STATE_NAME


def pending_incident_file() -> Path:
    """Return the per-user unresolved-incident marker path."""

    return log_dir() / PENDING_INCIDENT_NAME


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced application logger."""

    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def _start_session_tracking(logger: logging.Logger) -> None:
    """Preserve an unclean previous session and start the current marker."""

    global _current_session, _pending_incident
    previous = _read_json(session_state_file())
    pending = _read_json(pending_incident_file())
    if pending is None and previous and not previous.get("clean_exit", False):
        required = {"session_id", "started_at", "last_seen_at", "executable", "pid"}
        if required <= previous.keys():
            pending = {key: previous[key] for key in required}
            _write_json(pending_incident_file(), pending)
    try:
        _pending_incident = PreviousSessionIncident(**pending) if pending else None
    except (TypeError, ValueError):
        logger.warning("Ignoring invalid pending incident marker")
        _pending_incident = None

    now = _utc_now_text()
    _current_session = {
        "session_id": str(uuid.uuid4()),
        "started_at": now,
        "last_seen_at": now,
        "executable": str(Path(sys.argv[0]).resolve(strict=False)),
        "pid": os.getpid(),
        "clean_exit": False,
    }
    _write_json(session_state_file(), _current_session)
    if _pending_incident:
        logger.warning(
            "Previous session ended unexpectedly near %s; awaiting diagnostic consent",
            _pending_incident.last_seen_at,
        )


def _parse_windows_events(
    raw_xml: bytes,
    incident: PreviousSessionIncident,
) -> list[WindowsCrashDiagnostic]:
    """Parse and filter concatenated wevtutil event XML."""

    if not raw_xml.strip():
        return []
    root = ET.fromstring(b"<Events>" + raw_xml + b"</Events>")
    namespace = {"e": "http://schemas.microsoft.com/win/2004/08/events/event"}
    expected_name = Path(incident.executable).name.casefold()
    expected_path = str(Path(incident.executable)).casefold()
    events: list[WindowsCrashDiagnostic] = []
    for node in root.findall("e:Event", namespace):
        system = node.find("e:System", namespace)
        if system is None:
            continue
        event_id_node = system.find("e:EventID", namespace)
        provider_node = system.find("e:Provider", namespace)
        time_node = system.find("e:TimeCreated", namespace)
        if event_id_node is None or not event_id_node.text:
            continue
        values = {
            item.get("Name", ""): item.text or ""
            for item in node.findall("e:EventData/e:Data", namespace)
        }
        event_id = int(event_id_node.text)
        application = values.get("AppName", values.get("P1", ""))
        app_path = values.get("AppPath", "")
        if application.casefold() != expected_name:
            continue
        if app_path and app_path.casefold() != expected_path:
            continue
        events.append(
            WindowsCrashDiagnostic(
                timestamp=time_node.get("SystemTime", "") if time_node is not None else "",
                event_id=event_id,
                provider=provider_node.get("Name", "") if provider_node is not None else "",
                application=application,
                module=values.get("ModuleName", values.get("P4", "")),
                exception_code=values.get("ExceptionCode", values.get("P8", "")),
                report_id=values.get("IntegratorReportId", values.get("ReportId", "")),
            )
        )
    return events


def _read_json(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_json(path: Path, value: dict[str, object]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        get_logger("diagnostics").exception("Could not write session diagnostic state: %s", path)


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc)


def _event_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _install_exception_hooks() -> None:
    """Install process-wide exception hooks once logging is configured."""

    logger = get_logger("crash")
    original_excepthook = sys.excepthook
    original_threading_excepthook = threading.excepthook

    def excepthook(exc_type, exc_value, exc_traceback) -> None:
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        original_excepthook(exc_type, exc_value, exc_traceback)

    def threading_excepthook(args: threading.ExceptHookArgs) -> None:
        logger.critical(
            "Unhandled thread exception in %s",
            args.thread.name if args.thread else "<unknown>",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )
        original_threading_excepthook(args)

    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
