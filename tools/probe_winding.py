"""2D probe of the winding stage: the click (now tools/probe_click, the
pull-pawl of log 0027) and the crown-ratchet drive in the height band
of the crown wheel's underside slots. Everything in the ratchet frame
(origin = barrel). Rigid bodies throughout."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math import atan2, cos, degrees, hypot, radians, sin
import numpy as np
import calibers.k1.revc_parts as rp
from tools.probe_escapement import _outline
from tools.probe_click import study
from shapely import affinity
from shapely.ops import nearest_points

for label, fat in (("click, as drawn", 0.0), ("click, printed fat +0.08", 0.08)):
    print(label)
    for k, v in study(fat).items():
        print(f"   {k:18s} {v:.2f}" if isinstance(v, float)
              else f"   {k:18s} {v}")

Z = 16.8
ratchet = _outline(rp.ratchet_c(), z=Z)
crown = _outline(rp.crown_wheel_c(), z=Z)


def contact_edge_angle(poly_r, other):
    """Angle of the ratchet edge at the contact point, off RADIAL (deg):
    ~0-25 = cliff (locks), >50 = ramp (cams)."""
    p1, _ = nearest_points(poly_r, other)
    best = None
    for g in getattr(poly_r, "geoms", [poly_r]):
        c = list(g.exterior.coords)
        for i in range(len(c) - 1):
            a, b = c[i], c[i + 1]
            L2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
            if L2 < 1e-9:
                continue
            t = max(0, min(1, ((p1.x - a[0]) * (b[0] - a[0])
                               + (p1.y - a[1]) * (b[1] - a[1])) / L2))
            px, py = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            d = hypot(p1.x - px, p1.y - py)
            if best is None or d < best[0]:
                best = (d, a, b)
    _, a, b = best
    fd = (b[0] - a[0], b[1] - a[1])
    lf = hypot(*fd)
    fd = (fd[0] / lf, fd[1] / lf)
    rad = (p1.x, p1.y)
    lr = hypot(*rad)
    rad = (rad[0] / lr, rad[1] / lr)
    off_radial = degrees(atan2(abs(fd[0] * -rad[1] + fd[1] * rad[0]),
                               abs(fd[0] * rad[0] + fd[1] * rad[1])))
    return off_radial, (p1.x, p1.y)


def rot(th):
    return affinity.rotate(ratchet, th, origin=(0, 0))


# crown drive: crown at center distance 24 along +x, crown turns CW,
# ratchet must butt-advance CCW ~1:1
def crown_at(phi):
    return affinity.translate(affinity.rotate(crown, phi, origin=(0, 0)),
                              24.0, 0)


th_r = 0.0
phi0 = 0.0                        # find a free crown phase to start
while rot(th_r).intersects(crown_at(phi0)):
    phi0 -= 0.5
adv0 = th_r
jam = None
for step in range(1, 241):
    phi = phi0 - 0.25 * step      # crown CW
    guard = 0.0
    while rot(th_r).intersects(crown_at(phi)) and guard < 20.0:
        th_r += 0.05
        guard += 0.05
    if guard >= 20.0:
        jam = phi
        break
turned = 0.25 * step
print(f"crown CW {turned:.0f} deg -> ratchet CCW {th_r - adv0:.1f} deg "
      f"(1:1 would be {turned:.0f})"
      + (f"  JAM at crown {jam:.1f}" if jam else "  no jam"))
# reverse: crown CCW must cam apart, NOT drive the ratchet backward
th_b = th_r
back_contact = 0.0
for step in range(1, 81):
    phi_b = phi0 - 0.25 * 240 + 0.25 * step
    if rot(th_b).intersects(crown_at(phi_b)):
        ang, _ = contact_edge_angle(rot(th_b), crown_at(phi_b))
        back_contact = max(back_contact, 90 - ang)
print(f"crown reversed 20 deg: ratchet contacts only on edges >= "
      f"{90 - back_contact:.0f} deg off radial (ramps cam apart)"
      if back_contact else "crown reversed 20 deg: no contact at all")
