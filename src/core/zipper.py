"""ZIP creation helpers used by the backup workflow."""

from __future__ import annotations

import zipfile
from pathlib import Path


class BackupZipError(RuntimeError):
    pass


def create_backup_zip(source_file: Path, backup_name: str, output_dir: Path | None = None) -> Path:
    """Create a zip containing the original project file under its original name."""

    destination_dir = output_dir or source_file.parent
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / backup_name

    ensure_source_is_readable(source_file)
    with zipfile.ZipFile(destination, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        try:
            archive.write(source_file, arcname=source_file.name)
        except OSError as exc:
            raise BackupZipError(
                f"Nao foi possivel compactar o arquivo. Verifique se ele esta aberto "
                f"ou indisponivel: {source_file}"
            ) from exc

    return destination


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
