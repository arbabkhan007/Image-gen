"""Typography / vector engine for the Iqbal Day poster.

Text is shaped with HarfBuzz (real Nastaliq joining + ligatures) and glyph
outlines are pulled from FreeType, converted to cubic/quadratic matplotlib
paths.  Everything is laid out in poster pixel coordinates with the origin at
the top-left, y growing downwards.
"""
import os

import freetype
import numpy as np
import uharfbuzz as hb
from matplotlib.path import Path as MPath

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), "assets", "fonts", "static")

_ft, _hb = {}, {}


def _faces(name):
    if name not in _ft:
        path = os.path.join(FONTS, name)
        _ft[name] = freetype.Face(path)
        blob = hb.Blob.from_file_path(path)
        hbf = hb.Face(blob)
        f = hb.Font(hbf)
        # HarfBuzz advances must be in the same units FreeType outlines use
        f.scale = (hbf.upem, hbf.upem)
        _hb[name] = f
    return _ft[name], _hb[name]


def shape(text, font_name, features=None):
    ft, hbf = _faces(font_name)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    feats = {"kern": True, "liga": True, "calt": True, "curs": True,
             "mark": True, "mkmk": True, "rlig": True, "ccmp": True}
    if features:
        feats.update(features)
    hb.shape(hbf, buf, feats)
    out, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((info.codepoint, x + pos.x_offset, pos.y_offset))
        x += pos.x_advance
    return out, x


def _contours(ft, gid):
    """Return contours as lists of (x, y, tag) with tag in M/L/Q (font units)."""
    ft.load_glyph(gid, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING)
    ol = ft.glyph.outline
    pts, tags, ends = ol.points, ol.tags, ol.contours
    out = []
    start = 0
    for end in ends:
        idx = list(range(start, end + 1))
        start = end + 1
        if not idx:
            continue
        P = [(pts[i][0], pts[i][1], bool(tags[i] & 1)) for i in idx]
        if any(tags[i] & 2 for i in idx):  # cubic — not expected in these fonts
            raise ValueError("cubic outline in font %s" % ft.postscript_name)
        n = len(P)
        # find a starting on-curve point
        s = next((i for i in range(n) if P[i][2]), None)
        if s is None:
            # all off-curve: synthesise on-curve midpoints
            P = [(P[i][0], P[i][1], False) for i in range(n)]
            P = [((P[i][0] + P[(i + 1) % n][0]) / 2, (P[i][1] + P[(i + 1) % n][1]) / 2, True)
                 if i == 0 else P[i] for i in range(n)]
            s = 0
        seq = [P[(s + k) % n] for k in range(n)]
        cont = [(seq[0][0], seq[0][1], "M")]
        ctrl = None
        for (x, y, on) in seq[1:]:
            if on:
                if ctrl is None:
                    cont.append((x, y, "L"))
                else:
                    cont.append((ctrl[0], ctrl[1], "Q"))
                    cont.append((x, y, "Q"))
                    ctrl = None
            else:
                if ctrl is not None:
                    mx, my = (ctrl[0] + x) / 2, (ctrl[1] + y) / 2
                    cont.append((ctrl[0], ctrl[1], "Q"))
                    cont.append((mx, my, "Q"))
                ctrl = (x, y)
        # close
        if ctrl is not None:
            cont.append((ctrl[0], ctrl[1], "Q"))
            cont.append((seq[0][0], seq[0][1], "Q"))
        cont.append((seq[0][0], seq[0][1], "Z"))
        out.append(cont)
    return out


def text_path(text, font_name, size, x=0.0, baseline=0.0, tracking=0.0,
              align="left", features=None):
    """Build a matplotlib Path for `text`.

    Returns (path, width, ink_bbox) in pixel coordinates (y down).
    """
    ft, _ = _faces(font_name)
    scale = size / ft.units_per_EM
    glyphs, adv = shape(text, font_name, features)
    verts, codes = [], []
    width = (adv + tracking * max(0, len(glyphs) - 1)) * scale
    if align == "center":
        x -= width / 2.0
    elif align == "right":
        x -= width
    cursor = 0.0
    for gid, gx, gy in glyphs:
        for cont in _contours(ft, gid):
            for (vx, vy, t) in cont:
                px = x + (vx + gx + cursor) * scale
                py = baseline - (vy + gy) * scale
                if t == "M":
                    verts.append((px, py)); codes.append(MPath.MOVETO)
                elif t == "L":
                    verts.append((px, py)); codes.append(MPath.LINETO)
                elif t == "Q":
                    verts.append((px, py)); codes.append(MPath.CURVE3)
                else:
                    verts.append((px, py)); codes.append(MPath.CLOSEPOLY)
        cursor += tracking
    p = MPath(verts, codes, closed=False)
    return p, width, (adv * scale)


EPS = 0.35


def flatten(path, tol=EPS):
    """Flatten a path into polygons (lists of points) using adaptive subdivision."""
    polys, cur, ctrl = [], [], None
    v = path.vertices
    c = path.codes
    for i in range(len(v)):
        code = c[i]
        pt = tuple(v[i])
        if code == MPath.MOVETO:
            if len(cur) > 1:
                polys.append(cur)
            cur = [pt]
            ctrl = None
        elif code == MPath.LINETO:
            cur.append(pt)
        elif code == MPath.CURVE3:
            if ctrl is None:
                ctrl = pt
            else:
                p0 = cur[-1]
                _quad(p0, ctrl, pt, cur, tol)
                ctrl = None
        elif code == MPath.CURVE4:
            if ctrl is None:
                ctrl = [pt]
            elif len(ctrl) == 1:
                ctrl.append(pt)
            else:
                p0 = cur[-1]
                _cubic(p0, ctrl[0], ctrl[1], pt, cur, tol)
                ctrl = None
        elif code == MPath.CLOSEPOLY:
            if len(cur) > 2:
                polys.append(cur)
            cur = []
            ctrl = None
    if len(cur) > 2:
        polys.append(cur)
    return [p for p in polys if len(p) > 2]


def _quad(p0, p1, p2, out, tol, depth=0):
    # flatness check
    dx, dy = p2[0] - p0[0], p2[1] - p0[1]
    d = abs((p1[0] - p0[0]) * dy - (p1[1] - p0[1]) * dx) / (np.hypot(dx, dy) + 1e-9)
    if d <= tol or depth > 12:
        out.append(p2)
        return
    m01 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    m12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    mid = ((m01[0] + m12[0]) / 2, (m01[1] + m12[1]) / 2)
    _quad(p0, m01, mid, out, tol, depth + 1)
    _quad(mid, m12, p2, out, tol, depth + 1)


def _cubic(p0, p1, p2, p3, out, tol, depth=0):
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    L = np.hypot(dx, dy) + 1e-9
    d1 = abs((p1[0] - p0[0]) * dy - (p1[1] - p0[1]) * dx) / L
    d2 = abs((p2[0] - p0[0]) * dy - (p2[1] - p0[1]) * dx) / L
    if max(d1, d2) <= tol or depth > 12:
        out.append(p3)
        return
    a = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    b = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    cc = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
    d = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    e = ((b[0] + cc[0]) / 2, (b[1] + cc[1]) / 2)
    f = ((d[0] + e[0]) / 2, (d[1] + e[1]) / 2)
    _cubic(p0, a, d, f, out, tol, depth + 1)
    _cubic(f, e, cc, p3, out, tol, depth + 1)
