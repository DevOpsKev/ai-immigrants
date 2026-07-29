#!/usr/bin/env python3
"""
AI IMMIGRANTS — full paperback wrap for KDP
Outputs: ai-immigrants-full-cover.pdf   <- the file you upload to KDP
         ai-immigrants-full-cover.png   <- flattened preview
         ai-immigrants-full-cover.svg   <- editable source

Assembles the approved front and back panel SVGs into one wrap and adds the
spine, so the panels are byte-for-byte the artwork already signed off.

Geometry (KDP paperback):
  full width  = bleed + back trim + spine + front trim + bleed
  full height = bleed + trim height + bleed
  spine       = page count x paper thickness
Barcode: KDP prints it bottom-right of the back cover; that area is left clear.

Run generate-front-cover.py and generate-back-cover.py first.
Requires: pillow, fonttools, numpy, cairosvg
"""
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import numpy as np, cairosvg, io

# ── BOOK SPEC ────────────────────────────────────────────────────────
PAGE_COUNT = 212
PAPER      = "white"        # white | cream | premium_color | standard_color
TRIM_W_IN, TRIM_H_IN = 5.25, 8.0
BLEED_IN   = 0.125
DPI        = 300

THICKNESS = {"white": 0.002252, "cream": 0.0025,
             "premium_color": 0.002347, "standard_color": 0.002252}

SPINE_IN = PAGE_COUNT * THICKNESS[PAPER]
TRIM_W, TRIM_H = TRIM_W_IN * DPI, TRIM_H_IN * DPI          # 1575 x 2400
BLEED  = BLEED_IN * DPI                                     # 37.5
SPINE  = SPINE_IN * DPI
W = 2 * TRIM_W + SPINE + 2 * BLEED
H = TRIM_H + 2 * BLEED

BACK_X  = BLEED
SPINE_X = BLEED + TRIM_W
FRONT_X = SPINE_X + SPINE
SPINE_C = SPINE_X + SPINE / 2

# ── TOKENS ───────────────────────────────────────────────────────────
BG     = (0x13, 0x16, 0x1B)
INK    = (0xD4, 0xD8, 0xDF)
INK3   = (0x7B, 0x83, 0x90)
ACCENT = (0xE0, 0x52, 0x43)
hx = lambda c: "#%02X%02X%02X" % c

DISPLAY = "fonts/ArchivoBlack-Regular.ttf"
MONO    = "fonts/IBMPlexMono-Regular.ttf"

# ── SPINE SPEC ───────────────────────────────────────────────────────
# KDP asks for 0.0625" clear each side of the spine; type is kept well inside.
SPINE_SAFE  = SPINE - 2 * 0.0625 * DPI
TITLE_RATIO = 0.54          # cap height as a fraction of spine width
AUTH_RATIO  = 0.26
IMPR_RATIO  = 0.17
TITLE_Y     = 430           # distance down the spine, from the trim top
GAP_TITLE   = 150
IMPRINT_END = 2400 - 200    # imprint sits this far up from the trim foot

TITLE, AUTHOR, IMPRINT = "AI IMMIGRANTS", "KEVIN RYAN", "DEL PRESS"
SPLIT = 3                   # "AI " stays ink, "IMMIGRANTS" goes accent

_faces = {}


def face(path):
    if path not in _faces:
        tt = TTFont(path)
        _faces[path] = (tt, tt.getGlyphSet(), tt.getBestCmap(), tt["head"].unitsPerEm)
    return _faces[path]


def line(text, path, size, track_em=0.0):
    from PIL import ImageFont
    tt, gs, cmap, upem = face(path)
    s, pil = size / upem, ImageFont.truetype(path, size)
    tracking = track_em * size
    glyphs, pen = [], 0.0
    x0 = y0 = float("inf"); x1 = y1 = float("-inf")
    for i, ch in enumerate(text):
        g = cmap.get(ord(ch))
        if g:
            sp = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
            gs[g].draw(sp)
            bp = BoundsPen(gs); gs[g].draw(bp)
            if bp.bounds:
                gx0, gy0, gx1, gy1 = bp.bounds
                x0 = min(x0, pen + gx0 * s); x1 = max(x1, pen + gx1 * s)
                y0 = min(y0, -gy1 * s);      y1 = max(y1, -gy0 * s)
            glyphs.append((sp.getCommands(), pen))
        pen += (pil.getlength(text[: i + 1]) - pil.getlength(text[:i])) + tracking
    return {"glyphs": glyphs, "scale": s, "box": (x0, y0, x1, y1),
            "w": x1 - x0, "h": y1 - y0}


