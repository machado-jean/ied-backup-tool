from pathlib import Path

from src.core.hashing import calculate_sha256


def test_calculate_sha256_returns_uppercase_digest(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("abc", encoding="utf-8")

    assert calculate_sha256(source) == (
        "BA7816BF8F01CFEA414140DE5DAE2223"
        "B00361A396177A9CB410FF61F20015AD"
    )
