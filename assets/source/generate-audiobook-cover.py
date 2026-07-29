#!/usr/bin/env python3
"""
AI IMMIGRANTS — square cover art for Spotify (audiobook / podcast)
Outputs: ai-immigrants-audiobook-cover.png  (3000x3000, sRGB, no profile)
         ai-immigrants-audiobook-cover.svg

Spotify wants square, 2400x2400 minimum, PNG/TIF/JPG, no borders or
letterboxing, sRGB with no embedded colour profile. 3000x3000 clears the
audiobook spec and the podcast spec at once.

Same tokens and lockup as the print covers. Two deliberate differences,
both driven by the square format and by the fact that this art gets shown
as small as ~55px:
  - the shout is set on ONE line, not two. At full measure the two-line
    setting pushes the composition past 3000px tall.
  - no print grain. It is a press nicety, it inflates the PNG well past
    Spotify's 4MB ceiling, and it does nothing on screen.

Fonts (SIL OFL) — expected in ./fonts/:
  base=https://raw.githubusercontent.com/google/fonts/main
  curl -LO $base/ofl/archivoblack/ArchivoBlack-Regular.ttf
  curl -LO $base/ofl/ibmplexmono/IBMPlexMono-Medium.ttf

Requires: pillow, fonttools
"""
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

# ── CANVAS ───────────────────────────────────────────────────────────
S    = 3000                     # square side
M    = 250                      # margin, 8.3% — matches the print covers
CW   = S - 2 * M                # measure = 2500
HAIR = 6                        # hairline, scaled from the print 3px

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
TRACK_H1   = -0.03
TRACK_SH   = -0.025
AI_MEASURE = 0.96               # as approved on the front cover
SHOUT_MEASURE = 0.62
SHOUT = '"THE BLOODY ALGOS ARE HERE!"'
SHOUT_SPLIT = 18                # ".shout i" starts at "ARE HERE!"

TOP        = 300
STACK_K    = 0.30
GAP_SHOUT  = 150
GAP_RULE   = 100
GAP_AUTHOR = 90

_faces = {}


def face(path):
    if path not in _faces:
        tt = TTFont(path)
        _faces[path] = (tt, tt.getGlyphSet(), tt.getBestCmap(), tt["head"].unitsPerEm)
    return _faces[path]


def line(text, path, size, track_em=0.0):
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
    return {"glyphs": glyphs, "scale": s, "size": size, "text": text, "path": path,
            "track": tracking, "box": (x0, y0, x1, y1), "w": x1 - x0, "h": y1 - y0}


def fit(text, path, target_w, track_em, lo=10, hi=2600):
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        ln = line(text, path, mid, track_em)
        if ln["w"] <= target_w:
            best, lo = ln, mid + 1
        else:
            hi = mid - 1
    return best


# ── COMPOSE ──────────────────────────────────────────────────────────
imm   = fit("IMMIGRANTS", DISPLAY, CW, TRACK_H1)
ai    = fit("AI", DISPLAY, int(CW * AI_MEASURE), TRACK_H1)
shout = fit(SHOUT, DISPLAY, int(CW * SHOUT_MEASURE), TRACK_SH)
au    = line("Kevin Ryan", MONO, round(CW * 0.0397), 0.02)

ai_top    = TOP
imm_top   = ai_top + ai["h"] + STACK_K * imm["h"]
shout_top = imm_top + imm["h"] + GAP_SHOUT
rule_y    = shout_top + shout["h"] + GAP_RULE
au_top    = rule_y + HAIR + GAP_AUTHOR

blocks = [(ai, INK, ai_top, None), (imm, ACCENT, imm_top, None),
          (shout, (INK, HOT), shout_top, SHOUT_SPLIT), (au, INK2, au_top, None)]
rects = [(M, rule_y, S - M, rule_y + HAIR, LINE),
         (M, rule_y, M + 206, rule_y + HAIR, ACCENT)]      # the ticked rule

# ── PNG ──────────────────────────────────────────────────────────────
img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
for x0, y0, x1, y1, col in rects:
    d.rectangle([x0, round(y0), x1 - 1, round(y1) - 1], fill=col)

for ln, col, top, split in blocks:
    font = ImageFont.truetype(ln["path"], ln["size"])
    layer = Image.new("RGBA", (S * 2, ln["size"] * 4), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    pen, base = float(S // 2), ln["size"] * 3
    for i, ch in enumerate(ln["text"]):
        fill = col if split is None else (col[0] if i < split else col[1])
        ld.text((pen, base), ch, font=font, fill=fill + (255,), anchor="ls")
        pen += (font.getlength(ln["text"][: i + 1]) - font.getlength(ln["text"][:i])) + ln["track"]
    crop = layer.crop(layer.getbbox())
    img.paste(crop, (M, round(top)), crop)

img.save("ai-immigrants-audiobook-cover.png")     # sRGB, no embedded profile

# ── SVG ──────────────────────────────────────────────────────────────
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">',
       f'<rect width="{S}" height="{S}" fill="{hx(BG)}"/>']
for x0, y0, x1, y1, col in rects:
    out.append(f'<rect x="{x0}" y="{y0:.1f}" width="{x1-x0}" height="{y1-y0}" fill="{hx(col)}"/>')
for ln, col, top, split in blocks:
    bx0, by0, _, _ = ln["box"]
    tx, ty, sc = M - bx0, top - by0, ln["scale"]
    runs = [(ln["glyphs"], col)] if split is None else \
           [(ln["glyphs"][:split], col[0]), (ln["glyphs"][split:], col[1])]
    for glyphs, c in runs:
        out.append(f'<g fill="{hx(c)}" transform="translate({tx:.2f} {ty:.2f})">')
        for dcmd, pen in glyphs:
            if dcmd:
                out.append(f'<path transform="translate({pen:.2f} 0) scale({sc:.6f} {-sc:.6f})" d="{dcmd}"/>')
        out.append("</g>")
out.append("</svg>")
open("ai-immigrants-audiobook-cover.svg", "w").write("\n".join(out))

import os
print(f"canvas {S}x{S}   measure {CW}")
print(f"AI    {ai['w']:.0f}x{ai['h']:.0f}  y {ai_top:.0f}-{ai_top+ai['h']:.0f}  "
      f"({ai['w']/imm['w']*100:.1f}% of IMMIGRANTS)")
print(f"IMM   {imm['w']:.0f}x{imm['h']:.0f}  y {imm_top:.0f}-{imm_top+imm['h']:.0f}")
print(f"shout {shout['w']:.0f}px single line  y {shout_top:.0f}-{shout_top+shout['h']:.0f}")
print(f"rule y {rule_y:.0f}   author y {au_top:.0f}-{au_top+au['h']:.0f}")
print(f"bottom margin {S - (au_top+au['h']):.0f}   PNG {os.path.getsize('ai-immigrants-audiobook-cover.png')/1e6:.2f} MB (limit 4)")
