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
python -c "
from PIL import Image, ImageDraw
import os

os.makedirs('assets', exist_ok=True)

# Create 256x256 icon with paw print
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Background circle
d.ellipse([10, 10, 246, 246], fill='#1e1e2e')

# Paw pads
d.ellipse([78, 140, 178, 220], fill='#fab387')   # main pad
d.ellipse([58, 100, 108, 140],  fill='#fab387')  # toe 1
d.ellipse([108, 80, 148, 120],  fill='#fab387')  # toe 2
d.ellipse([148, 80, 188, 120],  fill='#fab387')  # toe 3
d.ellipse([188, 100, 228, 140], fill='#fab387')  # toe 4 (adjusted)

img.save('assets/icon.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(32,32),(16,16)])
print('  Icon created: assets/icon.ico')
"

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
