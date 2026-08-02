# 🐾 Taskbar Pets

<div align="center">

**Animated Pokémon companions that walk, idle, and play on your Windows Taskbar!**

[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows)](https://github.com/LashkariAditya/TaskBar-Pets)
[![Python](https://img.shields.io/badge/Python-3.10+-green?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Pokémon](https://img.shields.io/badge/Pok%C3%A9mon-Gen%201--5-red)](https://github.com/LashkariAditya/TaskBar-Pets)

</div>

---

<div align="center">

## ⚡ Quick Download

### 🚀 [**Click to Download TaskbarPets.exe**](https://github.com/LashkariAditya/TaskBar-Pets/raw/main/TaskbarPets.exe)

**No Python or installation required!** Simply download `TaskbarPets.exe` and double-click to run.

</div>

---

<div align="center">
  <img src="https://raw.githubusercontent.com/LashkariAditya/TaskBar-Pets/main/assets/preview.gif" alt="Taskbar Pets Preview" width="700"/>
</div>

---

## ⬇️ Download & Run Options

### Option 1 — Direct Executable Download (Recommended)

1. Download [**`TaskbarPets.exe`**](https://github.com/LashkariAditya/TaskBar-Pets/raw/main/TaskbarPets.exe) directly from this repository (or from [**Releases**](https://github.com/LashkariAditya/TaskBar-Pets/releases/latest))
2. Double-click **`TaskbarPets.exe`** to start — pets will appear on your taskbar!

> **Note:** On first launch, Windows SmartScreen might prompt *"Unknown Publisher"*. Click **"More info" → "Run anyway"**.

### Option 2 — Run from Source

```bash
# Clone the repo
git clone https://github.com/LashkariAditya/TaskBar-Pets.git
cd TaskBar-Pets

# Install dependencies
pip install -r requirements.txt

# Launch!
python main.py
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🐾 **634 Pokémon** | All Gen 1–5 Pokémon with authentic animated sprites |
| 🚶 **Walk & Idle** | Pets walk left/right, pause, and show front-facing idle model at turns |
| 🎮 **Interactive Mode** | Click to pet, double-click to feed, right-click for context menu |
| 💬 **Speech Bubbles** | Species-specific dialogue — *"Pika Pika!"*, *"Char!"*, *"Zzz..."* |
| ✨ **Particle Effects** | Hearts when petted, Zzz bubbles while sleeping |
| 📌 **Pin Anywhere** | Drag & pin pets at any screen position |
| 🔽 **Auto-hide Support** | Pets fall when taskbar hides, rise when it appears |
| 🧊 **Freeze Mode** | Keep pets stationary above clock |
| 🚀 **Startup Launch** | Option to start silently with Windows |
| 🔍 **Search & Filter** | Find any Pokémon instantly by name or generation |
| 🔢 **Max 5 Pets** | Choose up to 5 companions from the manager |

## 🔄 Updates

Taskbar Pets checks GitHub Releases in the background.

- New pet content is downloaded automatically when a release includes the content pack asset.
- App updates are staged automatically on Windows and the app relaunches after the current process exits.
- If the app cannot replace itself, it still notifies you in the tray so you can update from the release page.
- Use **System Tray → Check for Updates** to force a manual check.

## 🧩 Custom Asset Packs

The repository now supports a special asset group under `assets/naruto/`.

- Put a pet folder such as `assets/naruto/9tail/` in that path.
- Add `walk.gif` / `idle.gif` or matching PNG frame sequences inside the folder.
- The app will discover the pet automatically, and the release builder will include it in `TaskbarPets-content.zip`.

---

## 🖥️ System Requirements

- **OS**: Windows 10 or Windows 11
- **CPU**: Any modern processor
- **RAM**: ~50 MB
- **Python**: 3.10+ *(only if running from source)*

---

## 🎮 How to Use

### System Tray
Right-click the **Pokéball icon** in the system tray for quick controls:
- **Manage Pets & Settings** — Open the full manager
- **Check for Updates** — Force a background update check now
- **Interactive Mode** — Toggle click-through / interactive
- **Feed All Pets / Sleep All** — Quick actions
- **Add Random Pokémon** — Surprise pet!
- **Quit**

### Pet Manager
Open from the tray → **"Manage Pets & Settings"**:
- Search any of the 634 Pokémon by name
- Filter by **Gen 1 / Gen 2 / Gen 3 / Gen 4 / Gen 5**
- Select up to **5 pets** for your active roster
- Adjust size, speed, and behavior in the **Settings** tab
- Use **Check for Updates** in the manager to trigger an immediate update check

### Interactive Mode Controls
| Action | Result |
|---|---|
| Left Click | Pet & show hearts ♥️ |
| Double Click | Feed a berry 🍇 |
| Right Click | Open pet menu |
| Drag | Move pet anywhere on screen |
| Right-click → Pin | Lock pet position |

---

## 📁 Project Structure

```
TaskBar-Pets/
├── TaskbarPets.exe        # 🚀 Standalone Windows executable (download & run directly!)
├── main.py                # Entry point (run from source)
├── config.py              # Settings & roster configuration
├── build.bat              # One-click build script
├── TaskbarPets.spec       # PyInstaller configuration
├── TaskbarPets.iss        # Inno Setup installer script
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── .gitignore             # Git ignore file
├── assets/                # App icons & 634 animated Pokémon sprites
├── src/                   # Core application source code
└── tools/                 # Helper & asset generation scripts
```

---

## 🔧 Build from Source (Create your own exe)

```bash
pip install pyinstaller pillow pystray
python -m PyInstaller TaskbarPets.spec --noconfirm
# Output: dist/TaskbarPets.exe
# Output: dist/TaskbarPets-content.zip
# Output: dist/taskbarpets-release-manifest.json
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

- Pokémon sprites sourced from community sprite archives
- Inspired by [vscode-pets](https://github.com/tonybaloney/vscode-pets) by [@tonybaloney](https://github.com/tonybaloney)
- Built with Python, Tkinter, Pillow, and pystray

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/LashkariAditya">LashkariAditya</a>
</div>
