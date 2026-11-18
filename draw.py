#!/usr/bin/env python3
"""Draw the entry image for make.fun news-image-20261118.

A newspaper front page summarising the world news of Wednesday
18 November 2026, drawn entirely with PIL: crisp rendered text,
no AI-generated imagery, so nothing is garbled.

Run:  python3 draw.py            -> writes entry.png (1024x1024)
      python3 draw.py out.png    -> writes to the given path
"""

import math
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette -----------------------------------------------------------
NAVY = (16, 38, 63)        # masthead, skyline
NAVY2 = (24, 54, 86)
PAPER = (247, 243, 234)    # page background
WHITE = (255, 255, 255)
INK = (22, 22, 22)
GRAY = (88, 84, 76)
DARKGRAY = (64, 60, 54)
RED = (178, 34, 34)        # kickers, accents
GOLD = (212, 160, 23)      # date line
RULE = (203, 194, 176)     # hairlines
CELLBORDER = (214, 206, 188)

FONTS = "/usr/share/fonts/truetype"


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}", size)


SERIF_B = "dejavu/DejaVuSerif-Bold.ttf"
SERIF = "dejavu/DejaVuSerif.ttf"
SANS_B = "dejavu/DejaVuSans-Bold.ttf"
SANS = "dejavu/DejaVuSans.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, fnt, fill, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def star_points(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---- flags (simplified but recognisable) -------------------------------
def flag_usa(d, x, y, w, h):
    stripe = h / 13
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                        fill=(178, 34, 52))
        else:
            d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                        fill=WHITE)
    cw, ch = w * 0.42, stripe * 7
    d.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    for r in range(5):
        for c in range(6):
            sx = x + cw * (0.10 + 0.16 * c)
            sy = y + ch * (0.12 + 0.19 * r)
            d.ellipse([sx - 1.1, sy - 1.1, sx + 1.1, sy + 1.1], fill=WHITE)


def flag_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    r = h * 0.30
    d.ellipse([x + w / 2 - r, y + h / 2 - r, x + w / 2 + r, y + h / 2 + r],
              fill=(188, 0, 45))


def flag_india(d, x, y, w, h):
    third = h / 3
    d.rectangle([x, y, x + w, y + third], fill=(255, 153, 51))
    d.rectangle([x, y + third, x + w, y + 2 * third], fill=WHITE)
    d.rectangle([x, y + 2 * third, x + w, y + h], fill=(19, 136, 8))
    cx, cy, r = x + w / 2, y + h / 2, h * 0.17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(6, 22, 110), width=2)
    for i in range(12):
        a = math.radians(i * 30)
        d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)],
               fill=(6, 22, 110), width=1)


def flag_australia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
    # Union Jack canton, simplified
    cw, ch = w * 0.5, h * 0.5
    d.rectangle([x, y, x + cw, y + ch], fill=(1, 33, 105))
    d.line([x, y, x + cw, y + ch], fill=WHITE, width=4)
    d.line([x + cw, y, x, y + ch], fill=WHITE, width=4)
    d.line([x, y, x + cw, y + ch], fill=(204, 0, 0), width=2)
    d.line([x + cw, y, x, y + ch], fill=(204, 0, 0), width=2)
    d.rectangle([x + cw / 2 - 3, y, x + cw / 2 + 3, y + ch], fill=WHITE)
    d.rectangle([x, y + ch / 2 - 3, x + cw, y + ch / 2 + 3], fill=WHITE)
    d.rectangle([x + cw / 2 - 1, y, x + cw / 2 + 1, y + ch], fill=(204, 0, 0))
    d.rectangle([x, y + ch / 2 - 1, x + cw, y + ch / 2 + 1], fill=(204, 0, 0))
    # big star below the canton
    d.polygon(star_points(x + cw / 2, y + ch + (h - ch) / 2, 9, 3.6, 7),
              fill=WHITE)
    # Southern Cross
    for sx, sy, r in [(0.72, 0.28, 3.5), (0.85, 0.45, 3.0), (0.70, 0.62, 3.0),
                      (0.82, 0.78, 2.5), (0.60, 0.45, 2.0)]:
        d.polygon(star_points(x + w * sx, y + h * sy, r, r * 0.42, 5),
                  fill=WHITE)


