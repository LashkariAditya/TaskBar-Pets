"""Generate high-quality animated pixel-art sprites for 9tail (Naruto Nine-Tailed Fox / Kurama)."""

from pathlib import Path
from PIL import Image

TARGET_DIR = Path(__file__).resolve().parent.parent / "assets" / "naruto" / "9tail"
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# Grid dimensions: 32x32 pixels, scaled 2x to 64x64 for crisp pixel art
W, H = 32, 32
SCALE = 2

TRANSPARENT = (0, 0, 0, 0)
O = (245, 110, 20, 255)   # Primary Orange
o = (195, 75, 15, 255)    # Dark Orange Shadow
Y = (255, 215, 0, 255)    # Gold Flame Tip
y = (255, 170, 30, 255)   # Flame Body
R = (225, 25, 25, 255)    # Red Eye
W_ = (255, 255, 255, 255) # White Chest / Accent
B = (35, 25, 25, 255)     # Dark Outline / Eye Surround
K = (15, 10, 10, 255)     # Black Ear Tip / Whisker

PALETTE = {
    ".": TRANSPARENT,
    "O": O,
    "o": o,
    "Y": Y,
    "y": y,
    "R": R,
    "W": W_,
    "B": B,
    "K": K,
}

# --- Idle Frames (4 frames: breathing, ear twitching, tail swaying & flame pulsing) ---

# Frame 0: Neutral Idle
IDLE_0 = [
    "................................",
    "..YY...YY...YY...YY...YY...YY...",
    ".YyyY.YyyY.YyyY.YyyY.YyyY.YyyY..",
    ".yyyy.yyyy.yyyy.yyyy.yyyy.yyyy..",
    "..ooo..ooo..ooo..ooo..ooo..ooo..",
    "...oo...oo...oo...oo...oo...oo..",
    "....K.....K.....................",
    "...KOK...KOK....................",
    "...OOO...OOO....................",
    "..OOOOOOO...OO...OO...OO...OO...",
    "..OOROOOOO..oOO..oOO..oOO..oOO..",
    "..OOROOOOO.oOOOOoOOOOoOOOOoOOOO.",
    "..OOOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OWWWWOO.OOOOOOOOOOOOOOOOOOOO.",
    "....WWWW...OOOOOOOOOOOOOOOOOOOO.",
    "....OOOOOOOOOOOOOOOOOOOOOOOOOO..",
    "...OOOOOOOOOOOOOOOOOOOOOOOOOO...",
    "...OOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "...OO...OO......OO...OO.........",
    "...OO...OO......OO...OO.........",
    "..oOO..oOO.....oOO..oOO.........",
    "..oOO..oOO.....oOO..oOO.........",
    "..B....B.......B....B...........",
    "................................",
]

# Frame 1: Idle Breathing Up & Tail Sway 1
IDLE_1 = [
    "................................",
    "...YY...YY...YY...YY...YY...YY..",
    "..YyyY.YyyY.YyyY.YyyY.YyyY.YyyY.",
    "..yyyy.yyyy.yyyy.yyyy.yyyy.yyyy.",
    "...ooo..ooo..ooo..ooo..ooo..ooo.",
    "....oo...oo...oo...oo...oo...oo.",
    "....K.....K.....................",
    "...KOK...KOK....................",
    "...OOO...OOO....................",
    "..OOOOOOO...OO...OO...OO...OO...",
    "..OOROOOOO..oOO..oOO..oOO..oOO..",
    "..OOROOOOO.oOOOOoOOOOoOOOOoOOOO.",
    "..OOOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OWWWWOO.OOOOOOOOOOOOOOOOOOOO.",
    "....WWWW...OOOOOOOOOOOOOOOOOOOO.",
    "....OOOOOOOOOOOOOOOOOOOOOOOOOO..",
    "...OOOOOOOOOOOOOOOOOOOOOOOOOO...",
    "...OOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "...OO...OO......OO...OO.........",
    "...OO...OO......OO...OO.........",
    "..oOO..oOO.....oOO..oOO.........",
    "..oOO..oOO.....oOO..oOO.........",
    "..B....B.......B....B...........",
    "................................",
    "................................",
]

# Frame 2: Idle Breathing Peak & Flame Pulse
IDLE_2 = [
    "................................",
    ".YY...YY...YY...YY...YY...YY....",
    "YyyY.YyyY.YyyY.YyyY.YyyY.YyyY...",
    "yyyy.yyyy.yyyy.yyyy.yyyy.yyyy...",
    ".ooo..ooo..ooo..ooo..ooo..ooo...",
    "..oo...oo...oo...oo...oo...oo...",
    "....K.....K.....................",
    "...KOK...KOK....................",
    "...OOO...OOO....................",
    "..OOOOOOO...OO...OO...OO...OO...",
    "..OOROOOOO..oOO..oOO..oOO..oOO..",
    "..OOROOOOO.oOOOOoOOOOoOOOOoOOOO.",
    "..OOOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OWWWWOO.OOOOOOOOOOOOOOOOOOOO.",
    "....WWWW...OOOOOOOOOOOOOOOOOOOO.",
    "....OOOOOOOOOOOOOOOOOOOOOOOOOO..",
    "...OOOOOOOOOOOOOOOOOOOOOOOOOO...",
    "...OOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "...OO...OO......OO...OO.........",
    "...OO...OO......OO...OO.........",
    "..oOO..oOO.....oOO..oOO.........",
    "..oOO..oOO.....oOO..oOO.........",
    "..B....B.......B....B...........",
    "................................",
]

