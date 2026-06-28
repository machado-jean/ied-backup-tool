"""ABB PCM600 version extraction from project packages."""

from __future__ import annotations

import zipfile
from pathlib import Path

from src.core.naming import sanitize_filename_part

VERSIONS_INI_NAME = "ProjectDataServer%versions.ini"


class Pcm600VersionError(RuntimeError):
    pass


def extract_pcm600_version(project_path: Path) -> str:
    """Extract the PCM600 product/version prefix from a PCM600 package."""

    if not zipfile.is_zipfile(project_path):
        raise Pcm600VersionError(f"Arquivo PCM600 nao e um pacote ZIP valido: {project_path}")

    with zipfile.ZipFile(project_path) as archive:
        info = _find_versions_ini(archive)
        if info is None:
            raise Pcm600VersionError(
                f"Arquivo {VERSIONS_INI_NAME} nao encontrado em: {project_path}"
            )

        try:
            content = archive.read(info).decode("utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
            raise Pcm600VersionError(
                f"Nao foi possivel ler {VERSIONS_INI_NAME} em: {project_path}"
            ) from exc

    values = _parse_ini_values(content)
    product_version = values.get("ProductVersion")
    if not product_version:
        raise Pcm600VersionError(
            f"ProductVersion nao encontrado em {VERSIONS_INI_NAME}: {project_path}"
        )

    safe_version = sanitize_filename_part(product_version)
    return f"PCM600-V{safe_version}"


def _find_versions_ini(archive: zipfile.ZipFile) -> zipfile.ZipInfo | None:
    """Find the PCM600 versions file regardless of its package folder path."""

    for info in archive.infolist():
        normalized = info.filename.replace("\\", "/")
        if not info.is_dir() and normalized.endswith(VERSIONS_INI_NAME):
            return info
    return None


def _parse_ini_values(content: str) -> dict[str, str]:
    """Parse simple `key=value` lines from the PCM600 versions file."""

    values = {}
    for line in content.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key.strip()] = value.strip()
    return values
