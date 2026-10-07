"""Bench calibration coupons — the wobble/lockup diagnosis kit (log 0025).

Three fixtures, printed BEFORE any tolerance change is committed:

1. fit_ladder + fit_pin: six copies of the real train bushing (Ø2.6 pivot,
   blind, 3.0 engagement — mainplate geometry verbatim) at radial
   clearances 0.05..0.20. The tightest bore the pin spins dead-free in
   IS the print variant's next pivot_clearance. Tick marks 1..6 index
   the table below.

2. mesh_jig + test gears: three meshes side by side — today's
   third-fourth (45/6), an 8-leaf reference (60/8), and today's
   minute-third (56/7) — each with three pinion stations: center
   distance PINCHED -0.25 (what bore slop does dynamically), NOMINAL,
   and SPREAD +0.30. Ticks: 1=pinch, 2=nominal, 3=spread.

   NOTE (found by the layout solver, this session): a 60/8 recount does
   NOT pack at module 1 — the third wheel must clear the minute pinion
   across the fixed minute-third distance, capping Z3 at
   Zm + p3 - pm - 6 = 45. The train is already AT that limit, so 60/8
   here is a REFERENCE (what an 8-leaf mesh feels like), not a drop-in.
   If 45/6 binds at pinch even with tightened fits while 60/8 stays
   sweet, the fix is architectural (rev D); if both bind, it's module.

Coupons are calibration artifacts, not movement parts — they live in
exports/k1/print/coupons/ with their own generated README, outside the
kit MANIFEST.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math import cos, radians, sin

from build123d import Align, Box, Cylinder, Pos, export_stl, extrude

from calibers.k1 import gears
from calibers.k1.revc import PLATE_T
from calibers.k1.variants import active_variant

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

PIVOT_R = 1.3            # the train pivot, Ø2.6 (revc_parts arbors)
BORE_DEPTH = 3.0         # blind bushing engagement (mainplate_c verbatim)
LADDER_CLEARANCES = [0.05, 0.08, 0.11, 0.14, 0.17, 0.20]   # radial, tick 1..6
JIG_CLEARANCE = 0.11     # jig bores: the ladder-measured running fit
# (First jig ran 0.15: Jon's bench catch, Aug 2026 — under drive the
# tooth separation force parks both pivots on the LOOSE side of their
# bores, so slack bores relieve a drilled pinch back toward nominal.
# The pinch cells therefore measure the form's tolerance of ENTERING
# pinched geometry, not sustained pinch — read them accordingly.)
MESHES = [               # (wheel, pinion, station x of wheel bore, ticks)
    ("A", 45, 6, -55.0, 1),
    ("B", 60, 8, -12.0, 2),
    ("C", 56, 7, 42.0, 3),
]
DELTAS = [-0.25, 0.0, +0.30]      # pinch / nominal / spread, ticks 1/2/3
GEAR_T = 3.0             # train wheel thickness
PIN_LEN = 3.2            # pivot length: 3.0 engagement + 0.2 endshake float


def _tick_marks(part, x, y, n, ang=0.0):
    """n engraved ticks (0.8 x 2.5, 0.6 deep) centered at (x, y) on top,
    the row running along `ang` — each tick long-axis ACROSS the row, so
    neighbors stay distinct."""
    for k in range(n):
        dx = (k - (n - 1) / 2) * 1.6
        tick = Box(0.8, 2.5, 1.2, align=BOTTOM) if ang == 0.0 \
            else Box(2.5, 0.8, 1.2, align=BOTTOM)
        part -= Pos(x + dx * cos(radians(ang)), y + dx * sin(radians(ang)),
                    PLATE_T - 0.6) * tick
    return part


def _blind_bore(part, x, y, r):
    """The mainplate's blind train bushing: floor 3.0 below the top face."""
    part -= Pos(x, y, PLATE_T - BORE_DEPTH) * Cylinder(r, 4, align=BOTTOM)
    return part


def fit_ladder():
    part = Box(76, 14, PLATE_T, align=BOTTOM)
    for i, c in enumerate(LADDER_CLEARANCES):
        x = -27.5 + i * 11.0
        part = _blind_bore(part, x, 0.0, PIVOT_R + c)
        part = _tick_marks(part, x, -4.8, i + 1)
    return part


def fit_pin():
    """Prints disc-down; in use, flipped: pivot into a ladder bore, spin
    and rock the disc — the Ø14 disc is the tilt lever."""
    return (Cylinder(7.0, 2.0, align=BOTTOM)
            + Pos(0, 0, 2.0) * Cylinder(2.5, 3.0, align=BOTTOM)
            + Pos(0, 0, 5.0) * Cylinder(PIVOT_R, PIN_LEN, align=BOTTOM))


def _satellites(wx, z_wheel, z_pinion):
    d0 = gears.center_distance(z_wheel, z_pinion)
    for tick, delta in enumerate(DELTAS, start=1):
        az = (tick - 2) * 12.0                    # -12 / 0 / +12 deg
        d = d0 + delta
        yield tick, wx + d * cos(radians(az)), d * sin(radians(az))


def mesh_jig():
    part = Box(160, 20, PLATE_T, align=BOTTOM)
    r = PIVOT_R + JIG_CLEARANCE
    for _, zw, zp, wx, squares in MESHES:
        part = _blind_bore(part, wx, 0.0, r)
        part = _tick_marks(part, wx - 6.0, -6.5, squares)
        for tick, x, y in _satellites(wx, zw, zp):
            part = _blind_bore(part, x, y, r)
            part = _tick_marks(part, x + 3.5, y, tick, ang=90.0)
    return part


