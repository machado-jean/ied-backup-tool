from pathlib import Path
from zipfile import ZipFile

import pytest

from src.core.pcm600 import Pcm600VersionError, extract_pcm600_version


def test_extract_pcm600_version_from_versions_ini(tmp_path: Path) -> None:
    pcmp = tmp_path / "SE-DDD_20260619_1230.pcmp"
    with ZipFile(pcmp, "w") as archive:
        archive.writestr(
            "ProjectDataServer%versions.ini",
            "ProductName=PCM600_210\nProductVersion=2.10\n",
        )

    assert extract_pcm600_version(pcmp) == "PCM600-V2.10"


def test_extract_pcm600_version_finds_versions_ini_in_nested_folder(tmp_path: Path) -> None:
    pcmp = tmp_path / "SE-DDD_20260619_1230.pcmp"
    with ZipFile(pcmp, "w") as archive:
        archive.writestr(
            "ProjectData/ProjectDataServer%versions.ini",
            "ProductName=PCM600_210\nProductVersion=2.10\n",
        )

    assert extract_pcm600_version(pcmp) == "PCM600-V2.10"


def test_extract_pcm600_version_rejects_non_zip(tmp_path: Path) -> None:
    pcmp = tmp_path / "SE-DDD_20260619_1230.pcmp"
    pcmp.write_text("not a zip", encoding="utf-8")

    with pytest.raises(Pcm600VersionError, match="ZIP valido"):
        extract_pcm600_version(pcmp)


def test_extract_pcm600_version_requires_versions_ini(tmp_path: Path) -> None:
    pcmp = tmp_path / "SE-DDD_20260619_1230.pcmp"
    with ZipFile(pcmp, "w") as archive:
        archive.writestr("metadata.txt", "no versions")

    with pytest.raises(Pcm600VersionError, match="versions.ini"):
        extract_pcm600_version(pcmp)
