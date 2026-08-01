# -*- mode: python ; coding: utf-8 -*-
# TaskbarPets.spec  —  PyInstaller build specification
# Run with:  pyinstaller TaskbarPets.spec

import os
from pathlib import Path

ROOT = Path(SPEC).parent  # directory containing this .spec file

# ── Collect all pokemon sprite folders ────────────────────────────────────────
pokemon_datas = []
assets_dir = ROOT / "assets"
for gen in ["gen1", "gen2", "gen3", "gen4", "gen5", "pokemon"]:
    gen_dir = assets_dir / gen
    if gen_dir.exists():
        for pokemon_folder in gen_dir.iterdir():
            if pokemon_folder.is_dir():
                gifs = list(pokemon_folder.glob("*.gif")) + list(pokemon_folder.glob("*.png"))
                for gif in gifs:
                    dest = f"assets/{gen}/{pokemon_folder.name}"
                    pokemon_datas.append((str(gif), dest))

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=pokemon_datas,
    hiddenimports=[
        "PIL._tkinter_finder",
        "pystray._win32",
        "tkinter",
        "tkinter.ttk",
        "ctypes.wintypes",
        "src.app",
        "src.overlay",
        "src.pet",
        "src.taskbar",
        "src.sprites",
        "src.manager_gui",
        "src.autostart",
        "src.paths",
        "src.win32_helpers",
        "config",
        "download_sprites",
        "generate_sprites",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "scipy", "pandas", "pytest"],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TaskbarPets",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No command prompt window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "assets" / "icon.ico") if (ROOT / "assets" / "icon.ico").exists() else None,
    version=str(ROOT / "assets" / "file_version_info.txt") if (ROOT / "assets" / "file_version_info.txt").exists() else None,
)
