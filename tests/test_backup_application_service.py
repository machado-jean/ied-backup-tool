from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pytest

from src.config.config_manager import AppConfig
from src.core.backup_models import BackupStatus
from src.core.project_types.registry import get_project_type
from src.gui.backup_application_service import (
    PreviewRequest,
    PreviewValidationCode,
    PreviewValidationError,
    build_preview,
    executable_backup_count,
    manual_version_project_type,
    summarize_preview,
)


def test_build_preview_requires_stage(tmp_path: Path) -> None:
    with pytest.raises(PreviewValidationError) as error:
        build_preview(
            PreviewRequest(
                project_dir=tmp_path,
                config=_config(tmp_path),
                selected_project_types=[get_project_type("digsi5")],
                selected_stage=None,
                latest_only=False,
                software_version_override=None,
                software_version_overrides={},
            )
        )

    assert error.value.code == PreviewValidationCode.REQUIRED_STAGE


def test_build_preview_plans_selected_type(tmp_path: Path) -> None:
    project_dir = tmp_path / "IED-DES"
    project_dir.mkdir()
    create_dz5(project_dir / "SE-AAA_COMENTARIO_20260622_1350.dz5", datetime(2026, 6, 22, 13, 50))

    preview = build_preview(
        PreviewRequest(
            project_dir=project_dir,
            config=_config(tmp_path),
            selected_project_types=[get_project_type("digsi5")],
            selected_stage="DEV",
            latest_only=False,
            software_version_override=None,
            software_version_overrides={},
        )
    )
    summary = summarize_preview(preview.plans, preview.duplicate_plans)

    assert len(preview.plans) == 1
    assert preview.plans[0].status == BackupStatus.STORED
    assert preview.plans[0].project == "SE-AAA"
    assert executable_backup_count(summary) == 1


def test_manual_version_project_type_returns_selected_manual_type() -> None:
    assert manual_version_project_type([get_project_type("ingeteam")]).key == "ingeteam"
    assert manual_version_project_type([get_project_type("digsi5")]) is None


def _config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        collaborator="COLABORADOR-EXEMPLO",
        atu_path=tmp_path / "IED-ATU",
        his_path=tmp_path / "IED-HIS",
    )


def create_dz5(path: Path, mtime: datetime) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr(f"{path.stem}.dp5v100", "DIGSI project")
    timestamp = mtime.timestamp()
    os.utime(path, (timestamp, timestamp))
    return path
