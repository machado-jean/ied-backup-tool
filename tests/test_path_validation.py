from pathlib import Path

import pytest

from src.core.path_validation import (
    StoragePathValidationError,
    create_missing_storage_paths,
    validate_storage_paths,
)


def test_validate_storage_paths_rejects_same_folder(tmp_path: Path) -> None:
    folder = tmp_path / "ATU"
    folder.mkdir()

    with pytest.raises(StoragePathValidationError, match="mesma pasta"):
        validate_storage_paths(folder, folder)


def test_validate_storage_paths_rejects_files(tmp_path: Path) -> None:
    atu_file = tmp_path / "atu.txt"
    atu_file.write_text("not a folder", encoding="utf-8")
    his = tmp_path / "HIS"

    with pytest.raises(StoragePathValidationError, match="arquivo"):
        validate_storage_paths(atu_file, his)


def test_validate_storage_paths_reports_missing_folders(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"

    validation = validate_storage_paths(atu, his)

    assert validation.missing_paths == (atu, his)


def test_create_missing_storage_paths_creates_expected_folders(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    validation = validate_storage_paths(atu, his)

    create_missing_storage_paths(validation)

    assert atu.is_dir()
    assert his.is_dir()


def test_validate_storage_paths_warns_when_one_folder_is_nested(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = atu / "HIS"

    validation = validate_storage_paths(atu, his)

    assert validation.nested_warning == f"HIS esta dentro de ATU: {his}"


def test_validate_storage_paths_warns_for_synced_folders() -> None:
    atu = Path("C:/Users/Usuario/OneDrive - Empresa/ATU")
    his = Path("C:/Backups/HIS")

    validation = validate_storage_paths(atu, his)

    assert validation.synced_warnings == (f"ATU: {atu.resolve(strict=False)} (OneDrive - Empresa)",)


def test_validate_storage_paths_does_not_warn_for_regular_folders(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"

    validation = validate_storage_paths(atu, his)

    assert validation.synced_warnings == ()
