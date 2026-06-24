from pathlib import Path

import pytest

from src.core.backup_service import plan_latest_backup
from src.core.project_types.base import ProjectVersionRequiredError
from src.core.project_types.ingeteam import INGETEAM_PROJECT_TYPE
from src.core.project_types.registry import get_project_type


def test_registry_exposes_ingeteam_project_type() -> None:
    assert get_project_type("ingeteam") is INGETEAM_PROJECT_TYPE
    assert INGETEAM_PROJECT_TYPE.extensions == (".efspro", ".itpro2")


def test_ingeteam_requires_manual_version(tmp_path: Path) -> None:
    project_file = tmp_path / "SE-ING_DEV_20260619_0013.efsPro"
    project_file.write_text("TeamZipVer5.0", encoding="utf-8")

    with pytest.raises(ProjectVersionRequiredError):
        INGETEAM_PROJECT_TYPE.get_software_version(project_file)


def test_ingeteam_formats_manual_version(tmp_path: Path) -> None:
    project_file = tmp_path / "SE-ING_DEV_20260619_0013.ITPro2"
    project_file.write_text("zip placeholder", encoding="utf-8")

    assert (
        INGETEAM_PROJECT_TYPE.get_software_version(project_file, "5.5.4")
        == "INGESYS-V5.5.4"
    )


def test_ingeteam_plan_uses_configured_version(tmp_path: Path) -> None:
    project_dir = tmp_path / "IED-DES"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    project_file = project_dir / "SE-ING_DEV_20260619_0013.efsPro"
    project_file.write_text("TeamZipVer5.0", encoding="utf-8")

    plan = plan_latest_backup(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage="TAF",
        project_type=INGETEAM_PROJECT_TYPE,
        software_version_override="5.5.4",
    )

    assert plan.backup_name.startswith("INGESYS-V5.5.4_SE-ING_")

