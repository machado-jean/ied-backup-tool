from pathlib import Path
from zipfile import ZipFile

import pytest

from src.core.storage import (
    StorageError,
    parse_backup_filename,
    quarantine_file,
    update_storage,
)


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
    create_zip(old, "old")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    final_path = update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert final_path == atu / new.name
    assert read_zip_payload(final_path) == "new"
    assert not old.exists()
    assert read_zip_payload(his / old.name) == "old"


def test_update_storage_recreates_files_in_destination(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    staged = tmp_path / "staging"
    staged.mkdir()
    new = staged / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    final_path = update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert final_path == atu / new.name
    assert read_zip_payload(final_path) == "new"
    assert not new.exists()


def test_update_storage_reports_copy_progress(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    staged = tmp_path / "staging"
    staged.mkdir()
    new = staged / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")
    total_bytes = new.stat().st_size
    events = []

    update_storage(
        new_backup=new,
        atu_path=atu,
        his_path=his,
        progress_callback=lambda phase, current, total: events.append((phase, current, total)),
    )

    assert events
    assert events[0] == ("copy_current", 0, total_bytes)
    assert events[-1] == ("copy_current", total_bytes, total_bytes)


def test_update_storage_quarantines_partial_copy_when_destination_copy_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    staged = tmp_path / "staging"
    staged.mkdir()
    new = staged / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    def fail_copy(input_file, output_file, **kwargs):
        output_file.write(input_file.read(16))
        raise OSError("disk unavailable")

    monkeypatch.setattr("src.core.storage.copy_stream_with_progress", fail_copy)

    with pytest.raises(StorageError, match="quarentena"):
        update_storage(new_backup=new, atu_path=atu, his_path=his)

    quarantine = tmp_path / "IED-QUARENTENA"
    quarantined_files = [path for path in quarantine.iterdir() if path.suffix == ".tmp"]
    notes = list(quarantine.glob("*.tmp.txt"))
    assert len(quarantined_files) == 1
    assert len(notes) == 1
    note_text = notes[0].read_text(encoding="utf-8")
    assert "Falha durante copia temporaria" in note_text
    assert "Erro original: OSError: disk unavailable" in note_text
    assert not list(atu.glob("*.zip"))
    assert new.exists()


def test_update_storage_cleans_matching_quarantine_after_success(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    quarantine = tmp_path / "IED-QUARENTENA"
    staged = tmp_path / "staging"
    staged.mkdir()
    partial = tmp_path / "partial.tmp"
    partial.write_text("partial", encoding="utf-8")
    original = atu / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    quarantine_file(
        partial,
        quarantine_root=quarantine,
        original_path=original,
        reason="teste",
    )
    new = staged / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert not quarantine.exists()


def test_update_storage_keeps_newer_quarantine_after_success(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    quarantine = tmp_path / "IED-QUARENTENA"
    staged = tmp_path / "staging"
    staged.mkdir()
    partial = tmp_path / "partial.tmp"
    partial.write_text("partial", encoding="utf-8")
    newer_original = atu / "DIGSI5-V10.00_SE-BBB_20260620-0910_COLABORADOR-EXEMPLO_DEV.zip"
    quarantine_file(
        partial,
        quarantine_root=quarantine,
        original_path=newer_original,
        reason="teste",
    )
    new = staged / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert quarantine.exists()
    assert list(quarantine.glob("*.tmp"))
    assert list(quarantine.glob("*.tmp.txt"))


def test_update_storage_keeps_different_project_in_atu(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    other = atu / "DIGSI5-V10.00_SE-GGG_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(other, "other")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert other.exists()
    assert (atu / new.name).exists()
    assert not list(his.glob("*.zip"))


def test_update_storage_rejects_older_backup(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    current = atu / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(current, "current")
    older = tmp_path / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(older, "older")

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
    create_zip(old, "old atu")
    existing_his = his / old.name
    create_zip(existing_his, "old his")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert not old.exists()
    assert read_zip_payload(existing_his) == "old his"
    assert len(list(his.glob("*.zip"))) == 1


def test_update_storage_treats_same_timestamp_with_different_stage_as_same_backup(
    tmp_path: Path,
) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    current = atu / "DIGSI5-V10.00_SE-AAA_20260529-1624_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(current, "current")
    same_identity = tmp_path / "DIGSI5-V10.00_SE-AAA_20260529-1624_COLABORADOR-EXEMPLO_TAC.zip"
    create_zip(same_identity, "same")

    final_path = update_storage(new_backup=same_identity, atu_path=atu, his_path=his)

    assert final_path == current
    assert read_zip_payload(current) == "current"
    assert not same_identity.exists()
    assert not list(his.glob("*.zip"))


def test_update_storage_validates_new_zip_before_touching_current(tmp_path: Path) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    current = atu / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(current, "current")
    invalid = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    invalid.write_text("not a zip", encoding="utf-8")

    with pytest.raises(StorageError, match="invalido|ilegivel"):
        update_storage(new_backup=invalid, atu_path=atu, his_path=his)

    assert current.exists()
    assert read_zip_payload(current) == "current"
    assert not list(his.glob("*.zip"))


def test_update_storage_rolls_back_new_current_when_history_move_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    atu = tmp_path / "ATU"
    his = tmp_path / "HIS"
    atu.mkdir()
    current = atu / "DIGSI5-V10.00_SE-BBB_20260612-1739_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(current, "current")
    new = tmp_path / "DIGSI5-V10.00_SE-BBB_20260615-0910_COLABORADOR-EXEMPLO_DEV.zip"
    create_zip(new, "new")

    def fail_history(*args, **kwargs):
        raise StorageError("history unavailable")

    monkeypatch.setattr("src.core.storage.move_to_history", fail_history)

    with pytest.raises(StorageError, match="history unavailable"):
        update_storage(new_backup=new, atu_path=atu, his_path=his)

    assert current.exists()
    assert read_zip_payload(current) == "current"
    assert not (atu / new.name).exists()


def create_zip(path: Path, payload: str) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr("payload.txt", payload)
    return path


def read_zip_payload(path: Path) -> str:
    with ZipFile(path) as archive:
        return archive.read("payload.txt").decode("utf-8")

