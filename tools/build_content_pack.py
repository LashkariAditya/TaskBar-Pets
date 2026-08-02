"""Package asset folders into the release content zip."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.version import CONTENT_ASSET_NAME


def _iter_asset_files() -> list[Path]:
    asset_root = ROOT / "assets"
    groups = ["gen1", "gen2", "gen3", "gen4", "gen5", "naruto", "pokemon"]
    files: list[Path] = []
    for group in groups:
        group_dir = asset_root / group
        if not group_dir.is_dir():
            continue
        for path in group_dir.rglob("*"):
            if path.is_file():
                files.append(path)
    return files


def main() -> None:
    dist_dir = ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    out_path = dist_dir / CONTENT_ASSET_NAME

    files = _iter_asset_files()
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT / "assets"))

    print(f"Wrote {out_path} ({len(files)} files)")


if __name__ == "__main__":
    main()