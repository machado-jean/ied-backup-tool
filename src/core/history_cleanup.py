"""Controlled cleanup rules for historical backups stored in HIS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from src.core.storage import BackupFileInfo, parse_backup_filename


@dataclass(frozen=True)
class HistoryCleanupCandidate:
    """A historical backup that can be deleted after user confirmation."""

    path: Path
    info: BackupFileInfo
    age_days: int
    size_bytes: int
    reason: str


@dataclass(frozen=True)
class HistoryCleanupPlan:
    """Preview of controlled HIS cleanup."""

    candidates: list[HistoryCleanupCandidate]
    total_his_files: int
    total_his_size_bytes: int
    candidate_size_bytes: int


def plan_history_cleanup(
    his_path: Path,
    *,
    retention_days: int = 30,
    now: datetime | None = None,
) -> HistoryCleanupPlan:
    """Find old HIS backups while preserving the newest backup per key and stage."""

    infos = _read_history_infos(his_path)
    total_size = sum(_file_size(info.path) for info in infos)

    if retention_days <= 0:
        return HistoryCleanupPlan(
            candidates=[],
            total_his_files=len(infos),
            total_his_size_bytes=total_size,
            candidate_size_bytes=0,
        )

    reference = now or datetime.now()
    cutoff = reference - timedelta(days=retention_days)
    protected_paths = _latest_paths_by_key_and_stage(infos)

    candidates: list[HistoryCleanupCandidate] = []
    for info in infos:
        size = _file_size(info.path)
        if info.timestamp >= cutoff:
            continue
        if info.path in protected_paths:
            continue
        age_days = max(0, (reference.date() - info.timestamp.date()).days)
        candidates.append(
            HistoryCleanupCandidate(
                path=info.path,
                info=info,
                age_days=age_days,
                size_bytes=size,
                reason=f"Mais antigo que {retention_days} dias.",
            )
        )

    candidates.sort(
        key=lambda candidate: (
            candidate.info.project,
            candidate.info.software,
            candidate.info.stage,
            candidate.info.timestamp,
            candidate.path.name,
        )
    )
    return HistoryCleanupPlan(
        candidates=candidates,
        total_his_files=len(infos),
        total_his_size_bytes=total_size,
        candidate_size_bytes=sum(candidate.size_bytes for candidate in candidates),
    )


def execute_history_cleanup(candidates: list[HistoryCleanupCandidate]) -> list[Path]:
    """Delete selected cleanup candidates and return removed paths."""

    removed: list[Path] = []
    for candidate in candidates:
        candidate.path.unlink()
        removed.append(candidate.path)
    return removed


def _read_history_infos(his_path: Path) -> list[BackupFileInfo]:
    """Read parseable ZIP backups from HIS."""

    if not his_path.exists():
        return []
    infos: list[BackupFileInfo] = []
    for path in his_path.glob("*.zip"):
        try:
            infos.append(parse_backup_filename(path))
        except ValueError:
            continue
    return infos


def _latest_paths_by_key_and_stage(infos: list[BackupFileInfo]) -> set[Path]:
    """Return paths that must be preserved by the cleanup policy."""

    latest: dict[tuple[str, str], BackupFileInfo] = {}
    for info in infos:
        key = (info.key, info.stage)
        current = latest.get(key)
        if current is None or (info.timestamp, info.path.name) > (
            current.timestamp,
            current.path.name,
        ):
            latest[key] = info
    return {info.path for info in latest.values()}


def _file_size(path: Path) -> int:
    """Return file size, tolerating files that disappear during preview."""

    try:
        return path.stat().st_size
    except OSError:
        return 0
