"""Pet entity with interactive state machine, speech bubbles, and particle effects."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple

from src.sprites import SpriteSet


class PetState(Enum):
    WALK = "walk"
    IDLE = "idle"
    SLEEP = "sleep"
    HAPPY = "happy"
    CHASE = "chase"


POKEMON_SPEECH: dict[str, list[str]] = {
    "pikachu": ["Pika Pika!", "Chuuu!", "Pikachu!", "⚡ Pika!", "♥️"],
    "charmander": ["Char!", "Charmander!", "🔥 Char!", "♥️"],
    "squirtle": ["Squirtle!", "Squirt!", "💦 Water!", "♥️"],
    "bulbasaur": ["Bulba!", "Bulbasaur!", "🍃 Saur!", "♥️"],
    "eevee": ["Vee!", "Eevee!", "Eevvee!", "♥️", "✨"],
    "gengar": ["Hehehe!", "Gengar!", "👻 Boo!", "Heh!", "✨"],
    "dragonite": ["Draagon!", "Dragonite!", "✨ Fly!", "♥️"],
    "mewtwo": ["...", "Mewtwo.", "Hmph.", "✨"],
    "mew": ["Mew!", "Meww!", "✨", "♥️"],
    "charizard": ["ROAR!", "Charizard!", "🔥", "Char!"],
    "blastoise": ["Blastoise!", "Water Pump!", "💦"],
    "venusaur": ["Venu!", "Solar Beam!", "🍃"],
    "snorlax": ["Zzz...", "Snorlax...", "Hungry...", "Zzz..."],
    "lapras": ["Laaapras~", "Singing~", "🌊"],
    "jigglypuff": ["Jigglyyy!", "Puff puff!", "🎵 Lalala~"],
    "psyduck": ["Psy?...", "Headache...", "Psyduck?"],
    "lucario": ["Aura power!", "Lucario!", "✨"],
    "espeon": ["Espeon~", "Psychic!✨", "♥️"],
    "umbreon": ["Umbreon.", "Moonlight~", "✨"],
    "vaporeon": ["Vapor~", "Splash! 💦", "♥️"],
    "jolteon": ["Jolt!", "Spark! ⚡", "⚡"],
    "flareon": ["Warm~", "Flame! 🔥", "♥️"],
}


@dataclass
class Particle:
    kind: str  # "heart", "zzz", "sparkle"
    x: float
    y: float
    vy: float = -20.0
    lifetime: float = 1.2
    age: float = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.y += self.vy * dt
        return self.age < self.lifetime


@dataclass
class Pet:
    name: str
    sprites: SpriteSet
    x: float
    direction: int = 1
    state: PetState = PetState.WALK
    frame_index: int = 0
    frame_timer: float = 0.0
    state_timer: float = 0.0
    speed: float = field(default_factory=lambda: random.uniform(2.0, 3.5))

    # Speech bubble & particles
    speech_text: str | None = None
    speech_timer: float = 0.0
    particles: list[Particle] = field(default_factory=list)
    talk_cooldown: float = field(default_factory=lambda: random.uniform(5.0, 15.0))

    # Session-only custom position (None = use taskbar defaults; reset on every restart)
    custom_y: int | None = None          # Absolute screen Y where pet walks
    custom_x_start: int | None = None   # Absolute screen X of walk origin (left bound)

    # Physics vertical motion (for falling when taskbar auto-hides)
    curr_y: float | None = None
    vy: float = 0.0
    is_falling: bool = False

    def update_vertical(self, dt: float, target_floor_y: float) -> float:
        """Animate Y position: gravity fall when taskbar hides, smooth rise when it returns."""
        if self.custom_y is not None:
            self.curr_y = float(self.custom_y)
            self.vy = 0.0
            self.is_falling = False
            return self.curr_y

        target = float(target_floor_y)
        if self.curr_y is None:
            self.curr_y = target
            self.vy = 0.0
            self.is_falling = False
            return self.curr_y

        GRAVITY = 2200.0   # px/s²  — snappy fall
        RISE_SPEED = 800.0  # px/s   — smooth lift back up

        if self.is_falling:
            # ── Active fall / bounce sequence ─────────────────────────────
            self.vy += GRAVITY * dt
            self.curr_y += self.vy * dt

            if self.curr_y >= target:
                # Hit the floor
                self.curr_y = target
                if abs(self.vy) > 100.0:
                    # Bounce back up with dampened velocity
                    self.vy = -abs(self.vy) * 0.18
                    if len(self.particles) < 4:
                        self.particles.append(
                            Particle(
                                kind="sparkle",
                                x=self.x + self.width / 2,
                                y=-5, vy=-20, lifetime=0.8,
                            )
                        )
                else:
                    # Done bouncing — land cleanly
                    self.vy = 0.0
                    self.is_falling = False

        elif target > self.curr_y + 6.0:
            # ── Floor dropped away (taskbar hid) → start falling ──────────
            self.is_falling = True
            self.vy = 0.0  # start from rest, gravity will accelerate

        elif target < self.curr_y - 6.0:
            # ── Floor rose (taskbar reappeared) → smooth rise ─────────────
            self.curr_y -= RISE_SPEED * dt
            if self.curr_y <= target:
                self.curr_y = target
                self.vy = 0.0

        else:
            # ── Close enough → snap ──────────────────────────────────────
            self.curr_y = target
            self.vy = 0.0

        return self.curr_y

    def update(
        self,
        dt: float,
        min_x: float,
        max_x: float,
        target_x: float | None = None,
        speed_mult: float = 1.0,
        freeze: bool = False,
    ) -> None:
        self.frame_timer += dt
        self.state_timer += dt

        # Update speech bubble timer
        if self.speech_timer > 0:
            self.speech_timer -= dt
            if self.speech_timer <= 0:
                self.speech_text = None

        # Random speech chatter
        self.talk_cooldown -= dt
        if self.talk_cooldown <= 0 and self.state != PetState.SLEEP:
            self.say_random()
            self.talk_cooldown = random.uniform(8.0, 20.0)

        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # State machine behavior (skipped when frozen or in free-roam with freeze)
        if not freeze:
            effective_speed = self.speed * speed_mult

            if self.state == PetState.SLEEP:
                # Spawn Zzz particles periodically
                if random.random() < 0.03 and len(self.particles) < 3:
                    self.particles.append(
                        Particle(
                            kind="zzz",
                            x=self.x + self.width / 2,
                            y=-10,
                            vy=-15,
                            lifetime=1.5,
                        )
                    )

            elif self.state == PetState.HAPPY:
                if self.state_timer > 2.5:
                    self.state = PetState.WALK
                    self.state_timer = 0.0

            elif self.state == PetState.CHASE and target_x is not None:
                dx = target_x - (self.x + self.width / 2)
                if abs(dx) > 10:
                    self.direction = 1 if dx > 0 else -1
                    self.x += self.direction * effective_speed * 1.5 * dt * 60
                    self.x = max(min_x, min(max_x, self.x))
                else:
                    self.state = PetState.HAPPY
                    self.say("Yum! Tasty! 🍇")
                    self.state_timer = 0.0

            elif self.state == PetState.IDLE:
                # Pause in place for 1.0 to 2.0 seconds showing front-facing idle model
                if self.state_timer > random.uniform(1.0, 2.0):
                    self.state = PetState.WALK
                    self.state_timer = 0.0

            else:  # WALK
                self.x += effective_speed * self.direction * dt * 60
                if self.x <= min_x:
                    self.x = min_x
                    self.direction = 1
                    self.state = PetState.IDLE
                    self.state_timer = 0.0
                elif self.x >= max_x:
                    self.x = max_x
                    self.direction = -1
                    self.state = PetState.IDLE
                    self.state_timer = 0.0
                elif random.random() < 0.005:  # occasional random pause mid-walk
                    self.state = PetState.IDLE
                    self.state_timer = 0.0
                    if random.random() < 0.5:
                        self.direction = -self.direction

        # Frame animation calculation
        duration = self.sprites.frame_duration(
            self.frame_index, walking=(self.state in (PetState.WALK, PetState.CHASE))
        )
        if self.frame_timer >= duration:
            self.frame_timer -= duration
            self.frame_index = (self.frame_index + 1) % len(self.sprites.frames)

    def say(self, text: str, duration: float = 3.0) -> None:
        self.speech_text = text
        self.speech_timer = duration

    def say_random(self) -> None:
        options = POKEMON_SPEECH.get(self.name.lower(), ["Pet!", "♥️", "✨"])
        self.say(random.choice(options))

    def pet(self) -> None:
        """Trigger petting affection reaction."""
        self.state = PetState.HAPPY
        self.state_timer = 0.0
        options = ["♥️", "Hehe!", "Purrr~", "Happy! ✨"]
        phrase = POKEMON_SPEECH.get(self.name.lower(), options)[0]
        self.say(phrase)
        for _ in range(3):
            self.particles.append(
                Particle(
                    kind="heart",
                    x=self.x + self.width / 2 + random.uniform(-15, 15),
                    y=-5 + random.uniform(-10, 0),
                    vy=random.uniform(-25, -15),
                    lifetime=1.2,
                )
            )

    def feed(self, target_x: float | None = None) -> None:
        """Trigger feeding reaction."""
        if target_x is not None:
            self.state = PetState.CHASE
            self.say("Food?! 🍇")
        else:
            self.state = PetState.HAPPY
            self.say("Yum! 🍒")
        self.state_timer = 0.0

    def toggle_sleep(self) -> None:
        if self.state == PetState.SLEEP:
            self.state = PetState.WALK
            self.say("Yawn~ Good morning!")
        else:
            self.state = PetState.SLEEP
            self.say("Zzz...")


    @property
    def width(self) -> int:
        return self.sprites.width

    @property
    def height(self) -> int:
        return self.sprites.height
