"""ZIP creation helpers used by the backup workflow."""

from __future__ import annotations

import zipfile
from collections.abc import Sequence
from pathlib import Path


class BackupZipError(RuntimeError):
    pass


PACKAGE_SUMMARY_FILENAME = "IEDS-VERSIONS.txt"


def create_backup_zip(
    source_file: Path | Sequence[Path],
    backup_name: str,
    output_dir: Path | None = None,
    package_versions_text: str | None = None,
) -> Path:
    """Create a zip containing one or more source files under their original names."""

    source_files = [source_file] if isinstance(source_file, Path) else list(source_file)
    if not source_files:
        raise BackupZipError("Nenhum arquivo informado para compactacao.")

    destination_dir = output_dir or source_files[0].parent
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / backup_name

    arc_names = [path.name for path in source_files]
    if len(arc_names) != len(set(arc_names)):
        raise BackupZipError("Arquivos com nomes duplicados nao podem ser compactados juntos.")

    for path in source_files:
        ensure_source_is_readable(path)

    with zipfile.ZipFile(destination, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        if package_versions_text is not None:
            archive.writestr(PACKAGE_SUMMARY_FILENAME, package_versions_text)
        for path in source_files:
            try:
                archive.write(path, arcname=path.name)
            except OSError as exc:
                raise BackupZipError(
                    f"Nao foi possivel compactar o arquivo. Verifique se ele esta aberto "
                    f"ou indisponivel: {path}"
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

