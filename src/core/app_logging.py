"""Application logging setup for startup and crash diagnostics."""

from __future__ import annotations

import logging
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

LOGGER_NAME = "ied_backup_manager"
LOG_DIR_NAME = "IED Backup Manager"


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


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced application logger."""

    return logging.getLogger(f"{LOGGER_NAME}.{name}")


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
