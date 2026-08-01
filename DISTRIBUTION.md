# 🐾 How to Distribute Taskbar Pets (Like TranslucentTB)

## Overview

This guide explains the **two-step process** to package Taskbar Pets into a
proper Windows `.exe` installer that any user can download and run — no Python
required.

---

## Step 1 — Build the Standalone `.exe`

### Requirements (your machine only)
- Python 3.11+ installed (users don't need it)
- Internet connection (first build only)

### Just run:
```
build.bat
```

This automatically:
1. Installs PyInstaller
2. Downloads Pokemon sprites if missing
3. Generates the app icon
4. Bundles everything into `dist\TaskbarPets.exe` (~40-70 MB)

---

## Step 2 — Create the Windows Installer

For a professional installer (like TranslucentTB / Wallpaper Engine):

### a) Install Inno Setup (free)
Download from: https://jrsoftware.org/isinfo.php

### b) Open `TaskbarPets.iss` in Inno Setup and click **Compile**

This creates:
```
installer_output\TaskbarPets_Setup_v1.0.0.exe
```

The installer gives users:
- Standard Windows installation wizard
- Desktop shortcut (optional)
- Start with Windows option
- Clean uninstaller in Add/Remove Programs

---

## Distribution Options

### Option A — GitHub Releases (FREE, recommended)

1. Create a GitHub repo: `github.com/yourname/taskbar-pets`
2. Push your code
3. Go to **Releases → Create new release**
4. Upload `TaskbarPets_Setup_v1.0.0.exe` as an asset
5. Users click **"Download"** and run the installer

**Example:**
```
https://github.com/yourname/taskbar-pets/releases/latest
```

### Option B — Direct `.exe` Download (simplest)

If you just want a direct download with no installer:
- Upload `dist\TaskbarPets.exe` to GitHub releases, Google Drive, or any host
- Users download and double-click — no installation needed

### Option C — Microsoft Store (most professional)

Requires packaging as MSIX. More complex but gives:
- Store listing with ratings/reviews
- Auto-updates through Windows Update
- Trusted signature (no "Unknown Publisher" warning)

---

## What Users Experience

```
1. Download TaskbarPets_Setup.exe
2. Double-click → Windows Wizard opens
3. Click Next → Next → Install → Finish
4. App launches automatically
5. Pokemon walk on their taskbar!
```

No Python, no command prompt, no terminal — just works.

---

## File Structure After Build

```
dist\
  TaskbarPets.exe          ← Single standalone executable (~50 MB)

installer_output\
  TaskbarPets_Setup_v1.0.0.exe  ← Windows installer for distribution
```

---

## Auto-Update (Optional, Advanced)

To add update checking like TranslucentTB:
1. Host a `version.json` file on GitHub:
   ```json
   {"version": "1.0.1", "download": "https://github.com/.../releases/download/v1.0.1/TaskbarPets_Setup.exe"}
   ```
2. The app checks this URL on startup and shows an update notification

---

## Signing Your App (Removes "Unknown Publisher" Warning)

For trusted downloads without Windows SmartScreen warnings:
- **Free option**: Submit to Microsoft's App Certification (takes weeks)
- **Paid option**: Purchase a Code Signing Certificate (~$70-$200/year)
  from DigiCert, Sectigo, or GlobalSign

For a personal project, you can skip signing — users just click "Run anyway".

---

## Quick Checklist Before Release

- [ ] `build.bat` runs successfully and creates `dist\TaskbarPets.exe`
- [ ] `TaskbarPets.exe` launches and shows pets on taskbar
- [ ] Settings manager opens and saves correctly
- [ ] App closes cleanly from system tray
- [ ] Inno Setup compiles `TaskbarPets.iss` to an installer
- [ ] Installer creates desktop shortcut and starts the app
- [ ] Uninstall works from Add/Remove Programs
