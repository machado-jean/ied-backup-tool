"""DIGSI-specific version extraction from `.dz5` archives."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path


class DigsiVersionError(RuntimeError):
    pass


VERSION_PATTERN = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{1,3})\b")
DP5_VERSION_PATTERN = re.compile(r"\.dp5v(\d+)\b", re.IGNORECASE)


def extract_digsi_version(dz5_path: Path) -> str:
    """Extract the DIGSI version prefix from archive names or file contents."""

    if not zipfile.is_zipfile(dz5_path):
        raise DigsiVersionError(f"Arquivo .dz5 nao e um ZIP valido: {dz5_path}")

    with zipfile.ZipFile(dz5_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            version = _dp5_version_from_name(info.filename)
            if version:
                return version

        for info in archive.infolist():
            if info.is_dir():
                continue
            version = _version_from_name(info.filename)
            if version:
                return version

        for info in archive.infolist():
            if info.is_dir() or info.file_size > 2_000_000:
                continue
            version = _version_from_member(archive, info)
            if version:
                return version

    raise DigsiVersionError(f"Versao do DIGSI nao encontrada em: {dz5_path}")


def _dp5_version_from_name(name: str) -> str | None:
    """Read the preferred `.dp5v###` version marker from an archive member name."""

    match = DP5_VERSION_PATTERN.search(name)
    return f"DIGSI-V{int(match.group(1))}" if match else None


def _version_from_name(name: str) -> str | None:
    """Fallback version detection based on semantic-looking version fragments."""

    match = VERSION_PATTERN.search(name)
    return _format_version(match) if match else None


def _version_from_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> str | None:
    """Fallback version detection by scanning small text-like archive members."""

    try:
        content = archive.read(info).decode("utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError, zipfile.BadZipFile):
        return None

    match = VERSION_PATTERN.search(content)
    return _format_version(match) if match else None


def _format_version(match: re.Match[str]) -> str:
    """Convert a matched DIGSI version into the backup prefix format."""

    major, minor, patch = match.groups()
    version = f"{int(major)}{int(minor)}"
    if int(patch) != 0:
        version += str(int(patch))
    return f"DIGSI-V{version}"
