from __future__ import annotations

import logging
from pathlib import Path


def get_logger(log_path: Path = Path("logs/backup.log")) -> logging.Logger:
    logger = logging.getLogger("ied_backup_manager")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
    logger.addHandler(handler)
    return logger
