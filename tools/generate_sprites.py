"""Generate simple pixel-art Pokemon-style sprites."""

from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent / "assets" / "pokemon"
SCALE = 3
TRANSPARENT = (0, 0, 0, 0)


def _scale(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.resize((w * SCALE, h * SCALE), Image.NEAREST)


def _grid_to_image(grid: list[str], palette: dict[str, tuple[int, int, int, int]]) -> Image.Image:
    h = len(grid)
    w = len(grid[0])
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    px = img.load()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch in palette:
                px[x, y] = palette[ch]
    return _scale(img)


# --- Pikachu ---
PIKACHU_PALETTE = {
    ".": TRANSPARENT,
    "Y": (250, 220, 60, 255),
    "y": (230, 190, 40, 255),
    "B": (40, 40, 40, 255),
    "R": (180, 50, 50, 255),
    "W": (255, 255, 255, 255),
    "K": (120, 80, 20, 255),
}

PIKACHU_IDLE_1 = [
    "................",
    "......yy........",
    ".....YYYY.......",
    "....YYYYYY......",
    "....YYYYYY......",
    "...YYYYBYY......",
    "...YYYYBYY......",
    "..YYYYYYYY......",
    "..YYYYYYYY......",
    "...YYYYYY.......",
    "...YY..YY.......",
    "..YYY..YYY......",
    "..YYY..YYY......",
    "...YY..YY.......",
    "....Y..Y........",
    "................",
]

PIKACHU_IDLE_2 = [
    "................",
    "......yy........",
    ".....YYYY.......",
    "....YYYYYY......",
    "....YYYYYY......",
    "...YYYYBYY......",
    "...YYYYBYY......",
    "..YYYYYYYY......",
    "..YYYYYYYY......",
    "...YYYYYY.......",
    "...YY..YY.......",
    "..YYY..YYY......",
    "..YYY..YYY......",
    "...YY..YY.......",
    "....Y..Y........",
    "................",
]

PIKACHU_WALK = [
    PIKACHU_IDLE_1,
    [
        "................",
        "......yy........",
        ".....YYYY.......",
        "....YYYYYY......",
        "....YYYYYY......",
        "...YYYYBYY......",
        "...YYYYBYY......",
        "..YYYYYYYY......",
        "..YYYYYYYY......",
        "...YYYYYY.......",
        "...YY..YY.......",
        "..YYY..YYY......",
        "..YYY..YYY......",
        "...Y....Y.......",
        "....Y..Y........",
        "................",
    ],
    PIKACHU_IDLE_2,
    [
        "................",
        "......yy........",
        ".....YYYY.......",
        "....YYYYYY......",
        "....YYYYYY......",
        "...YYYYBYY......",
        "...YYYYBYY......",
        "..YYYYYYYY......",
        "..YYYYYYYY......",
        "...YYYYYY.......",
        "...YY..YY.......",
        "..YYY..YYY......",
        "..YYY..YYY......",
        "....Y..Y........",
        "...Y....Y.......",
        "................",
    ],
]

# --- Charmander ---
CHARMANDER_PALETTE = {
    ".": TRANSPARENT,
    "O": (240, 120, 50, 255),
    "o": (210, 90, 35, 255),
    "B": (40, 40, 40, 255),
    "W": (255, 255, 255, 255),
    "R": (220, 60, 40, 255),
    "Y": (250, 200, 50, 255),
}

CHARMANDER_IDLE = [
    "................",
    "................",
    ".....oooo.......",
    "....OOOOOO......",
    "...OOOOBOO......",
    "...OOOOBOO......",
    "..OOOOOOOO......",
    "..OOOOOOOO......",
    "...OOOOOO.......",
    "...OO..OO.......",
    "..OOO..OOO......",
    "..OOO..OOO......",
    "...OO..OO.......",
    "....O..O........",
    "...R....Y.......",
    "................",
]

CHARMANDER_WALK = [
    CHARMANDER_IDLE,
    [
        "................",
        "................",
        ".....oooo.......",
        "....OOOOOO......",
        "...OOOOBOO......",
        "...OOOOBOO......",
        "..OOOOOOOO......",
        "..OOOOOOOO......",
        "...OOOOOO.......",
        "...OO..OO.......",
        "..OOO..OOO......",
        "..OOO..OOO......",
        "...O....O.......",
        "....O..O........",
        "...R....Y.......",
        "................",
    ],
    CHARMANDER_IDLE,
    [
        "................",
        "................",
        ".....oooo.......",
        "....OOOOOO......",
        "...OOOOBOO......",
        "...OOOOBOO......",
        "..OOOOOOOO......",
        "..OOOOOOOO......",
        "...OOOOOO.......",
        "...OO..OO.......",
        "..OOO..OOO......",
        "..OOO..OOO......",
        "....O..O........",
        "...O....O.......",
        "...R....Y.......",
        "................",
    ],
]

# --- Squirtle ---
SQUIRTLE_PALETTE = {
    ".": TRANSPARENT,
    "C": (100, 160, 220, 255),
    "c": (70, 130, 190, 255),
    "B": (40, 40, 40, 255),
    "W": (255, 255, 255, 255),
    "S": (180, 200, 220, 255),
}

SQUIRTLE_IDLE = [
    "................",
    "................",
    ".....SSSS.......",
    "....CCCCCC......",
    "...CCCBBCC......",
    "...CCCBBCC......",
    "..CCCCCCCC......",
    "..CCCCCCCC......",
    "...CCCCCC.......",
    "...CC..CC.......",
    "..CCC..CCC......",
    "..CCC..CCC......",
    "...CC..CC.......",
    "....C..C........",
    "................",
    "................",
]

SQUIRTLE_WALK = [
    SQUIRTLE_IDLE,
    [
        "................",
        "................",
        ".....SSSS.......",
        "....CCCCCC......",
        "...CCCBBCC......",
        "...CCCBBCC......",
        "..CCCCCCCC......",
        "..CCCCCCCC......",
        "...CCCCCC.......",
        "...CC..CC.......",
        "..CCC..CCC......",
        "..CCC..CCC......",
        "...C....C.......",
        "....C..C........",
        "................",
        "................",
    ],
    SQUIRTLE_IDLE,
    [
        "................",
        "................",
        ".....SSSS.......",
        "....CCCCCC......",
        "...CCCBBCC......",
        "...CCCBBCC......",
        "..CCCCCCCC......",
        "..CCCCCCCC......",
        "...CCCCCC.......",
        "...CC..CC.......",
        "..CCC..CCC......",
        "..CCC..CCC......",
        "....C..C........",
        "...C....C.......",
        "................",
        "................",
    ],
]

# --- Bulbasaur ---
BULBASAUR_PALETTE = {
    ".": TRANSPARENT,
    "G": (100, 180, 90, 255),
    "g": (70, 150, 70, 255),
    "B": (40, 40, 40, 255),
    "W": (255, 255, 255, 255),
    "D": (60, 120, 60, 255),
}

BULBASAUR_IDLE = [
    "................",
    ".....DDDD.......",
    "...DDDDDDDD.....",
    "....GGGGGG......",
    "...GGBBGG.......",
    "...GGBBGG.......",
    "..GGGGGGGG......",
    "..GGGGGGGG......",
    "...GGGGGG.......",
    "...GG..GG.......",
    "..GGG..GGG......",
    "..GGG..GGG......",
    "...GG..GG.......",
    "....G..G........",
    "................",
    "................",
]

BULBASAUR_WALK = [
    BULBASAUR_IDLE,
    [
        "................",
        ".....DDDD.......",
        "...DDDDDDDD.....",
        "....GGGGGG......",
        "...GGBBGG.......",
        "...GGBBGG.......",
        "..GGGGGGGG......",
        "..GGGGGGGG......",
        "...GGGGGG.......",
        "...GG..GG.......",
        "..GGG..GGG......",
        "..GGG..GGG......",
        "...G....G.......",
        "....G..G........",
        "................",
        "................",
    ],
    BULBASAUR_IDLE,
    [
        "................",
        ".....DDDD.......",
        "...DDDDDDDD.....",
        "....GGGGGG......",
        "...GGBBGG.......",
        "...GGBBGG.......",
        "..GGGGGGGG......",
        "..GGGGGGGG......",
        "...GGGGGG.......",
        "...GG..GG.......",
        "..GGG..GGG......",
        "..GGG..GGG......",
        "....G..G........",
        "...G....G.......",
        "................",
        "................",
    ],
]

SPECIES = {
    "pikachu": (PIKACHU_PALETTE, PIKACHU_WALK, [PIKACHU_IDLE_1, PIKACHU_IDLE_2]),
    "charmander": (CHARMANDER_PALETTE, CHARMANDER_WALK, [CHARMANDER_IDLE, CHARMANDER_IDLE]),
    "squirtle": (SQUIRTLE_PALETTE, SQUIRTLE_WALK, [SQUIRTLE_IDLE, SQUIRTLE_IDLE]),
    "bulbasaur": (BULBASAUR_PALETTE, BULBASAUR_WALK, [BULBASAUR_IDLE, BULBASAUR_IDLE]),
}


def _save_species(name: str, palette, walk_grids, idle_grids) -> None:
    folder = ASSETS / name
    folder.mkdir(parents=True, exist_ok=True)
    for i, grid in enumerate(walk_grids):
        img = _grid_to_image(grid, palette)
        img.save(folder / f"walk_{i}.png")
    for i, grid in enumerate(idle_grids):
        img = _grid_to_image(grid, palette)
        img.save(folder / f"idle_{i}.png")
    print(f"  Created {name} ({len(walk_grids)} walk, {len(idle_grids)} idle frames)")


def main() -> None:
    print("Generating Pokemon-style sprites...")
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, (palette, walk, idle) in SPECIES.items():
        _save_species(name, palette, walk, idle)
    print("Done!")


if __name__ == "__main__":
    main()
