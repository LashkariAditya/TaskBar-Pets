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
    python download_sprites.py
    if errorlevel 1 (
        echo  Download failed. Generating pixel sprites instead...
        python generate_sprites.py
    )
)

:: ── Generate icon ──────────────────────────────────────────────────────────────
echo  [3/4] Generating app icon...
python generate_assets.py
if errorlevel 1 ( echo  [ERROR] Asset generation failed. & pause & exit /b 1 )

:: ── Build with PyInstaller ─────────────────────────────────────────────────────
echo  [4/4] Building standalone .exe with PyInstaller...
python -m PyInstaller TaskbarPets.spec --clean --noconfirm
if errorlevel 1 ( echo  [ERROR] PyInstaller build failed. & pause & exit /b 1 )

echo.
echo  ========================================
echo   BUILD COMPLETE!
echo  ========================================
echo.
echo   Your app:   dist\TaskbarPets.exe
echo   Size:       (check dist\ folder)
echo.
echo   Test it:    dist\TaskbarPets.exe
echo.
pause
