"""SEL project type implementation for QuickSet and Architect backups."""

from __future__ import annotations

import re
from pathlib import Path

from src.core.naming import get_project_id, sanitize_filename_part
from src.core.project_types.base import BaseProjectType, ProjectVersionRequiredError

QUICKSET_VERSION_RE = re.compile(
    r"Saved\s+with\s+Main\s+Shell\s+Version:\s*([0-9]+(?:\.[0-9]+)+)",
    re.IGNORECASE,
)
ARCHITECT_VERSION_RE = re.compile(
    r"AcSELerator\s+Architect\s+([0-9]+(?:\.[0-9]+)+)",
    re.IGNORECASE,
)
COMPANION_EXTENSIONS = (".scd", ".selaprj")


class SelProjectType(BaseProjectType):
    """Project type adapter for SEL `.rdb` backups and optional Architect files."""

    key = "sel"
    label = "SEL (.rdb)"
    extensions = (".rdb",)

    def get_project_id(self, project_file: Path) -> str:
        """Use the same first-underscore policy already applied to other IED files."""

        return get_project_id(project_file.name)

    def get_software_version(
        self,
        project_file: Path,
        fallback_version: str | None = None,
    ) -> str:
        """Return a filename-safe SEL software prefix.

        QuickSet is mandatory for automatic detection. Architect is optional and
        is included when a same-stem `.scd` or `.selaprj` file exposes its toolID.
        """

        text = _read_text_lossy(project_file)
        quickset_version = _last_match(QUICKSET_VERSION_RE, text)
        if not quickset_version:
            if fallback_version:
                return _manual_sel_version(fallback_version)
            raise ProjectVersionRequiredError(
                project_type_label=self.label,
                project_file=project_file,
            )

        parts = [f"SEL-QS-V{quickset_version}"]
        architect_version = self._get_architect_version(project_file)
        if architect_version:
            parts.append(f"AA-V{architect_version}")
        return "-".join(parts)

    def get_related_files(self, project_file: Path) -> list[Path]:
        """Include the `.rdb` plus same-stem Architect files when present."""

        related = [project_file]
        for extension in COMPANION_EXTENSIONS:
            companion = project_file.with_suffix(extension)
            if companion.exists() and companion.is_file():
                related.append(companion)
        return related

    def _get_architect_version(self, project_file: Path) -> str | None:
        """Read optional Architect companion files and return the latest match."""

        for companion in self.get_related_files(project_file)[1:]:
            version = _last_match(ARCHITECT_VERSION_RE, _read_text_lossy(companion))
            if version:
                return version
        return None


def _read_text_lossy(path: Path) -> str:
    """Read mixed text/binary SEL files while preserving searchable ASCII snippets."""

    return path.read_bytes().decode("utf-8", errors="ignore")


def _last_match(pattern: re.Pattern[str], text: str) -> str | None:
    """Return the last version match because SEL files may contain saved history."""

    matches = pattern.findall(text)
    return matches[-1] if matches else None


def _manual_sel_version(version: str) -> str:
    """Normalize a manually supplied SEL version into a backup-name prefix."""

    normalized = sanitize_filename_part(version.strip())
    if not normalized:
        raise ProjectVersionRequiredError(
            project_type_label=SEL_PROJECT_TYPE.label,
            project_file=Path("SEL"),
        )
    if normalized.upper().startswith("SEL-"):
        return normalized.upper()
    return f"SEL-QS-V{normalized.upper()}"


SEL_PROJECT_TYPE = SelProjectType()
