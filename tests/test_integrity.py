from pathlib import Path
from zipfile import ZipFile

from src.core.hashing import calculate_sha256
from src.core.integrity import has_sha256_conflict, read_backup_sha256_map
from src.core.zipper import BACKUP_INFO_FILENAME, create_backup_zip


def test_read_backup_sha256_map_from_backup_info(tmp_path: Path) -> None:
    backup = tmp_path / "backup.zip"
    with ZipFile(backup, "w") as archive:
        archive.writestr(
            BACKUP_INFO_FILENAME,
            "\n".join(
                [
                    "Included files:",
                    "- SE-AAA_20260619_1230.dz5",
                    "  Modified: 20260619-1230",
                    "  Size: 10 bytes",
                    "  SHA256: ABC123",
                    "",
                ]
            ),
        )

    assert read_backup_sha256_map(backup) == {"SE-AAA_20260619_1230.dz5": "ABC123"}


def test_has_sha256_conflict_detects_changed_source_content(tmp_path: Path) -> None:
    source = tmp_path / "SE-AAA_20260619_1230.dz5"
    source.write_text("old content", encoding="utf-8")
    old_sha = calculate_sha256(source)
    backup_info = (
        "Included files:\n"
        f"- {source.name}\n"
        "  Modified: 20260619-1230\n"
        "  Size: 11 bytes\n"
        "  SHA256: "
    )
    backup = create_backup_zip(
        source,
        "DIGSI5-V10.00_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_DEV.zip",
        output_dir=tmp_path / "out",
        backup_info_text=backup_info + f"{old_sha}\n",
    )
    source.write_text("new content", encoding="utf-8")

    assert has_sha256_conflict((source,), backup)


def test_has_sha256_conflict_ignores_backups_without_sha_metadata(tmp_path: Path) -> None:
    source = tmp_path / "SE-AAA_20260619_1230.dz5"
    source.write_text("new content", encoding="utf-8")
    backup = tmp_path / "legacy.zip"
    with ZipFile(backup, "w") as archive:
        archive.writestr("metadata.txt", "legacy")

    assert not has_sha256_conflict((source,), backup)
