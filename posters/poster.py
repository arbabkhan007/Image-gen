"""9 November — Allama Iqbal Day. Premium editorial poster compositor."""
import os
import sys

import numpy as np
from PIL import Image, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import typography as T

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1600, 2000

# ----------------------------------------------------------------------------
# palette
GOLD_LIGHT = (0.98, 0.93, 0.78)
GOLD_MID = (0.91, 0.76, 0.45)
GOLD_DEEP = (0.72, 0.53, 0.20)
EMERALD = (0.02, 0.16, 0.14)
CREAM = (0.99, 0.97, 0.90)

# ----------------------------------------------------------------------------
# 1. art plate
plate = Image.open(os.path.join(HERE, "plate.png")).convert("RGB")
plate = ImageEnhance.Color(plate).enhance(1.06)
plate = ImageEnhance.Contrast(plate).enhance(1.05)
plate = plate.resize((W, H), Image.LANCZOS)
img = np.asarray(plate).astype(np.float32) / 255.0

# gentle cinematic teal/emerald grade in the shadows, warm highlights
lum = img @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
shadow = np.clip(1.0 - lum * 2.2, 0, 1)[:, :, None]
highlight = np.clip((lum - 0.55) * 2.0, 0, 1)[:, :, None]
img = img * (1 - shadow * 0.20) + np.array([0.03, 0.16, 0.15], np.float32) * shadow * 0.20
img = R.screen(img, np.array([1.0, 0.93, 0.78], np.float32) * highlight * 0.18)

# vignette
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H * 0.45) / (H * 0.78)) ** 2)
vig = np.clip(1.0 - np.clip(d - 0.45, 0, 2) ** 1.6 * 0.55, 0, 1)[:, :, None]
img *= 0.55 + 0.45 * vig

# top scrim: gives the title a calm, dark royal-blue bed
ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
top_scrim = np.clip((0.30 - ys) / 0.30, 0, 1) ** 1.15 * 0.55
img = img * (1 - top_scrim) + np.array([0.02, 0.055, 0.11], np.float32) * top_scrim

# bottom scrim: deep emerald bed for the couplet, softly feathered
bot = np.clip((ys - 0.645) / 0.355, 0, 1) ** 1.35 * 0.93
img = img * (1 - bot) + np.array([0.011, 0.055, 0.049], np.float32) * bot
# a second, tighter band right behind the couplet lines
band = np.exp(-((ys - 0.855) ** 2) / (2 * 0.10 ** 2)) * 0.40
img = img * (1 - band) + np.array([0.007, 0.040, 0.036], np.float32) * band
# local corner falloff so the couplet reads over the bright right-hand sky
xxn = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
corner = np.clip((xxn - 0.40) / 0.60, 0, 1) ** 1.3 * np.clip((ys - 0.555) / 0.20, 0, 1) * 0.55
img = img * (1 - corner)

# soft bloom
bloom = np.clip(lum - 0.72, 0, 1)[:, :, None]
bloom = R.gaussian(np.repeat(bloom, 3, axis=2), 26) * 0.55
img = R.screen(img, bloom)

# ----------------------------------------------------------------------------
# 1b. ghosted calligraphic watermark in the open sky (Iqbal's core idea: Khudi)
def ghost_word(txt, font, size, cx, cy, alpha, blur=1.6, color=(0.92, 0.88, 0.74)):
    p, _, _ = T.text_path(txt, font, size, x=0, baseline=0)
    b = p.get_extents()
    p = T.text_path(txt, font, size, x=0, baseline=0)[0]
    p.vertices[:, 0] += cx - (b.x0 + b.x1) / 2
    p.vertices[:, 1] += cy - (b.y0 + b.y1) / 2
    m = R.paths_mask([p], W, H, supersample=2, blur=blur)[:, :, None]
    global img
    g = R.gaussian(m[:, :, 0], 24)[:, :, None]
    img = R.screen(img, np.array(color, np.float32) * g * alpha * 0.55)
    img = img * (1 - m * alpha) + np.array(color, np.float32) * m * alpha


ghost_word("خودی", "Nastaliq-600.ttf", 232, 322, 742, 0.17, blur=1.8,
          color=(1.0, 0.96, 0.85))

# ----------------------------------------------------------------------------
# 1c. abstract flag accent: a whisper of emerald + white silk in the high sky
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly


