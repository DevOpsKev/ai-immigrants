#!/usr/bin/env python3
"""
AI IMMIGRANTS — back cover generator
Outputs: ai-immigrants-back-cover.png  (1575x2400 @ 300dpi, matches the front)
         ai-immigrants-back-cover.svg  (vector; type as outlines, photo embedded)

Same design system as the front cover, tokens taken from the book site:
  --bg #13161B  --line #242932  --ink #D4D8DF  --ink-2 #9EA6B2
  --ink-3 #7B8390  --accent #E05243
  --display Archivo Black   --body IBM Plex Sans   --mono IBM Plex Mono
Site rules honoured: .pull (2px accent left rule) for the opening hook,
h2 display caps for the closing question, hairline rules, zero radius,
body copy at --ink-2, small print at --ink-3.

Copy is reproduced verbatim from the existing back cover.
The lower band is left clear for KDP's barcode.

Fonts (SIL OFL) — expected in ./fonts/:
  base=https://raw.githubusercontent.com/google/fonts/main
  curl -LO $base/ofl/archivoblack/ArchivoBlack-Regular.ttf
  curl -LO $base/ofl/ibmplexmono/IBMPlexMono-Medium.ttf
  curl -LO "$base/ofl/ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf"
  # then instantiate wght 400 / 600 statics with fontTools.varLib.instancer

Requires: pillow, fonttools, numpy
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import numpy as np, base64, io

# ── CANVAS ───────────────────────────────────────────────────────────
W, H, DPI = 1575, 2400, 300
M    = 132
CW   = W - 2 * M                    # measure = 1311
HAIR = 3

# ── TOKENS ───────────────────────────────────────────────────────────
BG     = (0x13, 0x16, 0x1B)
LINE   = (0x24, 0x29, 0x32)
INK    = (0xD4, 0xD8, 0xDF)
INK2   = (0x9E, 0xA6, 0xB2)
INK3   = (0x7B, 0x83, 0x90)
ACCENT = (0xE0, 0x52, 0x43)
hx = lambda c: "#%02X%02X%02X" % c

DISPLAY  = "fonts/ArchivoBlack-Regular.ttf"
BODY     = "fonts/IBMPlexSans-Regular.ttf"
BODY_SB  = "fonts/IBMPlexSans-SemiBold.ttf"
MONO     = "fonts/IBMPlexMono-Regular.ttf"
PHOTO    = "/mnt/user-data/uploads/kevin.jpg"

# ── COPY (verbatim from the existing back cover) ─────────────────────
HOOK  = "They've arrived\u2014uninvited, unstoppable, and already calling the shots."
PARAS = [
    "Artificial intelligence isn't just another technology; it's a new kind of "
    "immigrant\u2014one that doesn't sleep, doesn't eat, and learns faster than we do.",

    "In this provocative debut, Kevin Ryan unpacks the cultural, economic, and moral "
    "upheaval unleashed by intelligent machines. Drawing parallels between today's "
    "algorithms and yesterday's immigrants, AI Immigrants explores who wins, who loses, "
    "and what it really means to stay human in an automated age.",

    "From deep-fake politics to data colonialism, from algorithmic landlords to digital "
    "day-labourers, Ryan's narrative nonfiction blends insight, wit, and urgency. It's "
    "part social commentary, part survival guide\u2014and a manifesto for keeping humanity "
    "indispensable.",

    "Accessible, sharp, and deeply human, this book asks the question no algorithm can "
    "answer:",
]
PUNCH = "Who owns the future?"
IMPRINT = "DEL PRESS"
BIO   = ("Kevin Ryan has spent thirty years making complex technology work in production "
         "\u2014 from CERN and the Financial Times to Nestl\u00e9 and NatWest. He's been early "
         "to every wave, from XP in the nineties to AI-native engineering now. Based "
         "between London and Budapest, which means he's an immigrant too.")

# ── LAYOUT SPEC ──────────────────────────────────────────────────────
SEC_RULE     = 286                  # .sec { border-top }, echoes the front cover
CONTENT_TOP  = 372
CONTENT_END  = 1950                 # below this: clear band for KDP's barcode
PULL_BORDER  = 6                    # .pull border-left 2px
PULL_INDENT  = 72                   # .pull padding-left 24px
PHOTO_SIZE   = 300
PHOTO_GAP    = 60
IMPRINT_S    = 34                   # .mono: tracked caps, --ink-3
IMPRINT_TOP  = 2150                 # same baseline as "Kevin Ryan" on the front,
                                    # kept left so KDP's barcode block stays clear
PHOTO_SHIFT  = 150                  # crop window offset from the top of the source.
                                    # The head is taller than the source is wide, so a
                                    # square can't hold both hairline and jaw: this
                                    # trades a little off the hair to clear the chin.

_faces = {}


def face(path):
    if path not in _faces:
        tt = TTFont(path)
        _faces[path] = (tt, tt.getGlyphSet(), tt.getBestCmap(), tt["head"].unitsPerEm)
    return _faces[path]


def wrap(text, path, size, max_w):
    f = ImageFont.truetype(path, size)
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def line_layout(text, path, size, track_em=0.0):
    """Glyph outlines + tight ink box for one line, in final pixel units."""
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
    if x0 == float("inf"):
        x0 = y0 = x1 = y1 = 0.0
    return {"glyphs": glyphs, "scale": s, "size": size, "text": text, "path": path,
            "track": tracking, "box": (x0, y0, x1, y1), "w": x1 - x0, "h": y1 - y0}


def block_height(S):
    """Total height of the composed text column at body size S."""
    hook_s, punch_s, bio_s = round(S * 1.42), round(S * 1.78), round(S * 0.80)
    h = len(wrap(HOOK, BODY_SB, hook_s, CW - PULL_INDENT)) * hook_s * 1.24
    h += S * 1.55
    for i, p in enumerate(PARAS):
        h += len(wrap(p, BODY, S, CW)) * S * 1.55
        if i < len(PARAS) - 1:
            h += S * 0.85
    h += S * 1.45 + punch_s * 1.0 + S * 1.35        # gap, punch, gap
    h += HAIR + S * 0.95                            # ticked rule + gap
    bio_h = len(wrap(BIO, BODY, bio_s, CW - PHOTO_SIZE - PHOTO_GAP)) * bio_s * 1.5
    return h + max(PHOTO_SIZE, bio_h)


# largest body size that keeps the whole column inside the content area
S = max(s for s in range(18, 72) if block_height(s) <= CONTENT_END - CONTENT_TOP)
HOOK_S, PUNCH_S, BIO_S = round(S * 1.42), round(S * 1.78), round(S * 0.80)

# ── COMPOSE ──────────────────────────────────────────────────────────
draw_ops = []      # (line_layout, colour, x, ink_top)
rects    = [(M, SEC_RULE, W - M, SEC_RULE + HAIR, LINE)]

y = CONTENT_TOP
hook_lines = wrap(HOOK, BODY_SB, HOOK_S, CW - PULL_INDENT)
hook_top = y
for ln in hook_lines:
    draw_ops.append((line_layout(ln, BODY_SB, HOOK_S), INK, M + PULL_INDENT, y))
    y += HOOK_S * 1.24
rects.append((M, hook_top - HOOK_S * 0.18, M + PULL_BORDER, y - HOOK_S * 0.10, ACCENT))

y += S * 1.55
for i, p in enumerate(PARAS):
    for ln in wrap(p, BODY, S, CW):
        draw_ops.append((line_layout(ln, BODY, S), INK2, M, y))
        y += S * 1.55
    if i < len(PARAS) - 1:
        y += S * 0.85

y += S * 1.45
punch = line_layout(PUNCH.upper(), DISPLAY, PUNCH_S, -0.025)
draw_ops.append((punch, ACCENT, M, y))
y += punch["h"] + S * 1.35

rule_y = y
rects.append((M, rule_y, W - M, rule_y + HAIR, LINE))
rects.append((M, rule_y, M + 108, rule_y + HAIR, ACCENT))   # tick, as on the front
y += HAIR + S * 0.95

photo_top = y
bio_x = M + PHOTO_SIZE + PHOTO_GAP
bio_lines = wrap(BIO, BODY, BIO_S, CW - PHOTO_SIZE - PHOTO_GAP)
bio_h = len(bio_lines) * BIO_S * 1.5
by = y + max(0, (PHOTO_SIZE - bio_h) / 2) + BIO_S * 0.22   # optically centred on the photo
for ln in bio_lines:
    draw_ops.append((line_layout(ln, BODY, BIO_S), INK3, bio_x, by))
    by += BIO_S * 1.5

# imprint, bottom left — .mono treatment, clear of the barcode block
draw_ops.append((line_layout(IMPRINT, MONO, IMPRINT_S, 0.14), INK3, M, IMPRINT_TOP))

# ── AUTHOR PHOTO: square crop, graded to sit in the palette ──────────
src = Image.open(PHOTO).convert("RGB")
side = min(src.size)
left = (src.width - side) // 2
top  = min(PHOTO_SHIFT, src.height - side)
photo = src.crop((left, top, left + side, top + side)).resize(
    (PHOTO_SIZE, PHOTO_SIZE), Image.LANCZOS)
photo = ImageEnhance.Color(photo).enhance(0.80)      # ease the saturation
photo = ImageEnhance.Brightness(photo).enhance(0.94)

# ── PNG ──────────────────────────────────────────────────────────────
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
for x0, y0, x1, y1, col in rects:
    d.rectangle([x0, round(y0), x1 - 1, round(y1) - 1], fill=col)

img.paste(photo, (M, round(photo_top)))
d.rectangle([M, round(photo_top), M + PHOTO_SIZE - 1, round(photo_top) + PHOTO_SIZE - 1],
            outline=LINE, width=HAIR)

for ln, col, x, top in draw_ops:
    font = ImageFont.truetype(ln["path"], ln["size"])
    layer = Image.new("RGBA", (W * 2, ln["size"] * 4), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    pen, base = float(W // 2), ln["size"] * 3
    for i, ch in enumerate(ln["text"]):
        ld.text((pen, base), ch, font=font, fill=col + (255,), anchor="ls")
        pen += (font.getlength(ln["text"][: i + 1]) - font.getlength(ln["text"][:i])) + ln["track"]
    bb = layer.getbbox()
    if bb:
        crop = layer.crop(bb)
        img.paste(crop, (round(x), round(top)), crop)

a = np.asarray(img).astype(np.int16)
a += np.random.default_rng(7).integers(-2, 3, size=a.shape, dtype=np.int16)
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(
    "ai-immigrants-back-cover.png", dpi=(DPI, DPI))

# ── SVG ──────────────────────────────────────────────────────────────
buf = io.BytesIO(); photo.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()

out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="{hx(BG)}"/>']
for x0, y0, x1, y1, col in rects:
    out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" '
               f'height="{y1-y0:.1f}" fill="{hx(col)}"/>')
out.append(f'<image x="{M}" y="{photo_top:.1f}" width="{PHOTO_SIZE}" height="{PHOTO_SIZE}" '
           f'xlink:href="data:image/png;base64,{b64}"/>')
out.append(f'<rect x="{M+HAIR/2}" y="{photo_top+HAIR/2:.1f}" width="{PHOTO_SIZE-HAIR}" '
           f'height="{PHOTO_SIZE-HAIR}" fill="none" stroke="{hx(LINE)}" stroke-width="{HAIR}"/>')

for ln, col, x, top in draw_ops:
    bx0, by0, _, _ = ln["box"]
    tx, ty, s = x - bx0, top - by0, ln["scale"]
    out.append(f'<g fill="{hx(col)}" transform="translate({tx:.2f} {ty:.2f})">')
    for dcmd, pen in ln["glyphs"]:
        if dcmd:
            out.append(f'<path transform="translate({pen:.2f} 0) scale({s:.6f} {-s:.6f})" d="{dcmd}"/>')
    out.append("</g>")
out.append("</svg>")
open("ai-immigrants-back-cover.svg", "w").write("\n".join(out))

print(f"body {S}px ({S/DPI*72:.1f}pt)   hook {HOOK_S}   punch {PUNCH_S}   bio {BIO_S}")
print(f"column {CONTENT_TOP} -> {by - BIO_S*0.5:.0f}  (limit {CONTENT_END})")
print(f"photo y {photo_top:.0f}-{photo_top+PHOTO_SIZE:.0f}   clear band below {max(by, photo_top+PHOTO_SIZE):.0f}")
