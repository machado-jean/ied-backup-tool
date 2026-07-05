"""Progress helpers shared by ZIP creation, storage, and GUI execution."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from typing import BinaryIO

ProgressCallback = Callable[[str, int, int], None]
CancellationCallback = Callable[[], bool]

CHUNK_SIZE = 1024 * 1024


def copy_stream_with_progress(
    source: BinaryIO,
    destination: BinaryIO,
    *,
    total_bytes: int,
    phase: str,
    progress_callback: ProgressCallback | None = None,
) -> None:
    """Copy a binary stream and report cumulative bytes for the active phase."""

    if progress_callback is None:
        shutil.copyfileobj(source, destination)
        return

    copied = 0
    progress_callback(phase, copied, total_bytes)
    while True:
        chunk = source.read(CHUNK_SIZE)
        if not chunk:
            break
        destination.write(chunk)
        copied += len(chunk)
        progress_callback(phase, copied, total_bytes)
