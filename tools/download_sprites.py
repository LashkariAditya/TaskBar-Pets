"""Download animated Pokemon GIF sprites (Gen V — same style as VS Code Pokemon)."""

from __future__ import annotations

import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent / "assets" / "pokemon"
BASE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
    "/versions/generation-v/black-white/animated/{id}.gif"
)
SCALE = 2

POKEMON: dict[str, int] = {
    "bulbasaur": 1,
    "ivysaur": 2,
    "venusaur": 3,
    "charmander": 4,
    "charmeleon": 5,
    "charizard": 6,
    "squirtle": 7,
    "wartortle": 8,
    "blastoise": 9,
    "pikachu": 25,
    "raichu": 26,
    "jigglypuff": 39,
    "psyduck": 54,
    "gengar": 94,
    "lapras": 131,
    "eevee": 133,
    "vaporeon": 134,
    "jolteon": 135,
    "flareon": 136,
    "snorlax": 143,
    "dragonite": 149,
    "mewtwo": 150,
    "mew": 151,
    "espeon": 196,
    "umbreon": 197,
    "lucario": 448,
}


def _extract_gif_frames(data: bytes) -> list[Image.Image]:
    img = Image.open(BytesIO(data))
    frames: list[Image.Image] = []
    try:
        while True:
            frame = img.convert("RGBA")
            if SCALE != 1:
                w, h = frame.size
                frame = frame.resize((w * SCALE, h * SCALE), Image.NEAREST)
            frames.append(frame)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames


def _save_gif(data: bytes, folder: Path) -> list[Image.Image]:
    folder.mkdir(parents=True, exist_ok=True)
    gif_path = folder / "animated.gif"
    gif_path.write_bytes(data)

    # Also save PNG sequence as fallback
    frames = _extract_gif_frames(data)
    for old in folder.glob("*.png"):
        old.unlink()
    for i, frame in enumerate(frames):
        frame.save(folder / f"frame_{i:02d}.png")
    return frames


def download_pokemon(name: str, pokemon_id: int) -> bool:
    target_folder = ASSETS / name
    gif_file = target_folder / "animated.gif"
    if gif_file.is_file() and gif_file.stat().st_size > 0:
        print(f"  {name} already downloaded.")
        return True

    url = BASE_URL.format(id=pokemon_id)
    print(f"  Downloading {name} (#{pokemon_id})...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Taskbar-Pets/1.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
    except Exception as exc:
        print(f"    FAILED: {exc}")
        return False

    frames = _save_gif(data, target_folder)
    if not frames:
        print("    FAILED: no frames in GIF")
        return False

    print(f"    OK — {len(frames)} frames, {frames[0].size[0]}x{frames[0].size[1]}px")
    return True


def main() -> None:
    print("Downloading animated Pokemon sprites (Gen V Black/White)...")
    ASSETS.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, pid in POKEMON.items():
        if download_pokemon(name, pid):
            ok += 1
    print(f"\nDone! {ok}/{len(POKEMON)} Pokemon ready.")
    if ok == 0:
        raise SystemExit("No sprites downloaded — check your internet connection.")


if __name__ == "__main__":
    main()