def flag_uk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(1, 33, 105))
    d.line([x, y, x + w, y + h], fill=WHITE, width=max(6, h // 6))
    d.line([x + w, y, x, y + h], fill=WHITE, width=max(6, h // 6))
    d.line([x, y, x + w, y + h], fill=(204, 0, 0), width=max(3, h // 12))
    d.line([x + w, y, x, y + h], fill=(204, 0, 0), width=max(3, h // 12))
    d.rectangle([x + w / 2 - h / 10, y, x + w / 2 + h / 10, y + h], fill=WHITE)
    d.rectangle([x, y + h / 2 - h / 10, x + w, y + h / 2 + h / 10], fill=WHITE)
    d.rectangle([x + w / 2 - h / 22, y, x + w / 2 + h / 22, y + h],
                fill=(204, 0, 0))
    d.rectangle([x, y + h / 2 - h / 22, x + w, y + h / 2 + h / 22],
                fill=(204, 0, 0))


# ---- story icons (each draws inside the box x, y, w, h) ----------------
def icon_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 74, 92))
    # dusk sky band
    d.rectangle([x, y, x + w, y + h * 0.45], fill=(94, 112, 132))
    # water
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(30, 48, 66))
    for i in range(6):
        wx = x + 14 + i * (w - 28) / 5
        d.line([wx, y + h * 0.86, wx + 22, y + h * 0.86], fill=(90, 130, 160),
               width=2)
    # bridge deck + towers + cables
    deck = y + h * 0.62
    d.line([x + 8, deck, x + w - 8, deck], fill=(20, 24, 30), width=6)
    for tx in (x + w * 0.28, x + w * 0.72):
        d.rectangle([tx - 5, y + h * 0.18, tx + 5, deck], fill=(20, 24, 30))
    d.arc([x + w * 0.28, y + h * 0.10, x + w * 0.72, y + h * 0.95],
          start=200, end=340, fill=(20, 24, 30), width=3)
    d.line([x + 8, y + h * 0.30, x + w * 0.28, y + h * 0.18],
           fill=(20, 24, 30), width=3)
    d.line([x + w * 0.72, y + h * 0.18, x + w - 8, y + h * 0.30],
           fill=(20, 24, 30), width=3)
    # explosion starburst at mid-span
    ex, ey = x + w * 0.5, deck - 6
    d.polygon(star_points(ex, ey, 34, 12, 9), fill=(255, 170, 0))
    d.polygon(star_points(ex, ey, 22, 8, 9, rot=-70), fill=(255, 230, 120))
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(255, 255, 240))
    # smoke puffs
    for sx, sy, r in [(-38, -34, 9), (-24, -44, 12), (26, -40, 11), (40, -28, 8)]:
        d.ellipse([ex + sx - r, ey + sy - r, ex + sx + r, ey + sy + r],
                  fill=(120, 120, 120))
    # broken deck gap
    d.rectangle([ex - 16, deck - 4, ex + 16, deck + 4], fill=(58, 74, 92))
    d.line([ex - 16, deck + 3, ex - 6, deck + 16], fill=(20, 24, 30), width=3)
    d.line([ex + 16, deck + 3, ex + 6, deck + 16], fill=(20, 24, 30), width=3)


def icon_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 217, 176))
    d.rectangle([x, y, x + w, y + h * 0.62], fill=(168, 200, 220))
    # ground
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(198, 172, 120))
    # radar mast + dish
    bx, by = x + w * 0.30, y + h * 0.78
    d.line([bx, by, bx, by - h * 0.42], fill=(60, 60, 60), width=5)
    d.pieslice([bx - 34, by - h * 0.42 - 40, bx + 34, by - h * 0.42 + 28],
               start=200, end=340, fill=(240, 240, 235))
    d.arc([bx - 34, by - h * 0.42 - 40, bx + 34, by - h * 0.42 + 28],
          start=200, end=340, fill=(60, 60, 60), width=3)
    # sweep beam
    d.polygon([(bx + 8, by - h * 0.42 - 8), (bx + 78, by - h * 0.62),
               (bx + 78, by - h * 0.30)], fill=(120, 220, 130))
    # drones
    for dx, dy, s in [(0.62, 0.22, 1.0), (0.80, 0.38, 0.8), (0.70, 0.12, 0.6)]:
        cx, cy = x + w * dx, y + h * dy
        d.ellipse([cx - 6 * s, cy - 4 * s, cx + 6 * s, cy + 4 * s],
                  fill=(40, 40, 40))
        d.line([cx - 12 * s, cy - 6 * s, cx + 12 * s, cy + 6 * s],
               fill=(40, 40, 40), width=2)
        d.line([cx - 12 * s, cy + 6 * s, cx + 12 * s, cy - 6 * s],
               fill=(40, 40, 40), width=2)
        for px, py in [(-12, -6), (12, 6), (-12, 6), (12, -6)]:
            d.ellipse([cx + px * s - 3, cy + py * s - 1.5,
                       cx + px * s + 3, cy + py * s + 1.5], fill=(90, 90, 90))
    # impact flash on the dish
    d.polygon(star_points(bx + 14, by - h * 0.42 - 6, 13, 5, 8),
              fill=(255, 170, 0))


def icon_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(23, 68, 110))
    cx, cy = x + w * 0.5, y + h * 0.52
    # spiral arms
    for r0, width, col in [(56, 7, (255, 255, 255)), (44, 6, (220, 235, 245)),
                           (31, 6, (255, 255, 255)), (19, 5, (200, 225, 240))]:
        d.arc([cx - r0, cy - r0, cx + r0, cy + r0], start=30 + r0 * 2,
              end=300 + r0 * 2, fill=col, width=width)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(23, 68, 110))
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(255, 255, 255),
              width=2)
    # rain streaks
    for i in range(10):
        rx = x + 10 + i * (w - 20) / 9
        d.line([rx, y + 6, rx - 6, y + 22], fill=(160, 200, 230), width=2)
    # land strip
    d.polygon([(x + w * 0.72, y + h), (x + w, y + h * 0.72),
               (x + w, y + h)], fill=(46, 125, 50))
    d.polygon([(x, y + h), (x + w * 0.24, y + h * 0.84), (x, y + h * 0.84)],
              fill=(46, 125, 50))


