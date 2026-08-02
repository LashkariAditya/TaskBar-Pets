"""Generate a small release manifest for GitHub Releases."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.version import APP_ASSET_NAME, APP_VERSION, CONTENT_ASSET_NAME, RELEASE_MANIFEST_ASSET


def main() -> None:
    out_dir = ROOT / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "app_version": APP_VERSION,
        "content_version": APP_VERSION,
        "app_asset": APP_ASSET_NAME,
        "content_asset": CONTENT_ASSET_NAME,
    }
    out_path = out_dir / RELEASE_MANIFEST_ASSET
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()