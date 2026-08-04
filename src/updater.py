"""Background update checks for Taskbar Pets."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import subprocess
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.paths import get_assets_dir, get_data_dir
from src.version import (
    APP_ASSET_NAME,
    APP_NAME,
    APP_VERSION,
    CONTENT_ASSET_NAME,
    GITHUB_RELEASES_API,
    RELEASE_MANIFEST_ASSET,
)


def _parse_version(value: str) -> tuple[int, ...]:
    cleaned = value.strip().lower().removeprefix("v")
    parts: list[int] = []
    for chunk in cleaned.split("."):
        if not chunk:
            continue
        digits = ""
        for char in chunk:
            if char.isdigit():
                digits += char
            else:
                break
        if digits:
            parts.append(int(digits))
    return tuple(parts or [0])


def _version_is_newer(candidate: str, current: str) -> bool:
    left = _parse_version(candidate)
    right = _parse_version(current)
    width = max(len(left), len(right))
    return left + (0,) * (width - len(left)) > right + (0,) * (width - len(right))


@dataclass(frozen=True)
class ReleaseAsset:
    name: str
    download_url: str
    size: int


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    html_url: str
    assets: tuple[ReleaseAsset, ...]

    def asset_by_name(self, name: str) -> ReleaseAsset | None:
        for asset in self.assets:
            if asset.name.lower() == name.lower():
                return asset
        return None


@dataclass(frozen=True)
class UpdateStatus:
    latest_release: ReleaseInfo | None
    app_update_available: bool
    content_update_available: bool
    message: str | None = None


@dataclass(frozen=True)
class ReleaseManifest:
    app_version: str
    content_version: str
    app_asset: str
    content_asset: str


def _request_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Taskbar-Pets/2.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def _request_json(url: str) -> dict[str, Any]:
    return json.loads(_request_text(url))


def fetch_latest_release() -> ReleaseInfo | None:
    try:
        data = _request_json(GITHUB_RELEASES_API)
    except Exception:
        return None

    tag = str(data.get("tag_name", "")).strip() or APP_VERSION
    html_url = str(data.get("html_url", "")).strip()
    assets = []
    for item in data.get("assets", []):
        name = str(item.get("name", "")).strip()
        download_url = str(item.get("browser_download_url", "")).strip()
        if name and download_url:
            assets.append(ReleaseAsset(name=name, download_url=download_url, size=int(item.get("size", 0) or 0)))
    return ReleaseInfo(version=tag, html_url=html_url, assets=tuple(assets))


def fetch_release_manifest(release: ReleaseInfo) -> ReleaseManifest | None:
    asset = release.asset_by_name(RELEASE_MANIFEST_ASSET)
    if asset is None:
        return None
    try:
        payload = _request_text(asset.download_url)
        data = json.loads(payload)
        return ReleaseManifest(
            app_version=str(data.get("app_version", APP_VERSION)).strip() or APP_VERSION,
            content_version=str(data.get("content_version", APP_VERSION)).strip() or APP_VERSION,
            app_asset=str(data.get("app_asset", APP_ASSET_NAME)).strip() or APP_ASSET_NAME,
            content_asset=str(data.get("content_asset", CONTENT_ASSET_NAME)).strip() or CONTENT_ASSET_NAME,
        )
    except Exception:
        return None


def check_for_updates() -> UpdateStatus:
    release = fetch_latest_release()
    if release is None:
        return UpdateStatus(None, False, False, "Unable to reach GitHub releases.")

    manifest = fetch_release_manifest(release)
    app_version = manifest.app_version if manifest else release.version
    content_version = manifest.content_version if manifest else release.version
    content_asset_name = manifest.content_asset if manifest else CONTENT_ASSET_NAME
    app_asset_name = manifest.app_asset if manifest else APP_ASSET_NAME

    app_update = _version_is_newer(app_version, APP_VERSION)
    content_version_file = get_data_dir() / "updates" / "content_version.txt"
    try:
        local_content_version = content_version_file.read_text(encoding="utf-8").strip() or "0"
    except Exception:
        local_content_version = "0"

    content_update = False
    if release.asset_by_name(content_asset_name) is not None:
        content_update = _version_is_newer(content_version, local_content_version)
    return UpdateStatus(release, app_update, content_update)


def _safe_extract_zip(zip_file: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file) as archive:
        for member in archive.infolist():
            destination = (target_dir / member.filename).resolve()
            if target_dir.resolve() not in destination.parents and destination != target_dir.resolve():
                raise ValueError(f"Unsafe path in archive: {member.filename}")
        archive.extractall(target_dir)


def download_content_pack(release: ReleaseInfo) -> Path | None:
    manifest = fetch_release_manifest(release)
    asset_name = manifest.content_asset if manifest else CONTENT_ASSET_NAME
    asset = release.asset_by_name(asset_name)
    if asset is None:
        return None

    assets_dir = get_assets_dir()
    updates_dir = get_data_dir() / "updates"
    updates_dir.mkdir(parents=True, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(suffix=".zip", prefix="taskbarpets-content-")
    os.close(fd)
    temp_file = Path(temp_path)
    try:
        request = urllib.request.Request(asset.download_url, headers={"User-Agent": "Taskbar-Pets/2.0"})
        with urllib.request.urlopen(request, timeout=60) as response, open(temp_file, "wb") as handle:
            shutil.copyfileobj(response, handle)
        _safe_extract_zip(temp_file, assets_dir)
        content_version = manifest.content_version if manifest else release.version
        (updates_dir / "content_version.txt").write_text(content_version, encoding="utf-8")
        return assets_dir
    except urllib.error.URLError:
        return None
    except Exception:
        return None
    finally:
        try:
            temp_file.unlink(missing_ok=True)
        except Exception:
            pass


def download_app_update(release: ReleaseInfo) -> Path | None:
    manifest = fetch_release_manifest(release)
    asset_name = manifest.app_asset if manifest else APP_ASSET_NAME
    asset = release.asset_by_name(asset_name)
    if asset is None:
        for candidate in release.assets:
            if candidate.name.lower().endswith(".exe"):
                asset = candidate
                break
    if asset is None:
        return None

    updates_dir = get_data_dir() / "updates"
    updates_dir.mkdir(parents=True, exist_ok=True)
    staged_path = updates_dir / APP_ASSET_NAME

    fd, temp_path = tempfile.mkstemp(suffix=".exe", prefix="taskbarpets-update-")
    os.close(fd)
    temp_file = Path(temp_path)
    try:
        request = urllib.request.Request(asset.download_url, headers={"User-Agent": "Taskbar-Pets/2.0"})
        with urllib.request.urlopen(request, timeout=120) as response, open(temp_file, "wb") as handle:
            shutil.copyfileobj(response, handle)
        staged_path.unlink(missing_ok=True)
        shutil.move(str(temp_file), staged_path)
        app_version = manifest.app_version if manifest else release.version
        (updates_dir / "app_version.txt").write_text(app_version, encoding="utf-8")
        return staged_path
    except Exception as exc:
        print(f"Error downloading app update: {exc}")
        return None
    finally:
        try:
            temp_file.unlink(missing_ok=True)
        except Exception:
            pass


def get_pinned_executable_path() -> Path | None:
    import sys

    if not getattr(sys, "frozen", False):
        return None
    return Path(sys.executable)


def schedule_executable_update(staged_exe: Path, target_exe: Path, relaunch: bool = True) -> bool:
    if not staged_exe.is_file() or not target_exe:
        return False

    helper = get_data_dir() / "updates" / "apply_update.ps1"
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text(
        rf"""
