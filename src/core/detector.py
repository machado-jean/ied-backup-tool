from __future__ import annotations

from pathlib import Path


class Dz5DetectionError(RuntimeError):
    pass


def find_project_file(project_dir: Path) -> Path:
    if not project_dir.exists() or not project_dir.is_dir():
        raise Dz5DetectionError(f"Pasta do projeto invalida: {project_dir}")

    matches = sorted(
        _iter_dz5_files(project_dir),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not matches:
        raise Dz5DetectionError(f"Nenhum arquivo .dz5 encontrado em: {project_dir}")

    return matches[0]


def find_project_files(project_dir: Path) -> list[Path]:
    if not project_dir.exists() or not project_dir.is_dir():
        raise Dz5DetectionError(f"Pasta do projeto invalida: {project_dir}")

    matches = list(_iter_dz5_files(project_dir))

    if not matches:
        raise Dz5DetectionError(f"Nenhum arquivo .dz5 encontrado em: {project_dir}")

    return sorted(matches, key=lambda path: (path.stat().st_mtime, path.name))


def _iter_dz5_files(project_dir: Path):
    return (
        path for path in project_dir.iterdir() if path.is_file() and path.suffix.lower() == ".dz5"
    )
