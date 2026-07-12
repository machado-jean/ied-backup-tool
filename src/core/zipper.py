"""ZIP creation helpers used by the backup workflow."""

from __future__ import annotations

import os
import zipfile
from collections.abc import Sequence
from pathlib import Path

from src.core.progress import ProgressCallback, copy_stream_with_progress


class BackupZipError(RuntimeError):
    pass


BACKUP_INFO_FILENAME = "IEDS-BACKUP-INFO.txt"


def create_backup_zip(
    source_file: Path | Sequence[Path],
    backup_name: str,
    output_dir: Path | None = None,
    backup_info_text: str | None = None,
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Create a zip containing one or more source files under their original names."""

    source_files = [source_file] if isinstance(source_file, Path) else list(source_file)
    if not source_files:
        raise BackupZipError("Nenhum arquivo informado para compactacao.")

    destination_dir = output_dir or source_files[0].parent
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / backup_name

    archive_root = _archive_root_for(source_files)
    arc_names = [_archive_name(path, archive_root) for path in source_files]
    if len(arc_names) != len(set(arc_names)):
        raise BackupZipError("Arquivos com nomes duplicados nao podem ser compactados juntos.")

    for path in source_files:
        ensure_source_is_readable(path)

    with zipfile.ZipFile(destination, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        if backup_info_text is not None:
            archive.writestr(BACKUP_INFO_FILENAME, backup_info_text)
        for path, arc_name in zip(source_files, arc_names, strict=True):
            try:
                with path.open("rb") as source, archive.open(arc_name, "w") as target:
                    copy_stream_with_progress(
                        source,
                        target,
                        total_bytes=path.stat().st_size,
                        phase="zip",
                        progress_callback=progress_callback,
                    )
            except OSError as exc:
                raise BackupZipError(
                    f"Nao foi possivel compactar o arquivo. Verifique se ele esta aberto "
                    f"ou indisponivel: {path}"
                ) from exc

    return destination


def _archive_root_for(source_files: list[Path]) -> Path | None:
    """Return the common folder used to preserve subfolders in multi-file ZIPs."""

    parent_paths = {path.parent.resolve() for path in source_files}
    if len(parent_paths) <= 1:
        return None

    common = Path(os.path.commonpath([str(path.resolve()) for path in source_files]))
    if common.is_file():
        return common.parent
    if common in [path.resolve() for path in source_files]:
        return common.parent
    return common


def _archive_name(path: Path, archive_root: Path | None) -> str:
    """Return a portable ZIP path, preserving relative folders when needed."""

    if archive_root is None:
        return path.name
    return path.resolve().relative_to(archive_root).as_posix()


def ensure_source_is_readable(source_file: Path) -> None:
    """Fail early with a user-friendly message when the source file is unavailable."""

    try:
        with source_file.open("rb") as handle:
            handle.read(1024 * 1024)
    except OSError as exc:
        raise BackupZipError(
            f"Nao foi possivel ler o arquivo. Verifique se ele esta aberto "
            f"ou indisponivel: {source_file}"
        ) from exc