param(
    [string]$SourceExe,
    [string]$TargetExe,
    [string]$CurrentPid,
    [string]$LaunchExe
)

$ErrorActionPreference = 'SilentlyContinue'

$attempts = 0
while ((Get-Process -Id [int]$CurrentPid -ErrorAction SilentlyContinue) -and ($attempts -lt 25)) {{
    Start-Sleep -Milliseconds 400
    $attempts++
}}

$copied = $false
for ($i = 0; $i -lt 10; $i++) {{
    try {{
        Copy-Item -LiteralPath $SourceExe -Destination $TargetExe -Force -ErrorAction Stop
        $copied = $true
        break
    }} catch {{
        Start-Sleep -Milliseconds 500
    }}
}}

if ($LaunchExe -and (Test-Path -LiteralPath $LaunchExe)) {{
    Start-Process -FilePath $LaunchExe
}}
""".strip(),
        encoding="utf-8",
    )
    current_pid = str(os.getpid())
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-WindowStyle",
        "Hidden",
        "-File",
        str(helper),
        "-SourceExe",
        str(staged_exe),
        "-TargetExe",
        str(target_exe),
        "-CurrentPid",
        current_pid,
        "-LaunchExe",
        str(target_exe) if relaunch else "",
    ]
    try:
        subprocess.Popen(command, creationflags=0x08000000)
        return True
    except Exception as exc:
        print(f"Failed to launch update script: {exc}")
        return False


def notify_update(icon: Any | None, title: str, message: str) -> None:
    try:
        if icon is not None and hasattr(icon, "notify"):
            icon.notify(title, message)
            return
    except Exception:
        pass
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
        return
    except Exception:
        pass
    print(f"{APP_NAME}: {title} - {message}")