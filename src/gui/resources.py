"""Resource path helpers for development and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """Return a resource path from source checkout or PyInstaller extraction dir."""

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parents[2] / relative_path


def app_icon_path() -> Path:
    """Return the PNG icon used by the window header and taskbar icon."""

    return resource_path("assets/app_icon.png")


def language_flag_path(language: str) -> Path:
    """Return the flag icon for the target language."""

    filename = "flag_us.svg" if language == "pt_BR" else "flag_br.svg"
    return resource_path(f"assets/{filename}")
