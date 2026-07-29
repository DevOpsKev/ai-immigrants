#!/usr/bin/env python3
"""
AI IMMIGRANTS — front cover generator
Outputs: ai-immigrants-front-cover.png  (1575x2400 @ 300dpi)
         ai-immigrants-front-cover.svg  (vector, glyphs as outlines)

Design tokens taken verbatim from the book site's dark theme:
  --bg #13161B  --line #242932  --ink #D4D8DF  --ink-2 #9EA6B2
  --accent #E05243 (signal red)   --hot #7E1D1D (dried blood, display only)
  --display Archivo Black   --mono IBM Plex Mono
Site rules honoured: h1 last block = accent, .shout i = hot, hairline rules,
zero radius, uppercase display, negative display tracking.

Type is fitted by measuring real glyph outlines, so IMMIGRANTS justifies flush
to the measure and AI is set to a fixed fraction of it.

Fonts (SIL OFL) — expected in ./fonts/, fetch with:
  base=https://raw.githubusercontent.com/google/fonts/main
  curl -LO $base/ofl/archivoblack/ArchivoBlack-Regular.ttf
  curl -LO $base/ofl/ibmplexmono/IBMPlexMono-Medium.ttf

Requires: pillow, fonttools, numpy
"""
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import numpy as np

# ── CANVAS ───────────────────────────────────────────────────────────
W, H, DPI = 1575, 2400, 300
M    = 132                    # side margin
CW   = W - 2 * M              # measure = 1311
HAIR = 3                      # hairline at 300dpi (~0.7pt)

# ── TOKENS ───────────────────────────────────────────────────────────
BG     = (0x13, 0x16, 0x1B)
LINE   = (0x24, 0x29, 0x32)
INK    = (0xD4, 0xD8, 0xDF)
INK2   = (0x9E, 0xA6, 0xB2)
ACCENT = (0xE0, 0x52, 0x43)
HOT    = (0x7E, 0x1D, 0x1D)

hx = lambda c: "#%02X%02X%02X" % c

DISPLAY = "fonts/ArchivoBlack-Regular.ttf"
MONO    = "fonts/IBMPlexMono-Medium.ttf"

# ── TYPE SPEC ────────────────────────────────────────────────────────
TRACK_H1 = -0.03              # h1 letter-spacing
TRACK_SH = -0.025             # .shout letter-spacing
AI_MEASURE = 0.96             # AI sits just inside IMMIGRANTS' width
SHOUT_MEASURE = 0.74

TITLE_TOP = 430
SEC_RULE  = 286               # .sec { border-top }
BOT_RULE  = 2072              # ticked rule, per the manifest seam
STACK_K   = 0.30              # title stack gap, x IMMIGRANTS cap height
SHOUT_GAP = 132
AUTHOR_GAP = 78

_cache = {}


def face(path):
    if path not in _cache:
        tt = TTFont(path)
        _cache[path] = (tt, tt.getGlyphSet(), tt.getBestCmap(),
                        tt["head"].unitsPerEm)
    return _cache[path]


def layout(text, path, size, track_em):
    """Lay out a tracked line. Returns per-glyph outlines plus tight ink box,
    all in final pixel units. Advances come from PIL so PNG and SVG agree."""
    tt, gs, cmap, upem = face(path)
    s = size / upem
    pil = ImageFont.truetype(path, size)
    tracking = track_em * size

    glyphs, pen = [], 0.0
    x0 = y0 = float("inf")
    x1 = y1 = float("-inf")
    for i, ch in enumerate(text):
        g = cmap[ord(ch)]
        sp = SVGPathPen(gs)
        gs[g].draw(sp)
        bp = BoundsPen(gs)
        gs[g].draw(bp)
        if bp.bounds:
            gx0, gy0, gx1, gy1 = bp.bounds
            x0 = min(x0, pen + gx0 * s); x1 = max(x1, pen + gx1 * s)
            y0 = min(y0, -gy1 * s);      y1 = max(y1, -gy0 * s)
        glyphs.append((sp.getCommands(), pen))
        pen += (pil.getlength(text[: i + 1]) - pil.getlength(text[:i])) + tracking
    return {"glyphs": glyphs, "scale": s, "size": size, "text": text,
            "path": path, "track": tracking,
            "box": (x0, y0, x1, y1), "w": x1 - x0, "h": y1 - y0}


