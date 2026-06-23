from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from src.core.backup_service import process_all_backups
from src.core.naming import BackupStage
from src.core.project_types.base import BaseProjectType
from src.core.project_types.registry import DEFAULT_PROJECT_TYPE, get_project_type


class FakeProjectType(BaseProjectType):
    key = "fake"
    label = "Fake IED (.fake)"
    extensions = (".fake",)

    def get_project_id(self, project_file: Path) -> str:
        return project_file.stem

    def get_software_version(
        self,
        project_file: Path,
        fallback_version: str | None = None,
    ) -> str:
        return "FAKE-V1"


def test_default_project_type_is_digsi() -> None:
    assert DEFAULT_PROJECT_TYPE.key == "digsi5"
    assert DEFAULT_PROJECT_TYPE.extensions == (".dz5",)
    assert get_project_type("digsi5") is DEFAULT_PROJECT_TYPE


def test_backup_service_accepts_custom_project_type(tmp_path: Path) -> None:
    project_dir = tmp_path / "BKPs"
    atu = tmp_path / "IED-ATU"
    his = tmp_path / "IED-HIS"
    project_dir.mkdir()
    project_file = project_dir / "SEL-751.fake"
    project_file.write_text("fake project", encoding="utf-8")
    timestamp = datetime(2026, 6, 18, 10, 30).timestamp()
    os.utime(project_file, (timestamp, timestamp))

    results = process_all_backups(
        project_dir=project_dir,
        atu_path=atu,
        his_path=his,
        collaborator="JEAN-CARLOS-MACHADO",
        stage=BackupStage.TAF,
        project_type=FakeProjectType(),
    )

    assert [result.status for result in results] == ["stored"]
    assert [path.name for path in atu.glob("*.zip")] == [
        "FAKE-V1_SEL-751_20260618-1030_JEAN-CARLOS-MACHADO_TAF.zip"
    ]
