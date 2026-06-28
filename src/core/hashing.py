"""Hashing helpers for backup source file integrity metadata."""

from __future__ import annotations

import hashlib
from pathlib import Path


def calculate_sha256(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA256 hex digest for a file using chunked reads."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()
