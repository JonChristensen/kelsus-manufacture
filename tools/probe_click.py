"""2D probe of the pull-pawl click (log 0027), on the BUILT solids.

The pawl is treated as a rigid body pivoting about the middle of its
flexure neck. Everything is in the click frame (origin = ratchet
centre, before the click's pose angle) — the ratchet is periodic, so
its phase against the pose does not matter.

    from tools.probe_click import study
    study()   # -> dict; see the keys below
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math import acos, atan2, degrees, hypot, radians

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon

import calibers.k1.revc_parts as rp
from tools.probe_escapement import _outline

Z_PAWL = 18.7       # mid-height of the pawl band, above the bridge top


def _face_poly(face):
    from shapely import union_all
    verts, tris = face.tessellate(0.005)
    u = union_all([Polygon([(verts[i].X, verts[i].Y) for i in t])
                   for t in tris]).buffer(0)
    return Polygon(u.exterior)


def outlines():
    """(ratchet, pawl, plate, pivot) as shapely polygons + (x, y)."""
    ratchet = _outline(rp.ratchet_c(), z=Z_PAWL)
    whole = _outline(rp.click_c(), z=Z_PAWL)
    plate = _face_poly(rp._click_plate_face())
    rest = whole.difference(plate.buffer(0.02))
    pawl = max(getattr(rest, "geoms", [rest]), key=lambda g: g.area)
    return ratchet, Polygon(pawl.exterior), plate, rp.click_pawl_layout()["H"]


def _nearest_seg(poly, c):
    best = None
    co = list(poly.exterior.coords)
    for i in range(len(co) - 1):
        a, b = co[i], co[i + 1]
        L2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
        if L2 < 1e-12:
            continue
        t = max(0.0, min(1.0, ((c.x - a[0]) * (b[0] - a[0])
                               + (c.y - a[1]) * (b[1] - a[1])) / L2))
        d = hypot(c.x - (a[0] + t * (b[0] - a[0])),
                  c.y - (a[1] + t * (b[1] - a[1])))
        if best is None or d < best[0]:
            best = (d, a, b, L2 ** 0.5)
    return best


def study(fat=0.0):
    """Run the click's contract. `fat` grows both outlines (print
    realism). Keys:
      tension          +1 = the ratchet's letdown push points straight
                       AWAY from the pivot (the neck is pulled)
      draw_lever       moment arm (mm) of that push about the pivot with
                       no friction; NEGATIVE swings the hook INTO the tooth
      lock_face_deg    the ratchet face in contact, degrees off radial
      rest_lift_deg    how far short of its drawn rest position the hook
                       seats (0 as drawn; a fat print sits a little proud)
      wind_jam         ratchet angle of a winding jam, or None
      lift_deg/_mm     the most the pawl must swing out to pass a tooth
      drops_back       the pawl returns to rest between teeth
      gap_tips         pawl body (hook excluded) to the tooth tips
      gap_plate        pawl to plate away from the neck, at rest
      gap_plate_lifted the same at 9 deg of lift
    """
    ratchet, pawl, plate, H = outlines()
    if fat:
        ratchet, pawl = ratchet.buffer(fat), pawl.buffer(fat)
    R = lambda th: affinity.rotate(ratchet, th, origin=(0, 0))
    P = lambda phi: affinity.rotate(pawl, phi, origin=H)   # + = outward
    out = {}

    def settle(th, top=14.0):
        """Least outward swing at which the pawl clears the ratchet."""
        phi = 0.0
        while R(th).intersects(P(phi)):
            phi += 0.1
            if phi > top:
                return None
        return phi

    # where the hook sits deepest, and how deep (a fat print may not
    # reach the drawn rest position: it then rests slightly lifted)
    seats = [(settle(th), th) for th in np.arange(0, 15, 0.25)]
    rest = min(q[0] for q in seats)
    th = float(np.mean([q[1] for q in seats if q[0] == rest]))
    out["rest_lift_deg"] = rest
    start = th
    while not R(th - 0.02).intersects(P(rest)) and start - th < 16:
        th -= 0.02
    hit = R(th - 0.06)
    c = hit.intersection(P(rest)).centroid
    _, a, b, L = _nearest_seg(hit, c)
    n = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
    rc = hypot(c.x, c.y)
    cw = (c.y / rc, -c.x / rc)                 # the ratchet's CW motion
    if n[0] * cw[0] + n[1] * cw[1] < 0:
        n = (-n[0], -n[1])
    to_h = (H[0] - c.x, H[1] - c.y)
    out["tension"] = -(n[0] * to_h[0] + n[1] * to_h[1]) / hypot(*to_h)
    out["draw_lever"] = (c.x - H[0]) * n[1] - (c.y - H[1]) * n[0]
    out["lock_face_deg"] = degrees(acos(min(1.0, abs(
        (b[0] - a[0]) * c.x + (b[1] - a[1]) * c.y) / (L * rc))))
    out["contact_r"] = rc
    th += 0.3
    phis, out["wind_jam"] = [], None
    for _ in range(600):                       # 60 deg = four teeth
        th += 0.1
        phi = settle(th)
        if phi is None:
            out["wind_jam"] = th
            return out
        phis.append(phi)
    phis = np.array(phis)
    tip = min(pawl.exterior.coords, key=lambda q: hypot(*q))
    out["lift_deg"] = float(phis.max())
    out["lift_mm"] = float(radians(phis.max()) * hypot(tip[0] - H[0],
                                                        tip[1] - H[1]))
    out["drops_back"] = bool((phis[150:] < rest + 0.05).any())
    tip_a = atan2(tip[1], tip[0])
    out["gap_tips"] = min(hypot(x, y) for x, y in pawl.exterior.coords
                          if abs(degrees(atan2(y, x) - tip_a)) > 16) - 13.0
    neck = Point(*rp.click_pawl_layout()["N0"]).buffer(1.2)
    out["gap_plate"] = pawl.difference(neck).distance(plate)
    out["gap_plate_lifted"] = P(9.0).difference(neck).distance(plate)
    return out


if __name__ == "__main__":
    for label, fat in (("as drawn", 0.0), ("printed fat +0.08", 0.08)):
        print(label)
        for k, v in study(fat).items():
            print(f"   {k:18s} {v:.2f}" if isinstance(v, float)
                  else f"   {k:18s} {v}")
