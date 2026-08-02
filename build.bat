@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: build.bat  —  One-click build script for TaskbarPets
:: Creates a standalone TaskbarPets.exe in the dist\ folder
:: ─────────────────────────────────────────────────────────────────────────────

title TaskbarPets Builder
cd /d "%~dp0"

echo.
echo  ========================================
echo   Taskbar Pets  ^|  Build Script
echo  ========================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.11+ from python.org
    pause & exit /b 1
)

:: ── Install / upgrade build tools ─────────────────────────────────────────────
echo  [1/4] Installing build dependencies...
pip install --quiet --upgrade pyinstaller pillow pystray
if errorlevel 1 ( echo  [ERROR] pip install failed. & pause & exit /b 1 )

:: ── Download sprites if missing ────────────────────────────────────────────────
echo  [2/4] Checking Pokemon sprite assets...
python -c "from src.sprites import has_animated_assets; exit(0 if has_animated_assets() else 1)" 2>nul
if errorlevel 1 (
    echo  Downloading animated sprites...
    python tools\download_sprites.py
    if errorlevel 1 (
        echo  Download failed. Generating pixel sprites instead...
        python tools\generate_sprites.py
    )
)

:: ── Generate icon ──────────────────────────────────────────────────────────────
echo  [3/4] Generating app icon...
python tools\generate_assets.py
if errorlevel 1 ( echo  [ERROR] Asset generation failed. & pause & exit /b 1 )

:: ── Build with PyInstaller ─────────────────────────────────────────────────────
echo  [4/4] Building standalone .exe with PyInstaller...
python -m PyInstaller TaskbarPets.spec --clean --noconfirm
if errorlevel 1 ( echo  [ERROR] PyInstaller build failed. & pause & exit /b 1 )

:: ── Build content pack for release ───────────────────────────────────────────
echo  [5/5] Building content pack...
python tools\build_content_pack.py
if errorlevel 1 ( echo  [ERROR] Content pack build failed. & pause & exit /b 1 )

:: ── Generate release manifest ────────────────────────────────────────────────
echo  [6/6] Generating release manifest...
python tools\generate_release_manifest.py
if errorlevel 1 ( echo  [ERROR] Release manifest generation failed. & pause & exit /b 1 )

:: Copy output to root directory for easy GitHub access
copy /y dist\TaskbarPets.exe TaskbarPets.exe >nul

echo.
echo  ========================================
echo   BUILD COMPLETE!
echo  ========================================
echo.
echo   Your app:   TaskbarPets.exe
echo   Location:   Root directory & dist\TaskbarPets.exe
echo   Content:    dist\TaskbarPets-content.zip
echo   Manifest:   dist\taskbarpets-release-manifest.json
echo.
echo   Test it:    TaskbarPets.exe
echo.
pause