# Frame 3: Idle Breath Return & Tail Sway 2
IDLE_3 = IDLE_0

IDLE_GRIDS = [IDLE_0, IDLE_1, IDLE_2, IDLE_3]

# --- Walk Frames (4 frames stride sequence) ---

# Walk 0: Step 1 (Front-Left & Back-Right forward)
WALK_0 = [
    "................................",
    "..YY...YY...YY...YY...YY...YY...",
    ".YyyY.YyyY.YyyY.YyyY.YyyY.YyyY..",
    ".yyyy.yyyy.yyyy.yyyy.yyyy.yyyy..",
    "..ooo..ooo..ooo..ooo..ooo..ooo..",
    "...oo...oo...oo...oo...oo...oo..",
    "....K.....K.....................",
    "...KOK...KOK....................",
    "...OOO...OOO....................",
    "..OOOOOOO...OO...OO...OO...OO...",
    "..OOROOOOO..oOO..oOO..oOO..oOO..",
    "..OOROOOOO.oOOOOoOOOOoOOOOoOOOO.",
    "..OOOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OWWWWOO.OOOOOOOOOOOOOOOOOOOO.",
    "....WWWW...OOOOOOOOOOOOOOOOOOOO.",
    "....OOOOOOOOOOOOOOOOOOOOOOOOOO..",
    "...OOOOOOOOOOOOOOOOOOOOOOOOOO...",
    "...OOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "...OO...OO......OO...OO.........",
    "..oOO...OO......oOO..OO.........",
    "..oOO...oOO.....oOO..oOO........",
    "..B......oOO....B.....oOO.......",
    "..........B............B........",
    "................................",
    "................................",
    "................................",
]

# Walk 1: Passing / Mid-stride
WALK_1 = IDLE_0

# Walk 2: Step 2 (Front-Right & Back-Left forward)
WALK_2 = [
    "................................",
    "...YY...YY...YY...YY...YY...YY..",
    "..YyyY.YyyY.YyyY.YyyY.YyyY.YyyY.",
    "..yyyy.yyyy.yyyy.yyyy.yyyy.yyyy.",
    "...ooo..ooo..ooo..ooo..ooo..ooo.",
    "....oo...oo...oo...oo...oo...oo.",
    "....K.....K.....................",
    "...KOK...KOK....................",
    "...OOO...OOO....................",
    "..OOOOOOO...OO...OO...OO...OO...",
    "..OOROOOOO..oOO..oOO..oOO..oOO..",
    "..OOROOOOO.oOOOOoOOOOoOOOOoOOOO.",
    "..OOOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OOOOOOO.OOOOOOOOOOOOOOOOOOOO.",
    "...OWWWWOO.OOOOOOOOOOOOOOOOOOOO.",
    "....WWWW...OOOOOOOOOOOOOOOOOOOO.",
    "....OOOOOOOOOOOOOOOOOOOOOOOOOO..",
    "...OOOOOOOOOOOOOOOOOOOOOOOOOO...",
    "...OOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "..OOOOOOOOOOOOOOOOOOOOOOOOOO....",
    "...OOOOOOOOOOOOOOOOOOOOOOOO.....",
    "....OO...OO.......OO...OO.......",
    "....OO...oOO......OO...oOO......",
    "...oOO...oOO.....oOO...oOO......",
    "..oOO.....B.....oOO.....B.......",
    "..B.............B...............",
    "................................",
    "................................",
    "................................",
]

# Walk 3: Passing / Mid-stride 2
WALK_3 = IDLE_2

WALK_GRIDS = [WALK_0, WALK_1, WALK_2, WALK_3]


def grid_to_image(grid: list[str]) -> Image.Image:
    img = Image.new("RGBA", (W, H), TRANSPARENT)
    pixels = img.load()
    for y_idx, row in enumerate(grid):
        for x_idx, char in enumerate(row):
            if char in PALETTE:
                pixels[x_idx, y_idx] = PALETTE[char]
    return img.resize((W * SCALE, H * SCALE), Image.NEAREST)


def generate() -> None:
    print("Generating 9tail (Nine-Tailed Fox) pixel-art sprites...")
    
    idle_images: list[Image.Image] = []
    for idx, grid in enumerate(IDLE_GRIDS):
        img = grid_to_image(grid)
        img.save(TARGET_DIR / f"idle_{idx}.png")
        idle_images.append(img)
        
    walk_images: list[Image.Image] = []
    for idx, grid in enumerate(WALK_GRIDS):
        img = grid_to_image(grid)
        img.save(TARGET_DIR / f"walk_{idx}.png")
        walk_images.append(img)
        
    # Save default GIFs (8fps = 125ms per frame)
    duration_ms = 125
    
    idle_images[0].save(
        TARGET_DIR / "default_idle_8fps.gif",
        save_all=True,
        append_images=idle_images[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )
    idle_images[0].save(
        TARGET_DIR / "idle.gif",
        save_all=True,
        append_images=idle_images[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )

    walk_images[0].save(
        TARGET_DIR / "default_walk_8fps.gif",
        save_all=True,
        append_images=walk_images[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )
    walk_images[0].save(
        TARGET_DIR / "walk.gif",
        save_all=True,
        append_images=walk_images[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )

    print(f"SUCCESS: Generated 9tail assets in {TARGET_DIR}")


if __name__ == "__main__":
    generate()
