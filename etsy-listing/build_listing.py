#!/usr/bin/env python3
"""Photo-first 1:1 Etsy listing set for the crochet turtle pattern."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

OUT = Path("/home/user/Image-gen/etsy-listing")
PHOTO_TURTLE = OUT / "source" / "finished-turtle.jpg"
PHOTO_ROUNDS = OUT / "source" / "first-rounds.jpg"

SIZE = 2000
CREAM = (246, 241, 232)
INK = (42, 48, 38)
SAGE = (107, 127, 90)
SAGE_DEEP = (62, 78, 52)
WHITE = (255, 252, 247)
MUTED = (86, 92, 78)
OLIVE = (74, 90, 56)
YARN_SAGE = (138, 154, 126)
YARN_OLIVE = (90, 108, 72)
YARN_CREAM = (232, 222, 200)

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def fnt(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def cover(path: Path, w: int, h: int, center=(0.5, 0.45), zoom: float = 1.0) -> Image.Image:
    im = Image.open(path).convert("RGB")
    if zoom > 1.01:
        cw, ch = im.size
        nw, nh = max(64, int(cw / zoom)), max(64, int(ch / zoom))
        cx, cy = int(cw * center[0]), int(ch * center[1])
        left = max(0, min(cw - nw, cx - nw // 2))
        top = max(0, min(ch - nh, cy - nh // 2))
        im = im.crop((left, top, left + nw, top + nh))
        center = (0.5, 0.5)
    return ImageOps.fit(im, (w, h), method=Image.Resampling.LANCZOS, centering=center)


def rounded(im: Image.Image, radius: int) -> Image.Image:
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *im.size), radius=radius, fill=255)
    im.putalpha(mask)
    return im


def gradient_panel(w: int, h: int) -> Image.Image:
    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = panel.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        # fade from transparent to cream
        a = int(255 * min(1.0, t * 1.25))
        c = (*CREAM, a)
        for x in range(w):
            px[x, y] = c
    return panel


def save(im: Image.Image, name: str) -> None:
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, CREAM)
        bg.paste(im, mask=im.split()[-1])
        im = bg
    path = OUT / name
    im.convert("RGB").save(path, "JPEG", quality=93, optimize=True, subsampling=1)
    print("wrote", name)


def photo_step(
    name: str,
    photo: Path,
    kicker: str,
    title: str,
    lines: list[str],
    center=(0.5, 0.45),
    panel_h: int = 580,
    zoom: float = 1.0,
) -> None:
    im = cover(photo, SIZE, SIZE, center, zoom=zoom).convert("RGBA")
    # darken lower third slightly so cream text panel sits cleanly
    shade = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, SIZE - panel_h - 80, SIZE, SIZE), fill=(30, 28, 22, 70))
    im = Image.alpha_composite(im, shade)

    panel = Image.new("RGBA", (SIZE, panel_h), (*CREAM, 236))
    im.alpha_composite(panel, (0, SIZE - panel_h))

    # sage top stripe on panel
    d = ImageDraw.Draw(im)
    top = SIZE - panel_h
    d.rectangle((0, top, SIZE, top + 10), fill=SAGE)

    d.text((SIZE // 2, top + 48), kicker.upper(), font=fnt(FONT_SANS_B, 28), fill=SAGE, anchor="mt")
    d.text((SIZE // 2, top + 100), title, font=fnt(FONT_SERIF_B, 70), fill=INK, anchor="mt")

    y = top + 200
    body = fnt(FONT_SANS, 36)
    for line in lines:
        d.text((SIZE // 2, y), line, font=body, fill=MUTED, anchor="mt")
        y += 52

    # thin frame
    d.rectangle((0, 0, SIZE - 1, SIZE - 1), outline=SAGE_DEEP, width=16)
    d.rectangle((20, 20, SIZE - 21, SIZE - 21), outline=WHITE, width=4)
    save(im, name)


def make_01() -> None:
    im = cover(PHOTO_TURTLE, SIZE, SIZE, (0.48, 0.48)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, SIZE - 1, SIZE - 1), outline=SAGE_DEEP, width=16)
    d.rectangle((20, 20, SIZE - 21, SIZE - 21), outline=WHITE, width=4)
    save(im, "01-finished-turtle.jpg")


def make_02_materials() -> None:
    im = Image.new("RGBA", (SIZE, SIZE), CREAM)
    photo = rounded(cover(PHOTO_TURTLE, 2000, 860, (0.5, 0.42)), 0)
    im.paste(photo, (0, 0))
    d = ImageDraw.Draw(im)
    # fade into cream
    fade = Image.new("RGBA", (SIZE, 180), (0, 0, 0, 0))
    fp = fade.load()
    for y in range(180):
        a = int(255 * (y / 179))
        for x in range(SIZE):
            fp[x, y] = (*CREAM, a)
    im.alpha_composite(fade, (0, 700))
    d.rectangle((0, 840, SIZE, SIZE), fill=CREAM)

    d.text((SIZE // 2, 880), "BEFORE YOU START", font=fnt(FONT_SANS_B, 28), fill=SAGE, anchor="mt")
    d.text((SIZE // 2, 930), "Materials", font=fnt(FONT_SERIF_B, 72), fill=INK, anchor="mt")

    items = [
        (YARN_SAGE, "Yarn A  dusty sage", "Worsted · shell"),
        (YARN_OLIVE, "Yarn B  forest olive", "Head, flippers, tail"),
        (YARN_CREAM, "Yarn C  oatmeal cream", "Belly"),
        ((196, 164, 112), "3.5 mm hook", "Or size for tension"),
        (INK, "8 mm safety eyes", "Black, one pair"),
        ((230, 230, 226), "Fiberfill + needle", "Stuffing, marker, scissors"),
    ]
    cols = 2
    start_y = 1080
    for i, (color, title, sub) in enumerate(items):
        col = i % cols
        row = i // cols
        x = 180 + col * 900
        y = start_y + row * 220
        d.ellipse((x, y, x + 72, y + 72), fill=color, outline=OLIVE, width=3)
        d.text((x + 100, y + 4), title, font=fnt(FONT_SERIF_B, 36), fill=INK)
        d.text((x + 100, y + 52), sub, font=fnt(FONT_SANS, 28), fill=MUTED)

    d.rectangle((0, 0, SIZE - 1, SIZE - 1), outline=SAGE_DEEP, width=16)
    d.rectangle((20, 20, SIZE - 21, SIZE - 21), outline=WHITE, width=4)
    save(im, "02-materials.jpg")


def make_all() -> None:
    make_01()
    make_02_materials()

    photo_step(
        "03-magic-ring.jpg",
        PHOTO_ROUNDS,
        "Step 01  ·  Shell",
        "Magic ring",
        [
            "With sage yarn, make a magic ring.",
            "Work 6 single crochet into the ring.",
            "Pull the tail closed. Place a stitch marker.",
            "Do not join — work in a spiral from here.",
        ],
        center=(0.42, 0.58),
        zoom=1.7,
    )
    photo_step(
        "04-first-rounds.jpg",
        PHOTO_ROUNDS,
        "Step 02  ·  Shell",
        "First rounds",
        [
            "Rnd 2: increase in each stitch  (12)",
            "Rnd 3: (sc, inc) around         (18)",
            "Rnd 4: (2 sc, inc) around       (24)",
            "Keep the circle flat. Move the marker up.",
        ],
        center=(0.50, 0.42),
        zoom=1.15,
    )
    photo_step(
        "05-increase-rounds.jpg",
        PHOTO_ROUNDS,
        "Step 03  ·  Shell",
        "Grow the circle",
        [
            "Rnd 5: (3 sc, inc) × 6   (30)",
            "Rnd 6: (4 sc, inc) × 6   (36)",
            "Rnd 7: (5 sc, inc) × 6   (42)",
            "Disc should stay flat — about 9–10 cm across.",
        ],
        center=(0.62, 0.70),
        zoom=1.55,
    )
    photo_step(
        "06-shell-dome.jpg",
        PHOTO_TURTLE,
        "Step 04  ·  Shell",
        "Build the dome",
        [
            "Rnds 8–12: single crochet around (42).",
            "Stop increasing. The circle cups into a bowl.",
            "That bowl is the turtle’s shell.",
            "Fasten off sage yarn.",
        ],
        center=(0.36, 0.48),
        zoom=1.8,
    )
    photo_step(
        "07-shell-texture.jpg",
        PHOTO_TURTLE,
        "Step 05  ·  Shell",
        "Scute texture",
        [
            "Surface-slip-stitch olive hexagon lines,",
            "or work bobble clusters on Rnds 4, 6 and 8.",
            "This gives the classic turtle-shell scutes.",
            "Keep the inside of the dome smooth for stuffing.",
        ],
        center=(0.34, 0.40),
        zoom=2.5,
    )
    photo_step(
        "08-belly.jpg",
        PHOTO_TURTLE,
        "Step 06  ·  Body",
        "Cream belly",
        [
            "With cream yarn, repeat Rnds 1–7 (42 sts).",
            "Do not work the dome — keep a flat oval.",
            "This is the underside of the turtle.",
            "Fasten off and leave a long tail for sewing.",
        ],
        center=(0.50, 0.66),
        zoom=2.3,
    )
    photo_step(
        "09-head.jpg",
        PHOTO_TURTLE,
        "Step 07  ·  Head",
        "Olive head",
        [
            "Magic ring 6. Increase to 24 over 4 rounds.",
            "Rnds 6–10: sc around for a chubby head.",
            "Decrease to 12, stuff firmly, close.",
            "Leave a long olive tail to sew onto the shell.",
        ],
        center=(0.70, 0.36),
        zoom=2.4,
    )
    photo_step(
        "10-safety-eyes.jpg",
        PHOTO_TURTLE,
        "Step 08  ·  Face",
        "Safety eyes",
        [
            "Insert 8 mm eyes between Rnds 6 and 7.",
            "Space them 6 stitches apart, then lock washers.",
            "Embroider a tiny curved smile in dark brown.",
            "Optional: one cream stitch under each eye.",
        ],
        center=(0.72, 0.40),
        zoom=2.35,
    )
    photo_step(
        "11-flippers.jpg",
        PHOTO_TURTLE,
        "Step 09  ·  Limbs",
        "Four flippers",
        [
            "Make 4 in olive. MR 6, increase to 12.",
            "Rnds 3–7: sc around. Flatten and sc closed.",
            "Do not stuff. Leave a tail on each piece.",
            "Two front flippers, two back.",
        ],
        center=(0.48, 0.74),
        zoom=2.2,
    )
    photo_step(
        "12-tail.jpg",
        PHOTO_TURTLE,
        "Step 10  ·  Rear",
        "Tail & back flippers",
        [
            "Back flippers sit under the rear of the shell.",
            "The tail is a tiny pointed leaf: ch 6,",
            "then sc, hdc, dc, hdc, sc. Do not stuff.",
            "Sew it at the center back, between the flippers.",
        ],
        center=(0.18, 0.58),
        zoom=2.1,
    )
    photo_step(
        "13-stuffing.jpg",
        PHOTO_TURTLE,
        "Step 11  ·  Fill",
        "Stuff the shell",
        [
            "Fill the sage bowl with small pinches of fiberfill.",
            "Shape a smooth dome — firm, not rock-hard.",
            "Push stuffing into the edges so the shell",
            "does not dent when the belly is sewn on.",
        ],
        center=(0.38, 0.50),
        zoom=1.7,
    )
    photo_step(
        "14-sew-belly.jpg",
        PHOTO_TURTLE,
        "Step 12  ·  Body",
        "Sew shell to belly",
        [
            "Whip-stitch the cream belly to the shell opening.",
            "Catch flippers and tail in the seam as you go.",
            "Front pair near the head, back pair behind,",
            "tail at the rear. Add stuffing before closing.",
        ],
        center=(0.48, 0.62),
        zoom=1.9,
    )
    photo_step(
        "15-attach-head.jpg",
        PHOTO_TURTLE,
        "Step 13  ·  Assemble",
        "Attach the head",
        [
            "Sew the head to the front of the shell,",
            "slightly tucked under the rim so it peeks out.",
            "Check both eyes sit level before you knot off.",
            "Weave every remaining tail into the body.",
        ],
        center=(0.62, 0.40),
        zoom=1.6,
    )
    photo_step(
        "16-finishing.jpg",
        PHOTO_TURTLE,
        "Step 14  ·  Finish",
        "You made it",
        [
            "Weave ends · pose the flippers · check the smile.",
            "Finished size is about 12 cm / 5 inches long.",
            "Your sage-and-olive turtle is ready.",
        ],
        center=(0.50, 0.46),
        panel_h=520,
        zoom=1.05,
    )


if __name__ == "__main__":
    make_all()
    print("done")
