"""Windows startup integration helper for Taskbar Pets."""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

STARTUP_DIR = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
SHORTCUT_PATH = STARTUP_DIR / "TaskbarPets.lnk"
PROJECT_DIR = Path(__file__).resolve().parent.parent
MAIN_PY = PROJECT_DIR / "main.py"


def is_autostart_enabled() -> bool:
    return SHORTCUT_PATH.is_file()


def set_autostart(enable: bool) -> bool:
    """Create or remove Windows Startup shortcut to run Taskbar Pets silently on boot."""
    try:
        if enable:
            if getattr(sys, "frozen", False):
                # When compiled with PyInstaller, use TaskbarPets.exe directly
                target_exe = sys.executable
                arguments = ""
                work_dir = Path(sys.executable).parent
            else:
                pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(pythonw):
                    pythonw = sys.executable
                target_exe = pythonw
                arguments = f'"{MAIN_PY}"'
                work_dir = PROJECT_DIR

            # Create shortcut via PowerShell WScript.Shell
            ps_script = (
                f"$WshShell = New-Object -ComObject WScript.Shell; "
                f"$Shortcut = $WshShell.CreateShortcut('{SHORTCUT_PATH}'); "
                f"$Shortcut.TargetPath = '{target_exe}'; "
                f"$Shortcut.Arguments = '{arguments}'; "
                f"$Shortcut.WorkingDirectory = '{work_dir}'; "
                f"$Shortcut.WindowStyle = 7; "
                f"$Shortcut.Description = 'Taskbar Pets Desktop Companions'; "
                f"$Shortcut.Save()"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                check=True,
                creationflags=0x08000000,
            )
            return True
        else:
            if SHORTCUT_PATH.is_file():
                SHORTCUT_PATH.unlink()
            return True
    except Exception as exc:
        print(f"Failed to update autostart: {exc}")
        return False
