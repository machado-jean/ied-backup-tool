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
from collections import defaultdict
from ctypes import WinDLL, byref, create_unicode_buffer, wintypes
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOGGER_NAME = "ied_backup_manager"
LOG_DIR_NAME = "IED Backup Manager"
SESSION_DIR_NAME = "sessions"
LEGACY_SESSION_STATE_NAME = "session-state.json"
LEGACY_PENDING_INCIDENT_NAME = "pending-incident.json"
CRASH_EVENT_WINDOW = timedelta(minutes=2)
SESSION_RETENTION = timedelta(days=30)
MAX_PENDING_SESSIONS_PER_EXECUTABLE = 20
PROCESS_START_TOLERANCE = timedelta(seconds=2)


@dataclass(frozen=True)
class PreviousSessionIncident:
    """Minimal local state left by an execution that did not exit cleanly."""

    session_id: str
    started_at: str
    last_seen_at: str
    executable: str
    pid: int
    process_started_at: str = ""
    marker_path: str = ""


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
_current_session_path: Path | None = None
_pending_incident: PreviousSessionIncident | None = None


class _SessionContextFilter(logging.Filter):
    """Attach the current session identifier to every line in the shared daily log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.session_id = (
            str(_current_session.get("session_id")) if _current_session else "startup"
        )
        return True


def setup_application_logging(app_version: str) -> Path:
    """Configure daily local logging and global exception hooks."""

    log_file = daily_log_file()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.addFilter(_SessionContextFilter())
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s [%(name)s] "
            "[session=%(session_id)s pid=%(process)d] %(message)s"
        ),
        handlers=[handler],
        force=True,
    )
    logger = get_logger("startup")
    _start_session_tracking(logger)
    logger.info("Application logging started")
    logger.info("Version: %s", app_version)
    logger.info("Executable: %s", Path(sys.argv[0]).resolve(strict=False))
    logger.info("Python: %s", sys.version.replace("\n", " "))
    logger.info("Packaged executable: %s", bool(getattr(sys, "frozen", False)))
    _install_exception_hooks()
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
    if _current_session_path is not None:
        _write_json(_current_session_path, _current_session)


def mark_application_session_clean(exit_code: int) -> None:
    """Record a normal Qt event-loop return for the current session."""

    if _current_session is None:
        return
    _current_session["clean_exit"] = True
    _current_session["exit_code"] = exit_code
    _current_session["ended_at"] = _utc_now_text()
    _current_session["last_seen_at"] = _current_session["ended_at"]
    if _current_session_path is None:
        return
    _write_json(_current_session_path, _current_session)
    try:
        _current_session_path.unlink(missing_ok=True)
    except OSError:
        get_logger("diagnostics").exception("Could not remove clean session marker")


def resolve_pending_incident() -> None:
    """Mark the pending incident as handled, whether consent was granted or denied."""

    global _pending_incident
    marker_path = Path(_pending_incident.marker_path) if _pending_incident else None
    _pending_incident = None
    if marker_path is None:
        return
    try:
        marker_path.unlink(missing_ok=True)
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


def session_dir() -> Path:
    """Return the directory containing one transient marker per application session."""

    return log_dir() / SESSION_DIR_NAME


def session_file(session_id: str) -> Path:
    """Return the marker path for one unique application session."""

    return session_dir() / f"{session_id}.json"


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced application logger."""

    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def _start_session_tracking(logger: logging.Logger) -> None:
    """Clean stale markers, detect a same-path incident, and start this session."""

    global _current_session, _current_session_path, _pending_incident
    _retire_legacy_session_markers(logger)
    directory = session_dir()
    directory.mkdir(parents=True, exist_ok=True)
    executable = str(Path(sys.argv[0]).resolve(strict=False))
    candidates = _clean_and_collect_sessions(directory, executable, logger)
    _pending_incident = candidates[0] if candidates else None

    now = _utc_now_text()
    identity = _running_process_identity(os.getpid())
    session_id = str(uuid.uuid4())
    _current_session = {
        "session_id": session_id,
        "started_at": now,
        "last_seen_at": now,
        "executable": executable,
        "pid": os.getpid(),
        "process_executable": identity[0] if identity else "",
        "process_started_at": identity[1] if identity else now,
        "clean_exit": False,
    }
    _current_session_path = session_file(session_id)
    _write_json(_current_session_path, _current_session)
    if _pending_incident:
        logger.warning(
            "Previous session ended unexpectedly near %s: executable=%s, pid=%s; "
            "awaiting diagnostic consent",
            _pending_incident.last_seen_at,
            _pending_incident.executable,
            _pending_incident.pid,
        )