def icon_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(9, 26, 16))
    # chip
    cx, cy, s = x + w * 0.30, y + h * 0.52, 30
    for i in range(4):
        px = cx - s + i * (2 * s / 3)
        d.line([px, cy - s - 10, px, cy - s], fill=(118, 185, 0), width=3)
        d.line([px, cy + s, px, cy + s + 10], fill=(118, 185, 0), width=3)
        py = cy - s + i * (2 * s / 3)
        d.line([cx - s - 10, py, cx - s, py], fill=(118, 185, 0), width=3)
        d.line([cx + s, py, cx + s + 10, py], fill=(118, 185, 0), width=3)
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(20, 60, 30),
                outline=(118, 185, 0), width=3)
    d.rectangle([cx - s * 0.55, cy - s * 0.55, cx + s * 0.55, cy + s * 0.55],
                fill=(118, 185, 0))
    # rising chart
    pts = [(x + w * 0.52, y + h * 0.78), (x + w * 0.62, y + h * 0.66),
           (x + w * 0.72, y + h * 0.70), (x + w * 0.82, y + h * 0.42),
           (x + w * 0.92, y + h * 0.24)]
    d.line(pts, fill=(140, 230, 90), width=5, joint="curve")
    ax, ay = pts[-1]
    d.polygon([(ax, ay - 2), (ax - 12, ay + 2), (ax - 2, ay + 12)],
              fill=(140, 230, 90))
    # grid
    for gy in (0.3, 0.55, 0.8):
        d.line([x + w * 0.50, y + h * gy, x + w * 0.95, y + h * gy],
               fill=(40, 80, 55), width=1)
    text(d, (x + w * 0.52, y + h * 0.08), "+103%", font(SANS_B, 26),
         fill=(140, 230, 90), anchor="la")


