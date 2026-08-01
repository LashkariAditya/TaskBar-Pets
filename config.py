"""Configuration persistence for Taskbar Pets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.paths import get_data_dir

CONFIG_PATH = get_data_dir() / "config.json"

DEFAULT_ROSTER = ["pikachu", "charmander", "squirtle", "bulbasaur", "eevee"]


@dataclass
class AppConfig:
    active_pets: list[str] = field(default_factory=lambda: list(DEFAULT_ROSTER))
    pet_scale: float = 2.0
    pet_speed: float = 1.5
    interactive_mode: bool = False
    speech_enabled: bool = True
    particles_enabled: bool = True
    freeze_pets: bool = False
    auto_start: bool = False
    taskbar_offset: int = 0

    @classmethod
    def load(cls) -> AppConfig:
        if not CONFIG_PATH.is_file():
            cfg = cls()
            cfg.save()
            return cfg
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            active = data.get("active_pets", list(DEFAULT_ROSTER))
            if not isinstance(active, list) or not active:
                active = list(DEFAULT_ROSTER)
            active = active[:5]
            return cls(
                active_pets=active,
                pet_scale=float(data.get("pet_scale", 2.0)),
                pet_speed=float(data.get("pet_speed", 1.5)),
                interactive_mode=bool(data.get("interactive_mode", False)),
                speech_enabled=bool(data.get("speech_enabled", True)),
                particles_enabled=bool(data.get("particles_enabled", True)),
                freeze_pets=bool(data.get("freeze_pets", False)),
                auto_start=bool(data.get("auto_start", False)),
                taskbar_offset=int(data.get("taskbar_offset", 0)),
            )
        except Exception:
            return cls()

    def save(self) -> None:
        self.active_pets = self.active_pets[:5]
        try:
            CONFIG_PATH.write_text(
                json.dumps(asdict(self), indent=2), encoding="utf-8"
            )
        except Exception as exc:
            print(f"Failed to save config: {exc}")
