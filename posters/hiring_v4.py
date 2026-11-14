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
OUT = os.path.join(HERE, "hiring")

WHITE = (1.000, 1.000, 1.000)          # panel field
INK = (0.078, 0.184, 0.239)            # deep navy-ink, high contrast
TEAL = (0.000, 0.596, 0.729)           # primary brand teal
TEAL_DEEP = (0.000, 0.463, 0.588)      # footer strip
CORAL = (1.000, 0.420, 0.290)          # accent / numbers
SUN = (1.000, 0.757, 0.027)            # highlight yellow
MUTED = (0.361, 0.435, 0.478)          # secondary text
FOOT_WHITE = (1.000, 1.000, 1.000)

F7, F8, F6, F5 = ("Manrope-700.ttf", "Manrope-800.ttf",
                  "Manrope-600.ttf", "Manrope-500.ttf")

ROLES = [("01", "MONTESSORI SECTION", "Female only"),
         ("02", "PRIMARY · ENGLISH", "Female only"),
         ("03", "SUBJECT SPECIALISTS", None)]
SUBJECT_CHIPS = ["PHYSICS", "URDU"]
SCOPE = "MATRIC"

KICKER = "WE'RE HIRING"
H1, H2 = "TEACHERS", "REQUIRED"
LOGO_LAB = "SCHOOL LOGO"
PHONE = "0300 000 0000"
EMAIL = "careers@yourschool.edu.pk"
CTA = "APPLY NOW  ·  SEND YOUR CV"