def _clean_and_collect_sessions(
    directory: Path,
    current_executable: str,
    logger: logging.Logger,
) -> list[PreviousSessionIncident]:
    """Apply retention/limits and return dead sessions for the current executable path."""

    now = datetime.now(timezone.utc)
    dead_by_executable: dict[str, list[tuple[datetime, Path, dict[str, object]]]] = (
        defaultdict(list)
    )
    required = {"session_id", "started_at", "last_seen_at", "executable", "pid"}
    for marker in directory.glob("*.json"):
        data = _read_json(marker)
        if data is None or not required <= data.keys():
            logger.warning("Removing invalid session marker: %s", marker)
            _remove_marker(marker, logger)
            continue
        try:
            last_seen = _parse_utc(str(data["last_seen_at"]))
            int(data["pid"])
        except (TypeError, ValueError):
            logger.warning("Removing invalid session marker: %s", marker)
            _remove_marker(marker, logger)
            continue
        if data.get("clean_exit", False) or now - last_seen > SESSION_RETENTION:
            _remove_marker(marker, logger)
            continue
        if _session_is_active(data):
            continue
        key = _normalized_path(str(data["executable"]))
        dead_by_executable[key].append((last_seen, marker, data))

    current_key = _normalized_path(current_executable)
    candidates: list[PreviousSessionIncident] = []
    for executable_key, records in dead_by_executable.items():
        records.sort(key=lambda item: item[0], reverse=True)
        for _, marker, _ in records[MAX_PENDING_SESSIONS_PER_EXECUTABLE:]:
            _remove_marker(marker, logger)
        if executable_key != current_key:
            continue
        for _, marker, data in records[:MAX_PENDING_SESSIONS_PER_EXECUTABLE]:
            try:
                candidates.append(
                    PreviousSessionIncident(
                        session_id=str(data["session_id"]),
                        started_at=str(data["started_at"]),
                        last_seen_at=str(data["last_seen_at"]),
                        executable=str(data["executable"]),
                        pid=int(data["pid"]),
                        process_started_at=str(data.get("process_started_at", "")),
                        marker_path=str(marker),
                    )
                )
            except (TypeError, ValueError):
                logger.warning("Removing invalid session marker: %s", marker)
                _remove_marker(marker, logger)
    return candidates


def _session_is_active(data: dict[str, object]) -> bool:
    """Return whether PID, process image, and creation time still identify one process."""

    try:
        identity = _running_process_identity(int(data["pid"]))
    except (KeyError, TypeError, ValueError):
        return False
    if identity is None:
        return False
    process_executable, process_started_at = identity
    expected_executable = str(data.get("process_executable", ""))
    expected_started_at = str(data.get("process_started_at", ""))
    if not expected_executable or not expected_started_at:
        return False
    if _normalized_path(process_executable) != _normalized_path(expected_executable):
        return False
    try:
        difference = abs(_parse_utc(process_started_at) - _parse_utc(expected_started_at))
    except ValueError:
        return False
    return difference <= PROCESS_START_TOLERANCE


def _running_process_identity(pid: int) -> tuple[str, str] | None:
    """Read a Windows process image and creation time without administrator access."""

    if sys.platform != "win32":
        return None
    kernel32 = WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = (
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        wintypes.PDWORD,
    )
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.GetProcessTimes.argtypes = (
        wintypes.HANDLE,
        wintypes.LPFILETIME,
        wintypes.LPFILETIME,
        wintypes.LPFILETIME,
        wintypes.LPFILETIME,
    )
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    process = kernel32.OpenProcess(0x1000, False, pid)
    if not process:
        return None
    try:
        size = wintypes.DWORD(32768)
        buffer = create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(process, 0, buffer, byref(size)):
            return None
        creation = wintypes.FILETIME()
        exit_time = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if not kernel32.GetProcessTimes(
            process,
            byref(creation),
            byref(exit_time),
            byref(kernel),
            byref(user),
        ):
            return None
        ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        started_at = datetime.fromtimestamp(
            (ticks - 116444736000000000) / 10_000_000,
            tz=timezone.utc,
        ).isoformat()
        return buffer.value, started_at
    finally:
        kernel32.CloseHandle(process)


def _retire_legacy_session_markers(logger: logging.Logger) -> None:
    """Remove collision-prone marker files created by versions up to v1.17.2."""

    for name in (LEGACY_SESSION_STATE_NAME, LEGACY_PENDING_INCIDENT_NAME):
        marker = log_dir() / name
        if marker.exists():
            logger.info("Removing legacy shared session marker: %s", marker)
            _remove_marker(marker, logger)


def _remove_marker(path: Path, logger: logging.Logger) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        logger.exception("Could not remove session marker: %s", path)


def _normalized_path(value: str) -> str:
    return os.path.normcase(os.path.abspath(value))


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
