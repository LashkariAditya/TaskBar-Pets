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
  <img src="https://raw.githubusercontent.com/LashkariAditya/TaskBar-Pets/main/assets/preview.gif" alt="Taskbar Pets Preview" width="700"/>
</div>

---

## ⬇️ Download & Install

### Option 1 — Standalone Exe (Recommended, No Python needed)

1. Go to [**Releases**](https://github.com/LashkariAditya/TaskBar-Pets/releases/latest)
2. Download **`TaskbarPets.exe`**
3. Double-click to run — no installation needed!

> **Note:** Windows SmartScreen may show a warning on first run. Click **"More info" → "Run anyway"** — this is normal for unsigned apps.

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
├── main.py                # Entry point
├── config.py              # Settings manager
├── requirements.txt       # Python dependencies
├── assets/
│   ├── gen1/              # 153 Gen 1 Pokémon sprites
│   ├── gen2/              # 132 Gen 2 Pokémon sprites
│   ├── gen3/              # 138 Gen 3 Pokémon sprites
│   ├── gen4/              # 142 Gen 4 Pokémon sprites
│   └── gen5/              # 69  Gen 5 Pokémon sprites
└── src/
    ├── app.py             # Core app & system tray
    ├── manager_gui.py     # Pet Manager GUI
    ├── overlay.py         # Transparent taskbar overlay
    ├── pet.py             # Pet state machine & particles
    ├── sprites.py         # Sprite loading & animation
    ├── taskbar.py         # Taskbar position detection
    └── autostart.py       # Windows startup integration
```

---

## 🔧 Build from Source (Create your own exe)

```bash
pip install pyinstaller pillow pystray
python -m PyInstaller TaskbarPets.spec --noconfirm
# Output: dist/TaskbarPets.exe
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
