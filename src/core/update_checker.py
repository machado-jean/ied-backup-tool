"""GitHub release update checks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen

LATEST_RELEASE_API_URL = (
    "https://api.github.com/repos/machado-jean/ied-backup-tool/releases/latest"
)
LATEST_RELEASE_PAGE_URL = (
    "https://github.com/machado-jean/ied-backup-tool/releases/latest"
)


@dataclass(frozen=True)
class UpdateCheckResult:
    """Result from comparing the installed version against GitHub Releases."""

    current_version: str
    latest_version: str
    release_url: str
    update_available: bool


def check_latest_release(
    current_version: str,
    *,
    api_url: str = LATEST_RELEASE_API_URL,
    timeout: float = 4,
    opener=urlopen,
) -> UpdateCheckResult:
    """Fetch the latest GitHub release and compare it with the current version."""

    request = Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "IED-Backup-Manager",
        },
    )
    with opener(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    latest_version = _normalize_version(payload.get("tag_name", ""))
    return UpdateCheckResult(
        current_version=current_version,
        latest_version=latest_version,
        release_url=LATEST_RELEASE_PAGE_URL,
        update_available=is_version_newer(latest_version, current_version),
    )


def is_version_newer(candidate: str, current: str) -> bool:
    """Return whether candidate is newer than current using semantic version parts."""

    return _version_key(candidate) > _version_key(current)


def _normalize_version(version: str) -> str:
    """Remove a leading tag prefix from a version string."""

    return version.strip().lstrip("vV")


def _version_key(version: str) -> tuple[int, int, int]:
    """Convert a version string to a comparable three-part tuple."""

    parts = _normalize_version(version).split(".")
    numbers: list[int] = []
    for part in parts[:3]:
        digits = "".join(char for char in part if char.isdigit())
        numbers.append(int(digits) if digits else 0)
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])
