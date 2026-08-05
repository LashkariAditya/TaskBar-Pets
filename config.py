"""Configuration persistence for Taskbar Pets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.paths import get_data_dir

CONFIG_PATH = get_data_dir() / "config.json"

DEFAULT_ROSTER = ["pikachu", "charmander", "squirtle", "bulbasaur", "eevee"]
DEFAULT_MAX_ACTIVE_PETS = 5


@dataclass
class AppConfig:
    active_pets: list[str] = field(default_factory=lambda: list(DEFAULT_ROSTER))
    pet_scale: float = 2.0
    pet_speed: float = 1.5
    max_active_pets: int = DEFAULT_MAX_ACTIVE_PETS
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
            # respect configured max active pets when loading
            max_active = int(data.get("max_active_pets", DEFAULT_MAX_ACTIVE_PETS))
            active = active[:max_active]
            return cls(
                active_pets=active,
                pet_scale=float(data.get("pet_scale", 2.0)),
                pet_speed=float(data.get("pet_speed", 1.5)),
                max_active_pets=int(data.get("max_active_pets", DEFAULT_MAX_ACTIVE_PETS)),
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
        # enforce max active pets when saving
        # enforce the instance's configured max_active_pets
        try:
            max_active = int(getattr(self, "max_active_pets", DEFAULT_MAX_ACTIVE_PETS))
        except Exception:
            max_active = DEFAULT_MAX_ACTIVE_PETS
        self.active_pets = self.active_pets[:max_active]
        try:
            CONFIG_PATH.write_text(
                json.dumps(asdict(self), indent=2), encoding="utf-8"
            )
        except Exception as exc:
            print(f"Failed to save config: {exc}")
