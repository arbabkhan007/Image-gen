"""Rendering helpers: raster masks from vector paths, glows, gradients, grain."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from PIL import Image, ImageFilter


def _figarr(W, H, draw_fn, supersample=1):
    """Render draw_fn(ax) at W*ss x H*ss and return float mask HxW."""
    w, h = W * supersample, H * supersample
    fig = plt.figure(figsize=(w / 100.0, h / 100.0), dpi=100, facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("black")
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    draw_fn(ax, w, h, supersample)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, 0].astype(np.float32) / 255.0
    plt.close(fig)
    if supersample > 1:
        im = Image.fromarray((buf * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
        buf = np.asarray(im).astype(np.float32) / 255.0
    return buf


def paths_mask(paths, W, H, supersample=1, blur=0.0):
    """Rasterise a list of compound matplotlib paths (already in W/H coords).

    Paths are filled with the nonzero winding rule, which keeps counters
    (letter holes) open because TrueType outlines wind in opposite directions.
    """
    def draw(ax, w, h, ss):
        verts_all, codes_all = [], []
        for p in paths:
            v = np.asarray(p.vertices, dtype=np.float64) * ss
            verts_all.append(v)
            codes_all.append(np.asarray(p.codes))
        verts = np.concatenate(verts_all) if verts_all else np.zeros((0, 2))
        codes = np.concatenate(codes_all) if codes_all else np.zeros(0, dtype=np.uint8)
        ax.add_patch(PathPatch(MPath(verts, codes), facecolor="white",
                               edgecolor="none", antialiased=True))
    m = _figarr(W, H, draw, supersample)
    if blur > 0:
        m = gaussian(m, blur)
    return m


def gaussian(arr, radius):
    if radius <= 0:
        return arr
    if arr.ndim == 2:
        im = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8))
        im = im.filter(ImageFilter.GaussianBlur(radius))
        return np.asarray(im).astype(np.float32) / 255.0
    out = np.empty_like(arr)
    for c in range(arr.shape[2]):
        out[:, :, c] = gaussian(arr[:, :, c], radius)
    return out


def vgrad(H, W, stops):
    """Vertical gradient. stops = [(pos0..1, (r,g,b)), ...] -> HxWx3 float 0..1."""
    ys = np.linspace(0, 1, H, dtype=np.float32)
    cols = np.zeros((H, 3), dtype=np.float32)
    pos = [s[0] for s in stops]
    for c in range(3):
        cols[:, c] = np.interp(ys, pos, [s[1][c] for s in stops])
    return np.repeat(cols[:, None, :], W, axis=1)


def radial(W, H, cx, cy, r, power=1.0, aspect=1.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - cx * W) / (r * W)) ** 2 + ((yy - cy * H) / (r * W * aspect)) ** 2)
    v = np.clip(1.0 - d, 0, 1) ** power
    return v


def screen(base, layer, alpha=1.0):
    a = np.clip(layer * alpha, 0, 1)
    return 1.0 - (1.0 - base) * (1.0 - a)


def tint(mask_rgb, color, strength=1.0):
    return mask_rgb * np.asarray(color, dtype=np.float32) * strength


def grain(H, W, amount=0.012, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    n = gaussian(n * 0.5 + 0.5, 0.6) * 2 - 1
    n *= amount
    return np.repeat(n[:, :, None], 3, axis=2)


def to_pil(arr):
    return Image.fromarray(np.clip(arr * 255.0, 0, 255).astype(np.uint8))