def ribbon_mask(pts, widths, ss=2):
    verts_l, verts_r = [], []
    for i, (px, py) in enumerate(pts):
        j = min(i + 1, len(pts) - 1)
        k = max(i - 1, 0)
        dx, dy = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]
        L = np.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        w = widths[i]
        verts_l.append((px + nx * w, py + ny * w))
        verts_r.append((px - nx * w, py - ny * w))
    poly = verts_l + verts_r[::-1]
    w2, h2 = W * ss, H * ss
    fig = plt.figure(figsize=(w2 / 100, h2 / 100), dpi=100, facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("black"); ax.set_xlim(0, w2); ax.set_ylim(h2, 0); ax.axis("off")
    ax.add_patch(MPoly([(x * ss, y * ss) for x, y in poly], closed=True,
                       facecolor="white", edgecolor="none"))
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, 0].astype(np.float32) / 255.0
    plt.close(fig)
    im = Image.fromarray((buf * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


_t = np.linspace(0, 1, 220)
_cx = 1010 + 620 * _t
_cy = 660 - 200 * _t - 34 * np.sin(_t * 3.4 + 0.3) * (1 - _t * 0.4)
_pts = list(zip(_cx, _cy))
_wid = 21 * np.sin(np.pi * np.clip(_t * 1.12, 0, 1)) ** 0.75 + 1.2
_rib = ribbon_mask(_pts, _wid)                      # emerald silk
_rib2 = ribbon_mask([(x + 3, y + 15) for x, y in _pts], _wid * 0.30)  # white edge
_rib = R.gaussian(_rib, 3.0)
_rib2 = R.gaussian(_rib2, 2.0)
xs = np.linspace(0, 1, W, dtype=np.float32)[None, :]
_fade = np.clip((1.0 - xs) / 0.085, 0, 1) * np.clip(xs / 0.10, 0, 1)
_rib *= _fade
_rib2 *= _fade
img = R.screen(img, np.array([0.06, 0.62, 0.38], np.float32) * _rib[:, :, None] * 0.30)
img = R.screen(img, np.array([0.92, 0.98, 0.93], np.float32) * _rib2[:, :, None] * 0.20)
_g = R.gaussian(_rib, 22)[:, :, None]
img = R.screen(img, np.array([0.10, 0.80, 0.52], np.float32) * _g * 0.10)

# ----------------------------------------------------------------------------
# 2. typography
layers = []  # (paths, kind, meta)


def ink_bbox(txt, font, size, tracking=0.0):
    p, _, _ = T.text_path(txt, font, size, x=0, baseline=0, tracking=tracking)
    return p.get_extents()


def add_text(txt, font, size, cx=W / 2, ink_top=None, tracking=0.0,
             color="gold", max_width=None):
    """Place text centred on cx with its ink starting at ink_top."""
    b = ink_bbox(txt, font, size, tracking)
    while max_width and b.width > max_width:
        size *= 0.985
        b = ink_bbox(txt, font, size, tracking)
    baseline = ink_top - b.y0
    p = T.text_path(txt, font, size, x=0, baseline=baseline,
                    tracking=tracking, align="left")[0]
    dx = cx - (b.x0 + b.x1) / 2
    p.vertices[:, 0] += dx
    bb = p.get_extents()
    layers.append({"path": p, "color": color, "bbox": bb, "text": txt,
                   "font": font, "size": size})
    return bb


# --- header ornament -------------------------------------------------------
def hairline(ax, x0, x1, y, lw, color):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="butt")


def build_ornaments():
    """Return list of simple line/diamond primitives, drawn as masks."""
    orn = []
    cy = 104
    # rule with a gap in the middle for a diamond
    for (a, b) in [(160, 700), (900, 1440)]:
        orn.append(("line", a, cy, b, cy, 1.6))
    orn.append(("line", 160, cy - 9, 198, cy - 9, 1.0))
    orn.append(("line", 1402, cy - 9, 1440, cy - 9, 1.0))
    # centre diamond
    orn.append(("diamond", 800, cy, 9))
    orn.append(("diamond", 800, cy, 17, 1.0))   # outline ring
    return orn


def ornament_mask(orn, ss=2):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    w2, h2 = W * ss, H * ss
    fig = plt.figure(figsize=(w2 / 100, h2 / 100), dpi=100, facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("black")
    ax.set_xlim(0, w2); ax.set_ylim(h2, 0); ax.axis("off")
    for o in orn:
        if o[0] == "line":
            _, x0, y0, x1, y1, lw = o
            ax.plot([x0 * ss, x1 * ss], [y0 * ss, y1 * ss], color="white",
                    lw=lw * ss, solid_capstyle="butt")
        elif o[0] == "diamond":
            _, cx, cy, r = o[:4]
            filled = len(o) == 4
            pts = [(cx * ss, (cy - r) * ss), ((cx + r) * ss, cy * ss),
                   (cx * ss, (cy + r) * ss), ((cx - r) * ss, cy * ss)]
            ax.add_patch(Polygon(pts, closed=True,
                                 facecolor="white" if filled else "none",
                                 edgecolor="white" if not filled else "none",
                                 lw=1.3 * ss))
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, 0].astype(np.float32) / 255.0
    plt.close(fig)
    im = Image.fromarray((buf * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


orn = build_ornaments()
orn_mask = ornament_mask(orn)

# --- text lockup ------------------------------------------------------------
HEAD_RULE = 128
F9 = "Cinzel-500.ttf"
FI = "Cinzel-900.ttf"
FN = "Nastaliq-600.ttf"
FC = "Cormorant-400.ttf"

b_date = add_text("9 NOVEMBER", F9, 64, tracking=30, ink_top=146)
b_title = add_text("IQBAL DAY", FI, 214, ink_top=216, max_width=1330)
b_urdu = add_text("یومِ اقبال", FN, 100, ink_top=472)

CPL1 = "خودی کو کر بلند اتنا کہ ہر تقدیر سے پہلے"
CPL2 = "خدا بندے سے خود پوچھے، بتا تیری رضا کیا ہے"
CPL_SIZE = 74
b_cp1 = add_text(CPL1, FN, CPL_SIZE, ink_top=1626, max_width=1350)
b_cp2 = add_text(CPL2, FN, CPL_SIZE, ink_top=1740, max_width=1350)
b_tag = add_text("Dream  •  Believe  •  Rise", FC, 50, tracking=12,
                 ink_top=1886)

# ----------------------------------------------------------------------------
# 3. composite
def fill_gradient(bbox, stops, y0=None, y1=None):
    """Return an HxWx3 gradient image spanning bbox vertically."""
    y0 = bbox.y0 if y0 is None else y0
    y1 = bbox.y1 if y1 is None else y1
    yy = np.arange(H, dtype=np.float32)[:, None]
    t = np.clip((yy - y0) / max(1.0, (y1 - y0)), 0, 1)
    pos = [s[0] for s in stops]
    col = np.zeros((H, 3), dtype=np.float32)
    for c in range(3):
        col[:, c] = np.interp(t[:, 0], pos, [s[1][c] for s in stops])
    return np.repeat(col[:, None, :], W, axis=1)


def overlay(mask, color_img, shadow=True, glow=0.0, glow_color=GOLD_MID,
            glow_r=26, shadow_r=9, shadow_dy=7, shadow_a=0.55):
    global img
    if shadow and mask.any():
        sh = np.roll(R.gaussian(mask, shadow_r), int(shadow_dy), axis=0)
        sh = np.roll(sh, 3, axis=1)
        img = img * (1 - sh[:, :, None] * shadow_a)
    if glow > 0:
        g = R.gaussian(mask, glow_r)[:, :, None]
        img = R.screen(img, np.array(glow_color, np.float32) * g * glow)
    m = mask[:, :, None]
    img = img * (1 - m) + color_img * m


GOLD_STOPS = [(0.0, (1.00, 0.97, 0.86)),
              (0.30, (0.97, 0.87, 0.63)),
              (0.55, (0.90, 0.74, 0.42)),
              (0.80, (0.95, 0.83, 0.55)),
              (1.0, (0.78, 0.60, 0.28))]

# ornaments
overlay(orn_mask, np.repeat(np.array([0.93, 0.80, 0.52], np.float32)[None, None, :],
                            H, axis=0).repeat(W, axis=1),
        shadow=False, glow=0.30, glow_r=12)

# local contrast guard behind the couplet: darken only where the ink sits
_cp_paths = [L["path"] for L in layers if L["text"] in (CPL1, CPL2, "Dream  •  Believe  •  Rise")]
_ink = R.paths_mask(_cp_paths, W, H, supersample=1)
_bed = R.gaussian(_ink, 46)[:, :, None]
img = img * (1 - _bed * 0.42)

for L in layers:
    mask = R.paths_mask([L["path"]], W, H, supersample=2)
    if L["color"] == "gold":
        b = L["bbox"]
        col = fill_gradient(b, GOLD_STOPS, b.y0 - 4, b.y1 + 4)
        overlay(mask, col, shadow=True, glow=0.22, glow_r=22,
                shadow_r=10, shadow_dy=8, shadow_a=0.60)
    else:
        col = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
        overlay(mask, col, shadow=True)

# ----------------------------------------------------------------------------
# 4. finish: bloom on type, editorial frame, grain
img = R.screen(img, R.gaussian(np.clip(img - 0.80, 0, 1), 30) * 0.30)

# editorial hairline frame (double rule + corner ticks)
FM = 42          # outer margin
IN = 10          # gap
frame_orn = []
for off, lw in ((0.0, 1.5), (IN, 0.6)):
    m = FM + off
    frame_orn += [("line", m, m, W - m, m, lw), ("line", W - m, m, W - m, H - m, lw),
                  ("line", W - m, H - m, m, H - m, lw), ("line", m, H - m, m, m, lw)]
# corner ticks: short heavier strokes at each corner
TICK = 74
for (cx, cy, sx, sy) in ((FM, FM, 1, 1), (W - FM, FM, -1, 1),
                         (FM, H - FM, 1, -1), (W - FM, H - FM, -1, -1)):
    frame_orn += [("line", cx, cy, cx + sx * TICK, cy, 2.4),
                  ("line", cx, cy, cx, cy + sy * TICK, 2.4)]

fmask = ornament_mask(frame_orn)
fcol = np.ones((H, W, 3), np.float32) * np.array([0.90, 0.79, 0.55], np.float32)
overlay(fmask, fcol, shadow=True, shadow_r=4, shadow_dy=2, shadow_a=0.35)

img += R.grain(H, W, amount=0.009, seed=11)
img = np.clip(img, 0, 1)

out = R.to_pil(img)
out.save(os.path.join(HERE, "iqbal_day_9nov.png"))
out.save(os.path.join(HERE, "iqbal_day_9nov.jpg"), quality=95, subsampling=0,
         optimize=True)
print("saved", out.size)
