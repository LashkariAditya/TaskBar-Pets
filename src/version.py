"""App and release version metadata."""

from __future__ import annotations

APP_NAME = "Taskbar Pets"
APP_VERSION = "2.0.0"
APP_VERSION_WIN = "2,0,0,0"
REPOSITORY_OWNER = "LashkariAditya"
REPOSITORY_NAME = "TaskBar-Pets"
GITHUB_RELEASES_API = (
    f"https://api.github.com/repos/{REPOSITORY_OWNER}/{REPOSITORY_NAME}/releases/latest"
)
CONTENT_ASSET_NAME = "TaskbarPets-content.zip"
APP_ASSET_NAME = "TaskbarPets.exe"
RELEASE_MANIFEST_ASSET = "taskbarpets-release-manifest.json"