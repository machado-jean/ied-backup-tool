from pathlib import Path
from zipfile import ZipFile

import pytest

from src.core.digsi import DigsiVersionError, extract_digsi_version


def test_extract_digsi_version_from_zip_content(tmp_path: Path) -> None:
    dz5 = tmp_path / "SE-CTU_20260612_1736.dz5"
    with ZipFile(dz5, "w") as archive:
        archive.writestr("metadata.xml", "<version>10.0.0</version>")

    assert extract_digsi_version(dz5) == "DIGSI5-V10.00"


def test_extract_digsi_version_prefers_dp5_version_from_zip_name(tmp_path: Path) -> None:
    dz5 = tmp_path / "SE_GVM_20260529_1624.dz5"
    with ZipFile(dz5, "w") as archive:
        archive.writestr("SE_GVM_DEV_V1_20260529_1624.dp5v100", "internal 20.0.0")

    assert extract_digsi_version(dz5) == "DIGSI5-V10.00"


@pytest.mark.parametrize(
    ("member_name", "expected"),
    [
        ("UHESN_20260622_1350.dp5v75", "DIGSI5-V7.50"),
        ("UHESN_20260622_1350.dp5v98", "DIGSI5-V9.80"),
        ("UHESN_20260622_1350.dp5v100", "DIGSI5-V10.00"),
        ("UHESN_20260622_1350.dp4v75", "DIGSI4-V7.50"),
    ],
)
def test_extract_digsi_version_formats_dp_marker(
    tmp_path: Path,
    member_name: str,
    expected: str,
) -> None:
    dz5 = tmp_path / "SE_GVM_20260529_1624.dz5"
    with ZipFile(dz5, "w") as archive:
        archive.writestr(member_name, "DIGSI project")

    assert extract_digsi_version(dz5) == expected


def test_extract_digsi_version_rejects_non_zip(tmp_path: Path) -> None:
    dz5 = tmp_path / "SE-CTU_20260612_1736.dz5"
    dz5.write_text("not a zip", encoding="utf-8")

    with pytest.raises(DigsiVersionError, match="ZIP valido"):
        extract_digsi_version(dz5)

