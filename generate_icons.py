"""Generate PWA icons for the Kids Games launcher and each game.

Creates rounded-square PNGs at the sizes iOS / PWA installers expect:
  - 180x180 apple-touch-icon (iPad/iPhone home screen)
  - 192x192 and 512x512 PWA manifest icons
Each game gets its own gradient icon (same colors as its launcher tile)
with an emoji glyph. Needs an emoji font: Apple Color Emoji on a Mac,
or Noto Color Emoji on Linux (apt install fonts-noto-color-emoji).
Run once after editing GAMES below; commit the PNGs.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).parent
ICON_DIR = ROOT / "icons"
ICON_DIR.mkdir(exist_ok=True)

# (slug, gradient top-left hex, gradient bottom-right hex, emoji glyph)
GAMES = [
    ("launcher", "#7a7af0", "#3c3ca8", "🎮"),
    ("memory",   "#f07088", "#b03d56", "🧠"),
    ("target",   "#3fcf85", "#1f8a55", "🎯"),
    ("sequence", "#f7b955", "#c8821e", "🎵"),
    ("trivoca",  "#2fae82", "#17694e", "🔤"),
    ("imposter", "#ff5050", "#6a1818", "🕵"),
    ("pelea",    "#f08a4b", "#6b4fa0", "🥊"),
]

SIZES = [180, 192, 512]


# (path, the one pixel size the bitmap font supports)
EMOJI_FONTS = [
    ("/System/Library/Fonts/Apple Color Emoji.ttc", 137),
    ("/Library/Fonts/Apple Color Emoji.ttc", 137),
    ("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109),
    ("/usr/share/fonts/noto/NotoColorEmoji.ttf", 109),
]


def find_emoji_font():
    for path, px in EMOJI_FONTS:
        if Path(path).exists():
            return path, px
    return None, None


def hex_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(size: int, top: str, bottom: str) -> Image.Image:
    """Diagonal gradient, top-left to bottom-right, like the launcher tiles."""
    a, b = hex_rgb(top), hex_rgb(bottom)
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return img


def make_icon(slug: str, top_hex: str, bottom_hex: str, glyph: str, size: int) -> Image.Image:
    # Full square: iOS and Android round the corners themselves, and iOS
    # turns transparent corners black.
    img = gradient(size, top_hex, bottom_hex).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_path, font_px = find_emoji_font()
    # Color emoji fonts only render at one size; draw there and resize.
    glyph_img_size = int(size * 0.62)
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_px)
            canvas = int(font_px * 1.25)
            tmp = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(tmp)
            tdraw.text((canvas // 2, canvas // 2), glyph, font=font, anchor="mm", embedded_color=True)
            tmp = tmp.crop(tmp.getbbox())
            scale = glyph_img_size / max(tmp.size)
            tmp = tmp.resize((round(tmp.width * scale), round(tmp.height * scale)), Image.LANCZOS)
            offset = ((size - tmp.width) // 2, (size - tmp.height) // 2)
            img.paste(tmp, offset, tmp)
            return img
        except Exception as e:
            print(f"  emoji font failed ({e}), falling back to plain shape")

    # Fallback: draw a white circle so the icon still looks deliberate.
    pad = int(size * 0.25)
    draw.ellipse([(pad, pad), (size - pad, size - pad)], fill="white")
    return img


def main():
    for slug, top, bottom, glyph in GAMES:
        for size in SIZES:
            img = make_icon(slug, top, bottom, glyph, size)
            out = ICON_DIR / f"{slug}-{size}.png"
            img.save(out, "PNG")
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
