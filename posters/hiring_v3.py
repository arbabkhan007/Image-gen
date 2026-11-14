"""Meta ad — v2 art direction: full-bleed staff photo, cream notice card,
emerald contact strip. 1080x1080 and 1080x1350.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import typography as T

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "hiring_v2")

CREAM = (0.976, 0.961, 0.930)
INK = (0.078, 0.145, 0.129)
EMERALD = (0.039, 0.349, 0.278)
EMERALD_DEEP = (0.023, 0.216, 0.176)
MUTED = (0.365, 0.427, 0.396)
GOLD = (0.729, 0.596, 0.380)
FOOT_CREAM = (0.898, 0.847, 0.702)

F7, F8, F6, F5 = ("Manrope-700.ttf", "Manrope-800.ttf",
                  "Manrope-600.ttf", "Manrope-500.ttf")

ROLES = [("01", "MONTESSORI SECTION", "Female only"),
         ("02", "PRIMARY · ENGLISH", "Female only"),
         ("03", "SUBJECT SPECIALISTS", "Physics · Urdu · Matric")]

KICKER = "WE'RE HIRING"
H1, H2 = "TEACHERS", "REQUIRED"
LOGO_LAB = "SCHOOL LOGO"
PHONE = "0300 000 0000"
EMAIL = "careers@yourschool.edu.pk"
CTA = "APPLY NOW  ·  SEND YOUR CV"


# ---------------------------------------------------------------------------
def backdrop(W, H, square, anchor_y=0.30):
    im = Image.open(os.path.join(HERE, "plate_wide.png")).convert("RGB")
    pw, ph = im.size
    scale = max(W / pw, H / ph)
    im = im.resize((int(pw * scale + 1), int(ph * scale + 1)), Image.LANCZOS)
    nw, nh = im.size
    ox = int((nw - W) * (0.86 if square else 0.72))
    oy = int((nh - H) * anchor_y)
    im = im.crop((ox, oy, ox + W, oy + H))
    a = np.asarray(im).astype(np.float32) / 255.0
    # grade: cool emerald shadows, warm highlights
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    sh = np.clip(1 - lum * 2.1, 0, 1)[:, :, None]
    hi = np.clip((lum - 0.66) * 2.2, 0, 1)[:, :, None]
    a = a * (1 - sh * 0.20) + np.array(EMERALD_DEEP, np.float32) * sh * 0.20
    a = R.screen(a, np.array([1.0, 0.95, 0.85], np.float32) * hi * 0.12)
    # vignette
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    d = np.sqrt(((xs - 0.62) ** 2) * 1.1 + ((ys - 0.36) ** 2))
    a = a * (1 - np.clip(d - 0.40, 0, 2) ** 1.6 * 0.42)
    return a


def round_rect_mask(W, H, box, radius, feather=0.0):
    x, y, w, h = box
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=255)
    a = np.asarray(im).astype(np.float32) / 255.0
    if feather:
        a = R.gaussian(a, feather)
    return a


def text_layer(W, H, items, ss=3):
    """Draw text items onto a transparent RGBA array in one matplotlib pass."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MP

    w2, h2 = W * ss, H * ss
    fig = plt.figure(figsize=(w2 / 100.0, h2 / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w2); ax.set_ylim(h2, 0); ax.axis("off")
    ax.patch.set_alpha(0.0)
    fig.patch.set_alpha(0.0)
    for it in items:
        p = MP(np.asarray(it["p"].vertices) * ss, np.asarray(it["p"].codes))
        ax.add_patch(PathPatch(p, facecolor=it["color"], edgecolor="none",
                               antialiased=True))
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba()).astype(np.float32) / 255.0
    plt.close(fig)
    im = Image.fromarray((rgba * 255).astype(np.uint8))
    im = im.resize((W, H), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


# ---------------------------------------------------------------------------
def build(W, H, square):
    """Photo band on top, cream notice panel below, emerald contact strip."""
    s = W / 1080.0
    M = 56 * s
    foot_h = int((128 if square else 146) * s)
    foot_top = H - foot_h
    photo_h = int((452 if square else 596) * s)

    band = backdrop(W, photo_h, square, anchor_y=0.34)
    img = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
    img[:photo_h] = band

    card_x, card_y = 0, photo_h
    card_w, card_h = W, foot_top - photo_h

    # ---------------- cream panel ----------------
    img[card_y:foot_top] = np.array(CREAM, np.float32)
    # emerald keyline where the photo meets the panel
    img[card_y:card_y + max(1, int(3.0 * s))] = np.array(EMERALD, np.float32)

    # ---------------- footer strip ----------------
    img[foot_top:H] = np.array(EMERALD_DEEP, np.float32)
    img[foot_top:foot_top + max(1, int(2.2 * s))] = np.array(GOLD, np.float32)

    # ---------------- geometry ----------------
    pad = (34 if square else 40) * s
    inner_w = W - 2 * (M + 14 * s)

    probe = T.text_path(H1 + " " + H2, F8, 100, x=0, baseline=0)[0].get_extents()
    head_sz = 100 * inner_w / probe.width
    head_sz = min(head_sz, (150 if square else 176) * s)
    adv = head_sz * 0.782

    kick_sz = (21 if square else 23) * s
    row_h = (56 if square else 66) * s
    lab_sz = (26 if square else 29) * s
    tag_sz = (19 if square else 21) * s

    content_h = (kick_sz + 24 * s + adv + 20 * s + 18 * s + 14 * s
                 + row_h * len(ROLES))
    top = card_y + (card_h - content_h) / 2 + 6 * s
    cx = M + 14 * s

    items = []
    deco = []   # (y, x0, x1, thickness, colour) drawn after centring

    def add(txt, font, size, x, top=None, align="left", color=INK,
            tracking=0.0, group="panel"):
        t, w, _ = T.text_path(txt, font, size, x=0, baseline=0, tracking=tracking)
        b = t.get_extents()
        y = top - b.y0
        p = T.text_path(txt, font, size, x=x, baseline=y, tracking=tracking,
                        align=align)[0]
        items.append({"p": p, "color": color, "group": group})
        return p.get_extents()

    # ---- kicker ----
    kb = add(KICKER, F7, kick_sz, cx, top=top, color=EMERALD, tracking=7.5 * s)

    # ---- logo badge sits on the photograph, top-right ----
    logo_w, logo_h = (176 if square else 190) * s, (56 if square else 60) * s
    lb_x, lb_y = M - 4 * s, M - 6 * s
    box = round_rect_mask(W, H, (lb_x, lb_y, logo_w, logo_h), 5 * s)
    img = img * (1 - box[:, :, None] * 0.94) + \
        np.array((0.988, 0.978, 0.952), np.float32) * box[:, :, None] * 0.94
    inner = round_rect_mask(W, H, (lb_x + 1.6 * s, lb_y + 1.6 * s,
                                   logo_w - 3.2 * s, logo_h - 3.2 * s), 4 * s)
    edge = np.clip(box - R.gaussian(inner, 0.7), 0, 1)
    img = img * (1 - edge[:, :, None] * 0.55) + \
        np.array((0.42, 0.52, 0.46), np.float32) * edge[:, :, None] * 0.55
    lab = T.text_path(LOGO_LAB, F7, 12.5 * s, x=0, baseline=0,
                      tracking=2.8 * s)[0].get_extents()
    add(LOGO_LAB, F7, 12.5 * s, lb_x + (logo_w - lab.width) / 2,
        top=lb_y + logo_h / 2 - (lab.y0 + lab.y1) / 2,
        color=(0.40, 0.48, 0.43), tracking=2.8 * s, group="logo")

    # ---- single-line headline ----
    hy = kb.y1 + 22 * s
    w1 = T.text_path(H1 + " ", F8, head_sz, x=0, baseline=0,
                     tracking=-3.0 * s)[1]
    hb = add(H1, F8, head_sz, cx, top=hy, color=INK, tracking=-3.0 * s)
    hb2 = add(H2, F8, head_sz, cx + w1, top=hy, color=EMERALD,
              tracking=-3.0 * s)

    # ---- hairline ----
    ry = hb.y1 + 18 * s
    deco.append((ry, cx, cx + inner_w, 1.3 * s, (0.80, 0.79, 0.735)))

    # ---- role rows ----
    ry += 16 * s
    for i, (num, name, tag) in enumerate(ROLES):
        add(num, F7, (17 if square else 18.5) * s, cx, top=ry + 8 * s,
            color=GOLD, tracking=0.8 * s)
        add(name, F7, lab_sz, cx + 40 * s, top=ry, color=INK, tracking=0.2 * s)
        add(tag, F5, tag_sz, W - M - 14 * s, top=ry + 7 * s,
            color=MUTED, align="right")
        ry += row_h
        if i < len(ROLES) - 1:
            deco.append((ry - 15 * s, cx, cx + inner_w, 1.0 * s,
                         (0.875, 0.865, 0.82)))

    # ---- closing note fills the panel's lower band ----
    note_y = ry + 12 * s
    nb = add("LAHORE  ·  FULL-TIME POSITIONS  ·  INTERVIEWS THIS MONTH",
             F6, (17 if square else 18.5) * s, cx, top=note_y,
             color=(0.42, 0.47, 0.44), tracking=3.0 * s)
    deco.append((note_y - 16 * s, cx, cx + 54 * s, 1.2 * s, GOLD))

    # ---- footer copy ----
    add(CTA, F7, (19 if square else 21) * s, M + 14 * s,
        top=foot_top + (26 if square else 30) * s,
        color=FOOT_CREAM, tracking=2.4 * s, group="foot")
    add(PHONE, F8, (30 if square else 34) * s, W - M - 14 * s,
        top=foot_top + (20 if square else 24) * s,
        color=(0.988, 0.976, 0.949), align="right", group="foot")
    add(EMAIL, F5, (18 if square else 20) * s, W - M - 14 * s,
        top=foot_top + (58 if square else 66) * s,
        color=(0.678, 0.796, 0.741), align="right", group="foot")

    # ---- optically centre the panel copy inside the cream panel ----
    panel = [it for it in items if it.get("group") == "panel"]
    content0 = panel[0]["p"].get_extents().y0          # kicker cap top
    content1 = panel[-1]["p"].get_extents().y1         # note baseline area
    dy = (card_y + card_h * 0.485) - (content0 + content1) / 2
    for it in panel:
        it["p"].vertices[:, 1] += dy

    for (y, x0, x1, th, col) in deco:
        yy = int(y + dy)
        img[yy:yy + max(1, int(th)), int(x0):int(x1)] = np.array(col, np.float32)

    layer = text_layer(W, H, items)
    a = layer[:, :, 3:4]
    img = img * (1 - a) + layer[:, :, :3] * a

    img = np.clip(img + R.grain(H, W, 0.006, 33), 0, 1)
    return R.to_pil(img)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, (w, h) in {"meta_ad_1x1": (1080, 1080),
                         "meta_ad_4x5": (1080, 1350)}.items():
        im = build(w, h, square=(w == h))
        im.save(os.path.join(OUT, name + ".png"))
        im.save(os.path.join(OUT, name + ".jpg"), quality=95, subsampling=0,
                optimize=True)
        print("saved", name, im.size)
