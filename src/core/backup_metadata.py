"""Builders for human-readable metadata files stored inside backup ZIPs."""

from __future__ import annotations

from pathlib import Path

from src.core.hashing import calculate_sha256
from src.core.naming import BackupStage, get_file_timestamp

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
        f"Timestamp: {timestamp.strftime('%Y%m%d-%H%M')}",
        f"Collaborator: {collaborator}",
        f"Stage: {stage_text}",
        "",
        "Detected versions:",
    ]
    for label, version, project_file in versions:
        lines.append(f"- {label}: {version} ({project_file.name})")

    lines.extend(["", "Included files:"])
    for path in source_files:
        lines.append(
            f"- {path.name}",
        )
        lines.append(
            f"  Modified: {get_file_timestamp(path).strftime('%Y%m%d-%H%M')}",
        )
        lines.append(f"  Size: {path.stat().st_size} bytes")
        lines.append(f"  SHA256: {calculate_sha256(path)}")

    return "\n".join(lines) + "\n"
