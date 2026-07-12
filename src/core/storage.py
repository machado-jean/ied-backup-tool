"""Storage rules for the ATU/HIS backup folders.

ATU stores the current backup for each technical key (`SOFTWARE_PROJECT`).
HIS stores older backups and prevents technical duplicates based on
`SOFTWARE_PROJECT_TIMESTAMP`, regardless of collaborator or stage.
"""

from __future__ import annotations

import os
import re
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.core.progress import ProgressCallback, copy_stream_with_progress


class StorageError(RuntimeError):
    pass


BACKUP_TIMESTAMP_PATTERN = re.compile(r"^\d{8}-\d{4}$")
QUARANTINE_FOLDER_NAME = "IED-QUARENTENA"


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


@dataclass(frozen=True)
class QuarantineInfo:
    """Information about a file moved aside for manual recovery."""

    path: Path
    note_path: Path


def update_storage(
    *,
    new_backup: Path,
    atu_path: Path,
    his_path: Path,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Move a staged backup into ATU while preserving the previous current file in HIS."""

    new_info = parse_backup_filename(new_backup)
    validate_backup_zip(new_backup)
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
            cleanup_quarantine_for_successful_backup(current.path)
            return current.path
        destination = atu_path / new_backup.name
        if destination.exists():
            new_backup.unlink(missing_ok=True)
            raise StorageError(f"Ja existe um backup no destino: {destination}")

        prepared_backup = _copy_to_destination_temp(
            new_backup,
            destination,
            phase="copy_current",
            progress_callback=progress_callback,
        )
        try:
            os.replace(prepared_backup, destination)
            validate_backup_zip(destination)
            try:
                move_to_history(current.path, his_path, progress_callback=progress_callback)
            except Exception:
                destination.unlink(missing_ok=True)
                raise
            new_backup.unlink()
            cleanup_quarantine_for_successful_backup(destination)
            return destination
        except Exception:
            prepared_backup.unlink(missing_ok=True)
            raise

    destination = atu_path / new_backup.name
    if new_backup.resolve() != destination.resolve():
        place_staged_backup(new_backup, destination, progress_callback=progress_callback)
    validate_backup_zip(destination)
    cleanup_quarantine_for_successful_backup(destination)
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


def fix_atu_duplicates(
    atu_path: Path,
    his_path: Path,
    progress_callback: ProgressCallback | None = None,
) -> list[Path]:
    """Move older duplicate ATU files into HIS."""

    his_path.mkdir(parents=True, exist_ok=True)
    moved = []
    for duplicate in find_atu_duplicates(atu_path, his_path):
        moved.append(
            move_to_history(
                duplicate.duplicate.path,
                his_path,
                progress_callback=progress_callback,
            )
        )
    return moved


def move_to_history(
    path: Path,
    his_path: Path,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Move a backup to HIS, reusing an existing file with the same identity if present."""

    source_info = parse_backup_filename(path)
    validate_backup_zip(path)
    destination = find_backup_by_identity(his_path, source_info.identity)
    if destination is None:
        destination = his_path / path.name
    if destination.exists():
        validate_backup_zip(destination)
        path.unlink()
        return destination
    moved = _move_inheriting_destination_acl(
        path,
        destination,
        phase="archive_current",
        progress_callback=progress_callback,
    )
    validate_backup_zip(moved)
    cleanup_quarantine_for_successful_backup(moved)
    return moved


def validate_backup_zip(path: Path) -> None:
    """Ensure a backup ZIP exists, is non-empty, and can be read by the zip module."""

    try:
        if not path.exists() or path.stat().st_size == 0:
            raise StorageError(f"Backup compactado vazio ou inexistente: {path}")
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
    except (OSError, zipfile.BadZipFile) as exc:
        raise StorageError(f"Backup compactado invalido ou ilegivel: {path}") from exc

    if bad_member is not None:
        raise StorageError(f"Backup compactado invalido. Entrada corrompida: {bad_member}")


def place_staged_backup(
    source: Path,
    destination: Path,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Place a new staged ZIP in its final folder only after destination validation."""

    if destination.exists():
        raise StorageError(f"Ja existe um backup no destino: {destination}")

    temp_path = _copy_to_destination_temp(
        source,
        destination,
        phase="copy_current",
        progress_callback=progress_callback,
    )
    try:
        os.replace(temp_path, destination)
        validate_backup_zip(destination)
        source.unlink()
        cleanup_quarantine_for_successful_backup(destination)
    except Exception as exc:
        quarantined_paths = []
        if temp_path.exists():
            quarantined_paths.append(
                quarantine_file(
                    temp_path,
                    quarantine_root=_quarantine_root_for(destination),
                    original_path=destination,
                    reason="Falha antes de publicar o backup final.",
                    original_error=exc,
                ).path
            )
        if destination.exists():
            quarantined_paths.append(
                quarantine_file(
                    destination,
                    quarantine_root=_quarantine_root_for(destination),
                    original_path=destination,
                    reason="Backup final suspeito apos falha de publicacao.",
                    original_error=exc,
                ).path
            )
        if quarantined_paths:
            raise StorageError(
                "Falha ao publicar backup. Arquivo movido para quarentena: "
                + ", ".join(str(path) for path in quarantined_paths)
            ) from exc
        raise
    return destination


def _copy_to_destination_temp(
    source: Path,
    destination: Path,
    *,
    phase: str,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Copy a staged ZIP to a temporary file inside the destination folder."""

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
                copy_stream_with_progress(
                    input_file,
                    temp_handle,
                    total_bytes=source.stat().st_size,
                    phase=phase,
                    progress_callback=progress_callback,
        )
        validate_backup_zip(temp_path)
    except Exception as exc:
        if temp_path.exists():
            quarantined = quarantine_file(
                temp_path,
                quarantine_root=_quarantine_root_for(destination),
                original_path=destination,
                reason="Falha durante copia temporaria do backup.",
                original_error=exc,
            )
            raise StorageError(
                f"Falha ao copiar backup. Arquivo parcial movido para quarentena: "
                f"{quarantined.path}"
            ) from exc
        raise
    return temp_path


def _move_inheriting_destination_acl(
    source: Path,
    destination: Path,
    *,
    phase: str,
    progress_callback: ProgressCallback | None = None,
) -> Path:
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
                copy_stream_with_progress(
                    input_file,
                    temp_handle,
                    total_bytes=source.stat().st_size,
                    phase=phase,
                    progress_callback=progress_callback,
                )
        os.replace(temp_path, destination)
        source.unlink()
    except Exception as exc:
        quarantined_paths = []
        if temp_path.exists():
            quarantined_paths.append(
                quarantine_file(
                    temp_path,
                    quarantine_root=_quarantine_root_for(destination),
                    original_path=destination,
                    reason="Falha antes de arquivar backup em HIS.",
                    original_error=exc,
                ).path
            )
        if destination.exists() and source.exists():
            quarantined_paths.append(
                quarantine_file(
                    destination,
                    quarantine_root=_quarantine_root_for(destination),
                    original_path=destination,
                    reason="Arquivo arquivado suspeito; origem ainda existe.",
                    original_error=exc,
                ).path
            )
        if quarantined_paths:
            raise StorageError(
                "Falha ao arquivar backup. Arquivo movido para quarentena: "
                + ", ".join(str(path) for path in quarantined_paths)
            ) from exc
        raise
    return destination


def quarantine_file(
    path: Path,
    *,
    quarantine_root: Path,
    original_path: Path,
    reason: str,
    original_error: BaseException | None = None,
) -> QuarantineInfo:
    """Move a suspicious file to quarantine and write a recovery note."""

    quarantine_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = _unique_quarantine_path(quarantine_root / f"{timestamp}_{path.name}")
    os.replace(path, target)
    note_path = target.with_suffix(target.suffix + ".txt")
    lines = [
        "IED Backup Manager - Quarentena",
        "",
        f"Arquivo original: {original_path}",
        f"Arquivo em quarentena: {target}",
        f"Motivo: {reason}",
    ]
    if original_error is not None:
        lines.append(
            f"Erro original: {type(original_error).__name__}: {original_error}",
        )
    lines.extend(
        [
            f"Data/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Analise este arquivo manualmente antes de apagar ou restaurar.",
        ]
    )
    note_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return QuarantineInfo(path=target, note_path=note_path)


def cleanup_quarantine_for_successful_backup(successful_backup: Path) -> list[Path]:
    """Remove older/equal quarantine entries covered by a successful backup."""

    try:
        successful_info = parse_backup_filename(successful_backup)
    except ValueError:
        return []

    quarantine_root = _quarantine_root_for(successful_backup)
    if not quarantine_root.exists():
        return []

    removed: list[Path] = []
    for note_path in sorted(quarantine_root.glob("*.txt")):
        note = _read_quarantine_note(note_path)
        original_path_text = note.get("Arquivo original")
        quarantined_path_text = note.get("Arquivo em quarentena")
        if not original_path_text or not quarantined_path_text:
            continue

        try:
            original_info = parse_backup_filename(Path(original_path_text))
        except ValueError:
            continue

        if original_info.key != successful_info.key:
            continue
        if original_info.timestamp > successful_info.timestamp:
            continue

        quarantined_path = Path(quarantined_path_text)
        if quarantined_path.exists():
            quarantined_path.unlink()
            removed.append(quarantined_path)
        note_path.unlink(missing_ok=True)
        removed.append(note_path)

    _remove_empty_quarantine_folder(quarantine_root)
    return removed


def _quarantine_root_for(destination: Path) -> Path:
    """Return the quarantine folder beside the destination storage folder."""

    return destination.parent.parent / QUARANTINE_FOLDER_NAME


def _read_quarantine_note(note_path: Path) -> dict[str, str]:
    """Read key/value fields written beside quarantined files."""

    fields: dict[str, str] = {}
    try:
        lines = note_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return fields
    for line in lines:
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        fields[key.strip()] = value.strip()
    return fields


def _remove_empty_quarantine_folder(quarantine_root: Path) -> None:
    """Delete the quarantine folder only when there is nothing left inside."""

    try:
        next(quarantine_root.iterdir())
    except StopIteration:
        quarantine_root.rmdir()
    except OSError:
        return


def _unique_quarantine_path(path: Path) -> Path:
    """Avoid overwriting an existing quarantine file."""

    if not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise StorageError(f"Nao foi possivel criar caminho unico de quarentena: {path}")


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
