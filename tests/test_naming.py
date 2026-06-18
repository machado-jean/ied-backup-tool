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
    assert get_project_id("SE-CTU_20260612_1736.dz5") == "SE-CTU"


def test_get_project_id_supports_underscore_inside_project_name() -> None:
    assert get_project_id("SE_GVM_20260529_1624.dz5") == "SE_GVM"


def test_build_backup_name_uses_required_pattern() -> None:
    result = build_backup_name(
        software_version="DIGSI-V100",
        project_id="SE-CTU",
        timestamp=datetime(2026, 6, 12, 17, 39),
        collaborator="Jean Carlos Machado",
        stage=BackupStage.DEV,
    )

    assert result == "DIGSI-V100_SE-CTU_20260612-1739_JEAN-CARLOS-MACHADO_DEV.zip"


def test_build_backup_name_accepts_free_stage_description() -> None:
    result = build_backup_name(
        software_version="DIGSI-V100",
        project_id="SE-CTU",
        timestamp=datetime(2026, 6, 12, 17, 39),
        collaborator="Jean Carlos Machado",
        stage="backup antes de grande alteração",
    )

    assert (
        result
        == "DIGSI-V100_SE-CTU_20260612-1739_JEAN-CARLOS-MACHADO_"
        "BACKUP-ANTES-DE-GRANDE-ALTERACAO.zip"
    )


def test_build_backup_name_accepts_empty_stage_description() -> None:
    result = build_backup_name(
        software_version="DIGSI-V100",
        project_id="SE-CTU",
        timestamp=datetime(2026, 6, 12, 17, 39),
        collaborator="Jean Carlos Machado",
        stage="",
    )

    assert result == "DIGSI-V100_SE-CTU_20260612-1739_JEAN-CARLOS-MACHADO_.zip"


def test_normalize_stage_removes_filename_unsafe_separators() -> None:
    assert normalize_stage(" grande_alteracao / fase 2 ") == "GRANDE-ALTERACAO-FASE-2"
