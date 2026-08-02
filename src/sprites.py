"""Load animated Pokemon GIF sprites (Gen V style across Gen 1 - Gen 5 assets)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageTk

from src.paths import get_asset_roots, get_assets_dir

DEFAULT_FRAME_MS = 80
DISPLAY_SCALE = 2  # upscale Gen V sprites for taskbar visibility
MIN_UPSCALE = 64

GEN_KEYS = ["gen1", "gen2", "gen3", "gen4", "gen5"]
SPECIAL_KEYS = ["naruto"]
ASSET_GROUPS = GEN_KEYS + SPECIAL_KEYS + ["pokemon"]
GEN_LABELS = {
    "gen1": "Generation 1 (Kanto)",
    "gen2": "Generation 2 (Johto)",
    "gen3": "Generation 3 (Hoenn)",
    "gen4": "Generation 4 (Sinnoh)",
    "gen5": "Generation 5 (Unova)",
    "naruto": "Naruto / Special",
    "all": "All Generations",
}


def get_pokemon_folder(pokemon_name: str) -> Path | None:
    """Find the asset directory for a pet name across all supported asset groups."""
    for base_dir in get_asset_roots():
        for group in ASSET_GROUPS:
            folder = base_dir / group / pokemon_name
            if folder.is_dir():
                return folder
    return None


def discover_pokemon_by_gen() -> dict[str, list[str]]:
    """Return dictionary mapping gen key ('gen1'..'gen5') to sorted list of pokemon names."""
    result: dict[str, list[str]] = {}

    for gen in GEN_KEYS + SPECIAL_KEYS:
        names: list[str] = []
        for base_dir in get_asset_roots():
            gen_dir = base_dir / gen
            if gen_dir.is_dir():
                for folder in sorted(gen_dir.iterdir()):
                    if folder.is_dir():
                        gifs = list(folder.glob("*.gif")) + list(folder.glob("*.png"))
                        if gifs and folder.name not in names:
                            names.append(folder.name)
        result[gen] = names
    return result


def discover_pokemon() -> list[str]:
    """Return all available pokemon names sorted across all generations."""
    by_gen = discover_pokemon_by_gen()
    all_names: set[str] = set()
    for gen_list in by_gen.values():
        all_names.update(gen_list)

    if not all_names:
        for base_dir in get_asset_roots():
            for group in ASSET_GROUPS:
                pokemon_dir = base_dir / group
                if pokemon_dir.is_dir():
                    for folder in sorted(pokemon_dir.iterdir()):
                        if folder.is_dir():
                            all_names.add(folder.name)

    return sorted(all_names)


def has_animated_assets() -> bool:
    return len(discover_pokemon()) > 0


def _scale_frames(frames: list[Image.Image], target_scale: float = 2.0) -> list[Image.Image]:
    w, h = frames[0].size
    scale = max(0.5, float(target_scale))
    new_w = max(16, int(w * scale))
    new_h = max(16, int(h * scale))
    if new_w == w and new_h == h:
        return frames
    return [
        f.resize((new_w, new_h), Image.NEAREST)
        for f in frames
    ]


@dataclass
class SpriteSet:
    name: str
    walk_frames: list[Image.Image]
    walk_durations: list[float]
    idle_frames: list[Image.Image]
    idle_durations: list[float]
    width: int
    height: int

    @property
    def frames(self) -> list[Image.Image]:
        return self.walk_frames

    @property
    def frame_durations(self) -> list[float]:
        return self.walk_durations

    def frame_duration(self, index: int, walking: bool) -> float:
        durs = self.walk_durations if walking else self.idle_durations
        base = durs[index % len(durs)]
        return base * (0.55 if walking else 1.0)

    def to_tk_frames(self) -> dict[str, list[ImageTk.PhotoImage]]:
        walk_norm = [ImageTk.PhotoImage(f) for f in self.walk_frames]
        walk_flip = [ImageTk.PhotoImage(f.transpose(Image.FLIP_LEFT_RIGHT)) for f in self.walk_frames]

        idle_norm = [ImageTk.PhotoImage(f) for f in self.idle_frames]
        idle_flip = [ImageTk.PhotoImage(f.transpose(Image.FLIP_LEFT_RIGHT)) for f in self.idle_frames]

        return {
            "walk": walk_norm,
            "walk_flip": walk_flip,
            "idle": idle_norm,
            "idle_flip": idle_flip,
        }


def _load_gif(path: Path) -> tuple[list[Image.Image], list[float]]:
    img = Image.open(path)
    frames: list[Image.Image] = []
    durations: list[float] = []
    try:
        while True:
            frame = img.convert("RGBA")
            ms = img.info.get("duration", DEFAULT_FRAME_MS)
            if not ms:
                ms = DEFAULT_FRAME_MS
            frames.append(frame)
            durations.append(ms / 1000.0)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames, durations


def _load_png_sequence(folder: Path, prefix: str) -> list[Image.Image]:
    paths = sorted(folder.glob(f"{prefix}_*.png"))
    if not paths:
        paths = sorted(folder.glob(f"{prefix}*.png"))
    return [Image.open(p).convert("RGBA") for p in paths]


def load_sprite_set(pokemon_name: str, scale: float = 2.0) -> SpriteSet | None:
    folder = get_pokemon_folder(pokemon_name)
    if not folder:
        return None

    # Look for separate WALK and IDLE gifs
    walk_candidates = [
        folder / "default_walk_8fps.gif",
        folder / "walk_8fps.gif",
        folder / "walk.gif",
    ]
    idle_candidates = [
        folder / "default_idle_8fps.gif",
        folder / "idle_8fps.gif",
        folder / "idle.gif",
    ]

    walk_gif: Path | None = None
    for c in walk_candidates:
        if c.is_file():
            walk_gif = c
            break

    idle_gif: Path | None = None
    for c in idle_candidates:
        if c.is_file():
            idle_gif = c
            break

    # General gif fallback
    all_gifs = list(folder.glob("*.gif"))
    if not walk_gif and all_gifs:
        walk_gif = all_gifs[0]
    if not idle_gif:
        if len(all_gifs) > 1 and all_gifs[1] != walk_gif:
            idle_gif = all_gifs[1]
        else:
            idle_gif = walk_gif

    # Load WALK frames
    if walk_gif:
        walk_frames, walk_durations = _load_gif(walk_gif)
        walk_frames = _scale_frames(walk_frames, scale)
    else:
        walk_frames = _load_png_sequence(folder, "walk")
        walk_durations = [DEFAULT_FRAME_MS / 1000.0] * len(walk_frames)

    # Load IDLE frames
    if idle_gif:
        idle_frames, idle_durations = _load_gif(idle_gif)
        idle_frames = _scale_frames(idle_frames, scale)
    else:
        idle_frames = _load_png_sequence(folder, "idle")
        if not idle_frames:
            idle_frames = walk_frames
            idle_durations = walk_durations
        else:
            idle_durations = [DEFAULT_FRAME_MS / 1000.0] * len(idle_frames)

    if not walk_frames:
        return None
    if not idle_frames:
        idle_frames = walk_frames
        idle_durations = walk_durations

    w, h = walk_frames[0].size
    return SpriteSet(
        name=pokemon_name,
        walk_frames=walk_frames,
        walk_durations=walk_durations,
        idle_frames=idle_frames,
        idle_durations=idle_durations,
        width=w,
        height=h,
    )
