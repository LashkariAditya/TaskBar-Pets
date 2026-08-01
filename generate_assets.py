"""Generate app icon and installer banner images."""

import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("assets", exist_ok=True)


def make_icon():
    """Create the main app .ico icon."""
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # Dark background circle
        pad = max(2, size // 16)
        d.ellipse([pad, pad, size - pad, size - pad], fill="#1e1e2e")

        # Accent ring
        ring_w = max(1, size // 32)
        d.ellipse([pad, pad, size - pad, size - pad],
                  outline="#cba6f7", width=ring_w)

        # Paw print (scaled)
        cx, cy = size // 2, size // 2
        r = size * 0.18

        # Main central pad
        d.ellipse([cx - r, cy + r * 0.1, cx + r, cy + r * 2.2], fill="#fab387")

        # 4 toe pads
        toe_r = r * 0.52
        positions = [
            (cx - r * 1.1, cy - r * 0.3),  # top-left
            (cx - r * 0.3, cy - r * 1.0),  # top-mid-left
            (cx + r * 0.3, cy - r * 1.0),  # top-mid-right
            (cx + r * 1.1, cy - r * 0.3),  # top-right
        ]
        for tx, ty in positions:
            d.ellipse([tx - toe_r, ty - toe_r, tx + toe_r, ty + toe_r], fill="#fab387")

        images.append(img)

    images[0].save("assets/icon.ico", format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )
    images[0].save("assets/icon.png")
    print("[OK] assets/icon.ico and assets/icon.png created")


def make_installer_banner():
    """Create Inno Setup wizard banner (164x314 px)."""
    img = Image.new("RGB", (164, 314), "#11111b")
    d = ImageDraw.Draw(img)

    for y in range(314):
        frac = y / 314
        r = int(0x11 + (0x1e - 0x11) * frac)
        g = int(0x11 + (0x1e - 0x11) * frac)
        b = int(0x1b + (0x2e - 0x1b) * frac)
        d.line([(0, y), (163, y)], fill=(r, g, b))

    d.line([(0, 0), (163, 0)], fill="#cba6f7", width=3)

    cx, cy = 82, 130
    r = 28
    d.ellipse([cx - r, cy + 5, cx + r, cy + r * 2 + 10], fill="#fab387")
    toe_r = 13
    for tx, ty in [(cx - 30, cy - 8), (cx - 10, cy - 26),
                   (cx + 10, cy - 26), (cx + 30, cy - 8)]:
        d.ellipse([tx - toe_r, ty - toe_r, tx + toe_r, ty + toe_r], fill="#fab387")

    d.text((82, 200), "Taskbar", anchor="mm", fill="#cdd6f4",
           font=ImageFont.load_default(size=14))
    d.text((82, 220), "Pets", anchor="mm", fill="#cba6f7",
           font=ImageFont.load_default(size=14))
    d.text((82, 248), "v1.0.0", anchor="mm", fill="#585b70",
           font=ImageFont.load_default(size=10))

    img.save("assets/installer_banner.bmp")
    print("[OK] assets/installer_banner.bmp created")


def make_installer_icon():
    """Small 55x55 bmp for Inno Setup small image."""
    img = Image.new("RGB", (55, 55), "#11111b")
    d = ImageDraw.Draw(img)
    cx, cy, r = 27, 30, 10
    d.ellipse([cx - r, cy, cx + r, cy + r * 2], fill="#fab387")
    toe_r = 4
    for tx, ty in [(cx - 12, cy - 4), (cx - 4, cy - 11),
                   (cx + 4, cy - 11), (cx + 12, cy - 4)]:
        d.ellipse([tx - toe_r, ty - toe_r, tx + toe_r, ty + toe_r], fill="#fab387")
    img.save("assets/installer_icon.bmp")
    print("[OK] assets/installer_icon.bmp created")


if __name__ == "__main__":
    make_icon()
    make_installer_banner()
    make_installer_icon()
    print("\nAll assets generated! Run build.bat to build the installer.")