def icon_saff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(27, 120, 55))
    # pitch lines
    d.rectangle([x + 10, y + 8, x + w - 10, y + h - 8], outline=WHITE, width=2)
    d.line([x + w / 2, y + 8, x + w / 2, y + h - 8], fill=WHITE, width=2)
    d.ellipse([x + w / 2 - 18, y + h / 2 - 18, x + w / 2 + 18, y + h / 2 + 18],
              outline=WHITE, width=2)
    # football
    bx, by, br = x + w * 0.30, y + h * 0.52, 30
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=WHITE,
              outline=(30, 30, 30), width=2)
    d.polygon(star_points(bx, by, 10, 10, 5), fill=(30, 30, 30))
    for a in range(0, 360, 72):
        px = bx + 24 * math.cos(math.radians(a))
        py = by + 24 * math.sin(math.radians(a))
        d.polygon(star_points(px, py, 6, 6, 5), fill=(30, 30, 30))
    # trophy
    tx, ty = x + w * 0.72, y + h * 0.50
    d.polygon([(tx - 20, ty - 26), (tx + 20, ty - 26), (tx + 14, ty + 2),
               (tx - 14, ty + 2)], fill=(255, 200, 40),
              outline=(150, 100, 0))
    d.arc([tx - 32, ty - 30, tx - 12, ty + 2], start=90, end=270,
          fill=(255, 200, 40), width=5)
    d.arc([tx + 12, ty - 30, tx + 32, ty + 2], start=270, end=90,
          fill=(255, 200, 40), width=5)
    d.rectangle([tx - 4, ty + 2, tx + 4, ty + 18], fill=(255, 200, 40))
    d.rectangle([tx - 16, ty + 18, tx + 16, ty + 26], fill=(255, 200, 40))


def icon_britain(d, x, y, w, h):
    # Union Jack on the left, sanctioned building on the right
    flag_uk(d, x, y, w * 0.52, h)
    d.rectangle([x + w * 0.52, y, x + w, y + h], fill=(240, 236, 224))
    bx, by = x + w * 0.76, y + h * 0.62
    # building
    d.rectangle([bx - 26, by - 34, bx + 26, by + 20], fill=(120, 116, 106))
    d.polygon([(bx - 32, by - 34), (bx, by - 52), (bx + 32, by - 34)],
              fill=(90, 86, 78))
    for wy in (by - 24, by - 6):
        for wx in (bx - 17, bx + 5):
            d.rectangle([wx, wy, wx + 12, wy + 12], fill=(255, 240, 180))
    # prohibition ring
    d.ellipse([bx - 38, by - 48, bx + 38, by + 28], outline=(200, 30, 30),
              width=7)
    d.line([bx - 27, by + 20, bx + 27, by - 40], fill=(200, 30, 30), width=7)


