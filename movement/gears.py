"""Cycloidal gear profile generator — the horologically-correct tooth form.

Clock/watch trains use cycloidal (not involute) teeth: wheel teeth get an
epicycloidal addendum traced by a circle rolling on the pitch circle, and
low-count pinions get straight radial flanks with rounded noses. This form
tolerates the low tooth counts (8-16 leaf pinions) that watch trains demand,
where involute teeth would undercut.

Fidelity pass (log 0026 coda 4, Jon's bench: "the train is a little
sticky" + his reference diagram of a true cycloidal pair):
- dedendum flanks are now TRUE HYPOCYCLOIDS (the deep hollow gullets of
  the textbook form), not the old straight-radial shortcut that needed a
  0.35 root relief so pinion noses wouldn't scrape;
- flanks carry 24 sample points (was 12 — the facet flats were part of
  the stickiness at module 1);
- tip corners are eased with a small arc (no square snag corners);
- pinion noses are full semicircles (the 0.65 squash undercut the roll).

All profiles are returned as build123d faces built from sampled polygons —
numerically robust, no exotic B-rep operations.

This module is caliber-agnostic: module/backlash/addendum/dedendum are
explicit. Calibers bind their defaults (see calibers.k1.gears).
"""

from math import atan2, cos, pi, sin

from build123d import Polygon


def _rotate(pts, ang):
    c, s = cos(ang), sin(ang)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def _epicycloid_flank(pitch_r: float, gen_r: float, tip_r: float, n: int = 24,
                      max_ang: float = None):
    """Epicycloid from the pitch circle outward, capped at tip_r.

    Returns points starting ON the pitch circle at angle 0, curving
    outward/forward (+angle).
    """
    pts = []
    t = 0.0
    step = 0.01
    while t < 2.0:
        x = (pitch_r + gen_r) * cos(t) - gen_r * cos((pitch_r + gen_r) / gen_r * t)
        y = (pitch_r + gen_r) * sin(t) - gen_r * sin((pitch_r + gen_r) / gen_r * t)
        r = (x * x + y * y) ** 0.5
        if max_ang is not None and atan2(y, x) >= max_ang:
            break                      # flanks must never cross the midline
        pts.append((x, y))
        if r >= tip_r:
            break
        t += step
    if len(pts) > n:
        idx = [round(i * (len(pts) - 1) / (n - 1)) for i in range(n)]
        pts = [pts[i] for i in idx]
    return pts


def _hypocycloid_flank(pitch_r: float, gen_r: float, root_r: float,
                       n: int = 12):
    """TRUE dedendum flank: hypocycloid of gen_r rolling inside the
    pitch circle — the curve the mate's flank actually rolls against
    (the deep hollow gullet of the textbook cycloidal form). Returns
    points from the pitch circle (angle 0) INWARD to root_r, curving
    into the gullet (-angle side). Degenerates to a radial line when
    gen_r == pitch_r/2, which is why the old straight shortcut *almost*
    worked."""
    pts = []
    t = 0.0
    step = 0.01
    while t < 2.0:
        x = (pitch_r - gen_r) * cos(t) + gen_r * cos((pitch_r - gen_r) / gen_r * t)
        y = (pitch_r - gen_r) * sin(t) - gen_r * sin((pitch_r - gen_r) / gen_r * t)
        r = (x * x + y * y) ** 0.5
        pts.append((x, y if y <= 0 else -y))   # gullet side is -angle
        if r <= root_r:
            break
        t += step
    if len(pts) > n:
        idx = [round(i * (len(pts) - 1) / (n - 1)) for i in range(n)]
        pts = [pts[i] for i in idx]
    return pts


