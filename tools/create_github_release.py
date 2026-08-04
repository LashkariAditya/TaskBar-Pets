"""
Create a GitHub Release v2.1.0 with content pack and manifest assets.
Uses the Windows Credential Manager token already stored from git pushes.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OWNER = "LashkariAditya"
REPO  = "TaskBar-Pets"
TAG   = "v2.1.0"
RELEASE_NAME = "v2.1.0 — 22 New Custom Pets (Mod Pack)"
RELEASE_BODY = (
    "## 🐾 New Pets: Mod / Custom Pack (22 Animals)\n\n"
    "This content release adds **22 brand-new animated pets** under the **Mod / Custom Pets** category:\n\n"
    "🐔 Chicken · 📎 Clippy · 🦜 Cockatiel · 🦀 Crab · 🦕 Deno · 🐶 Dog · 🦊 Fox · 🐴 Horse\n"
    "🧬 Mod · 🐒 Monkey · 🔮 Morph · 🐼 Panda · 🦝 Raccoon · 🐀 Rat · 🪨 Rocky · 🦆 Rubber-Duck\n"
    "💀 Skeleton · 🐌 Snail · 🐍 Snake · 🐻 Totoro · 🐢 Turtle · ⚡ Zappy\n\n"
    "### Changes\n"
    "- ✅ Added 22 new animated custom pets\n"
    "- ❌ Removed: 9tail (Nine-Tailed Fox / Kurama)\n\n"
    "### How to get the new pets\n"
    "Open the app → **System Tray → Check for Updates** and all new pets will be "
    "downloaded automatically. Then open **Manage Pets** and browse **Mod / Custom Pets**.\n\n"
    "---\n"
    "_Content-only release — no app binary change._"
)

API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"
ASSETS = [
    ROOT / "dist" / "TaskbarPets-content.zip",
    ROOT / "dist" / "taskbarpets-release-manifest.json",
]

HEADERS = {
    "Accept":               "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent":           "Taskbar-Pets/release-script",
}


def _get_token_from_credential_manager() -> str | None:
    """Try to retrieve the GitHub PAT from Windows Credential Manager."""
    try:
        # Use cmdkey / PowerShell to extract credential
        # Try GCM token lookup via git credential fill
        import subprocess
        result = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.splitlines():
            if line.startswith("password="):
                return line[len("password="):]
    except Exception:
        pass
    return None


def _api(method: str, path: str, body: dict | None = None, token: str = "") -> dict:
    url = API_BASE + path
    data = json.dumps(body).encode() if body else None
    headers = dict(HEADERS)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _upload_asset(upload_url: str, path: Path, token: str) -> dict:
    """Upload a release asset. upload_url has {?name,label} template."""
    base_url = upload_url.split("{")[0]
    url = f"{base_url}?name={path.name}"
    mime = "application/zip" if path.suffix == ".zip" else "application/json"
    data = path.read_bytes()
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = mime
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    token = _get_token_from_credential_manager()
    if not token:
        print("ERROR: Could not retrieve GitHub token from credential manager.")
        print("Please set the GITHUB_TOKEN environment variable and re-run.")
        sys.exit(1)

    token = token.strip()
    print(f"Token retrieved (len={len(token)})")

    # Check if tag already exists - delete release if it does
    try:
        existing = _api("GET", f"/releases/tags/{TAG}", token=token)
        print(f"Release {TAG} already exists (id={existing['id']}), deleting...")
        _api("DELETE", f"/releases/{existing['id']}", token=token)
        print("  Deleted existing release.")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    # Try deleting the tag ref too (if it exists)
    try:
        _api("DELETE", f"/git/refs/tags/{TAG}", token=token)
        print(f"Deleted existing tag ref {TAG}.")
    except urllib.error.HTTPError:
        pass

    # Create the release
    print(f"Creating release {TAG}...")
    release = _api("POST", "/releases", body={
        "tag_name":         TAG,
        "target_commitish": "main",
        "name":             RELEASE_NAME,
        "body":             RELEASE_BODY,
        "draft":            False,
        "prerelease":       False,
    }, token=token)

    release_id  = release["id"]
    upload_url  = release["upload_url"]
    release_url = release["html_url"]
    print(f"  Created release: {release_url}")

    # Upload assets
    for asset_path in ASSETS:
        if not asset_path.exists():
            print(f"  SKIP (not found): {asset_path}")
            continue
        size_kb = asset_path.stat().st_size // 1024
        print(f"  Uploading {asset_path.name} ({size_kb} KB)...")
        result = _upload_asset(upload_url, asset_path, token)
        print(f"    OK: {result.get('browser_download_url', '?')}")

    print(f"\n✅ Release {TAG} published successfully!")
    print(f"   {release_url}")
    print("\nUsers will now be notified automatically when they click 'Check for Updates'.")


if __name__ == "__main__":
    main()
