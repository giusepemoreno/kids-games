"""Generate PWA icons for the Kids Games launcher and each game.

Creates rounded-square PNGs at the sizes iOS / PWA installers expect:
  - 180x180 apple-touch-icon (iPad/iPhone home screen)
  - 192x192 and 512x512 PWA manifest icons
Each game gets its own colored icon with an emoji glyph.
Run once after editing GAMES below; commit the PNGs.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).parent
ICON_DIR = ROOT / "icons"
ICON_DIR.mkdir(exist_ok=True)

# (slug, background hex, emoji glyph)
GAMES = [
    ("launcher", "#5B5BD6", "🎮"),
    ("memory",   "#E85D75", "🧠"),
    ("target",   "#2EB872", "🎯"),
    ("sequence", "#F2A93B", "🎵"),
    ("wordle",   "#3a86ff", "📝"),
    ("imposter", "#ff3c3c", "🕵"),
]

SIZES = [180, 192, 512]


def find_emoji_font():
    candidates = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        "/Library/Fonts/Apple Color Emoji.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def make_icon(slug: str, bg_hex: str, glyph: str, size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = int(size * 0.22)
    draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=bg_hex)

    font_path = find_emoji_font()
    # Apple Color Emoji only supports specific sizes; 137 is safe and we resize.
    glyph_img_size = int(size * 0.62)
    if font_path:
        try:
            font = ImageFont.truetype(font_path, 137)
            tmp = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(tmp)
            tdraw.text((80, 80), glyph, font=font, anchor="mm", embedded_color=True)
            tmp = tmp.resize((glyph_img_size, glyph_img_size), Image.LANCZOS)
            offset = ((size - glyph_img_size) // 2, (size - glyph_img_size) // 2)
            img.paste(tmp, offset, tmp)
            return img
        except Exception as e:
            print(f"  emoji font failed ({e}), falling back to plain shape")

    # Fallback: draw a white circle so the icon still looks deliberate.
    pad = int(size * 0.25)
    draw.ellipse([(pad, pad), (size - pad, size - pad)], fill="white")
    return img


def main():
    for slug, bg, glyph in GAMES:
        for size in SIZES:
            img = make_icon(slug, bg, glyph, size)
            out = ICON_DIR / f"{slug}-{size}.png"
            img.save(out, "PNG")
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
