"""Validation helpers for configured ATU and HIS storage folders."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class StoragePathValidationError(ValueError):
    pass


@dataclass(frozen=True)
class StoragePathValidation:
    """Structured result for ATU/HIS path validation."""

    atu_path: Path
    his_path: Path
    missing_paths: tuple[Path, ...] = ()
    nested_warning: str | None = None


def validate_storage_paths(atu_path: Path, his_path: Path) -> StoragePathValidation:
    """Validate ATU/HIS folder relationship without creating folders."""

    normalized_atu = _normalize_path(atu_path)
    normalized_his = _normalize_path(his_path)

    if _path_key(normalized_atu) == _path_key(normalized_his):
        raise StoragePathValidationError("ATU e HIS nao podem apontar para a mesma pasta.")

    for label, path in (("ATU", normalized_atu), ("HIS", normalized_his)):
        if path.exists() and not path.is_dir():
            raise StoragePathValidationError(
                f"{label} aponta para um arquivo, nao uma pasta: {path}"
            )

    nested_warning = _nested_warning(normalized_atu, normalized_his)
    missing_paths = tuple(path for path in (normalized_atu, normalized_his) if not path.exists())
    return StoragePathValidation(
        atu_path=normalized_atu,
        his_path=normalized_his,
        missing_paths=missing_paths,
        nested_warning=nested_warning,
    )


def create_missing_storage_paths(validation: StoragePathValidation) -> None:
    """Create missing ATU/HIS folders from a validation result."""

    for path in validation.missing_paths:
        path.mkdir(parents=True, exist_ok=True)


def _normalize_path(path: Path) -> Path:
    """Return a comparable absolute path without requiring it to exist."""

    return path.expanduser().resolve(strict=False)


def _path_key(path: Path) -> str:
    """Return a platform-aware comparison key for a path."""

    return os.path.normcase(str(path))


def _nested_warning(atu_path: Path, his_path: Path) -> str | None:
    """Return a warning when ATU and HIS are nested inside each other."""

    if _is_relative_to(his_path, atu_path):
        return f"HIS esta dentro de ATU: {his_path}"
    if _is_relative_to(atu_path, his_path):
        return f"ATU esta dentro de HIS: {atu_path}"
    return None


def _is_relative_to(path: Path, possible_parent: Path) -> bool:
    """Return whether path is a descendant of possible_parent, excluding equality."""

    if _path_key(path) == _path_key(possible_parent):
        return False
    try:
        path.relative_to(possible_parent)
    except ValueError:
        return False
    return True
