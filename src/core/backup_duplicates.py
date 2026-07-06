"""Planning and execution helpers for duplicate current backups in ATU."""

from __future__ import annotations

from pathlib import Path

from src.core.backup_models import STATUS_ATU_DUPLICATE, AtuDuplicatePlan
from src.core.progress import ProgressCallback
from src.core.storage import find_atu_duplicates, fix_atu_duplicates


def plan_atu_duplicate_fixes(*, atu_path: Path, his_path: Path) -> list[AtuDuplicatePlan]:
    """Describe ATU duplicate corrections without moving files."""

    return [
        AtuDuplicatePlan(
            source_file=duplicate.duplicate.path,
            backup_name=duplicate.duplicate.path.name,
            destination_path=duplicate.history_path,
            status=STATUS_ATU_DUPLICATE,
            key=duplicate.key,
            keep_file=duplicate.keep.path,
        )
        for duplicate in find_atu_duplicates(atu_path, his_path)
    ]


def fix_atu_duplicate_backups(
    *,
    atu_path: Path,
    his_path: Path,
    progress_callback: ProgressCallback | None = None,
) -> list[AtuDuplicatePlan]:
    """Move older duplicate ATU files to HIS and return the planned actions."""

    plans = plan_atu_duplicate_fixes(atu_path=atu_path, his_path=his_path)
    fix_atu_duplicates(atu_path, his_path, progress_callback=progress_callback)
    return plans
