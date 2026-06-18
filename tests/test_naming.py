from datetime import datetime

from src.core.naming import BackupStage, build_backup_name, get_project_id


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
