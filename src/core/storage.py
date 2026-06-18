from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class StorageError(RuntimeError):
    pass


BACKUP_TIMESTAMP_PATTERN = re.compile(r"^\d{8}-\d{4}$")


@dataclass(frozen=True)
class BackupFileInfo:
    path: Path
    software: str
    project: str
    timestamp: datetime
    collaborator: str
    stage: str

    @property
    def key(self) -> str:
        return f"{self.software}_{self.project}"

    @property
    def identity(self) -> str:
        return f"{self.key}_{self.timestamp.strftime('%Y%m%d-%H%M')}"


@dataclass(frozen=True)
class AtuDuplicateInfo:
    key: str
    keep: BackupFileInfo
    duplicate: BackupFileInfo
    history_path: Path


def update_storage(*, new_backup: Path, atu_path: Path, his_path: Path) -> Path:
    new_info = parse_backup_filename(new_backup)
    atu_path.mkdir(parents=True, exist_ok=True)
    his_path.mkdir(parents=True, exist_ok=True)

    current = find_current_backup(atu_path, new_info.key)
    if current is not None:
        if current.timestamp > new_info.timestamp:
            new_backup.unlink(missing_ok=True)
            raise StorageError("Ja existe um backup mais recente em ATU.")
        if current.identity == new_info.identity:
            new_backup.unlink(missing_ok=True)
            return current.path
        move_to_history(current.path, his_path)

    destination = atu_path / new_backup.name
    if new_backup.resolve() != destination.resolve():
        if destination.exists():
            destination.unlink()
        shutil.move(str(new_backup), destination)
    return destination


def find_current_backup(atu_path: Path, key: str) -> BackupFileInfo | None:
    candidates = []
    for path in atu_path.glob("*.zip"):
        try:
            info = parse_backup_filename(path)
        except ValueError:
            continue
        if info.key == key:
            candidates.append(info)
    return max(candidates, key=lambda info: info.timestamp, default=None)


def find_atu_duplicates(atu_path: Path, his_path: Path) -> list[AtuDuplicateInfo]:
    grouped: dict[str, list[BackupFileInfo]] = {}
    for path in atu_path.glob("*.zip"):
        try:
            info = parse_backup_filename(path)
        except ValueError:
            continue
        grouped.setdefault(info.key, []).append(info)

    duplicates = []
    for key, items in grouped.items():
        if len(items) < 2:
            continue
        ordered = sorted(items, key=lambda info: (info.timestamp, info.path.name), reverse=True)
        keep = ordered[0]
        for duplicate in ordered[1:]:
            duplicates.append(
                AtuDuplicateInfo(
                    key=key,
                    keep=keep,
                    duplicate=duplicate,
                    history_path=his_path / duplicate.path.name,
                )
            )
    return duplicates


def fix_atu_duplicates(atu_path: Path, his_path: Path) -> list[Path]:
    his_path.mkdir(parents=True, exist_ok=True)
    moved = []
    for duplicate in find_atu_duplicates(atu_path, his_path):
        moved.append(move_to_history(duplicate.duplicate.path, his_path))
    return moved


def move_to_history(path: Path, his_path: Path) -> Path:
    source_info = parse_backup_filename(path)
    destination = find_backup_by_identity(his_path, source_info.identity)
    if destination is None:
        destination = his_path / path.name
    if destination.exists():
        path.unlink()
        return destination
    return Path(shutil.move(str(path), destination))


def find_backup_by_identity(folder: Path, identity: str) -> Path | None:
    if not folder.exists():
        return None
    for path in folder.glob("*.zip"):
        try:
            info = parse_backup_filename(path)
        except ValueError:
            continue
        if info.identity == identity:
            return path
    return None


def parse_backup_filename(path: Path) -> BackupFileInfo:
    stem = path.stem
    parts = stem.split("_")
    if len(parts) < 5:
        raise ValueError(f"Nome de backup invalido: {path.name}")

    timestamp_index = next(
        (index for index, part in enumerate(parts) if BACKUP_TIMESTAMP_PATTERN.match(part)),
        None,
    )
    if timestamp_index is None or timestamp_index < 2 or timestamp_index >= len(parts) - 2:
        raise ValueError(f"Nome de backup invalido: {path.name}")

    software = parts[0]
    project = "_".join(parts[1:timestamp_index])
    raw_timestamp = parts[timestamp_index]
    collaborator = "_".join(parts[timestamp_index + 1 : -1])
    stage = parts[-1]
    try:
        timestamp = datetime.strptime(raw_timestamp, "%Y%m%d-%H%M")
    except ValueError as exc:
        raise ValueError(f"Data/hora invalida no backup: {path.name}") from exc

    return BackupFileInfo(
        path=path,
        software=software,
        project=project,
        timestamp=timestamp,
        collaborator=collaborator,
        stage=stage,
    )
