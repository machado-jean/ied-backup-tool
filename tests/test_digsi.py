from pathlib import Path
from zipfile import ZipFile

import pytest

from src.core.digsi import DigsiVersionError, extract_digsi_version


def test_extract_digsi_version_from_zip_content(tmp_path: Path) -> None:
    dz5 = tmp_path / "SE-CTU_20260612_1736.dz5"
    with ZipFile(dz5, "w") as archive:
        archive.writestr("metadata.xml", "<version>10.0.0</version>")

    assert extract_digsi_version(dz5) == "DIGSI-V100"


def test_extract_digsi_version_prefers_dp5_version_from_zip_name(tmp_path: Path) -> None:
    dz5 = tmp_path / "SE_GVM_20260529_1624.dz5"
    with ZipFile(dz5, "w") as archive:
        archive.writestr("SE_GVM_DEV_V1_20260529_1624.dp5v100", "internal 20.0.0")

    assert extract_digsi_version(dz5) == "DIGSI-V100"


def test_extract_digsi_version_rejects_non_zip(tmp_path: Path) -> None:
    dz5 = tmp_path / "SE-CTU_20260612_1736.dz5"
    dz5.write_text("not a zip", encoding="utf-8")

    with pytest.raises(DigsiVersionError, match="ZIP valido"):
        extract_digsi_version(dz5)
