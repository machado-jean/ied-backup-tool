"""Builders for human-readable metadata files stored inside backup ZIPs."""

from __future__ import annotations

import os
from pathlib import Path

from src.core.hashing import calculate_sha256
from src.core.naming import BackupStage, format_backup_timestamp, get_file_timestamp

StageValue = BackupStage | str


def build_backup_info_text(
    *,
    backup_name: str,
    project: str,
    software: str,
    timestamp,
    collaborator: str,
    stage: StageValue,
    project_type_label: str,
    source_file: Path,
    source_files: list[Path],
    detected_versions: list[tuple[str, str, Path]] | None,
    extra_sections: list[str] | None = None,
) -> str:
    """Build a human-readable metadata file included in every backup zip."""

    stage_text = stage.value if isinstance(stage, BackupStage) else str(stage)
    versions = detected_versions or [(project_type_label, software, source_file)]
    lines = [
        "IED Backup Manager - Backup Information",
        "",
        f"Backup: {backup_name}",
        f"Project: {project}",
        f"Software: {software}",
        f"Timestamp: {format_backup_timestamp(timestamp)}",
        f"Collaborator: {collaborator}",
        f"Stage: {stage_text}",
        "",
        "Detected versions:",
    ]
    for label, version, project_file in versions:
        lines.append(f"- {label}: {version} ({project_file.name})")

    for section in extra_sections or []:
        lines.extend(["", section.rstrip()])

    lines.extend(["", "Included files:"])
    display_root = _display_root_for(source_files)
    for path in source_files:
        lines.append(
            f"- {_display_path(path, display_root)}",
        )
        lines.append(
            f"  Modified: {format_backup_timestamp(get_file_timestamp(path))}",
        )
        lines.append(f"  Size: {path.stat().st_size} bytes")
        lines.append(f"  SHA256: {calculate_sha256(path)}")

    return "\n".join(lines) + "\n"


def _display_root_for(source_files: list[Path]) -> Path | None:
    """Return a common root when included files span multiple folders."""

    if len({path.parent.resolve() for path in source_files}) <= 1:
        return None
    return Path(os.path.commonpath([str(path.resolve()) for path in source_files]))


def _display_path(path: Path, display_root: Path | None) -> str:
    """Format source paths in a readable way for the ZIP metadata file."""

    if display_root is None:
        return path.name
    return path.resolve().relative_to(display_root).as_posix()