def _ease_corner(prev, corner, nxt, r=0.12):
    """Replace a sharp polygon corner with a 3-point arc blend."""
    import math
    d1 = math.hypot(corner[0] - prev[0], corner[1] - prev[1])
    d2 = math.hypot(nxt[0] - corner[0], nxt[1] - corner[1])
    if d1 < 1e-9 or d2 < 1e-9:
        return [corner]
    t1 = min(r / d1, 0.45)
    t2 = min(r / d2, 0.45)
    a = (corner[0] - (corner[0] - prev[0]) * t1,
         corner[1] - (corner[1] - prev[1]) * t1)
    b = (corner[0] + (nxt[0] - corner[0]) * t2,
         corner[1] + (nxt[1] - corner[1]) * t2)
    mid = ((a[0] + b[0]) / 2 * 0.35 + corner[0] * 0.65,
           (a[1] + b[1]) / 2 * 0.35 + corner[1] * 0.65)
    return [a, mid, b]


def wheel_face(teeth: int, mate_teeth: int, module: float,
               backlash: float, addendum: float = 1.0,
               dedendum: float = 1.3):
    """Face of a cycloidal WHEEL (drives a pinion). Centered at origin.
    addendum: x module; low-leaf mates want ~0.85 (BS978 practice)."""
    m, bl, add = module, backlash, addendum
    R = m * teeth / 2
    tip_r = R + add * m
    root_r = R - dedendum * m
    gen_r = m * mate_teeth / 4          # half the mate pinion's pitch radius

    half_tooth = pi / (2 * teeth) - bl / (2 * R)   # half angular width at pitch
    up = _epicycloid_flank(R, gen_r, tip_r, max_ang=half_tooth * 0.95)
    down = _hypocycloid_flank(R, gen_r, root_r)
    # small residual relief at the very root (print squish safety; the
    # true curve already clears the nose, so 0.15 not the old 0.35)
    relief = 0.15 / root_r

    up_m = [(x, -y) for x, y in up]       # mirrored curves for the
    down_m = [(x, -y) for x, y in down]   # left (+angle) side
    outline = []
    for k in range(teeth):
        a = 2 * pi * k / teeth
        # right side, root -> pitch -> tip: the hypocycloid walked
        # outward (reversed), then the epicycloid; hung at -half_tooth
        right = _rotate([down[-1]], -half_tooth - relief)
        right += _rotate(list(reversed(down)), -half_tooth)
        right += _rotate(up, -half_tooth)
        # left side: mirrored curves, tip -> pitch -> root
        left = _rotate(list(reversed(up_m)), half_tooth)
        left += _rotate(down_m, half_tooth)
        left += _rotate([down_m[-1]], half_tooth + relief)
        # ease BOTH tip corners (flank end <-> tip chord)
        tooth = right + left
        j = len(right) - 1
        eased = (tooth[:j - 1]
                 + _ease_corner(tooth[j - 1], tooth[j], tooth[j + 1])
                 + _ease_corner(tooth[j], tooth[j + 1], tooth[j + 2])
                 + tooth[j + 2:])
        outline += _rotate(eased, a)
    return Polygon(*outline, align=None)


def pinion_face(teeth: int, module: float, backlash: float,
                dedendum: float = 1.3):
    """Face of a cycloidal PINION: radial flanks, FULL rounded noses
    (printed-clock canon; the old 0.65-squashed nose undercut the roll
    and scraped the wheel's gullet on the approach side)."""
    m, bl = module, backlash
    R = m * teeth / 2
    root_r = R - dedendum * m
    half_leaf = pi / (2 * teeth) - bl / (2 * R)
    nose_r = R * sin(half_leaf)         # semicircular nose atop radial flanks

    outline = []
    for k in range(teeth):
        a = 2 * pi * k / teeth
        leaf = [(root_r * cos(-half_leaf), root_r * sin(-half_leaf)),
                (R * cos(-half_leaf), R * sin(-half_leaf))]
        # nose arc: full semicircle centered at (R, 0) bulging outward
        for i in range(13):
            th = -pi / 2 + pi * i / 12
            leaf.append((R + nose_r * cos(th), nose_r * sin(th)))
        leaf += [(R * cos(half_leaf), R * sin(half_leaf)),
                 (root_r * cos(half_leaf), root_r * sin(half_leaf))]
        outline += _rotate(leaf, a)
    return Polygon(*outline, align=None)


def center_distance(z1: int, z2: int, module: float) -> float:
    return module * (z1 + z2) / 2