# ---- lead illustration: Manila skyline + Quad flags + plane ------------
def lead_illustration(d, x, y, w, h):
    # sky gradient
    for i in range(h):
        t = i / h
        r = int(191 + (247 - 191) * t)
        g = int(217 + (233 - 217) * t)
        b = int(232 + (210 - 232) * t)
        d.line([x, y + i, x + w, y + i], fill=(r, g, b))
    # sun
    sx, sy, sr = x + w * 0.84, y + h * 0.22, 26
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 224, 130))
    d.ellipse([sx - sr - 8, sy - sr - 8, sx + sr + 8, sy + sr + 8],
              outline=(255, 236, 170), width=3)
    # plane with dotted flight path
    d.line([x + 20, y + 44, x + 150, y + 30], fill=(120, 130, 140), width=2)
    for i in range(6):
        px = x + 20 + i * 26
        py = y + 44 - i * 2.8
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(120, 130, 140))
    px, py = x + 165, y + 26
    d.polygon([(px, py), (px + 34, py + 6), (px + 10, py + 10),
               (px + 4, py + 20), (px - 2, py + 10), (px - 18, py + 14),
               (px - 14, py + 4)], fill=(240, 240, 240),
              outline=(90, 100, 110))
    # skyline
    base = y + h - 14
    buildings = [(0.00, 0.42, 0.10), (0.09, 0.62, 0.09), (0.17, 0.34, 0.08),
                 (0.24, 0.55, 0.11), (0.34, 0.72, 0.09), (0.42, 0.40, 0.10),
                 (0.51, 0.58, 0.09), (0.59, 0.80, 0.08), (0.66, 0.46, 0.10),
                 (0.75, 0.64, 0.09), (0.83, 0.38, 0.09), (0.91, 0.52, 0.09)]
    for fx, fh, fw in buildings:
        bx0, bx1 = x + w * fx, x + w * (fx + fw)
        by0 = base - h * fh
        d.rectangle([bx0, by0, bx1, base], fill=NAVY)
        # lit windows
        for wy in range(int(by0) + 8, int(base) - 8, 14):
            for wx in range(int(bx0) + 6, int(bx1) - 6, 12):
                if (wx * 7 + wy * 13) % 5 < 2:
                    d.rectangle([wx, wy, wx + 4, wy + 5],
                                fill=(255, 214, 120))
    # flag poles in front of the skyline
    flags = [flag_usa, flag_japan, flag_india, flag_australia]
    labels = ["USA", "JAPAN", "INDIA", "AUSTRALIA"]
    fw, fh = 74, 46
    gap = (w - 4 * fw) / 5
    pole_top = base - 118
    for i, (fn, lab) in enumerate(zip(flags, labels)):
        fx = x + gap * (i + 1) + fw * i
        d.line([fx + 2, pole_top, fx + 2, base], fill=(230, 230, 230), width=3)
        d.ellipse([fx - 1, pole_top - 4, fx + 5, pole_top + 2],
                  fill=(230, 230, 230))
        fn(d, fx + 4, pole_top + 4, fw, fh)
        d.rectangle([fx + 4, pole_top + 4, fx + 4 + fw, pole_top + 4 + fh],
                    outline=(0, 0, 0))
        text(d, (fx + 4 + fw / 2, pole_top + fh + 12), lab, font(SANS_B, 13),
             fill=WHITE, anchor="ma")
    # caption ribbon
    d.rectangle([x, y + h - 34, x + w, y + h], fill=NAVY)
    text(d, (x + 16, y + h - 27), "MANILA, PHILIPPINES",
         font(SANS_B, 17), fill=GOLD, anchor="la")
    text(d, (x + w - 16, y + h - 26), "US  •  JAPAN  •  INDIA  •  AUSTRALIA",
         font(SANS_B, 13), fill=WHITE, anchor="ra")


