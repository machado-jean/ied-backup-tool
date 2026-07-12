from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.core.backup_metadata import build_backup_info_text
from src.core.hashing import calculate_sha256
from src.core.naming import BackupStage


def test_build_backup_info_text_includes_source_hash_and_detected_versions(
    tmp_path: Path,
) -> None:
    source = tmp_path / "SE-AAA_COMENTARIO_20260622_1350.dz5"
    source.write_bytes(b"backup-content")
    backup_name = "DIGSI5-V10.00_SE-AAA_20260622-1350_COLABORADOR-EXEMPLO_DEV.zip"

    text = build_backup_info_text(
        backup_name=backup_name,
        project="SE-AAA",
        software="DIGSI5-V10.00",
        timestamp=datetime(2026, 6, 22, 13, 50),
        collaborator="COLABORADOR-EXEMPLO",
        stage=BackupStage.DEV,
        project_type_label="DIGSI 5 (.dz5)",
        source_file=source,
        source_files=[source],
        detected_versions=[("DIGSI 5 (.dz5)", "DIGSI5-V10.00", source)],
    )

    assert f"Backup: {backup_name}" in text
    assert "Project: SE-AAA" in text
    assert "Stage: DEV" in text
    assert f"SHA256: {calculate_sha256(source)}" in text
    assert "- DIGSI 5 (.dz5): DIGSI5-V10.00" in text


def test_build_backup_info_text_uses_relative_paths_for_nested_sources(
    tmp_path: Path,
) -> None:
    root_file = tmp_path / "SE-AAA.ENV"
    nested = tmp_path / "IED-A" / "IED-A.urs"
    nested.parent.mkdir()
    root_file.write_text("env", encoding="utf-8")
    nested.write_text("urs", encoding="utf-8")

    text = build_backup_info_text(
        backup_name="GE-MULTILIN-V8.40_SE-AAA_20260622-1350_COLABORADOR_DEV.zip",
        project="SE-AAA",
        software="GE-MULTILIN-V8.40",
        timestamp=datetime(2026, 6, 22, 13, 50),
        collaborator="COLABORADOR",
        stage=BackupStage.DEV,
        project_type_label="GE Multilin UR (.urs, .urk)",
        source_file=nested,
        source_files=[root_file, nested],
        detected_versions=None,
        extra_sections=["GE Multilin IED Summary:\n- IED-A"],
    )

    assert "GE Multilin IED Summary:" in text
    assert "- SE-AAA.ENV" in text
    assert "- IED-A/IED-A.urs" in text
