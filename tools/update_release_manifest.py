"""
Re-upload the release manifest to the existing v2.0.1 GitHub Release with updated version.
This replaces the old manifest (2.0.0) with the new one (2.0.1) so users get notified.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OWNER = "LashkariAditya"
REPO  = "TaskBar-Pets"
TAG   = "v2.0.1"

API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"

HEADERS = {
    "Accept":               "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent":           "Taskbar-Pets/release-script",
}


def _get_token() -> str:
    result = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True, timeout=5,
    )
    for line in result.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):].strip()
    return ""


def _api(method: str, path: str, body=None, token: str = "") -> dict | None:
    url = API_BASE + path
    data = json.dumps(body).encode() if body else None
    headers = dict(HEADERS)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def _upload_asset(upload_url: str, path: Path, token: str, mime: str) -> dict:
    base_url = upload_url.split("{")[0]
    url = f"{base_url}?name={path.name}"
    data = path.read_bytes()
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = mime
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def main() -> None:
    token = _get_token()
    if not token:
        print("ERROR: No token found.")
        sys.exit(1)
    print(f"Token ok (len={len(token)})")

    # Get release
    release = _api("GET", f"/releases/tags/{TAG}", token=token)
    if not release:
        print(f"ERROR: Release {TAG} not found")
        sys.exit(1)

    release_id = release["id"]
    upload_url = release["upload_url"]
    print(f"Found release id={release_id}: {release['html_url']}")

    # Delete old manifest asset if present
    for asset in release.get("assets", []):
        if asset["name"] == "taskbarpets-release-manifest.json":
            print(f"  Deleting old manifest asset (id={asset['id']})...")
            _api("DELETE", f"/releases/assets/{asset['id']}", token=token)
            print("  Deleted.")
            break

    # Upload new manifest
    manifest_path = ROOT / "dist" / "taskbarpets-release-manifest.json"
    print(f"  Uploading {manifest_path.name}...")
    result = _upload_asset(upload_url, manifest_path, token, "application/json")
    print(f"  OK: {result.get('browser_download_url')}")

    print("\nDone! Release manifest updated to v2.0.1")
    print("Users clicking 'Check for Updates' will now receive a notification and content download.")


if __name__ == "__main__":
    main()
