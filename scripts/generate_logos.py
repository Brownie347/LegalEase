"""Generate Image/Logo.png (dark) and Image/inverseLogo.png (white).

Run from the project root:  python scripts/generate_logos.py
Replace the PNGs with your own branding at any time - the file names are all
the app cares about.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "Image"
S = 4  # supersampling factor for smooth edges

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/times.ttf",
    "/Library/Fonts/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
]


def load_font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def draw_scales(d: ImageDraw.ImageDraw, color, ox=10, oy=10):
    def p(x, y):
        return ((ox + x) * S, (oy + y) * S)

    w = 6 * S
    d.ellipse([*p(93, 27), *p(107, 41)], fill=color)                 # finial
    d.rectangle([*p(97, 40), *p(103, 168)], fill=color)              # pole
    d.rounded_rectangle([*p(58, 168), *p(142, 182)], radius=5 * S, fill=color)  # base
    d.line([p(30, 58), p(170, 58)], fill=color, width=w)             # beam
    for cx in (32, 168):                                             # pans
        d.line([p(cx, 58), p(cx - 22, 108)], fill=color, width=3 * S)
        d.line([p(cx, 58), p(cx + 22, 108)], fill=color, width=3 * S)
        d.pieslice([*p(cx - 26, 84), *p(cx + 26, 136)], 0, 180, fill=color)


def make(color, name):
    W, H = 900, 200
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_scales(d, color)
    d.text((245 * S, 105 * S), "LegalEase", font=load_font(96 * S), fill=color, anchor="lm")
    bbox = img.getbbox()
    pad = 12 * S
    img = img.crop((bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad))
    img = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    img.save(OUT / name)
    print("wrote", OUT / name, img.size)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    make((27, 42, 73, 255), "Logo.png")
    make((255, 255, 255, 255), "inverseLogo.png")