def fit_cap(text, path, cap, track_em=0.0):
    """Largest size whose ink height fits cap."""
    lo, hi, best = 6, 400, None
    while lo <= hi:
        mid = (lo + hi) // 2
        ln = line(text, path, mid, track_em)
        if ln["h"] <= cap:
            best, lo = ln, mid + 1
        else:
            hi = mid - 1
    return best


def rotated(ln, y_start, fill, first=None):
    """Emit a spine line rotated to read top-to-bottom, centred across the spine.
    `first` splits the glyph run so the title can carry two colours."""
    x0, y0, _, _ = ln["box"]
    t = (f'translate({SPINE_C + ln["h"]/2:.3f} {y_start:.3f}) rotate(90) '
         f'translate({-x0:.3f} {-y0:.3f})')
    runs = [(ln["glyphs"], fill)] if first is None else \
           [(ln["glyphs"][:first], fill[0]), (ln["glyphs"][first:], fill[1])]
    out = []
    for glyphs, col in runs:
        out.append(f'<g fill="{hx(col)}" transform="{t}">')
        for d, pen in glyphs:
            if d:
                out.append(f'<path transform="translate({pen:.2f} 0) '
                           f'scale({ln["scale"]:.6f} {-ln["scale"]:.6f})" d="{d}"/>')
        out.append("</g>")
    return out


def inner(path):
    """Strip the outer <svg> wrapper off a panel file."""
    s = open(path).read()
    return s[s.index(">", s.index("<svg")) + 1: s.rindex("</svg>")]


# ── ASSEMBLE ─────────────────────────────────────────────────────────
title = fit_cap(TITLE,   DISPLAY, SPINE * TITLE_RATIO, -0.03)
auth  = fit_cap(AUTHOR,  MONO,    SPINE * AUTH_RATIO,   0.12)
impr  = fit_cap(IMPRINT, MONO,    SPINE * IMPR_RATIO,   0.14)

title_y = BLEED + TITLE_Y
auth_y  = title_y + title["w"] + GAP_TITLE
impr_y  = BLEED + IMPRINT_END - impr["w"]

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{W/DPI:.4f}in" height="{H/DPI:.4f}in" viewBox="0 0 {W:.4f} {H:.4f}">',
       f'<rect width="{W:.4f}" height="{H:.4f}" fill="{hx(BG)}"/>',
       f'<g transform="translate({BACK_X:.3f} {BLEED:.3f})">', inner("ai-immigrants-back-cover.svg"), '</g>',
       f'<g transform="translate({FRONT_X:.3f} {BLEED:.3f})">', inner("ai-immigrants-front-cover.svg"), '</g>']
svg += rotated(title, title_y, (INK, ACCENT), first=SPLIT)
svg += rotated(auth,  auth_y,  INK)
svg += rotated(impr,  impr_y,  INK3)
svg.append("</svg>")
src = "\n".join(svg)
open("ai-immigrants-full-cover.svg", "w").write(src)

# ── PDF (what KDP wants: one file, back + spine + front) ─────────────
cairosvg.svg2pdf(bytestring=src.encode(), write_to="ai-immigrants-full-cover.pdf")

# ── PNG preview, with the print grain the panels carry ───────────────
png = cairosvg.svg2png(bytestring=src.encode(),
                       output_width=round(W), output_height=round(H))
img = Image.open(io.BytesIO(png)).convert("RGB")
a = np.asarray(img).astype(np.int16)
a += np.random.default_rng(7).integers(-2, 3, size=a.shape, dtype=np.int16)
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(
    "ai-immigrants-full-cover.png", dpi=(DPI, DPI))

print(f"{PAGE_COUNT} pages on {PAPER} paper")
print(f"spine      {SPINE_IN:.4f} in  ({SPINE:.1f} px)")
print(f"full cover {W/DPI:.4f} x {H/DPI:.4f} in  ({round(W)} x {round(H)} px @ {DPI}dpi)")
print(f"panels     back x {BACK_X:.1f}-{SPINE_X:.1f} | spine {SPINE_X:.1f}-{FRONT_X:.1f} "
      f"| front {FRONT_X:.1f}-{FRONT_X+TRIM_W:.1f}")
print(f"spine type title cap {title['h']:.1f}px, author {auth['h']:.1f}, imprint {impr['h']:.1f} "
      f"(safe {SPINE_SAFE:.1f}px)")
print(f"spine runs title y {title_y:.0f}-{title_y+title['w']:.0f}, "
      f"author {auth_y:.0f}-{auth_y+auth['w']:.0f}, imprint {impr_y:.0f}-{impr_y+impr['w']:.0f}")
