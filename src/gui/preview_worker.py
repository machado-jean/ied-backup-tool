"""Worker-thread preview planning for large project folders."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from src.core.app_logging import get_logger
from src.core.project_types.base import ProjectVersionRequiredError
from src.gui.backup_application_service import (
    PreviewRequest,
    PreviewValidationError,
    build_preview,
)


class PreviewWorker(QObject):
    """Build a batch preview outside the GUI thread."""

    finished = Signal(object)
    failed = Signal(object)

    def __init__(self, request: PreviewRequest) -> None:
        super().__init__()
        self.request = request

    @Slot()
    def run(self) -> None:
        """Build the preview and emit either a result or the raised exception."""

        logger = get_logger("preview")
        try:
            logger.info(
                "Preview started: folder=%s, types=%s, stage=%s, latest_only=%s",
                self.request.project_dir,
                [project_type.key for project_type in self.request.selected_project_types],
                self.request.selected_stage,
                self.request.latest_only,
            )
            preview = build_preview(self.request)
            logger.info(
                "Preview finished: plans=%s, duplicate_plans=%s",
                len(preview.plans),
                len(preview.duplicate_plans),
            )
            self.finished.emit(preview)
        except (PreviewValidationError, ProjectVersionRequiredError) as exc:
            logger.info("Preview validation stopped planning: %s", exc)
            self.failed.emit(exc)
        except Exception as exc:
            logger.exception("Preview failed")
            self.failed.emit(exc)
