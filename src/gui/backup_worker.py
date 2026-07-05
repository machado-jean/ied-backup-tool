"""Worker-thread execution for backup batches."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from src.core.backup_service import (
    AtuDuplicatePlan,
    BackupCanceledError,
    BackupPlan,
    BackupResult,
    execute_backup_plan,
    fix_atu_duplicate_backups,
)


@dataclass(frozen=True)
class BackupProgressEvent:
    """Progress payload emitted by the backup worker."""

    index: int
    total: int
    file_text: str
    phase: str
    current_bytes: int
    total_bytes: int
    is_duplicate_fix: bool = False


class BackupExecutionWorker(QObject):
    """Execute backup plans outside the GUI thread."""

    progress = Signal(object)
    finished = Signal(object, object, bool)
    failed = Signal(str)

    def __init__(
        self,
        *,
        plans: list[BackupPlan],
        atu_duplicate_plans: list[AtuDuplicatePlan],
        atu_path: Path,
        his_path: Path,
        fix_duplicates: bool,
    ) -> None:
        super().__init__()
        self.plans = list(plans)
        self.atu_duplicate_plans = list(atu_duplicate_plans)
        self.atu_path = atu_path
        self.his_path = his_path
        self.fix_duplicates = fix_duplicates
        self._cancel_requested = False

    @Slot()
    def request_cancel(self) -> None:
        """Request cancellation before the next backup item starts."""

        self._cancel_requested = True

    @Slot()
    def run(self) -> None:
        """Run the planned work and emit a final result signal."""

        duplicate_results: list[AtuDuplicatePlan] = []
        results: list[BackupResult] = []
        try:
            if self.fix_duplicates and not self._cancel_requested:
                duplicate_results = fix_atu_duplicate_backups(
                    atu_path=self.atu_path,
                    his_path=self.his_path,
                    progress_callback=self._progress_callback(
                        index=0,
                        total=len(self.plans),
                        file_text="ATU",
                        is_duplicate_fix=True,
                    ),
                )

            total = len(self.plans)
            for index, plan in enumerate(self.plans, start=1):
                if self._cancel_requested:
                    self.finished.emit(duplicate_results, results, True)
                    return

                self.progress.emit(
                    BackupProgressEvent(
                        index=index,
                        total=total,
                        file_text=_source_files_text(plan.source_files or (plan.source_file,)),
                        phase="preparing",
                        current_bytes=0,
                        total_bytes=0,
                    )
                )
                results.append(
                    execute_backup_plan(
                        plan=plan,
                        atu_path=self.atu_path,
                        his_path=self.his_path,
                        progress_callback=self._progress_callback(
                            index=index,
                            total=total,
                            file_text=_source_files_text(
                                plan.source_files or (plan.source_file,)
                            ),
                            is_duplicate_fix=False,
                        ),
                        cancellation_callback=self._is_cancel_requested,
                    )
                )

            self.finished.emit(duplicate_results, results, self._cancel_requested)
        except BackupCanceledError:
            self.finished.emit(duplicate_results, results, True)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _is_cancel_requested(self) -> bool:
        """Return whether the GUI requested cancellation."""

        return self._cancel_requested

    def _progress_callback(
        self,
        *,
        index: int,
        total: int,
        file_text: str,
        is_duplicate_fix: bool,
    ):
        """Create a callback that forwards core progress to Qt signals."""

        def callback(phase: str, current_bytes: int, total_bytes: int) -> None:
            self.progress.emit(
                BackupProgressEvent(
                    index=index,
                    total=total,
                    file_text=file_text,
                    phase=phase,
                    current_bytes=current_bytes,
                    total_bytes=total_bytes,
                    is_duplicate_fix=is_duplicate_fix,
                )
            )

        return callback


def _source_files_text(files: tuple[Path, ...]) -> str:
    """Format one or more source files for progress text."""

    if len(files) <= 1:
        return files[0].name if files else "-"
    return f"{files[0].name} + {len(files) - 1}"