# ---- page assembly ------------------------------------------------------
def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ===== masthead =====
    d.rectangle([0, 0, W, 156], fill=NAVY)
    text(d, (W / 2, 16), "THE WORLD TODAY", font(SERIF_B, 62), fill=WHITE,
         anchor="ma")
    d.line([48, 96, W - 48, 96], fill=GOLD, width=3)
    text(d, (W / 2, 106), "WEDNESDAY, 18 NOVEMBER 2026", font(SANS_B, 30),
         fill=GOLD, anchor="ma")

    # ===== lead story =====
    ly = 172
    lx, lw, lh = 24, 532, 296
    lead_illustration(d, lx, ly, lw, lh)
    d.rectangle([lx, ly, lx + lw, ly + lh], outline=(0, 0, 0), width=2)

    tx = 580
    text(d, (tx, ly + 2), "ASIA  •  DIPLOMACY", font(SANS_B, 19), fill=RED,
         anchor="la")
    d.line([tx, ly + 32, tx + 420, ly + 32], fill=RULE, width=2)
    head = wrap(d, "Trump in Manila for Quad summit",
                font(SERIF_B, 40), 420)
    yy = ly + 44
    for line in head:
        text(d, (tx, yy), line, font(SERIF_B, 40), fill=INK, anchor="la")
        yy += 48
    detail = ("The leaders of the US, Japan, India and Australia meet for "
              "the first time in two years — maritime security, AI and "
              "critical minerals on the agenda. Trump meets Marcos "
              "today, then flies to Shenzhen for talks with Xi and "
              "Putin.")
    dlines = wrap(d, detail, font(SANS, 19), 420)
    yy += 8
    for line in dlines:
        text(d, (tx, yy), line, font(SANS, 19), fill=DARKGRAY, anchor="la")
        yy += 25

    # ===== grid of five more stories =====
    stories = [
        ("WAR  •  UKRAINE", "Crimea bridge hit again",
         "A section of the bridge linking Russia and Crimea partially "
         "collapses after a Ukrainian strike.",
         icon_bridge, (58, 74, 92)),
        ("WAR  •  MIDDLE EAST", "Iran drones hit US radar in Bahrain",
         "Drones strike a US radar site at Sheikh Isa Air Base, the "
         "third attack on US targets there in days.",
         icon_radar, (232, 217, 176)),
        ("WEATHER  •  INDIA", "Cyclone Akvan bears down on India",
         "Severe storm over the Bay of Bengal; Andhra Pradesh and "
         "Odisha on alert, landfall due 20 Nov.",
         icon_cyclone, (23, 68, 110)),
        ("TECH  •  BUSINESS", "Nvidia sales double; Huang won't return",
         "Third-quarter revenue $115.8bn, up 103% on a year ago; the "
         "board says it will not reinstate its ex-CEO.",
         icon_nvidia, (9, 26, 16)),
        ("SPORT  •  FOOTBALL", "India win a 10th SAFF title",
         "A late Mandi header seals a 2–1 comeback over Pakistan in "
         "the final in Dhaka.",
         icon_saff, (27, 120, 55)),
        ("DIPLOMACY  •  EUROPE", "Britain sanctions settlement firms",
         "Eight Israeli construction firms face asset freezes in a "
         "push to protect the two-state solution.",
         icon_britain, (240, 236, 224)),
    ]

    cols_x = [24, 355, 686]
    rows_y = [484, 724]
    cw, ch = 314, 224
    icon_h = 92

    for i, (kicker, headline, detail, icon_fn, _bg) in enumerate(stories):
        cx = cols_x[i % 3]
        cy = rows_y[i // 3]
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=WHITE,
                    outline=CELLBORDER, width=2)
        d.rectangle([cx, cy, cx + cw, cy + 6], fill=RED)
        icon_fn(d, cx + 2, cy + 8, cw - 4, icon_h)
        text(d, (cx + 12, cy + icon_h + 16), kicker, font(SANS_B, 14),
             fill=RED, anchor="la")
        hlines = wrap(d, headline, font(SANS_B, 21), cw - 24)
        yy = cy + icon_h + 36
        for line in hlines[:2]:
            text(d, (cx + 12, yy), line, font(SANS_B, 21), fill=INK,
                 anchor="la")
            yy += 26
        dlines = wrap(d, detail, font(SANS, 15), cw - 24)
        yy += 2
        for line in dlines[:3]:
            text(d, (cx + 12, yy), line, font(SANS, 15), fill=DARKGRAY,
                 anchor="la")
            yy += 19

    # ===== footer =====
    d.line([24, 962, W - 24, 962], fill=RULE, width=2)
    text(d, (W / 2, 970),
         "A drawn summary of the day's world news  •  Wednesday, 18 November 2026",
         font(SANS, 15), fill=GRAY, anchor="ma")
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = draw_page()
    img.save(out, optimize=True)
    print(f"wrote {out}: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
