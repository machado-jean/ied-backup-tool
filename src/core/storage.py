"""Storage rules for the ATU/HIS backup folders.

ATU stores the current backup for each technical key (`SOFTWARE_PROJECT`).
HIS stores older backups and prevents technical duplicates based on
`SOFTWARE_PROJECT_TIMESTAMP`, regardless of collaborator or stage.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class StorageError(RuntimeError):
    pass


BACKUP_TIMESTAMP_PATTERN = re.compile(r"^\d{8}-\d{4}$")


@dataclass(frozen=True)
class BackupFileInfo:
    """Parsed metadata from a generated backup filename."""

    path: Path
    software: str
    project: str
    timestamp: datetime
    collaborator: str
    stage: str

    @property
    def key(self) -> str:
        """Technical group that can have only one current file in ATU."""
        return f"{self.software}_{self.project}"

    @property
    def identity(self) -> str:
        """Technical identity used to avoid duplicates across ATU and HIS."""
        return f"{self.key}_{self.timestamp.strftime('%Y%m%d-%H%M')}"


@dataclass(frozen=True)
class AtuDuplicateInfo:
    """Represents an older ATU file that should be moved to HIS."""

    key: str
    keep: BackupFileInfo
    duplicate: BackupFileInfo
    history_path: Path


def update_storage(*, new_backup: Path, atu_path: Path, his_path: Path) -> Path:
    """Move a staged backup into ATU while preserving the previous current file in HIS."""

    new_info = parse_backup_filename(new_backup)
    atu_path.mkdir(parents=True, exist_ok=True)
    his_path.mkdir(parents=True, exist_ok=True)

    current = find_current_backup(atu_path, new_info.key)
    if current is not None:
        # A staged older backup must never replace a newer current backup.
        if current.timestamp > new_info.timestamp:
            new_backup.unlink(missing_ok=True)
            raise StorageError("Ja existe um backup mais recente em ATU.")
        # Same technical identity means the current backup already exists.
        if current.identity == new_info.identity:
            new_backup.unlink(missing_ok=True)
            return current.path
        move_to_history(current.path, his_path)

    destination = atu_path / new_backup.name
    if new_backup.resolve() != destination.resolve():
        if destination.exists():
            destination.unlink()
        _move_inheriting_destination_acl(new_backup, destination)
    return destination


def find_current_backup(atu_path: Path, key: str) -> BackupFileInfo | None:
    """Return the newest ATU backup for a project key, ignoring invalid filenames."""

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
    """Find extra ATU files for the same key, keeping only the newest one current."""

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
    """Move older duplicate ATU files into HIS."""

    his_path.mkdir(parents=True, exist_ok=True)
    moved = []
    for duplicate in find_atu_duplicates(atu_path, his_path):
        moved.append(move_to_history(duplicate.duplicate.path, his_path))
    return moved


def move_to_history(path: Path, his_path: Path) -> Path:
    """Move a backup to HIS, reusing an existing file with the same identity if present."""

    source_info = parse_backup_filename(path)
    destination = find_backup_by_identity(his_path, source_info.identity)
    if destination is None:
        destination = his_path / path.name
    if destination.exists():
        path.unlink()
        return destination
    return _move_inheriting_destination_acl(path, destination)


def _move_inheriting_destination_acl(source: Path, destination: Path) -> Path:
    """Move a file by recreating it in the destination folder.

    A direct same-volume move on Windows can preserve the source file ACL. Backups
    staged in temporary folders should inherit the ACL from ATU/HIS instead.
    """

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_handle = tempfile.NamedTemporaryFile(
        delete=False,
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_handle.name)
    try:
        with temp_handle:
            with source.open("rb") as input_file:
                shutil.copyfileobj(input_file, temp_handle)
        os.replace(temp_path, destination)
        source.unlink()
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return destination


def find_backup_by_identity(folder: Path, identity: str) -> Path | None:
    """Find a backup by technical identity inside a folder."""

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
    """Parse the standard backup filename into structured metadata."""

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