# ---------------------------------------------------------------------------
def backdrop(W, H, square, anchor_y=0.30):
    im = Image.open(os.path.join(HERE, "plate_bright.png")).convert("RGB")
    pw, ph = im.size
    scale = max(W / pw, H / ph)
    im = im.resize((int(pw * scale + 1), int(ph * scale + 1)), Image.LANCZOS)
    nw, nh = im.size
    ox = int((nw - W) * (0.86 if square else 0.72))
    oy = int((nh - H) * anchor_y)
    im = im.crop((ox, oy, ox + W, oy + H))
    a = np.asarray(im).astype(np.float32) / 255.0
    # bright, airy grade: lift exposure, add a touch of warmth and saturation
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = a * 1.055 + 0.012                                  # exposure
    a = np.clip(a, 0, 1)
    hi = np.clip((lum - 0.72) * 2.0, 0, 1)[:, :, None]
    a = R.screen(a, np.array([1.0, 0.97, 0.90], np.float32) * hi * 0.22)
    # gentle saturation boost
    g = a.mean(axis=2, keepdims=True)
    a = np.clip(g + (a - g) * 1.14, 0, 1)
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
    img = np.ones((H, W, 3), np.float32) * np.array(WHITE, np.float32)
    img[:photo_h] = band

    card_x, card_y = 0, photo_h
    card_w, card_h = W, foot_top - photo_h

    # ---------------- cream panel ----------------
    img[card_y:foot_top] = np.array(WHITE, np.float32)
    # emerald keyline where the photo meets the panel
    img[card_y:card_y + max(1, int(3.0 * s))] = np.array(TEAL, np.float32)

    # ---------------- footer strip ----------------
    img[foot_top:H] = np.array(TEAL_DEEP, np.float32)
    img[foot_top:foot_top + max(1, int(2.2 * s))] = np.array(SUN, np.float32)

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
    deferred = []   # (x, y, w, h, r, rgb) rounded fills that follow the copy

    def dfr(x, y, w, h, r, rgb):
        deferred.append((x, y, w, h, r, rgb))
        return round_rect_mask(W, H, (x, y, w, h), r)  # for preview only

    def add(txt, font, size, x, top=None, align="left", color=INK,
            tracking=0.0, group="panel"):
        t, w, _ = T.text_path(txt, font, size, x=0, baseline=0, tracking=tracking)
        b = t.get_extents()
        y = top - b.y0
        p = T.text_path(txt, font, size, x=x, baseline=y, tracking=tracking,
                        align=align)[0]
        items.append({"p": p, "color": color, "group": group})
        return p.get_extents()

    # ---- kicker in a coral pill ----
    kw = T.text_path(KICKER, F7, kick_sz, x=0, baseline=0,
                     tracking=7.5 * s)[1]
    pill_h = kick_sz * 1.86
    pill_pad = 20 * s
    dfr(cx, top - pill_h * 0.34, kw + pill_pad * 1.30, pill_h, pill_h / 2, CORAL)
    kb = add(KICKER, F7, kick_sz, cx + pill_pad * 0.65,
             top=top - pill_h * 0.34 + (pill_h - kick_sz * 0.735) / 2,
             color=(1, 1, 1), tracking=7.5 * s)

    # ---- logo card, bottom-right of the white panel ----
    logo_w, logo_h = (196 if square else 212) * s, (64 if square else 70) * s
    lb_x, lb_y = W - M - 14 * s - logo_w, foot_top - logo_h - 26 * s
    box = round_rect_mask(W, H, (lb_x, lb_y, logo_w, logo_h), 10 * s)
    img = img * (1 - box[:, :, None] * 1.0) + \
        np.array((0.949, 0.976, 0.984), np.float32) * box[:, :, None] * 1.0
    inner = round_rect_mask(W, H, (lb_x + 1.8 * s, lb_y + 1.8 * s,
                                   logo_w - 3.6 * s, logo_h - 3.6 * s), 9 * s)
    edge = np.clip(box - R.gaussian(inner, 0.7), 0, 1)
    img = img * (1 - edge[:, :, None] * 0.75) + \
        np.array(TEAL, np.float32) * edge[:, :, None] * 0.75
    lab = T.text_path(LOGO_LAB, F7, 12.5 * s, x=0, baseline=0,
                      tracking=2.8 * s)[0].get_extents()
    add(LOGO_LAB, F7, 12.5 * s, lb_x + (logo_w - lab.width) / 2,
        top=lb_y + logo_h / 2 - (lab.y0 + lab.y1) / 2,
        color=TEAL, tracking=2.8 * s, group="logo")

    # ---- single-line headline ----
    hy = kb.y1 + 30 * s
    w1 = T.text_path(H1 + " ", F8, head_sz, x=0, baseline=0,
                     tracking=-3.0 * s)[1]
    w2 = T.text_path(H2, F8, head_sz, x=0, baseline=0,
                     tracking=-3.0 * s)[1]
    dfr(cx + w1 - 6 * s, hy + adv * 0.055, w2 + 14 * s, adv * 0.90, 7 * s, SUN)
    hb = add(H1, F8, head_sz, cx, top=hy, color=INK, tracking=-3.0 * s)
    hb2 = add(H2, F8, head_sz, cx + w1, top=hy, color=INK,
              tracking=-3.0 * s)

    # ---- hairline ----
    ry = hb.y1 + 18 * s
    deco.append((ry, cx, cx + inner_w, 1.3 * s, (0.80, 0.79, 0.735)))

    # ---- role rows ----
    ry += 16 * s
    for i, (num, name, tag) in enumerate(ROLES):
        add(num, F7, (17 if square else 18.5) * s, cx, top=ry + 8 * s,
            color=CORAL, tracking=0.8 * s)
        nb = add(name, F7, lab_sz, cx + 40 * s, top=ry, color=INK,
                 tracking=0.2 * s)
        if tag:
            add(tag, F5, tag_sz, W - M - 14 * s, top=ry + 7 * s,
                color=MUTED, align="right")
        else:
            # "SUBJECT SPECIALISTS" + coral chips + scope, chips hug the label
            chip_sz = (16 if square else 17) * s
            chip_h = chip_sz * 2.05
            cxp = nb.x1 + 16 * s
            for label in SUBJECT_CHIPS:
                tw = T.text_path(label, F7, chip_sz, x=0, baseline=0,
                                 tracking=1.8 * s)[1]
                cw = tw + 24 * s
                chy = ry + lab_sz * 0.735 / 2 - chip_h / 2 + 2 * s
                dfr(cxp, chy, cw, chip_h, chip_h / 2, CORAL)
                add(label, F7, chip_sz, cxp + 12 * s,
                    top=chy + (chip_h - chip_sz * 0.735) / 2,
                    color=(1, 1, 1), tracking=1.8 * s)
                cxp += cw + 8 * s
            add(SCOPE + " CLASSES", F7, chip_sz, cxp + 6 * s,
                top=ry + lab_sz * 0.735 / 2 - chip_sz * 0.735 / 2 + 1 * s,
                color=TEAL, tracking=1.6 * s)
        ry += row_h
        if i < len(ROLES) - 1:
            deco.append((ry - 15 * s, cx, cx + inner_w, 1.0 * s,
                         (0.875, 0.865, 0.82)))

    # ---- closing note fills the panel's lower band ----
    note_y = ry + 12 * s
    nb = add("LAHORE  ·  FULL-TIME POSITIONS  ·  INTERVIEWS THIS MONTH",
             F6, (17 if square else 18.5) * s, cx, top=note_y,
             color=(0.42, 0.47, 0.44), tracking=3.0 * s)
    deco.append((note_y - 16 * s, cx, cx + 54 * s, 3.4 * s, CORAL))

    # ---- footer copy ----
    cta_sz = (17 if square else 19) * s
    cta_w = T.text_path(CTA, F7, cta_sz, x=0, baseline=0,
                        tracking=2.2 * s)[1]
    btn_h = (54 if square else 58) * s
    btn_x = M + 14 * s
    btn_y = foot_top + (foot_h - btn_h) / 2
    bp = round_rect_mask(W, H, (btn_x, btn_y, cta_w + 40 * s, btn_h),
                         btn_h / 2)
    img = img * (1 - bp[:, :, None]) + np.array(CORAL, np.float32) * bp[:, :, None]
    add(CTA, F7, cta_sz, btn_x + 20 * s,
        top=btn_y + btn_h / 2 - cta_sz * 0.735 / 2,
        color=(1, 1, 1), tracking=2.2 * s, group="foot")
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
    dy = (card_y + card_h * 0.455) - (content0 + content1) / 2
    for it in panel:
        it["p"].vertices[:, 1] += dy

    for (x, y, w, h, r, rgb) in deferred:
        m = round_rect_mask(W, H, (x, y + dy, w, h), r)[:, :, None]
        img = img * (1 - m) + np.array(rgb, np.float32) * m

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