def fit(text, path, target_w, track_em, lo=10, hi=2400):
    """Largest size whose outline ink width fits target_w."""
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        ln = layout(text, path, mid, track_em)
        if ln["w"] <= target_w:
            best, lo = ln, mid + 1
        else:
            hi = mid - 1
    return best


# ── COMPOSE ──────────────────────────────────────────────────────────
imm   = fit("IMMIGRANTS", DISPLAY, CW, TRACK_H1)
ai    = fit("AI", DISPLAY, int(CW * AI_MEASURE), TRACK_H1)
L1, L2 = '"THE BLOODY ALGOS', 'ARE HERE!"'
sh1   = fit(L1, DISPLAY, int(CW * SHOUT_MEASURE), TRACK_SH)
sh2   = layout(L2, DISPLAY, sh1["size"], TRACK_SH)
au    = layout("Kevin Ryan", MONO, 52, 0.02)

imm_top   = TITLE_TOP + ai["h"] + STACK_K * imm["h"]
shout_top = imm_top + imm["h"] + SHOUT_GAP
shout2_top = shout_top + sh1["size"]          # .shout line-height 1
au_top    = BOT_RULE + AUTHOR_GAP

# (line, colour, ink-top y) in draw order
BLOCKS = [
    (ai,  INK,    TITLE_TOP),
    (imm, ACCENT, imm_top),
    (sh1, INK,    shout_top),
    (sh2, HOT,    shout2_top),
    (au,  INK2,   au_top),
]

RULES = [                                      # x0, y0, x1, y1, colour
    (M, SEC_RULE, W - M, SEC_RULE + HAIR, LINE),
    (M, BOT_RULE, W - M, BOT_RULE + HAIR, LINE),
    (M, BOT_RULE, M + 108, BOT_RULE + HAIR, ACCENT),
]

# ── PNG ──────────────────────────────────────────────────────────────
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
for x0, y0, x1, y1, col in RULES:
    d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=col)

for ln, col, top in BLOCKS:
    text, font = ln["text"], ImageFont.truetype(ln["path"], ln["size"])
    layer = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    pen, base = float(W // 2), H // 2
    for i, ch in enumerate(text):
        ld.text((pen, base), ch, font=font, fill=col + (255,), anchor="ls")
        pen += (font.getlength(text[: i + 1]) - font.getlength(text[:i])) + ln["track"]
    crop = layer.crop(layer.getbbox())        # paste by true ink box -> flush left
    img.paste(crop, (M, int(round(top))), crop)

# barely-there tonal noise so the flat ground doesn't band in print
a = np.asarray(img).astype(np.int16)
a += np.random.default_rng(7).integers(-2, 3, size=a.shape, dtype=np.int16)
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(
    "ai-immigrants-front-cover.png", dpi=(DPI, DPI))

# ── SVG ──────────────────────────────────────────────────────────────
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="{hx(BG)}"/>']
for x0, y0, x1, y1, col in RULES:
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{hx(col)}"/>')

for ln, col, top in BLOCKS:
    bx0, by0, _, _ = ln["box"]
    tx, ty, s = M - bx0, top - by0, ln["scale"]
    out.append(f'<g fill="{hx(col)}" transform="translate({tx:.3f} {ty:.3f})">')
    for dcmd, pen in ln["glyphs"]:
        if dcmd:
            out.append(f'<path transform="translate({pen:.3f} 0) scale({s:.6f} {-s:.6f})" d="{dcmd}"/>')
    out.append("</g>")
out.append("</svg>")
open("ai-immigrants-front-cover.svg", "w").write("\n".join(out))

# ── REPORT ───────────────────────────────────────────────────────────
print(f"IMMIGRANTS  size {imm['size']:4}  w {imm['w']:7.1f}  y {imm_top:.0f}-{imm_top+imm['h']:.0f}")
print(f"AI          size {ai['size']:4}  w {ai['w']:7.1f}  y {TITLE_TOP}-{TITLE_TOP+ai['h']:.0f}"
      f"   ({ai['w']/imm['w']*100:.1f}% of IMMIGRANTS)")
print(f"SHOUT       size {sh1['size']:4}  w {sh1['w']:7.1f}  y {shout_top:.0f}-{shout2_top+sh2['h']:.0f}")
print(f"void before bottom rule: {BOT_RULE - (shout2_top + sh2['h']):.0f}px")
