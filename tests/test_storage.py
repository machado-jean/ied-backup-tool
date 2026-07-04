from pathlib import Path

import pytest

from src.core.storage import StorageError, parse_backup_filename, update_storage


def test_parse_backup_filename_extracts_key_and_timestamp(tmp_path: Path) -> None:
    path = tmp_path / "DIGSI5-V10.00_SE_AAA_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    path.write_text("backup", encoding="utf-8")

    info = parse_backup_filename(path)

    assert info.key == "DIGSI5-V10.00_SE_AAA"
    assert info.project == "SE_AAA"
    assert info.stage == "DEV"


def test_update_storage_moves_previous_atu_backup_to_his(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    old = atu / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    old.write_text("old", encoding="utf-8")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    new.write_text("new", encoding="utf-8")

    final_path = update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert final_path == atu / new.name
    assert final_path.read_text(encoding="utf-8") == "new"
    assert not old.exists()
    assert (his / old.name).read_text(encoding="utf-8") == "old"


def test_update_storage_recreates_files_in_destination_without_shutil_move(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    staged = tmp_path / "staging"
    staged.mkdir()
    new = staged / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    new.write_text("new", encoding="utf-8")

    def fail_move(*args, **kwargs):
        raise AssertionError("shutil.move must not be used for final backup placement")

    monkeypatch.setattr("src.core.storage.shutil.move", fail_move)

    final_path = update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert final_path == atu / new.name
    assert final_path.read_text(encoding="utf-8") == "new"
    assert not new.exists()


def test_update_storage_keeps_different_project_in_atu(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    other = atu / "DIGSI5-V10.00_SE-GGG_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    other.write_text("other", encoding="utf-8")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    new.write_text("new", encoding="utf-8")

    update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert other.exists()
    assert (atu / new.name).exists()
    assert not list(his.glob("*.zip"))


def test_update_storage_rejects_older_backup(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    current = atu / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    current.write_text("current", encoding="utf-8")
    older = tmp_path / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    older.write_text("older", encoding="utf-8")

    with pytest.raises(StorageError, match="mais recente"):
        update_storage(new_backup=older, atu_path=atu, his_path=his)

    assert current.exists()
    assert not older.exists()
    assert not list(his.glob("*.zip"))


def test_update_storage_does_not_duplicate_identical_his_file(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    his.mkdir()
    old = atu / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    old.write_text("old atu", encoding="utf-8")
    existing_his = his / old.name
    existing_his.write_text("old his", encoding="utf-8")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    new.write_text("new", encoding="utf-8")

    update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert not old.exists()
    assert existing_his.read_text(encoding="utf-8") == "old his"
    assert len(list(his.glob("*.zip"))) == 1


def test_update_storage_treats_same_timestamp_with_different_stage_as_same_backup(
    tmp_path: Path,
) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    current = atu / "DIGSI5-V10.00_SE-AAA_20260529-1624_COLABORADOR-EXEMPLO_DEV.zip"
    current.write_text("current", encoding="utf-8")
    same_identity = tmp_path / "DIGSI5-V10.00_SE-AAA_20260529-1624_COLABORADOR-EXEMPLO_TAC.zip"
    same_identity.write_text("same", encoding="utf-8")

    final_path = update_storage(new_backup=same_identity, atu_path=atu, his_path=his)

    assert final_path == current
    assert current.read_text(encoding="utf-8") == "current"
    assert not same_identity.exists()
    assert not list(his.glob("*.zip"))

