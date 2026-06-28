from datetime import datetime

from src.core.naming import BackupStage, build_backup_name, get_project_id, normalize_stage


def test_backup_stage_order_matches_workflow() -> None:
    assert [stage.value for stage in BackupStage] == [
        "DEV",
        "PRE-TAF",
        "TAF",
        "POS-TAF",
        "PRE-TAC",
        "TAC",
        "POS-TAC",
    ]


def test_get_project_id_uses_text_before_first_underscore() -> None:
    assert get_project_id("SE-BBB_20260612_1736.dz5") == "SE-BBB"


def test_get_project_id_ignores_text_between_project_and_timestamp() -> None:
    assert get_project_id("SE-BBB_DEV_01_20260619_0013.dz5") == "SE-BBB"


def test_get_project_id_uses_first_block_even_without_timestamp_suffix() -> None:
    assert get_project_id("SE-BBB_REVISAO_FINAL.dz5") == "SE-BBB"


def test_build_backup_name_uses_required_pattern() -> None:
    result = build_backup_name(
        software_version="DIGSI5-V10.00",
        project_id="SE-BBB",
        timestamp=datetime(2026, 6, 12, 17, 39),
        collaborator="Colaborador Exemplo",
        stage=BackupStage.DEV,
    )

    assert result == "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"


def test_build_backup_name_accepts_free_stage_description() -> None:
    result = build_backup_name(
        software_version="DIGSI5-V10.00",
        project_id="SE-BBB",
        timestamp=datetime(2026, 6, 12, 17, 39),
        collaborator="Colaborador Exemplo",
        stage="backup antes de grande alteração",
    )

    assert (
        result
        == "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_"
        "BACKUP-ANTES-DE-GRANDE-ALTERACAO.zip"
    )


def test_build_backup_name_accepts_empty_stage_description() -> None:
    result = build_backup_name(
        software_version="DIGSI5-V10.00",
        project_id="SE-BBB",
        timestamp=datetime(2026, 6, 12, 17, 39),
        collaborator="Colaborador Exemplo",
        stage="",
    )

    assert result == "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_.zip"


def test_normalize_stage_removes_filename_unsafe_separators() -> None:
    assert normalize_stage(" grande_alteracao / fase 2 ") == "GRANDE-ALTERACAO-FASE-2"

