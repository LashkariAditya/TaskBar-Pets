"""Main application controller for Taskbar Pets with System Tray and GUI Manager."""

from __future__ import annotations

import ctypes
import random
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---- MUST be set before any window or DPI-sensitive call ----
try:
    # Per-monitor v2 DPI awareness: all Win32 coords = physical pixels
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
# ------------------------------------------------------------

from PIL import Image, ImageDraw

from config import AppConfig
from src.manager_gui import PetManagerWindow
from src.overlay import OverlayWindow
from src.pet import Pet
from src.sprites import (
    discover_pokemon,
    has_animated_assets,
    load_sprite_set,
)
from src.taskbar import get_taskbar_info


def _ensure_assets() -> None:
    if has_animated_assets():
        return
    if discover_pokemon():
        return
    print("Downloading animated Pokemon sprites...")
    try:
        from download_sprites import main as download

        download()
    except Exception as exc:
        print(f"Download failed ({exc}), using built-in pixel sprites...")
        from generate_sprites import main as generate

        generate()


def _create_pets_from_config(config: AppConfig) -> list[Pet]:
    available = discover_pokemon()
    if not available:
        raise RuntimeError("No pet sprites found. Run: python download_sprites.py")

    target_names = [n for n in config.active_pets if n in available]
    if not target_names:
        target_names = [available[0]]

    taskbar = get_taskbar_info()
    walk_length = taskbar.walk_axis_length()

    loaded: list[tuple[str, any]] = []
    for name in target_names:
        sprites = load_sprite_set(name, scale=config.pet_scale)
        if sprites:
            loaded.append((name, sprites))

    pets: list[Pet] = []
    gap = walk_length / (len(loaded) + 1) if loaded else 0
    for i, (name, sprites) in enumerate(loaded):
        start_x = max(0.0, min(gap * (i + 1), walk_length - sprites.width))
        direction = -1 if i % 2 == 0 else 1
        pets.append(Pet(name=name, sprites=sprites, x=start_x, direction=direction))

    return pets


def _make_tray_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Pokéball style tray icon
    draw.ellipse([4, 4, size - 4, size - 4], fill=(235, 60, 60, 255))
    draw.chord([4, 4, size - 4, size - 4], 0, 180, fill=(245, 245, 245, 255))
    draw.line([4, size // 2, size - 4, size // 2], fill=(30, 30, 30, 255), width=6)
    draw.ellipse([22, 22, 42, 42], fill=(30, 30, 30, 255))
    draw.ellipse([26, 26, 38, 38], fill=(255, 255, 255, 255))
    return img


class TaskbarPetsApp:
    def __init__(self):
        _ensure_assets()
        self.config = AppConfig.load()
        self.pets = _create_pets_from_config(self.config)
        self.overlay: OverlayWindow | None = None
        self.manager_gui: PetManagerWindow | None = None
        self._tray = None
        self._tray_thread: threading.Thread | None = None

    def _start_overlay(self) -> None:
        if self.overlay is not None:
            return
        self.overlay = OverlayWindow(
            self.pets,
            self.config,
            on_close=self._on_overlay_closed,
            on_pet_dismiss=self._on_pet_dismissed,
        )
        self.overlay.run()

    def _on_overlay_closed(self) -> None:
        self.overlay = None
        if self._tray:
            self._tray.stop()

    def _on_pet_dismissed(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)
            if pet.name in self.config.active_pets:
                self.config.active_pets.remove(pet.name)
                self.config.save()
            if self.overlay:
                self.overlay.update_pets(self.pets)

    def _open_manager_gui(self) -> None:
        if self.overlay and self.overlay.root.winfo_exists():

            def _show():
                if self.manager_gui is None or not self.manager_gui.root.winfo_exists():
                    self.manager_gui = PetManagerWindow(
                        self.config, on_save_callback=self._on_config_updated
                    )

            self.overlay.root.after(0, _show)

    def _on_config_updated(self, new_config: AppConfig) -> None:
        self.config = new_config
        self.pets = _create_pets_from_config(self.config)
        if self.overlay:
            self.overlay.update_pets(self.pets)
            self.overlay.update_interactivity(self.config.interactive_mode)

    def _toggle_interactivity(self, _icon=None, _item=None) -> None:
        self.config.interactive_mode = not self.config.interactive_mode
        self.config.save()
        if self.overlay:
            self.overlay.root.after(
                0, lambda: self.overlay.update_interactivity(self.config.interactive_mode)
            )

    def _feed_all(self, _icon=None, _item=None) -> None:
        for pet in self.pets:
            pet.feed()

    def _sleep_toggle_all(self, _icon=None, _item=None) -> None:
        for pet in self.pets:
            pet.toggle_sleep()

    def _add_random_pet(self, _icon=None, _item=None) -> None:
        available = discover_pokemon()
        if not available:
            return
        choice = random.choice(available)
        if choice not in self.config.active_pets:
            self.config.active_pets.append(choice)
            self.config.save()
            self.pets = _create_pets_from_config(self.config)
            if self.overlay:
                self.overlay.root.after(0, lambda: self.overlay.update_pets(self.pets))

    def _quit(self, _icon=None, _item=None) -> None:
        if self.overlay and self.overlay.root.winfo_exists():
            self.overlay.root.after(0, self.overlay.root.destroy)
        if self._tray:
            self._tray.stop()

    def _run_tray(self) -> None:
        import pystray

        menu = pystray.Menu(
            pystray.MenuItem("🐾 Taskbar Pets", lambda _icon, _item: self._open_manager_gui(), default=True),
            pystray.MenuItem("⚙️ Manage Pets & Settings...", lambda _icon, _item: self._open_manager_gui()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🖱️ Interactive Mode",
                self._toggle_interactivity,
                checked=lambda _item: self.config.interactive_mode,
            ),
            pystray.MenuItem("🍇 Feed All Pets", self._feed_all),
            pystray.MenuItem("💤 Sleep / Wake All", self._sleep_toggle_all),
            pystray.MenuItem("➕ Add Random Pokemon", self._add_random_pet),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Quit", self._quit),
        )
        self._tray = pystray.Icon(
            "taskbar_pets",
            _make_tray_icon(),
            "Taskbar Pets",
            menu,
        )
        self._tray.run()

    def run(self) -> None:
        self._tray_thread = threading.Thread(target=self._run_tray, daemon=True)
        self._tray_thread.start()
        self._start_overlay()


def main() -> None:
    app = TaskbarPetsApp()
    app.run()


if __name__ == "__main__":
    main()
