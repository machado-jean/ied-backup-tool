"""GE Multilin / EnerVista UR project type implementation."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from src.core.naming import sanitize_filename_part
from src.core.project_types.base import BaseProjectType, ProjectDetectionError

IED_MARKER_EXTENSIONS = (".urs", ".urk")
INCLUDED_EXTENSIONS = (".urs", ".urk", ".cid", ".icd")
ENV_EXTENSION = ".env"

UR_SETUP_VERSION_RE = re.compile(
    r"GE\s+Digital\s+Energy\s+UR\s+Setup\s+([0-9]+(?:\.[0-9]+)+)",
    re.IGNORECASE,
)
SCL_HEADER_VERSION_RE = re.compile(
    r"<Header[^>]+id=\"[^\"]+_([0-9]+(?:\.[0-9]+)?)\"",
    re.IGNORECASE,
)


class GeMultilinProjectType(BaseProjectType):
    """Project type adapter for GE Multilin / EnerVista UR environments.

    A GE UR backup is environment-oriented: the selected folder represents the
    substation/application, and direct child folders with `.urs` or `.urk` files
    represent IEDs. The top-level `.ENV` file is included when present, but it is
    not required to recognize a valid GE backup.
    """

    key = "ge_multilin"
    label = "GE Multilin UR (.urs, .urk)"
    extensions = IED_MARKER_EXTENSIONS

    def find_files(self, project_dir: Path) -> list[Path]:
        """Return one representative file for the GE environment."""

        if not project_dir.exists() or not project_dir.is_dir():
            raise ProjectDetectionError(f"Pasta do projeto invalida: {project_dir}")

        source_files = _collect_ge_source_files(project_dir)
        if not source_files:
            raise ProjectDetectionError(
                f"Nenhuma pasta GE Multilin com .urs ou .urk encontrada em: {project_dir}"
            )

        return [max(source_files, key=lambda path: (path.stat().st_mtime, path.name))]

    def get_project_id(self, project_file: Path) -> str:
        """Use the GE environment folder name as the project identifier."""

        root = _environment_root(project_file)
        project_id = sanitize_filename_part(root.name)
        if not project_id:
            raise ValueError(f"Identificador do projeto invalido: {root}")
        return project_id

    def get_software_version(
        self,
        project_file: Path,
        fallback_version: str | None = None,
    ) -> str:
        """Return the highest detected GE UR Setup version.

        When SCL files are unavailable, fall back to the highest GEMULTILIN
        application version found in `.urs`/`.urk` headers.
        """

        source_files = self.get_related_files(project_file)
        setup_versions = [
            version
            for path in source_files
            if path.suffix.lower() in {".cid", ".icd"}
            for version in _ur_setup_versions(path)
        ]
        if setup_versions:
            return f"GE-URSETUP-V{_max_version(setup_versions)}"

        ied_versions = [
            version
            for path in source_files
            if path.suffix.lower() in IED_MARKER_EXTENSIONS
            for version in [_gemultilin_header_version(path)]
            if version
        ]
        if ied_versions:
            return f"GE-MULTILIN-V{_max_version(ied_versions)}"

        if fallback_version:
            normalized = sanitize_filename_part(fallback_version)
            if normalized:
                if normalized.startswith("GE-"):
                    return normalized
                if normalized.startswith("V"):
                    return f"GE-URSETUP-{normalized}"
                return f"GE-URSETUP-V{normalized}"

        raise ProjectDetectionError(
            f"Nao foi possivel detectar a versao GE Multilin em: {project_file}"
        )

    def get_related_files(self, project_file: Path) -> list[Path]:
        """Return the optional `.ENV` and files from GE IED folders."""

        return _collect_ge_source_files(_environment_root(project_file))

    def get_backup_info_sections(
        self,
        project_file: Path,
        source_files: list[Path],
    ) -> list[str]:
        """Return a GE-specific IED summary for `IEDS-BACKUP-INFO.txt`."""

        root = _environment_root(project_file)
        env_files = [path for path in source_files if path.suffix.lower() == ENV_EXTENSION]
        folders: dict[Path, list[Path]] = defaultdict(list)
        for path in source_files:
            if path.suffix.lower() in INCLUDED_EXTENSIONS:
                folders[path.parent].append(path)

        lines = [
            "GE Multilin IED Summary:",
            f"- Environment folder: {root.name}",
        ]
        if env_files:
            lines.append(f"- ENV file: {env_files[0].name}")
            env_versions = _env_versions(env_files[0])
            for label, version in env_versions:
                lines.append(f"  {label}: {version}")
        else:
            lines.append("- ENV file: not found")

        lines.append("- Selection rule: direct child folders containing .urs or .urk")
        lines.append("")
        lines.append("IED folders included:")
        for folder in sorted(folders):
            folder_files = sorted(folders[folder], key=lambda path: path.name.lower())
            setup_version = _max_version(
                version
                for path in folder_files
                if path.suffix.lower() in {".cid", ".icd"}
                for version in _ur_setup_versions(path)
            )
            ied_version = _max_version(
                version
                for path in folder_files
                if path.suffix.lower() in IED_MARKER_EXTENSIONS
                for version in [_gemultilin_header_version(path)]
                if version
            )
            extensions = ", ".join(
                sorted({path.suffix.lower() for path in folder_files if path.suffix})
            )
            lines.append(f"- {folder.name}")
            lines.append(f"  Files: {extensions}")
            if setup_version:
                lines.append(f"  Developed with: GE UR Setup V{setup_version}")
            if ied_version:
                lines.append(f"  IED/application version: V{ied_version}")

        return ["\n".join(lines)]


def _collect_ge_source_files(root: Path) -> list[Path]:
    """Collect all files that are part of a GE UR environment backup."""

    ied_folders = _find_ied_folders(root)
    if not ied_folders:
        return []

    source_files = [
        path
        for path in sorted(root.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() == ENV_EXTENSION
    ]
    for folder in ied_folders:
        source_files.extend(
            path
            for path in sorted(folder.iterdir(), key=lambda item: item.name.lower())
            if path.is_file() and path.suffix.lower() in INCLUDED_EXTENSIONS
        )
    return source_files


def _find_ied_folders(root: Path) -> list[Path]:
    """Return folders that contain at least one GE UR settings file."""

    return [
        path
        for path in sorted(root.iterdir(), key=lambda item: item.name.lower())
        if path.is_dir() and _folder_has_ge_marker(path)
    ]


def _folder_has_ge_marker(folder: Path) -> bool:
    """Return true when a folder has a GE UR settings marker file."""

    return any(
        path.is_file() and path.suffix.lower() in IED_MARKER_EXTENSIONS
        for path in folder.iterdir()
    )


def _environment_root(project_file: Path) -> Path:
    """Infer the GE environment root from a representative source file."""

    if project_file.is_dir():
        return project_file
    if project_file.suffix.lower() == ENV_EXTENSION:
        return project_file.parent
    if _folder_has_ge_marker(project_file.parent):
        return project_file.parent.parent
    return project_file.parent


def _ur_setup_versions(path: Path) -> list[str]:
    """Extract all GE UR Setup versions from SCL files."""

    text = path.read_bytes()[:4096].decode("utf-8", errors="ignore")
    return UR_SETUP_VERSION_RE.findall(text)


def _gemultilin_header_version(path: Path) -> str | None:
    """Extract and normalize the version field from a GEMULTILIN header."""

    try:
        line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    except IndexError:
        return None
    parts = line.split(",")
    if len(parts) < 5 or parts[0] != "HEADER" or parts[1] != "GEMULTILIN":
        return None
    raw_version = parts[4].strip()
    if raw_version.isdigit() and len(raw_version) == 3:
        return f"{raw_version[0]}.{raw_version[1:]}"
    return raw_version or None


def _env_versions(path: Path) -> list[tuple[str, str]]:
    """Read known version fields from the optional GE environment file."""

    versions = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()[:50]:
        if "," not in line:
            continue
        label, value = [part.strip() for part in line.split(",", maxsplit=1)]
        if label in {"Environment Version", "Application Version"} and value:
            versions.append((label, value))
    return versions


def _max_version(versions) -> str | None:
    """Return the highest dotted numeric version from an iterable."""

    collected = [version for version in versions if version]
    if not collected:
        return None
    return max(collected, key=_version_key)


def _version_key(version: str) -> tuple[int, ...]:
    """Convert a dotted numeric version into a comparable tuple."""

    return tuple(int(part) for part in version.split(".") if part.isdigit())


GE_MULTILIN_PROJECT_TYPE = GeMultilinProjectType()
