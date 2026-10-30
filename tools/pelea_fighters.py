"""Build the Pelea de Papel fighters from the kids' drawing packs.

Each pack (a folder or .zip, e.g. luchador-03-mikati.zip) holds:
  luchador.json      sheet data: name, stats, moves, pieces and their anchor points
  piezas/*.png       each body piece cut out on a transparent background

For every fighter this writes, under games/pelea/fighters/<slug>/:
  one PNG per piece, with a white paper-cut border added and the colors
  reduced so the files stay small,
and rewrites games/pelea/fighters.js with the data the game reads (anchor
points are moved to match the bordered PNGs). The artists' names and the
reference sheets are left out on purpose.

    python3 tools/pelea_fighters.py path/to/luchador-01-romboman.zip path/to/...

Pass every pack each time: fighters.js is rebuilt from the packs given.
A new fighter also needs its moves added in games/pelea.html (see MOVES).
Then add its PNGs to CORE_ASSETS in sw.js and bump CACHE_VERSION.
"""
import io
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "games" / "pelea" / "fighters"
OUT_JS = ROOT / "games" / "pelea" / "fighters.js"

BORDER = 9            # paper border width, in piece pixels
PAPER = (251, 247, 238)
KEEP = ["especialidad", "frase_victoria", "poderes", "historia", "movimientos", "colores"]


def slugify(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def read_pack(path):
    """Returns (data, {relative path: bytes}) for a pack folder or zip."""
    path = Path(path)
    files = {}
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if not n.endswith("/"):
                    files[n.split("/", 1)[1] if "/" in n else n] = z.read(n)
    else:
        for f in path.rglob("*"):
            if f.is_file():
                files[f.relative_to(path).as_posix()] = f.read_bytes()
    return json.loads(files["luchador.json"]), files


def alpha_of(img):
    return np.asarray(img.getchannel("A"), dtype=np.uint8)


def body_points(a, anchors):
    """Neck (top of the body above the shoulders) and pelvis (between the hips)."""
    h = a.shape[0]
    sx = (anchors["hombro_izq"]["x"] + anchors["hombro_der"]["x"]) / 2
    cols = a[:, max(0, int(sx) - 6):int(sx) + 6]
    rows = np.where(cols.max(axis=1) > 128)[0]
    top = rows.min() if len(rows) else 0
    neck = {"x": sx, "y": top + 0.03 * h}
    pelvis = {"x": (anchors["cadera_izq"]["x"] + anchors["cadera_der"]["x"]) / 2,
              "y": (anchors["cadera_izq"]["y"] + anchors["cadera_der"]["y"]) / 2}
    return neck, pelvis


def limb_end(a):
    """Where the hand or foot goes: the middle of the limb's bottom, a bit up."""
    h = a.shape[0]
    rows = np.where(a.max(axis=1) > 128)[0]
    bottom = rows.max()
    band = a[int(bottom - 0.08 * h):bottom + 1]
    xs = np.where(band.max(axis=0) > 128)[0]
    return {"x": float(xs.mean()), "y": bottom - 0.06 * h}


def bordered(img):
    """Adds the white paper-cut edge. Returns the new image and the (dx, dy)
    shift applied to the original pixels."""
    pad = BORDER + 4
    w, h = img.size
    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    canvas.paste(img, (pad, pad))
    # Blur the silhouette and cut it at a low level: a rounded outward edge.
    solid = canvas.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    blur = np.asarray(solid.filter(ImageFilter.GaussianBlur(BORDER * 0.55)), dtype=np.float32)
    edge = np.clip((blur - 8) * 6, 0, 255).astype(np.uint8)
    paper = Image.new("RGBA", canvas.size, PAPER + (0,))
    paper.putalpha(Image.fromarray(edge))
    out = Image.alpha_composite(paper, canvas)
    l, t, r, b = out.getbbox()
    return out.crop((l, t, r, b)), (pad - l, pad - t)


def shift(p, d):
    return {"x": round(p["x"] + d[0], 1), "y": round(p["y"] + d[1], 1)}


def build(pack_path):
    data, files = read_pack(pack_path)
    slug = slugify(data["nombre"])
    out_dir = OUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()

    pieces = {}
    for name, info in data["piezas"].items():
        img = Image.open(io.BytesIO(files[info["archivo"]])).convert("RGBA")
        a = alpha_of(img)
        anchors = {k: {"x": v["x"], "y": v["y"]} for k, v in info["anclajes"].items()}
        if name == "cuerpo":
            anchors["cuello"], anchors["pelvis"] = body_points(a, anchors)
        if name.startswith(("brazo", "pierna")):
            anchors["fin"] = limb_end(a)
        out, d = bordered(img)
        out = out.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        out.save(out_dir / f"{name}.png", optimize=True)
        pieces[name] = {
            "src": f"pelea/fighters/{slug}/{name}.png",
            "w": out.width,
            "h": out.height,
            "anchors": {k: shift(v, d) for k, v in anchors.items()},
        }

    fighter = {"id": slug, "n": data["id"], "nombre": data["nombre"]}
    for k in KEEP:
        if k in data:
            fighter[k] = data[k]
    fighter.get("poderes", {}).pop("_nota", None)
    fighter["piezas"] = pieces
    return fighter


def main(paths):
    if not paths:
        sys.exit(__doc__)
    fighters = sorted((build(p) for p in paths), key=lambda f: f["n"])
    body = json.dumps(fighters, ensure_ascii=False, indent=1)
    OUT_JS.write_text(
        "// Generated by tools/pelea_fighters.py from the kids' drawing packs. Do not edit by hand.\n"
        f"window.PELEA_FIGHTERS = {body};\n",
        encoding="utf-8",
    )
    for f in fighters:
        print(f"{f['nombre']}: {len(f['piezas'])} pieces")
    print(f"wrote {OUT_JS.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
