"""Generate app icon and installer banner images with the clean classic Pokéball logo."""

import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("assets", exist_ok=True)


def create_pokeball_logo(size=512) -> Image.Image:
    """Draw a clean, crisp, classic Pokéball logo."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    pad = max(2, int(size * 0.04))
    r = cx - pad

    # 1. Outer Dark Border
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 30, 30, 255))

    # 2. Pokéball Shell
    r_inner = r - max(2, int(size * 0.04))

    # Red Top Half
    d.pieslice([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], 180, 360, fill=(235, 60, 60, 255))

    # White Bottom Half
    d.pieslice([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], 0, 180, fill=(245, 245, 245, 255))

    # 3. Center Black Belt Line
    belt_h = max(2, int(r_inner * 0.20))
    d.rectangle([cx - r_inner, cy - belt_h // 2, cx + r_inner, cy + belt_h // 2], fill=(30, 30, 30, 255))

    # 4. Center Button
    # Outer dark circle
    btn_r = int(r_inner * 0.35)
    d.ellipse([cx - btn_r, cy - btn_r, cx + btn_r, cy + btn_r], fill=(30, 30, 30, 255))

    # Inner white core
    core_r = int(r_inner * 0.22)
    d.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(255, 255, 255, 255))

    return img


def make_icon():
    """Create main app .ico and .png icon."""
    base_512 = create_pokeball_logo(512)
    sizes = [256, 128, 64, 48, 32, 16]
    images = [base_512.resize((s, s), Image.Resampling.LANCZOS) for s in sizes]

    images[0].save(
        "assets/icon.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )
    images[0].save("assets/icon.png")
    print("[OK] assets/icon.ico and assets/icon.png created with clean classic Pokéball logo")


def make_installer_banner():
    """Create Inno Setup wizard banner (164x314 px)."""
    img = Image.new("RGB", (164, 314), "#181825")
    d = ImageDraw.Draw(img)

    for y in range(314):
        frac = y / 314
        r = int(0x18 + (0x11 - 0x18) * frac)
        g = int(0x18 + (0x11 - 0x18) * frac)
        b = int(0x25 + (0x1b - 0x25) * frac)
        d.line([(0, y), (163, y)], fill=(r, g, b))

    d.line([(0, 0), (163, 0)], fill="#eb3c3c", width=3)

    logo = create_pokeball_logo(110).convert("RGB")
    img.paste(logo, (27, 50))

    d.text((82, 195), "Taskbar", anchor="mm", fill="#f5f5f5", font=ImageFont.load_default(size=14))
    d.text((82, 215), "Pets", anchor="mm", fill="#eb3c3c", font=ImageFont.load_default(size=14))
    d.text((82, 245), "v1.0.0", anchor="mm", fill="#888888", font=ImageFont.load_default(size=10))

    img.save("assets/installer_banner.bmp")
    print("[OK] assets/installer_banner.bmp updated with classic Pokéball logo")


def make_installer_icon():
    """Small 55x55 bmp for Inno Setup small image."""
    logo = create_pokeball_logo(55).convert("RGB")
    logo.save("assets/installer_icon.bmp")
    print("[OK] assets/installer_icon.bmp updated with classic Pokéball logo")


if __name__ == "__main__":
    make_icon()
    make_installer_banner()
    make_installer_icon()
    print("\nAll assets updated! Run build.bat to update the executable.")