def mesh_wheel(teeth, mate):
    """Test wheel: train tooth form (addendum 0.85 into a low-leaf mate),
    lightening holes, pivot stub. Prints face-down, pivot up."""
    bl = active_variant().backlash
    part = extrude(gears.wheel_face(teeth, mate, backlash=bl, addendum=0.85),
                   GEAR_T)
    hole_r = teeth / 2 * 0.6
    for az in range(0, 360, 72):
        part -= Pos(hole_r * cos(radians(az)), hole_r * sin(radians(az)),
                    -1) * Cylinder(4.0, GEAR_T + 2, align=BOTTOM)
    return part + Pos(0, 0, GEAR_T) * Cylinder(PIVOT_R, PIN_LEN, align=BOTTOM)


def mesh_pinion(teeth):
    """Test pinion: knob to twiddle, face 0.4 taller than the wheel so the
    knob clears the wheel tips, pivot stub. Prints knob-down (brim!)."""
    bl = active_variant().backlash
    return (Cylinder(2.5, 5.0, align=BOTTOM)
            + Pos(0, 0, 5.0) * extrude(gears.pinion_face(teeth, backlash=bl),
                                       GEAR_T + 0.4)
            + Pos(0, 0, 5.0 + GEAR_T + 0.4)
            * Cylinder(PIVOT_R, PIN_LEN, align=BOTTOM))


README = """\
# K1 calibration coupons — wobble / lockup diagnosis (log 0025)

GENERATED by tools/export_fit_coupons.py — edit that, never this file.

All parts class B: 0.12 layers, 4 walls, 100% infill, outer wall 50 mm/s.
Same X-Y hole compensation as your mainplate — the whole point is to
measure the movement's real fits, so change nothing else.

| part | qty | orientation |
|---|---|---|
| fit_ladder | 1 | flat, ticks up |
| fit_pin | 2 | as exported (disc down); brim 5 |
| mesh_jig | 1 | flat, ticks up |
| mesh_w45, mesh_w60, mesh_w56 | 1 each | as exported (face down, pivot up) |
| mesh_p6, mesh_p8, mesh_p7 | 1 each | as exported (knob down); brim 5 — the
first tooth layers print over the knob edge and may sag; that end is cosmetic |

## Test 1 — pivot fit ladder

Bores are the mainplate's blind train bushing verbatim (Ø2.6 pivot,
3.0 mm engagement), at radial clearance by tick count:

| ticks | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| clearance | 0.05 | 0.08 | 0.11 | 0.14 | 0.17 | 0.20 |

(6 ticks = 0.20 = the retired pre-measurement guess.)

Flip a pin into each bore, spin the disc, rock it sideways. Record the
tightest tick where the pin (a) drops in under its own weight, (b) spins
freely > 1 s from a flick, (c) re-seats without force after lifting.
That tick's clearance is the new print `pivot_clearance`. Run BOTH pins:
the spread between them is your printer's pivot-to-pivot variance.

*First measurement (Jon's H2C, Aug 2026): tick 3 → 0.11, now in
variants.py. The two pins differed by ~2 ticks — hence the bench rule:
spin-test every arbor, let spares absorb outliers.*

## Test 2 — mesh jig: one wheel + one pinion at a time

Stations by square count next to the wheel bore:
▪ = 45/6 (today's third-fourth, the suspected binder) ·
▪▪ = 60/8 (8-leaf reference — see note below) ·
▪▪▪ = 56/7 (today's minute-third, the higher-torque control)

Wheel pivot in the station's center bore, pinion in a satellite:
1 tick = center distance PINCHED −0.25, 2 = NOMINAL, 3 = SPREAD +0.30.
Jig bores are the measured running fit (0.11), identical everywhere, so
any difference you feel is the mesh, not the fit. Caveat (Jon's catch):
under drive, tooth separation force parks pivots on the loose side of
their bores — a drilled pinch relieves toward nominal, so the pinch
cell tests entering pinched geometry, not sustained pinch.

Drive the WHEEL rim gently with a fingertip; the pinion is the load
(that's the going-train direction). At each satellite, note: smooth /
gritty / catches. The decisive cell is PINCH on the 6-leaf.

Why 60/8 is only a reference: the layout solver shows a 60t third wheel
cannot clear the minute pinion at module 1 (Z3 caps at 45 in this
architecture) — the current train is at the packing limit, so an 8-leaf
fourth pinion is not a drop-in recount.

## Report back

- Tightest free ladder tick (and whether one pin differs from the other).
- The nine mesh-feel cells (3 meshes x pinch/nominal/spread).

Decision table: if 45/6 is fine at NOMINAL and only binds at PINCH,
tightened fits (Test 1's number) should carry rev C. If 45/6 binds even
at nominal while 60/8 is sweet, the leaf count is the wall → rev D
architecture question. If everything binds at pinch including 60/8,
module 1 itself is marginal on FDM → the scale-up conversation reopens.
"""


def main():
    out = "exports/k1/print/coupons"
    os.makedirs(out, exist_ok=True)
    parts = {
        "fit_ladder": fit_ladder(),
        "fit_pin": fit_pin(),
        "mesh_jig": mesh_jig(),
    }
    for _, zw, zp, _, _ in MESHES:
        parts[f"mesh_w{zw}"] = mesh_wheel(zw, zp)
        parts[f"mesh_p{zp}"] = mesh_pinion(zp)
    for name, part in parts.items():
        export_stl(part, f"{out}/{name}.stl", tolerance=0.02)
        print(f"  {name}.stl")
    with open(f"{out}/README.md", "w") as f:
        f.write(README)
    print(f"wrote {len(parts)} STLs + README -> {out}/")


if __name__ == "__main__":
    main()
