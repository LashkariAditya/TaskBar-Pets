"""Resolve the correct assets/config path whether running from source or as a PyInstaller .exe."""

from __future__ import annotations

import sys
from pathlib import Path


def get_app_dir() -> Path:
    """Return the root directory of the app (works both in source and bundled .exe)."""
    if getattr(sys, "frozen", False):
        # Running inside PyInstaller bundle
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # Running from source
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Return the writable data directory (config.json, etc.).

    For installed .exe: %APPDATA%\\TaskbarPets
    For source:         project root
    """
    if getattr(sys, "frozen", False):
        import os
        data = Path(os.environ.get("APPDATA", Path.home())) / "TaskbarPets"
        data.mkdir(parents=True, exist_ok=True)
        return data
    return Path(__file__).resolve().parent.parent
