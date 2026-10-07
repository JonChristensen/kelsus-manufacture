"""Caliber K1 rev C — real parts on the approved massing (Jon's gate,
July 3 2026). Every generator here is the rev B design re-derived onto
REVC_LAYOUT coordinates and the ZC z-map; nothing is free-floating.

Architecture facts this module encodes (derived, not asserted):
- HANGING BARREL: the 80t minute wheel overhangs the barrel center by
  6mm at plane B, so the barrel arbor tops out at z11 — single plate
  bearing, like modern movements. Winding enters from the DIAL side
  (arbor square below the plate; keyless stage builds on it).
- BAY STRAP: with the ring at z7.6 there is no room for a classic
  pallet cock — the removable cassette becomes a thin strap spanning
  the recessed escapement bay, feet screwed to the plate UNDER the
  ring's airspace (M2 x2 = lift the fork out, Jon's serviceability).
- INDIRECT MINUTE: only the minute arbor pierces the plate (through
  bore + dial-side stub) — the 1:1 transfer pair to the central cannon
  is the dial-side stage's job. All other lower pivots are blind.

Parts are modeled at LOCAL XY origin but GLOBAL z (the builder only
translates in XY and rotates for mesh phase).
"""
from math import atan2, cos, degrees, sin, pi, radians, hypot

from build123d import (Align, Box, Circle, Cylinder, Polygon, Pos, Rectangle,
                       RegularPolygon, Rot, extrude)

from . import gears
from .decor import _ccw_polygon, _polyline_band, swirl_windows
from .variants import active_variant
from .revc import (BAY_FLOOR, PLATE_T, REVC_BACKLASH, REVC_LAYOUT, RIM,
                   STRAP_PILOT_Z, ZC, bay_band, bay_stations,
                   bridge_pillar_xy, cock_layout_c, lever_layout_c)

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def _bl():
    return active_variant().backlash


def _counts():
    return REVC_LAYOUT["counts"]


def _clr():
    return active_variant().pivot_clearance


def _drum_wall_o():
    """Drum wall outer radius — the datum the floor, wall, cover lugs AND
    the drop-in cover all key off. Derived from the drum tooth count so a
    tooth-count revision can't leave the cover stranded (it once did: a
    56t->60t change moved the wall out 2mm and the hard-coded cover fell
    through the lugs)."""
    return _counts()[0] / 2 - 1.5


def _press_r():
    """Bore radius that press-grips the Ø3 staff (variant interference)."""
    return 1.5 - active_variant().press_r


def _stack(z0, sections):
    """Bottom-up (face_or_radius, height) sections starting at z0."""
    part, z = None, z0
    for spec, h in sections:
        if isinstance(spec, (int, float)):
            layer = Pos(0, 0, z) * Cylinder(float(spec), h, align=BOTTOM)
        else:
            layer = Pos(0, 0, z) * extrude(spec, h)
        part = layer if part is None else part + layer
        z += h
    return part


def _band(path, half_w):
    return _ccw_polygon(_polyline_band(path, half_w))


# --- the mainplate ------------------------------------------------------------

def mainplate_c():
    """Ø170 x 6.5. Barrel recess, escapement bay (2.5 deep) with its
    lower pivot cups and integral banking pins, blind train bushings,
    the minute through-bore (indirect-minute interface), and every
    screw seat: strap M2, cock + bridge pillars M3 (dial-side hex
    pockets), stand feet M3 at the rim."""
    v = active_variant()
    L = lever_layout_c()
    Zd = _counts()[0]
    part = Cylinder(85, PLATE_T, align=BOTTOM)

    # barrel recess + BLIND arbor cup in its floor: the arbor rises to
    # a real bridge bearing (Jon's NH35 catch) and the dial face under
    # the barrel stays untouched
    bx, by = REVC_LAYOUT["barrel"]
    part -= Pos(bx, by, 2.2) * Cylinder(Zd / 2 - 1.0, 10, align=BOTTOM)
    part -= Pos(bx, by, 0.7) * Cylinder(2.85 + v.pivot_clearance, 2,
                                        align=BOTTOM)

    # escapement bay: union of resident circles + the E-P band (no cusp
    # wedge for the lever arm to hit), floor at BAY_FLOOR
    for (cx, cy), wall_r in bay_stations():
        part -= Pos(cx, cy, BAY_FLOOR) * Cylinder(wall_r, PLATE_T, align=BOTTOM)
    bpath, bhw = bay_band()
    part -= Pos(0, 0, BAY_FLOOR) * extrude(_band(bpath, bhw), PLATE_T)
    # lower pivot cups in the bay floor (escape, pallet, balance staff)
    for (cx, cy), r_cup in ((L["E"], 1.3), (L["P"], 1.3), (L["B"], 1.6)):
        part -= Pos(cx, cy, BAY_FLOOR - 1.8) * Cylinder(
            r_cup + v.pivot_clearance, 2.0, align=BOTTOM)
    # banking pins rise from the bay floor, flanking the fork neck
    for px, py in L["bank_pins"]:
        part += Pos(px, py, BAY_FLOOR) * Cylinder(1.0, 2.3, align=BOTTOM)

    # train bushings: blind from the top (dial face stays clean)...
    for k in ("third", "fourth"):
        x, y = REVC_LAYOUT[k]
        part -= Pos(x, y, PLATE_T - 3.0) * Cylinder(
            1.3 + v.pivot_clearance, 4, align=BOTTOM)
    # ...except the minute arbor: THROUGH (the indirect-minute interface)
    mx, my = REVC_LAYOUT["minute"]
    part -= Pos(mx, my, -1) * Cylinder(1.4 + v.pivot_clearance, 10,
                                       align=BOTTOM)

    # pallet strap screws (M2 thread-forming pilot, blind). Floor at
    # z2.5 = the dial-side solver's cap under the near foot (B2 pockets
    # 1.9 deep + 0.6 web); the strap's foot bosses lift the M2x6 head
    # so its tip lands 0.3 above this (log 0026). Both feet identical.
    # Registered in revc_dial's floor map.
    for fx, fy in L["strap_feet"]:
        part -= Pos(fx, fy, STRAP_PILOT_Z) * Cylinder(0.9, PLATE_T - STRAP_PILOT_Z + 1,
                                                       align=BOTTOM)
    # cock feet + bridge pillars: M3 through, dial-side hex nut pockets
    anchors = list(cock_layout_c()["feet"]) + bridge_pillar_xy()
    for ax, ay in anchors:
        part -= Pos(ax, ay, -1) * Cylinder(1.7, 10, align=BOTTOM)
        part -= Pos(ax, ay, -0.01) * extrude(RegularPolygon(5.7 / 3**0.5, 6), 2.4)
    # stand feet (M3) at the rim
    for az in (30, 150, 270):
        part -= Pos(78 * cos(radians(az)), 78 * sin(radians(az)), -1) * \
            Cylinder(1.7, 12, align=BOTTOM)
    # dial side: stepped pockets for the solved face (revc_dial), Ø2
    # register-post bores, the Ø3 center-post bore, platform M2 screws
    from .revc_dial_parts import PLATFORM_SCREWS, dial_pockets_and_bores
    cuts, posts = dial_pockets_and_bores()
    for cx, cy, pr, depth in cuts:
        part -= Pos(cx, cy, -0.01) * Cylinder(pr, depth + 0.01, align=BOTTOM)
    for name, px, py, tip, top in posts:
        part -= Pos(px, py, -0.01) * Cylinder(1.0 - v.press_r, top + 0.01,
                                              align=BOTTOM)
    part -= Pos(0, 0, -0.01) * Cylinder(1.5 - v.press_r, 5.91, align=BOTTOM)
    # platform M2 pilots: 5.5 deep for the ONE movement-wide screw
    # (M2x6 Taptite, log 0026): 6.0 under-head - 0.8 platform = 5.2 in
    # the plate, +0.3 tip air, 1.0 floor left under the top face. All
    # three sites probed solid to that depth (no pocket, bushing or bay)
    for sx, sy in PLATFORM_SCREWS:
        part -= Pos(sx, sy, -0.01) * Cylinder(0.8, 5.5, align=BOTTOM)
    return part


# --- barrel: hanging drum, dial-side winding ---------------------------------

DRUM_WALL_R = None  # derived below


def drum_c():
    """Going barrel, recessed z2.2-11.0: floor + wall carrying the 60t
    band at plane A. Slim walls inside the gear roots; interior hosts
    the strip (bench-formed; see SPRING_C). Cover rests on three lugs."""
    Zd = _counts()[0]
    r_wall_o = _drum_wall_o()                    # 28.5, inside root r28.65
    floor = Pos(0, 0, ZC["drum"][0]) * Cylinder(r_wall_o, 1.2, align=BOTTOM)
    wall = Pos(0, 0, ZC["drum"][0] + 1.2) * (
        Cylinder(r_wall_o, ZC["drum"][1] - ZC["drum"][0] - 1.2, align=BOTTOM)
        - Cylinder(r_wall_o - 1.5, 20, align=BOTTOM))
    band = gears.wheel_face(Zd, _counts()[1], backlash=_bl(), addendum=0.85) \
        - Circle(r_wall_o - 0.2)
    part = floor + wall + Pos(0, 0, ZC["planeA"][0]) * extrude(band, 3.0)
    part -= Cylinder(2.85 + _clr(), 30)          # arbor bore
    # cover lugs at z9.6 + outer-end hook rib on the inner wall
    for k in range(3):
        a = radians(120 * k + 60)
        part += Pos((r_wall_o - 2.2) * cos(a), (r_wall_o - 2.2) * sin(a),
                    9.6 - 1.2) * Cylinder(1.4, 1.2, align=BOTTOM)
    part += Pos(r_wall_o - 2.6, 0, 3.4) * Box(2.2, 2.2, 4.5, align=BOTTOM)
    return part


ARBOR_SQUARE = 4.0          # across flats: the largest square whose diagonal
#   (5.66) still passes the bridge web bearing (O5.7 + clearance) at assembly
ARBOR_SQUARE_TOP = 19.4     # ratchet seat z16.0..19.4
RATCHET_Z = (16.05, 19.5)   # in the pocket to z17.65, then 1.8 proud of the bridge
RATCHET_BORE = 4.15         # 0.075 a side on the square


def barrel_arbor_c():
    """Two-bearing barrel arbor (Jon's NH35 catch): plate cup below,
    bridge-web bearing above, then the ratchet's square. The square is
    SOLID and 3.4 tall (log 0027 — Jon's bench: the first one was 1.6
    tall and hollowed to a 0.7 wall by a key socket; under half a turn
    of mainspring it let the ratchet climb off even pressed down). It
    now stands 1.7 proud of the bridge, inside the taller ratchet."""
    part = _stack(0.8, [(2.7, 2.75),             # plate cup to drum floor
                        (5.5, 5.9),              # spring hub 3.55-9.45
                        (2.7, 1.4),              # cover journal to 10.85
                        (2.85, 5.15)])           # column to the bridge web
    sq = extrude(Rectangle(ARBOR_SQUARE, ARBOR_SQUARE), ARBOR_SQUARE_TOP - 16.0)
    part += Pos(0, 0, 16.0) * sq                 # ratchet seat
    part += Pos(5.5, 0, 3.4) * Box(2.4, 2.4, 6.2, align=BOTTOM)  # inner hook
    return part


def drum_cover_c():
    """Drop-in lid on the three lugs, flush at z10.8, carrying the
    mainspring's anchor pin on its underside (log 0028). Radius tracks the
    wall: drops inside the wall inner (r_wall_o - 1.5) with 0.2 running
    clearance, overlapping the lug tops (inner edge r_wall_o - 3.6) by
    ~1.9mm so it actually lands."""
    r_cover = _drum_wall_o() - 1.5 - 0.2         # inside the wall, 0.2 clear
    part = Pos(0, 0, 9.6) * Cylinder(r_cover, 1.2, align=BOTTOM)
    part -= Cylinder(2.85 + _clr(), 30)
    # the mainspring's anchor pin (log 0028): down from the underside
    # into the blind hole in the spring's outer tab, chamfered tip
    from build123d import Cone
    px, py = cover_pin_xy()
    pr, pl = SPRING_C["pin_r"], SPRING_C["pin_len"]
    part += Pos(px, py, 9.6 - pl + 0.5) * Cylinder(pr, pl - 0.5 + 0.01, align=BOTTOM)
    part += Pos(px, py, 9.6 - pl) * Cone(pr - 0.45, pr, 0.5, align=BOTTOM)
    return part


SPRING_C = dict(
    strip_t=1.7,        # the kit spring; MAINSPRING_LADDER has the trial rungs
    strip_h=6.0,        # drum interior is 6.2 (floor top 3.4, cover 9.6)
    ring_r=8.5,         # the inner end is a solid ring keyed to the arbor rib
    hub_clr=0.15,       # ring bore over the r5.5 hub
    outer_clr=0.3,      # last coil off the cover lugs' inner face (r24.9)
    root_bump=0.6,      # root is (1 + root_bump) t thick, tapering out
    root_deg=115.0,     # ... over this much of the first turn
    E=2000.0,           # PETG, printed in-line, MPa
    eps_full=0.015,     # 1.5% bending strain = 30 MPa: the wind-to-solid ceiling
    tab_deg=-9.1,       # outer tab centre (the drum rib is at 0); tab is 5 mm
    tab_len=5.0,        #   along the wall, 0.8 outside the previous coil to
                        #   0.4 off the drum wall, CCW face 0.3 off the rib
    pin_r=1.25,         # the COVER's pin (O2.5 x 2.5) drops into a O2.8 hole in
    pin_hole_r=24.3,    #   the tab at this radius: it is what holds the tab
    pin_len=2.5,        #   against the INWARD pull a wound spiral puts on its end
    note="PETG, printed as a relaxed spiral, outward CLOCKWISE in bridge "
         "view (winding turns the arbor CCW, which tightens exactly that "
         "hand). Log 0028: the first spring (2.2 strip, inner C-loop) was "
         "the OTHER hand, so every CCW wind forced it outward against the "
         "wall, and its C-loop/strip junction was a notch; it broke there. "
         "The ring + tapered root replaces the loop; the strip is sized "
         "so the coils pack solid on the ring at ~1.4% strain, i.e. it "
         "cannot be overwound. OUTER END (Jon's bench, same day): a "
         "wound spiral pulls its outer end INWARD, and nothing on a drum "
         "wall faces outward to stop that — the old tab slid off the rib "
         "the moment the right-hand spring took torque. So the cover now "
         "carries a pin into a hole in the tab; the rib still takes the "
         "tangential load. Turns and torque: mainspring_layout().")
MAINSPRING_LADDER = (1.4, 1.7, 2.0)      # strip thicknesses to bench, mm


def mainspring_layout(t=None):
    """The spring's numbers for a strip thickness t (default: the kit's).
    pitch/coils/length describe the printed (relaxed) spiral; turns is
    where the coils pack solid on the ring (the geometric limit, and the
    only stop there is); k_per_turn and torque_full from E t^3 h / L;
    strain_full = pi * turns * t / length, uniform along a spiral strip
    under a pure moment — it must stay under eps_full."""
    from math import sqrt
    C = SPRING_C
    t = C["strip_t"] if t is None else t
    R = C["ring_r"]
    r_lug = _drum_wall_o() - 2.2 - 1.4                    # 24.9
    r0, r_out = R + t / 2, r_lug - C["outer_clr"] - t / 2
    pitch = (1 + C["root_bump"]) * t + 0.9                # next coil clears the root by 0.9
    coils = (r_out - r0) / pitch
    length = pi * (r0 + r_out) * coils
    n_wound = (sqrt(R * R + length * t / pi) - R) / t
    turns = n_wound - coils
    k = pi * C["E"] * t ** 3 * C["strip_h"] / (6 * length)
    turns_safe = min(turns, C["eps_full"] * length / (pi * t))
    return dict(t=t, r0=r0, r_out=r_out, pitch=pitch, coils=coils,
                length=length, turns=turns, k_per_turn=k,
                torque_full=k * turns, strain_full=pi * turns * t / length,
                turns_safe=turns_safe, torque_safe=k * turns_safe)


def _mainspring_centreline(t=None, n=720):
    """[(u, r, phi_deg)] along the strip: u = angle travelled (rad) from
    the root, r its centreline radius, phi its position angle. phi FALLS
    with u — the spiral runs outward clockwise."""
    from math import tau
    L = mainspring_layout(t)
    b = L["pitch"] / tau
    U = L["coils"] * tau
    phi0 = SPRING_C["tab_deg"] + L["coils"] * 360.0
    return [(u, L["r0"] + b * u, phi0 - u * 180 / pi)
            for u in (U * i / n for i in range(n + 1))]


def mainspring_c(t=None):
    """THE mainspring (log 0028): a PETG strip printed as a relaxed
    spiral, running outward CLOCKWISE in bridge view. Inner end: a solid
    ring that drops over the arbor hub with the hub's rib in its keyway,
    the strip growing out of it through a tapered root (no loop, no
    notch). Outer end: a tab just clockwise of the drum wall's rib —
    the rib's clockwise face takes the tangential pull — with a blind
    hole in its top for the drum cover's pin, which takes the INWARD
    pull (a wound spiral lifts its outer coil off the wall; a rib on a
    wall has no outward-facing surface, so a hooked or pocketed tab
    slides off — Jon's bench). The hole is also the up-marker: hole
    toward the cover."""
    from math import tau
    C = SPRING_C
    t = C["strip_t"] if t is None else t
    L = mainspring_layout(t)
    R, h = C["ring_r"], C["strip_h"]
    b = L["pitch"] / tau
    U = L["coils"] * tau
    phi0 = radians(C["tab_deg"]) + U
    uf = radians(C["root_deg"])                  # root taper runs out here
    ua = 0.35 * uf                               # inner face peels off the ring here
    u_start = -1.2                               # root rises out of the ring behind the exit

    def smooth(x):
        x = min(1.0, max(0.0, x))
        return x * x * (3 - 2 * x)

    def r_outer(u):
        bump = C["root_bump"] * t * (1 - smooth(u / uf))
        full = L["r0"] + b * max(u, 0) + t / 2 + bump
        rise = smooth((u - u_start) / (-0.3 - u_start))   # ramp, not a shoulder
        return R + (full - R) * rise

    def r_inner(u):
        return R - 0.05 + b * max(u, 0) * smooth((u - ua) / (uf - ua))

    n = int(L["coils"] * 180)
    us = [u_start + (U - u_start) * i / n for i in range(n + 1)]
    pt = lambda r, u: (r * cos(phi0 - u), r * sin(phi0 - u))
    outer = [pt(r_outer(u), u) for u in us]
    inner = [pt(r_inner(u), u) for u in us]
    face = _ccw_polygon(outer + inner[::-1])       # CW point order would extrude DOWN
    # inner ring: bore over the hub, keyway for its 2.4 x 2.4 rib
    # (x 4.3..6.7), set opposite the root
    face += Circle(R) - Circle(5.5 + C["hub_clr"])
    ka = phi0 + pi
    key = [(4.25, -1.35), (7.25, -1.35), (7.25, 1.35), (4.25, 1.35)]
    face -= Polygon(*[(x * cos(ka) - y * sin(ka), x * sin(ka) + y * cos(ka))
                      for x, y in key], align=None)
    # outer tab: a block from inside the last coil out to 0.4 off the
    # wall, tab_len along the wall, centred on tab_deg; the rib (angle 0)
    # is CCW of it, 0.3 off its CCW face
    r_in = L["r_out"] - L["pitch"] + t / 2 + 0.8      # clears the coil inside it
    r_tab = _drum_wall_o() - 1.5 - 0.4
    half = degrees(C["tab_len"] / 2 / C["pin_hole_r"])
    a0, a1 = radians(C["tab_deg"] - half), radians(C["tab_deg"] + half)
    face += Polygon((r_in * cos(a0), r_in * sin(a0)), (r_tab * cos(a0), r_tab * sin(a0)),
                    (r_tab * cos(a1), r_tab * sin(a1)), (r_in * cos(a1), r_in * sin(a1)),
                    align=None)
    part = Pos(0, 0, 3.5) * extrude(face, h)
    # blind hole from the top for the cover's pin: O(2*pin_r + 0.3), 3 deep
    px, py = cover_pin_xy()
    part -= Pos(px, py, 3.5 + h - 3.0) * Cylinder(C["pin_r"] + 0.15, 5.0, align=BOTTOM)
    return part


def cover_pin_xy():
    """Where the drum cover's pin stands (drum frame: rib at angle 0)."""
    a = radians(SPRING_C["tab_deg"])
    return SPRING_C["pin_hole_r"] * cos(a), SPRING_C["pin_hole_r"] * sin(a)


def stand_foot_c():
    """Desk-stand foot (x3): M3 through, seats against the plate's rim
    holes from the dial side. Lifts the hands/platform clear of the desk."""
    part = Cylinder(6.0, 14.0, align=BOTTOM)
    part -= Cylinder(1.7, 40)
    part -= Pos(0, 0, -0.01) * extrude(RegularPolygon(5.7 / 3**0.5, 6), 2.6)
    return part


# --- train arbors (wheel + pinion + pivots, one print each) -------------------

def minute_arbor_c():
    """14t pinion (A) + 80t wheel (B). The ONE through arbor: dial-side
    stub with a D-flat for the future 1:1 transfer pinion."""
    part = _stack(1.6, [(1.25, 4.9),                       # stub, to plate top
                        (1.9, 0.4),   # DOWN-STOP collar (coda 5): rides
                        #   the plate bore mouth at r1.5-1.9 — the one
                        #   arbor with no cup floor gets its axial seat
                        #   here, at collar radius, never wheel-on-drum
                        (1.75, 0.35),
                        (gears.pinion_face(_counts()[1], backlash=_bl()), 3.0),
                        (3.0, 0.3), (2.3, 0.4), (3.0, 0.3),   # neck with
    #   stepped cone-fillets (coda 5 rev 2: the old O3.5 neck was a
    #   torsion fuse across layer lines — Jon twisted two apart). Drum
    #   tips pass 4.0 from this axis: r3.0 junctions clear by 1.0
                        (gears.wheel_face(_counts()[2], _counts()[3],
                                          backlash=_bl(), addendum=0.85), 3.0),
                        (1.25, 2.0)])   # plain pivot to 16.1: its END
    #   FACE rides the bridge's blind shelf (coda 5 rev 2 — the Ø1.4
    #   reduced tip snapped off in Jon's hands: a 1.5mm^2 column across
    #   layer lines. Same small-radius up-stop, zero fragile features)
    # dial stub stays ROUND: the transfer pinion grips it by friction
    # (slit collet) — that joint is how hands get SET without fighting
    # the whole train (the classic cannon-pinion slip, relocated)
    return part


def third_arbor_c():
    """45t wheel (A) + 7-leaf pinion (B)."""
    return _stack(3.6, [(1.25, 3.3),   # flat pivot end: nose deleted
                        (1.75, 0.35),                 # contact at r0.6
                        (gears.wheel_face(_counts()[4], _counts()[5],
                                          backlash=_bl(), addendum=0.85), 3.0),
                        (2.6, 0.3), (2.0, 0.7),   # neck: fat at the wheel,
    #   r2.0 toward the 8-leaf pinion (minute-wheel tips pass 2.5 from
    #   this axis in the float-overlap zone — 2.0 clears by 0.5)
                        (gears.pinion_face(_counts()[3], backlash=_bl()), 3.0),
                        (1.25, 2.0)])


def fourth_arbor_c():
    """6-leaf pinion (A) + 36t wheel (B). Turns in exactly 60s — the future
    seconds/metronome tap."""
    return _stack(3.6, [(1.25, 3.3),   # flat end, nose deleted (rev 6)
                        (1.75, 0.35),
                        (gears.pinion_face(_counts()[5], backlash=_bl()), 3.0),
                        (1.75, 0.35), (2.2, 0.35), (2.6, 0.3),   # neck:
    #   third-wheel tips pass 2.0 from this axis in the bottom float
    #   zone (1.75 clears by 0.25, as always), then fatten to the wheel
                        (gears.wheel_face(_counts()[6], _counts()[7],
                                          backlash=_bl(), addendum=0.85), 3.0),
                        (1.25, 2.0)])


def escape_arbor_c():
    """Bay-floor pivot, D-seat for the club wheel down in the bay,
    long climb to the 18t pinion at plane B, top pivot into the bridge."""
    part = _stack(2.3, [(1.25, 1.95),                      # bay pivot, flat:
    #   (coda 5 rev 6) the O1.6 noses printed FIRST, shrank under
    #   elephant-foot comp, and snapped off with the wheel supports —
    #   twice on Jon's bench. Flat O2.5 ends survived every early build
                        (1.5, 2.45),                       # D-seat 4.25-6.7
                        (1.75, ZC["planeB"][0] - 6.7),     # the climb
                        (gears.pinion_face(_counts()[7], backlash=_bl()), 3.0),
                        (1.25, 2.0)])
    part -= Pos(1.13 + 15, 0, 4.25) * Box(30, 30, 2.45, align=BOTTOM)  # D-flat
    return part


# --- escapement (register parts: ciechanow.ski anatomy) ------------------------

def club_escape_wheel_c(teeth=None):
    """Deadbeat wheel, r16, t2.4, D-bore Ø3 — teeth leaning back, tip
    foremost (log 0027).

    teeth: the count is beat-rate only — the arbor turns 30 s/rev
    train-fixed, so balance f = teeth/30 Hz. Defaults to the variant's
    esc_teeth: print 16 (0.53 Hz, teeth a 0.4 nozzle renders true),
    metal 30 (the 1 Hz watch beat fine tolerances can hold).

    Re-cut July 2026 after the first bench build: the old club form's
    asymmetry (0.985r at 22% pitch) vanished at 0.4-nozzle scale, so the
    printed teeth read as fat symmetric triangles and the stones landed
    on FLANKS instead of catching tips (Jon's catch). New form measured
    off a published printable clock's wheel (12t, depth 0.66 of tip r,
    faces raked ~50deg) and re-proportioned to our frozen 30t/r16:
    thin hooks, ~33deg raked locking face, 0.25 tip land, concave
    swept-back trailing edge = wide-open gullets; only TIPS touch the
    stones. Parameters derived from measurement, no mesh copied."""
    if teeth is None:
        teeth = active_variant().esc_teeth
    from .revc import tooth_profile_pts
    # the rim's outline comes from ONE source shared with the stone
    # solver (revc.tooth_profile_pts) — the tooth leans back, tip
    # foremost; see TOOTH there for why
    pts = tooth_profile_pts(teeth)
    face = _ccw_polygon(pts)
    for wdw in swirl_windows(4.0, 11.0, spokes=4, spoke_w=3.0):
        face -= wdw
    part = extrude(face, 2.4)
    # D-bore is a PRESS fit on the arbor's seat (coda 5 bench: the old
    # +0.03 clearance bore gave ~5 deg of rotational wiggle — which is
    # wheel PHASE slop, spent straight out of the escapement's gate
    # margins). Interference from the variant (0.03 radial + flat):
    # firm thumb press onto the existing seat — arbors unchanged.
    pr = active_variant().press_r
    bore = Circle(1.5 - pr) - Pos(1.13 - pr, 0) * Rectangle(
        30, 30, align=(Align.MIN, Align.CENTER))
    part -= extrude(bore, 10)                    # drive fit on the D-seat
    return part


ROLLER_PIN_ORBIT = 5.5      # impulse pin centre from the balance axis
ROLLER_PIN_R = 0.9          # impulse pin radius (was 1.25)
FORK_NOTCH_CLR = 0.20       # notch half-width = pin radius + this
FORK_WALL_SHORT = 0.36      # notch walls end this far short of the pin's
#   centre-line position; the horns flare from there
FORK_FLARE_DEG = 60.0       # horn flare, from the fork's axis
FORK_GUARD_REACH = 3.16     # guard dart's tip centre, from the balance axis
FORK_GUARD_TIP_R = 0.3


def swiss_lever_c():
    """The pallet fork on rev C geometry: t2.1 body (bay band), stones
    generated by lever_layout_c for the tips-only wheel (locking face
    crossing the tip circle + traced impulse ramp, log 0026), long
    horns, guard finger, short integral pivots (down into the bay-floor
    cup, up into the strap). Modeled in the PALLET frame (P origin,
    +x toward the balance)."""
    L = lever_layout_c()
    ang = L["ang"]
    t_body = ZC["lever"][1] - ZC["lever"][0]              # 2.1

    def loc(pt):
        dx, dy = pt[0] - L["P"][0], pt[1] - L["P"][1]
        c, s = cos(-ang), sin(-ang)
        return (dx * c - dy * s, dx * s + dy * c)

    face = None
    for poly, via, wa in zip(L["stones"], L["arm_vias"], L["arm_welds"]):
        pts_l = [loc(p) for p in poly]
        stone = _ccw_polygon(pts_l)
        # arm: the tip-contact stones sit ~1mm closer to the wheel than
        # the flank-era ones, so a straight boss-to-stone chord (and its
        # weld corners) dips INSIDE the tip circle — the bench tooth
        # butted the ARM 10 deg before the locking face. Route around:
        # one band out to the layout's waypoint (r18.4 from E at the
        # ENGAGED pose, 3 deg past the stone on its fin side), then
        # hull-weld down onto the outer corners.
        W = loc(via)
        arm = _band([(0, 0), W], 1.3)
        # weld the waypoint cap to the stone's outer corners (hull filler)
        dl = hypot(*W)
        pp = (-W[1] / dl, W[0] / dl)
        # weld onto the stone's BACK PAD, never the fin side (a hull
        # that grabbed the peak would roof the impulse ramp's working
        # notch). The layout supplies TWO anchors strictly interior to
        # the pad, so the joint is a wide strap of real overlap — the
        # single-point weld this replaces fused into one solid but
        # necked to <0.1mm (Jon caught it in the render before the
        # printer could snap it off)
        caps = [(W[0] + s * 1.3 * pp[0], W[1] + s * 1.3 * pp[1])
                for s in (+1, -1)]
        pts = sorted([loc(a) for a in wa] + caps)
        cross = lambda o, a, b: ((a[0] - o[0]) * (b[1] - o[1])
                                 - (a[1] - o[1]) * (b[0] - o[0]))
        hull = []                                 # true convex hull —
        for phase in (pts, pts[::-1]):            # an angle-sort left a
            base = len(hull)                      # void at a reflex corner
            for p in phase:
                while len(hull) - base >= 2 and cross(hull[-2], hull[-1], p) <= 0:
                    hull.pop()
                hull.append(p)
            hull.pop()
        arm += _ccw_polygon(hull)
        face = stone + arm if face is None else face + stone + arm
    face += Circle(3.2)
    fl = L["fork_len"] - ROLLER_PIN_ORBIT                 # to the pin orbit
    face += _band([(0, 0), (fl + 0.7, 0)], 2.4)
    part = extrude(face, t_body)
    # THE FORK END (log 0027, Jon's eye before printing the balance: "I'm
    # just not entirely certain that little three prong area is going
    # to allow that thing to control it"). It could not. Run from the
    # solids (tools/probe_fork): the first end had two straight prongs
    # reaching 0.7 past the pin's centre, and with the fork parked at
    # its banking the returning pin BUTTED the flat end of the near
    # prong 42 deg before centre — a push that turns the fork INTO its
    # banking, i.e. a dead stop. Three changes, which only work together:
    #   - the notch's parallel walls stop FORK_WALL_SHORT short of the
    #     pin's centre-line position; beyond them the horns flare at
    #     FORK_FLARE_DEG, so at either banking the near horn lies outside
    #     the pin's path in and out;
    #   - the pin itself is slimmer (ROLLER_PIN_R) — a fat pin sweeps
    #     through the very place the wall has to stand;
    #   - the guard finger is a pointed dart reaching FORK_GUARD_REACH
    #     from the balance axis. The old square finger stopped 0.3 short
    #     of the safety roller AT CENTRE, so it never touched it at any
    #     fork angle: no safety action at all.
    from math import tan
    a = ROLLER_PIN_R + FORK_NOTCH_CLR
    x_tip = fl - FORK_WALL_SHORT
    reach = 5.0
    notch = Pos(fl - 1.6 + reach / 2, 0) * Rectangle(reach, 2 * a)
    dy = reach * tan(radians(FORK_FLARE_DEG))
    mouth = _ccw_polygon([(x_tip, -a), (x_tip + reach, -a - dy),
                          (x_tip + reach, a + dy), (x_tip, a)])
    # floor at fl-1.6: the pin's deepest sweep is fl - ROLLER_PIN_R
    part -= Pos(0, 0, 0.95) * extrude(notch + mouth, 3)
    # guard level: nothing but the dart reaches toward the balance
    part -= Pos(fl - 1.0 + 15, 0, -0.01) * Box(30, 30, 0.97, align=BOTTOM)
    g = L["fork_len"] - FORK_GUARD_REACH
    dart = _ccw_polygon([(fl - 1.05, -0.6), (g, -FORK_GUARD_TIP_R),
                         (g, FORK_GUARD_TIP_R), (fl - 1.05, 0.6)])
    dart += Pos(g, 0) * Circle(FORK_GUARD_TIP_R)
    part += extrude(dart, 0.95)
    # integral pivots: 2.0 down (tip rides the bay-cup floor), 0.9 up
    # (through the strap's hole, 0.1 witness above it)
    part += Pos(0, 0, -2.0) * Cylinder(1.25, 2.0, align=BOTTOM)
    part += Pos(0, 0, t_body) * Cylinder(1.25, 0.9, align=BOTTOM)
    return part


def bay_strap_c():
    """The rev C pallet cassette: a thin strap across the bay, blind cup
    over the fork's upper pivot, 2x M2 to the plate — remove it, lift
    the fork, service the balance. Rides UNDER the ring (0.6 air).

    Feet (log 0026): r2.2 bosses 1.7 tall carry the M2x6 heads — the
    ONE movement-wide screw — so the tip lands 0.3 above the near
    foot's dial-capped pilot floor (z2.5); the feet sit at 20.8 from P
    so head + boss clear the balance rim by 0.25 (a Ø4 head at the old
    19.5 overlapped the rim by 0.5 — the old service test only checked
    the SHANK radius)."""
    from .revc import STRAP_BOSS_H
    L = lever_layout_c()
    P, feet = L["P"], L["strap_feet"]
    face = _band([loc for loc in (feet[0], P, feet[1])], 3.5)
    for f in feet:
        face += Pos(*f) * Circle(4.0)
    part = Pos(0, 0, ZC["strap"][0]) * extrude(face, ZC["strap"][1] - ZC["strap"][0])
    for fx, fy in feet:                                    # head bosses
        part += Pos(fx, fy, ZC["strap"][1] - 0.01) * Cylinder(
            2.2, STRAP_BOSS_H + 0.01, align=BOTTOM)
    part -= Pos(P[0], P[1], 0) * Cylinder(1.3 + _clr(), 20, align=BOTTOM)
    for fx, fy in feet:
        part -= Pos(fx, fy, 0) * Cylinder(1.1, 20, align=BOTTOM)  # M2 pass
    return part


def roller_c():
    """Two-tier roller for the bay band: safety tier (crescent) below,
    impulse tier (pin at r5.5) above. Friction-fits the Ø3 staff. The
    pin is O1.8, not the O2.5 it started as — see the fork end in
    swiss_lever_c for why the two were redesigned together."""
    saf = Circle(3.2) - Pos(3.4, 0) * Circle(1.4)
    part = Pos(0, 0, ZC["roller_saf"][0]) * extrude(
        saf, ZC["roller_saf"][1] - ZC["roller_saf"][0])
    imp = (Circle(4.4) + Pos(ROLLER_PIN_ORBIT, 0) * Circle(ROLLER_PIN_R)
           + Pos(4.85, 0) * Rectangle(1.3, 1.5))
    part += Pos(0, 0, ZC["roller_imp"][0]) * extrude(
        imp, ZC["roller_imp"][1] - ZC["roller_imp"][0])
    part -= Pos(0, 0, 0) * Cylinder(_press_r(), 20, align=BOTTOM)
    return part


# --- oscillator ----------------------------------------------------------------

def balance_staff_c():
    """The staff IS the register's Ø3 rod: plain cylinder, bay cup to
    cock cup (print: printed; metal: cut steel rod). Grip parts (roller,
    wheel, collet) friction-press onto it."""
    return Pos(0, 0, 2.3) * Cylinder(1.5, 16.1 - 2.3, align=BOTTOM)


BALANCE_WEIGHTS = dict(n=16, r=22.5, af=5.5, depth=2.5)
#   M3 hex nuts (5.5 across flats, 2.4 thick, ~0.40 g steel) pressed
#   into pockets in the rim's top face. 16 at r22.5 bring the balance to
#   the inertia the six M3x8 screws were meant to give it (~5500 g.mm^2).


def balance_weight_poses():
    """(x, y, z, rot_deg) of each nut pocket, balance-local XY."""
    w = BALANCE_WEIGHTS
    z = ZC["ring"][1] - w["depth"]
    return [(w["r"] * cos(2 * pi * k / w["n"]), w["r"] * sin(2 * pi * k / w["n"]),
             z, 360.0 * k / w["n"] + 30.0) for k in range(w["n"])]


def m3_nut_c():
    """M3 hex nut, NOT printed: a balance timing weight. Local origin
    at the centre of its lower face."""
    nut = extrude(RegularPolygon(BALANCE_WEIGHTS["af"] / 3 ** 0.5, 6), 2.4)
    return nut - Cylinder(1.25, 10)


def balance_wheel_c():
    """O52 ring at z7.6-11.0, whirlpool spokes, 16 weight pockets.

    The 16t beat needs more inertia than the printed ring has, and the
    first answer — six M3x8 steel screws through the rim at r23 — never
    fitted (log 0027, Jon's bench): at that radius the hairspring's
    outer coil passes 0.7 above the rim and the pallet strap 0.5 below,
    so nothing may stand proud of either face, and a socket-head M3x8
    stands 3.0 proud on one side and 4.6 on the other. The weights are
    now M3 NUTS pressed flush into hex pockets (flats radial, 0.75 of
    wall outside them, a O1.6 push-out hole under each). Count is the
    bench rate trim: remove them in opposite pairs to speed the beat."""
    win_out = 14.0 if active_variant().esc_teeth == 16 else 20.0
    face = Circle(26.0)
    for w in swirl_windows(5.5, win_out, spokes=3, spoke_w=5.0):
        face -= w
    part = Pos(0, 0, ZC["ring"][0]) * extrude(face, ZC["ring"][1] - ZC["ring"][0])
    bw = BALANCE_WEIGHTS
    for x, y, z, rz in balance_weight_poses():
        part -= Pos(x, y, z) * Rot(0, 0, rz) * extrude(
            RegularPolygon(bw["af"] / 3 ** 0.5, 6), bw["depth"] + 0.01)
        part -= Pos(x, y, 0) * Cylinder(0.8, 30, align=BOTTOM)
    part -= Cylinder(_press_r(), 30, align=BOTTOM)    # same press as the
    #   roller and collet (was a tighter O2.90 that a O2.96 rod refused)
    return part


def hairspring_c():
    """Slit-collet spiral, squeezed to h2.4 for the flat stack; grips
    the Ø3 rod, stud tab pinned to the cock's hanging post."""
    # rate: f = esc_teeth/30 Hz, f^2 ~ k/I. 16t needs k*I to shrink x0.284.
    # The spring alone can't get there: >13 coils in the r8-24 annulus
    # walks the first coil onto the collet lip and the beat slit would
    # sever it. So the spring gives x0.55 (h 2.5->1.75, coils 11->13,
    # L x1.36) and the balance rim gives the rest (I x1.94, see
    # balance_wheel_c): sqrt(0.55/1.94) = 0.532 vs 16/30 target — dead on.
    if active_variant().esc_teeth == 16:
        t, h, r0, r1, coils = 0.45, 1.75, 8.0, 24.0, 13
    else:
        t, h, r0, r1, coils = 0.45, ZC["spring"][1] - ZC["spring"][0], 8.0, 24.0, 11
    theta_end = coils * 2 * pi
    b = (r1 - r0) / theta_end
    outer, inner = [], []
    n = coils * 40
    for i in range(n + 1):
        th = theta_end * i / n
        r = r0 + b * th
        outer.append(((r + t / 2) * cos(th), (r + t / 2) * sin(th)))
        inner.append(((r - t / 2) * cos(th), (r - t / 2) * sin(th)))
    face = Polygon(*(outer + inner[::-1]), align=None)
    face += Circle(r0 - t / 2 + 0.6) - Circle(_press_r() - 0.03)  # collet
    face += Pos(r1 + 3.2, 0) * Circle(3.4)                # stud tab ring
    face += Pos(r1 + 1.2, 0) * Rectangle(4.0, 3.4)
    face -= Pos(r1 + 3.2, 0) * Circle(2.3)                # ring slides OVER
                                                          # the cock's post
    # the SLIT (beat adjust): cuts the collet ring only, at an azimuth
    # where the first coil stands 0.56 off the collet lip (at -x the coil
    # is 0.13 away and the old slit severed the spring in two)
    sa = 5.3                       # rad — clears coil 1 at 11 AND 13 coils
    slit = _ccw_polygon([( (1.0) * cos(sa) - w * -sin(sa),
                           (1.0) * sin(sa) - w * cos(sa)) for w in (-0.25, 0.25)]
                        + [( (8.6) * cos(sa) - w * -sin(sa),
                             (8.6) * sin(sa) - w * cos(sa)) for w in (0.25, -0.25)])
    face -= slit
    part = Pos(0, 0, ZC["spring"][0]) * extrude(face, h)
    return part


COCK_ENDSTONE_Z = 16.3      # the staff's upper stop


def balance_cock_c():
    """Coplanar with the bridge (14.7-17.7): two feet columns down to
    the PLATE (M3 through), arm over the staff with a blind cup that is
    the staff's upper bearing and endstone, stud post hanging to the
    hairspring."""
    ck = cock_layout_c()
    B, feet, stud = ck["B"], ck["feet"], ck["stud"]
    face = _band([feet[0], B, feet[1]], 5.5)
    face += Pos(*B) * Circle(7.0)
    face += _band([B, stud], 2.8)                # stud finger off the boss
    for f in feet:
        face += Pos(*f) * Circle(5.0)
    part = Pos(0, 0, ZC["bridge"][0]) * extrude(face, 3.0)
    for fx, fy in feet:                                   # columns to plate
        part += Pos(fx, fy, PLATE_T) * Cylinder(
            5.0, ZC["bridge"][0] - PLATE_T, align=BOTTOM)
        part -= Pos(fx, fy, 0) * Cylinder(1.7, 30, align=BOTTOM)
    # staff cup with a PRINTED endstone: a blind cup whose flat floor at
    # COCK_ENDSTONE_Z is the staff's upper stop — 0.30 of endshake over
    # a 13.8 staff resting in the plate cup. The cock prints arm-down,
    # so that floor is a clean top-of-layer surface. (The garnet
    # cabochon that used to do this job pressed into a O3.95 pocket
    # from above; on Jon's print it would not stay put — log 0027.)
    part -= Pos(B[0], B[1], ZC["bridge"][0] - 0.01) * Cylinder(
        1.6 + _clr(), COCK_ENDSTONE_Z - ZC["bridge"][0] + 0.01, align=BOTTOM)
    part += Pos(stud[0], stud[1], 11.9) * Cylinder(
        2.15, ZC["bridge"][0] - 11.9 + 0.3, align=BOTTOM) # stud post, fused
    return part


# --- dial-side ratchet + click (M1's proven jamming click, ported) -------------

def click_geometry_c():
    """The click's mounting, in the RATCHET frame (origin = ratchet
    centre): two peg positions and the pose angle. The bridge's pocket,
    peg holes and screw boss are cut from these and are already printed
    — treat them as frozen."""
    pegs = [(18.0, 1.5), (21.5, 1.5)]
    return {"pegs": pegs, "angle_deg": -30.0}


def _click_face():
    """Outline of the FIRST click (block, arced arm, wedge). The bridge
    pocket is this outline offset by 0.6, so it stays exactly as
    printed; the click that now lives there is click_c below, which
    only uses the block end of it."""
    from build123d import Rectangle as R_
    face = Pos(19.5, 1.95) * R_(5.2, 6.5)                 # the block
    face += _band([(17.5, 4.0), (10.5, 10.6), (4.35, 13.1)], 0.65)
    # wedge DEEPENED (coda 5 rev 3 — Jon's bench, twice: a ~0.95mm
    # engagement kept evaporating into print shrink + peg slop). Tip
    # now reaches r11.3 = 1.7 into the r13 tips, 0.6 above the root;
    # winding deflection 1.7mm over the ~16mm PETG arm = ~1.3% strain,
    # well inside PETG's ~5%
    face += _ccw_polygon([(4.0, 13.5), (2.70, 10.97), (6.2, 12.0)])
    #   the wedge's winding-side flank (tip -> (6.2,12.0), ~54 deg off
    #   radial) is the camming surface: the tooth's knee CORNER slides
    #   along it and lifts the click — required because below the knee
    #   the tooth ramp is near-radial and cannot lift anything
    face += Pos(4.55, 13.35) * Circle(0.7)                # fuse the wedge
    return face


CLICK_BOSS_ROOT_R = 5.5     # under-web screw boss: radius where it meets the web
CLICK_BOSS_TIP_R = 3.0      # ...and at its free end (z11.6)
CLICK_SCREW_SEAT_Z = 17.75  # the M2 head sits in the click's counterbore,
#   on 1.6 of block: the tip ends at z11.75, 0.15 inside the under-web
#   boss, with 2.95 of thread in it


def click_screw_xy():
    g = click_geometry_c()
    bx, by = REVC_LAYOUT["barrel"]
    a = radians(g["angle_deg"])
    return (bx + 19.5 * cos(a) - 2.0 * sin(a),
            by + 19.5 * sin(a) + 2.0 * cos(a))


def click_pegs_global():
    g = click_geometry_c()
    bx, by = REVC_LAYOUT["barrel"]
    a = radians(g["angle_deg"])
    return [(bx + x * cos(a) - y * sin(a), by + x * sin(a) + y * cos(a))
            for x, y in g["pegs"]]


def _saw_face(n, r_tip, r_root, cliff_lean_deg=8.0, tip_flat=0.3,
              mirror=False, knee_drop=0.85):
    """Saw-tooth wheel face (coda 4). Per tooth, in +az order: tip flat,
    near-radial CLIFF falling to the root, then one long chordal RAMP
    rising to the next tip. A click riding the ramps passes CCW and
    butts a cliff CW; two of these mesh cliff-to-cliff in the drive
    direction and cam apart ramp-on-ramp in reverse (the real-watch
    crown/ratchet interface). mirror=True flips the handedness."""
    from math import tan
    w = 2 * pi / n
    tf = tip_flat / r_tip / 2
    run = (r_tip - r_root) * tan(radians(cliff_lean_deg)) / (
        (r_tip + r_root) / 2)
    ramp = 0.55 * w              # the ramp's angular share of the pitch;
    #   the rest is a ROOT LAND. Without the land (first cut) the ramp
    #   rose straight off the cliff foot and the pair could not nest at
    #   ANY phase — 0.68mm^3 minimum overlap at center distance 24
    sgn = -1 if mirror else 1
    pts = []
    for k in range(n):
        a = sgn * 2 * pi * k / n
        pts += [(r_tip * cos(a - sgn * tf), r_tip * sin(a - sgn * tf)),
                (r_tip * cos(a + sgn * tf), r_tip * sin(a + sgn * tf)),
                (r_root * cos(a + sgn * (tf + run)),
                 r_root * sin(a + sgn * (tf + run)))]
        for t in (0.5, 1.0):     # root land, sampled to follow the arc
            th = a + sgn * ((tf + run) + t * (w - ramp - tf - run))
            pts.append((r_root * cos(th), r_root * sin(th)))
        # CONVEX ramp knee: the click rides only above r12 (its wedge
        # dips to r12.03), the crown's nesting tip only needs the gap
        # below it — so the ramp is steep below the knee (mesh volume)
        # and shallow above it (a 30-deg top ramp made winding stiff)
        knee_r = r_tip - knee_drop
        knee_az = a + sgn * (w - radians(6.3))   # 6.3 deg of top ramp:
        #   0.85 rise over ~1.35 tangential = ~57 deg off radial.
        #   (A full-depth shallow ramp is IMPOSSIBLE here: 2.3 of rise
        #   at 57 deg needs 14.8 deg of arc and the pitch has 8.25
        #   free — so the deepened click cams on its OWN angled back
        #   instead, the classic pawl move; see _click_face)
        pts.append((knee_r * cos(knee_az), knee_r * sin(knee_az)))
    if mirror:
        pts = pts[::-1]
    return _ccw_polygon(pts)


def ratchet_c():
    """24t RATCHET (a real one, coda 4 — the July wheel was a symmetric
    involute spur, which no click can lock) on the arbor square, FLUSH
    in the bridge-top pocket (z16.05-17.65): winds by key from above,
    holds via the click. Cliffs face CW (bridge view): the click rides
    the ramps winding CCW and butts a cliff against letdown.
    (mirror=True: the first cut of this wheel came out backward —
    slipped at letdown, jammed winding; the directional probe is the
    authority on handedness, not the docstring.)"""
    face = _saw_face(24, 13.0, 10.7, mirror=True)   # root 10.7:
    #   0.3 clearance under the crown tips (24 - 13 = 11.0 grazed 11.0)
    face -= Rectangle(RATCHET_BORE, RATCHET_BORE)         # square bore
    part = Pos(0, 0, RATCHET_Z[0]) * extrude(face, RATCHET_Z[1] - RATCHET_Z[0])
    # 3.45 thick since log 0027: the lower 1.6 sits in the bridge pocket
    # as before, the rest stands proud — where the pull-pawl click works
    # and where the square has room to be 3.4 long. The bore mouth is
    # chamfered: it prints on the bed, and an elephant-footed mouth is a
    # taper that helps the square climb out.
    from build123d import Cone
    part -= Pos(0, 0, RATCHET_Z[0] - 0.01) * Cone(
        RATCHET_BORE * 0.7071 + 0.45, RATCHET_BORE * 0.7071 - 0.15, 0.6,
        align=BOTTOM)
    return part


KNOB_R = 12.5               # winding knob grip radius
KNOB_H = 8.0                # grip height above the flare


def ratchet_knob_c():
    """BENCH TOOL, not a kit part: the ratchet with a finger knob grown
    on top, so the barrel can be wound directly while the crown-and-
    stem train is being redesigned (log 0027). Up to the ratchet's top
    it IS ratchet_c — same saw teeth for the click, same square bore —
    so it drops in where the ratchet sits. Above, a 45-deg flare
    (prints without support, ratchet face down) carries a fluted grip
    that stays inside r12.5: clear of the click, whose pawl lifts
    outward in the plane below it."""
    from build123d import Cone
    part = ratchet_c()
    z0 = RATCHET_Z[1]
    z1 = z0 + (KNOB_R - 10.3)
    part += Pos(0, 0, z0 - 0.01) * Cone(10.3, KNOB_R, z1 - z0 + 0.01,
                                        align=BOTTOM)
    grip = Pos(0, 0, z1) * Cylinder(KNOB_R, KNOB_H, align=BOTTOM)
    for k in range(12):
        a = radians(30 * k)
        grip -= Pos((KNOB_R + 0.9) * cos(a), (KNOB_R + 0.9) * sin(a),
                    z1) * Cylinder(2.2, 20, align=BOTTOM)
    part += grip
    # the square runs 0.4 past the arbor's top, then a round bore to
    # the knob's top — a drift pushes the arbor out for service
    part -= Pos(0, 0, 16.0) * extrude(Rectangle(RATCHET_BORE, RATCHET_BORE),
                                      ARBOR_SQUARE_TOP + 0.4 - 16.0)
    part -= Pos(0, 0, ARBOR_SQUARE_TOP) * Cylinder(1.6, 30, align=BOTTOM)
    return part


# --- the click, second design (log 0027): a PULL-PAWL above the bridge --------
# Jon's bench, Oct 2026: "the click does not hold at all". Measured why:
# the first click was a 1.3-wide kinked flexure that the ratchet pushed
# INTO its own anchor (a strut in compression), and its pocket let the
# tip lift 0.64 where a tooth needs 1.70. So this one (a) is pulled, not
# pushed — the pivot sits on the far side of the contact, 18 deg inside
# the tangent, so load draws the hook INTO the tooth; (b) works in the
# open air above the bridge top, where nothing limits its lift; and (c)
# keeps the printed bridge: same block pocket, same two pegs, same
# screw boss. _click_face() above is now only that pocket's outline.
CLICK_NECK_ROOT = (16.6, 0.5)   # where the flexure neck leaves the plate
CLICK_DRAW_DEG = 18.0           # pivot-contact line vs the tangent at contact
CLICK_NECK = (0.8, 3.0)         # flexure neck width x length
CLICK_BODY = (15.7, 1.5)        # pawl body centreline radius, half width
CLICK_CONTACT_R = 12.0
CLICK_Z = {"pegs": (14.95, 16.15), "block": (16.15, 17.7),
           "plate": (17.7, 19.5), "pawl": (17.9, 19.5)}
CLICK_CBORE_R = 2.15
_CLICK_WEDGE = [(2.95, 13.56), (2.70, 10.97), (6.2, 12.0)]   # lock-outer,
#   tip, cam-outer. Tip and cam flank are the hook the saw teeth were
#   tuned against (coda 5 rev 3), re-aimed. The lock face is new: it
#   leans 8.3 deg like the ratchet's cliff, so the two meet flat (the
#   old face touched at its point only)


def click_pawl_layout():
    """Solve the pawl from where its neck leaves the plate. Click frame
    (origin = ratchet centre, before the angle_deg pose). Returns the
    neck root N0, pivot H (mid-neck), neck end N1, nominal contact C,
    the hook's tip angle and the unit vector u from C toward the pivot."""
    from math import acos, degrees, sqrt
    nx, ny = CLICK_NECK_ROOT
    rc = CLICK_CONTACT_R
    r0, a0 = hypot(nx, ny), atan2(ny, nx)
    sb = sin(radians(CLICK_DRAW_DEG))
    d = (2 * rc * sb + sqrt((2 * rc * sb) ** 2 - 4 * (rc * rc - r0 * r0))) / 2
    c_ang = a0 - acos((rc * rc + r0 * r0 - d * d) / (2 * rc * r0))
    C = (rc * cos(c_ang), rc * sin(c_ang))
    u = ((nx - C[0]) / d, (ny - C[1]) / d)
    ln = CLICK_NECK[1]
    return {"N0": (nx, ny), "u": u, "C": C,
            "H": (nx - ln / 2 * u[0], ny - ln / 2 * u[1]),
            "N1": (nx - ln * u[0], ny - ln * u[1]),
            "tip_deg": degrees(c_ang) + 0.3}


def _click_pawl_face():
    """Neck + curved body + hook, as one face (click frame)."""
    from math import degrees
    L = click_pawl_layout()
    (nx, ny), u, N1 = L["N0"], L["u"], L["N1"]
    rb, hw = CLICK_BODY
    turn = radians(L["tip_deg"]) - atan2(_CLICK_WEDGE[1][1], _CLICK_WEDGE[1][0])

    def rt(p):
        return (p[0] * cos(turn) - p[1] * sin(turn),
                p[0] * sin(turn) + p[1] * cos(turn))

    a1 = degrees(atan2(N1[1], N1[0])) - 3.0
    a2 = L["tip_deg"] + 1.0
    arc = [(rb * cos(radians(a1 + (a2 - a1) * i / 39)),
            rb * sin(radians(a1 + (a2 - a1) * i / 39))) for i in range(40)]
    face = _band(arc, hw)
    for end in (arc[0], arc[-1]):
        face += Pos(*end) * Circle(hw)
    nw = CLICK_NECK[0] / 2
    face += _band([(nx + 0.3 * u[0], ny + 0.3 * u[1]), N1], nw)   # the neck,
    #   rooted 0.3 inside the plate
    lug = [N1, arc[0], arc[3]]                    # blends neck into body
    face += _band(lug, nw + 0.5)
    for q in lug:
        face += Pos(*q) * Circle(nw + 0.5)
    face += _ccw_polygon([rt(q) for q in _CLICK_WEDGE])
    face += Pos(*rt((4.55, 13.35))) * Circle(0.7)
    root = [rt((4.3, 13.3)), (rb * cos(radians(L["tip_deg"] - 2.5)),
                              rb * sin(radians(L["tip_deg"] - 2.5)))]
    face += _band(root, 1.1)                      # hook root, thick: it
    for q in root:                                # carries the offset
        face += Pos(*q) * Circle(1.1)             # between hook and body
    return face


def _click_plate_face():
    """The plate that sits ON the bridge top around the block pocket: an
    L, covering the block and carrying the neck root on an inner strip.
    Below the strip it is cut back so the pawl body swings clear."""
    nx = CLICK_NECK_ROOT[0]
    return _ccw_polygon([(nx, 0.0), (17.9, 0.0), (17.9, -3.6), (24.2, -3.6),
                         (24.2, 7.2), (nx, 7.2)])


def click_c():
    """Pull-pawl click (PETG). From the bottom: two O2.4 pegs and a block
    that drop into the bridge's existing pocket and peg holes; a plate
    that seats on the bridge top and takes the M2 screw in a counterbore;
    and, 0.2 above the bridge, the pawl — hook, curved body, and a 0.8
    flexure neck that is both its pivot and its return spring."""
    g = click_geometry_c()
    z = CLICK_Z
    part = Pos(19.5, 1.95, z["block"][0]) * Box(
        5.2, 6.5, z["block"][1] - z["block"][0] + 0.01, align=BOTTOM)
    for x, y in g["pegs"]:
        part += Pos(x, y, z["pegs"][0]) * Cylinder(
            1.2, z["pegs"][1] - z["pegs"][0] + 0.01, align=BOTTOM)
    part += Pos(0, 0, z["plate"][0]) * extrude(
        _click_plate_face(), z["plate"][1] - z["plate"][0])
    part += Pos(0, 0, z["pawl"][0]) * extrude(
        _click_pawl_face(), z["pawl"][1] - z["pawl"][0])
    part -= Pos(19.5, 2.0, 0) * Cylinder(1.05, 30, align=BOTTOM)   # M2
    part -= Pos(19.5, 2.0, CLICK_SCREW_SEAT_Z) * Cylinder(
        CLICK_CBORE_R, 5, align=BOTTOM)           # head sits recessed
    return part


# --- the winding stage: crown wheel, stud, stem, clip (Jon's gate r6) ----------

def crown_wheel_c():
    """One flat crown wheel at the ratchet plane: 24t m1 spur rim (meshes
    the ratchet) with 23 bevel SLOTS in its underside annulus — meshed
    FROM BELOW by the stem's pinion (the rev B face-slot pair, flipped).
    Rides the shoulder stud; head counterbore keeps everything flush."""
    from math import degrees
    from .revc import WINDING
    # saw rim MIRRORED vs the ratchet: at the mesh the pair engage
    # cliff-to-cliff driving the ratchet CCW (winding), and cam apart
    # ramp-on-ramp if the stem is turned backward (probe-verified)
    face = _saw_face(24, 13.0, 10.7)
    part = Pos(0, 0, 16.05) * extrude(face, 1.6)
    r0, r1 = WINDING["slot_ring"]
    n = WINDING["slots"]                     # 24, = the rim tooth count:
    for k in range(n):                       # slots PHASE-LOCKED under
        a = 360 * k / n + 180.0 / n          # the ramp midlines, so all
        part -= Pos(0, 0, 16.04) * (         # 24 teeth stay identical
            Rot(0, 0, a) * Pos((r0 + r1) / 2, 0, 0) *   # and SOLID (the
            Box(r1 - r0, 1.7, 1.11, align=BOTTOM))      # 23-slot moire
                                             # hollowed half of them)
    part -= Cylinder(2.55 + _clr(), 40)                   # stud bore
    part -= Pos(0, 0, 17.05) * Cylinder(3.7, 2, align=BOTTOM)  # head seat
    # phase trim: the saw pair's clean-nest plateau sits at -1.5..0 deg
    # around the standard mesh convention (asymmetric tooth); -0.75
    # centers it so print slop eats margin on both sides equally
    return Rot(0, 0, -0.75) * part


def crown_stud_c():
    """Shoulder stud: press tail into the bridge web, Ø5.1 bearing
    shoulder, mushroom head flush in the wheel's counterbore."""
    from build123d import Cone
    v = active_variant()
    # press tail = bridge bore (r2.35) + press interference. A stray
    # "+0.35" here shipped a Ø5.34 tail against the Ø4.70 bore — 10x a
    # press fit, and too fat to pass the wheel's own Ø5.32 bore (Jon's
    # bench, Aug 24: "the holes feel too small". They were fine; the
    # tail was the bug). Lead-in cone starts the press square.
    tail = 2.35 + v.press_r
    part = Pos(0, 0, 14.69) * Cone(2.2, tail, 0.4, align=BOTTOM)
    part += Pos(0, 0, 15.09) * Cylinder(tail, 0.91, align=BOTTOM)
    part += Pos(0, 0, 16.0) * Cylinder(2.55, 1.05, align=BOTTOM)
    part += Pos(0, 0, 17.05) * Cylinder(3.55, 0.6, align=BOTTOM)
    return part


def stem_c():
    """The stem, one print: fluted crown OUTSIDE the rim, body through
    the bridge tunnel (clip groove inside), 7t m1 pinion at the tip
    meshing the crown wheel's underside slots. Axis y, z12.8."""
    from build123d import Rot as R_
    from .revc import WINDING
    z = WINDING["stem_z"]
    part = Pos(0, 87.5, z) * R_(-90, 0, 0) * Cylinder(6.8, 7.0, align=BOTTOM)
    for k in range(16):                                   # crown flutes
        a = 360 * k / 16
        part -= Pos(7.1 * cos(radians(a)), 87.5,
                    z + 7.1 * sin(radians(a))) * R_(-90, 0, 0) *             Cylinder(1.1, 8, align=BOTTOM)
    # TWO-PIECE STEM (coda 5 rev 4): the one-print stem could never be
    # installed — O9 pinion on one end, O13.6 crown on the other, a
    # closed O5.4 tunnel between (Jon broke the tunnel boss discovering
    # it; the pose gates never walk the ASSEMBLY PATH). The shaft now
    # ends in a D-flat tip; winding_pinion_c presses on from INSIDE
    # after the stem is through, butting the tunnel's inner face as
    # its inward thrust shoulder. The C-clip is unchanged.
    py = WINDING["pinion_y"] - 1.8            # pinion seat py..py+3.6
    # D-tip is SLIM (Ø3, flat at 1.1): the mating pinion's root circle
    # is only r2.2, so a tip at the shaft's full Ø5 forced a bore that
    # severed all 7 leaves into islands (Jon's print: "7 disconnected
    # tiny pieces"). Ø3 leaves the pinion a 0.73 web ring + full torque
    # capacity on the flat (~7mm^2 of drive face)
    d_tip = Circle(1.5) - Pos(1.1 + 15, 0) * Rectangle(30, 30)
    part += Pos(0, py, z) * R_(-90, 0, 0) * extrude(d_tip, 4.6)
    part += Pos(0, py + 4.6, z) * R_(-90, 0, 0) * Cylinder(
        2.5, 88.0 - (py + 4.6), align=BOTTOM)
    # clip groove inside the tunnel: retention against pull
    part -= (Pos(0, 82.6, z) * R_(-90, 0, 0) *
             (Cylinder(4.0, 1.3, align=BOTTOM) - Cylinder(1.7, 1.3,
                                                          align=BOTTOM)))
    return part


def winding_pinion_c():
    """The stem's 7t pinion, its own print (coda 5 rev 4): D-bore
    presses onto the stem's D-tip FROM INSIDE the tunnel — the only
    assembly order the geometry permits. Modeled flat at origin."""
    v = active_variant()
    part = extrude(gears.pinion_face(7, backlash=_bl()), 3.6)
    bore = Circle(1.5 - v.press_r) - Pos(1.1 - v.press_r + 15, 0) * \
        Rectangle(30, 30)
    part -= extrude(bore, 10)
    return part


def stem_clip_c():
    """Printed C-clip: snaps into the stem's groove behind the tunnel."""
    from .revc import WINDING
    z = WINDING["stem_z"]
    face = Circle(3.3) - Circle(1.75)
    face -= Pos(0, -2.5) * Rectangle(2.6, 5)              # the C opening
    from build123d import Rot as R_
    return Pos(0, 82.65, z) * R_(-90, 0, 0) * extrude(face, 1.2)


# --- fasteners (NOT printed; modeled so the assembled gate sees them) ----------

M2_SCREW = {"head_r": 2.0, "head_h": 1.4, "shank_r": 1.0, "under_head": 6.0}
#   McMaster 94209A343: M2x6 Taptite pan-head Phillips — the ONE M2 screw
#   in the movement (log 0026). Head Ø4 x 1.4-1.6 per the catalog.


def m2x6_screw_c():
    """The M2x6 as a posed solid: head sits on z=0 (bearing face), the
    shank runs DOWN 6.0. Pose with Pos(x, y, z_bearing) [* Rot(180) to
    drive it upward, e.g. the dial platform]. Included in the movement
    build so the assembled-interference gate can catch a head under a
    moving part — which the old shank-radius test did not (log 0026)."""
    s = M2_SCREW
    head = Cylinder(s["head_r"], s["head_h"], align=BOTTOM)
    shank = Pos(0, 0, -s["under_head"]) * Cylinder(s["shank_r"],
                                                   s["under_head"],
                                                   align=BOTTOM)
    return head + shank


def m2_screw_poses():
    """(label, Pos*Rot) for every M2 site: strap x2 (heads on the foot
    bosses), click x1 (head on the click's raised boss), platform x3 (heads on
    the platform's dial face, driving UP into the plate)."""
    from .revc import STRAP_BOSS_H
    from .revc_dial_parts import PLATFORM_SCREWS
    L = lever_layout_c()
    out = []
    for i, (fx, fy) in enumerate(L["strap_feet"]):
        out.append((f"M2x6 strap {i}", Pos(fx, fy, ZC["strap"][1] + STRAP_BOSS_H)))
    out.append(("M2x6 click", Pos(*click_screw_xy(), CLICK_SCREW_SEAT_Z)))
    for i, (sx, sy) in enumerate(PLATFORM_SCREWS):
        out.append((f"M2x6 platform {i}", Pos(sx, sy, -0.8) * Rot(180, 0, 0)))
    return out


# --- the WAVE (2f, Jon's art direction: Hokusai crest + flowing bands,
# solid rim, skeleton openings revealing the train). Structure is safe
# BY CONSTRUCTION: every cut has the keep-outs (pillar roots, pivot
# bosses, winding station, tunnel, rim ring) subtracted before it
# touches the bridge, and all cuts clip inside r69.
# The crest curls around the MINUTE boss — the pivot rides in the eye
# of the wave (the old rev B promise, kept at last). It breaks WESTWARD,
# away from the balance: serenity around the oscillator.

def _wave_keepouts():
    from .revc import WINDING as _W
    L = REVC_LAYOUT
    keep = Pos(*L["barrel"]) * Circle(16.5)               # winding pocket
    keep += Pos(*_W["crown_wheel"]) * Circle(16.2)
    keep += Pos(L["barrel"][0] + 14.3, L["barrel"][1] - 1.3) * Circle(11.5)
    keep += Pos(0, 80, 0) * Rectangle(15, 14)             # stem tab/tunnel
    for px, py in bridge_pillar_xy():
        keep += Pos(px, py) * Circle(7.5)                 # pillar roots
    for k in ("minute", "third", "fourth", "escape"):
        keep += Pos(*L[k]) * Circle(6.0)                  # pivot bosses
    ck = cock_layout_c()
    keep += _band([ck["feet"][0], ck["B"], ck["feet"][1]], 9.0)
    return keep


def traced_wave_faces():
    """The wave, TRACED from art/wave_reference.png (tools/trace_wave.py):
    each white gap is a closed shape subtracted as-drawn. Keep-outs
    (pillar roots, pivot bosses, winding station, tunnel, cock) are
    removed from every cut BEFORE it touches the bridge, and cuts clip
    inside r76 so a solid ~3mm rim ring survives (the mockup's gray
    ring). Structure is safe no matter how wild the art gets."""
    from art.wave_traced import WAVE_POLYS
    keep = _wave_keepouts()
    ring = Circle(76.0)
    faces = []
    for poly in WAVE_POLYS:
        if len(poly) < 4:
            continue
        try:
            f = (_ccw_polygon(poly) & ring) - keep
        except Exception:
            continue
        if f is not None and f.area > 6:
            faces.append(f)
    return faces


# --- the bridge (broad cover; wave openings live in bridge_c below) ------------

def _cock_cutout_face(gap=1.5):
    ck = cock_layout_c()
    B, feet = ck["B"], ck["feet"]
    face = _band([feet[0], B, feet[1]], 5.5 + gap)
    face += Pos(*B) * Circle(8.5 + gap)
    face += _band([B, ck["stud"]], 2.8 + gap)
    for f in feet:
        face += Pos(*f) * Circle(5.0 + gap)
    return face


def bridge_c():
    """ONE broad bridge over everything (14.7-17.7): four rim pillars
    down to the plate, upper pivot holes for the whole train (through,
    with cone lead-ins — a sighted four-pivot landing), and the balance
    bay OPEN to the rim with the cock nestled inside (no orphan rim
    sliver) — the NH35 composition. Plain; the wave pass sculpts it."""
    from build123d import Cone
    L = REVC_LAYOUT
    ck = cock_layout_c()
    B = L["balance"]
    a1 = ck["az"] + radians(26 + 8)
    a2 = ck["az"] - radians(26 + 8)
    wedge = _ccw_polygon([
        (B[0] + 30.5 * cos(a2), B[1] + 30.5 * sin(a2)),
        (B[0] + 95 * cos(a2), B[1] + 95 * sin(a2)),
        (B[0] + 95 * cos(a1), B[1] + 95 * sin(a1)),
        (B[0] + 30.5 * cos(a1), B[1] + 30.5 * sin(a1))])
    from .revc import WINDING as _W
    face = Circle(79.0) - Pos(*B) * Circle(30.0) - _cock_cutout_face() - wedge
    # the stem-tunnel TAB: the bridge reaches the rim over the tunnel
    # boss (Jon's catch: the boss only kissed the r79 edge and floated)
    face += Pos(0, 81.9) * Rectangle(13, 6.2)   # behind the pinion
    part = Pos(0, 0, ZC["bridge"][0]) * extrude(face, 3.0)
    for wf in traced_wave_faces():                        # the TRACED wave
        part -= Pos(0, 0, ZC["bridge"][0] - 0.05) * extrude(wf, 3.2)
    for px, py in bridge_pillar_xy():
        part += Pos(px, py, PLATE_T) * Cylinder(
            4.0, ZC["bridge"][0] - PLATE_T, align=BOTTOM)
        part -= Pos(px, py, 0) * Cylinder(1.7, 30, align=BOTTOM)
    # STEPPED train bearings (coda 5, the printed-jewel move): a
    # r1.35 guide bore up to a SHELF, then r0.85 for the arbor's
    # reduced tip. The arbor's shoulder (r0.7-1.25 annulus) meets the
    # shelf = the UP-stop at small radius, so wheel faces can never
    # reach the bridge. Shelf height = at-rest shoulder + endshake:
    # cup-floored arbors rest 0.1 low (shoulder 14.9), the minute's
    # collar rests at nominal (shoulder 15.0).
    es = active_variant().endshake
    for k, rest_drop in (("minute", 0.0), ("third", 0.1),
                         ("fourth", 0.1), ("escape", 0.1)):
        x, y = L[k]
        # BLIND shelf (coda 5 rev 2): the plain pivot's END FACE is the
        # up-stop — the reduced tip it replaced snapped off in the hand
        # anchored to the pivot end (16.25) so endshake 0.20 lands the
        # shelves at the SAME z as the 0.35/16.1 bridge already printed
        # (coda 5 rev 5: the 0.10 margin between shoulder-stop and
        # face-rub was one short-printed pivot wide — Jon's bench)
        shelf = 16.25 - rest_drop + es
        part -= Pos(x, y, ZC["bridge"][0] - 0.01) * Cylinder(
            1.35, shelf - (ZC["bridge"][0] - 0.01), align=BOTTOM)
        part -= Pos(x, y, shelf - 0.01) * Cylinder(0.6, 4, align=BOTTOM)
        part -= Pos(x, y, ZC["bridge"][0] - 0.01) * Cone(
            1.9, 1.35, 0.5, align=BOTTOM)   # lead-in chamfer — SHORT:
        #   the old 2.3x1.2 cone stayed wider than the guide bore up to
        #   z15.9 and swallowed the shelf entirely (probe-caught)
    # the winding station (Jon's NH35 catch): arbor bearing through the
    # web, ratchet + click recessed FLUSH in the bridge top
    bx, by = L["barrel"]
    g = click_geometry_c()
    from math import cos as c_, sin as s_
    a = radians(g["angle_deg"])
    pocket = Pos(bx, by) * Circle(13.8)
    from build123d import Rot as R2, offset as _off
    pocket += Pos(bx, by) * R2(0, 0, g["angle_deg"]) * _click_face()
    part -= Pos(0, 0, 16.0) * extrude(_off(pocket, 0.6), 2.0)
    part -= Pos(bx, by, ZC["bridge"][0] - 0.01) * Cylinder(
        2.85 + _clr(), 4, align=BOTTOM)                   # arbor bearing
    # crown wheel: flush pocket + stud press bore in the web
    from .revc import WINDING
    cwx, cwy = WINDING["crown_wheel"]
    part -= Pos(cwx, cwy, 16.0) * Cylinder(14.2, 2.0, align=BOTTOM)
    part -= Pos(cwx, cwy, 14.69) * Cylinder(2.35, 1.4, align=BOTTOM)
    # the winding-pinion WINDOW: the pinion reaches through the web to
    # the crown wheel's underside slots (every real movement has this)
    part -= Pos(0, WINDING["pinion_y"], 14.69) * Box(9.5, 8.4, 1.4,
                                                     align=BOTTOM)
    # stem tunnel boss under the bridge (the case-tube analog), with the
    # C-clip slot opening downward inside the run
    from build123d import Rot as R_
    zs = WINDING["stem_z"]
    part += Pos(0, 81.65, zs - 2.5) * Box(11, 5.7, 14.7 - (zs - 2.5),
                                         align=BOTTOM)  # behind the pinion
    part -= Pos(0, 78.7, zs) * R_(-90, 0, 0) * Cylinder(2.7, 20,
                                                        align=BOTTOM)
    part -= Pos(0, 83.25, zs - 2.6) * Box(7.0, 1.6, 6.5, align=BOTTOM)
    for x, y in g["pegs"]:
        px_, py_ = bx + x * c_(a) - y * s_(a), by + x * s_(a) + y * c_(a)
        part -= Pos(px_, py_, 14.69) * Cylinder(1.35, 1.4, align=BOTTOM)
        part -= Pos(px_, py_, 15.69) * Cone(1.35, 1.75, 0.41,
                                            align=BOTTOM)  # mouth chamfer:
        #   the pocket prints face-down and its small holes scar; the
        #   chamfer sheds the scar and leads the peg in (coda 5 rev 5)
    # click M2 pilot: ONE screw for the whole movement (log 0026 —
    # Jon's McMaster order: 94209A343, M2x6 Taptite, the only M2
    # thread-former sold retail). Under-head length 6.0 from the
    # click's top face (z17.65) reaches z11.65 — but the web is only
    # 1.3 thick (z14.7-16.0), so a BOSS hangs under the web to give the
    # screw thread the whole way, floor at z11.6 = 0.6 air over the
    # drum top (drum ends at z11.0; nothing else enters r9 of this XY
    # above z11.05 — probed). The pilot runs THROUGH web + boss (a
    # blind floor would bottom the tip); the screw ends flush with it.
    # The boss is a CONE, root r5.5 on the web tapering to r3.0 at the
    # tip (coda 5 rev 8 — Jon's bench: the old r2.4 stub twisted clean
    # off under the thread-former). The root MUST outrun the two peg
    # holes, which sit 1.6 and 2.1 from the screw axis: they cut the
    # stub's root to 8.3 mm^2 of web, two crescents. Under the cone
    # they are blind (floored by the boss) and the outer root ring
    # lands on unbroken web. The r3.0 tip leaves 2.1 of wall around
    # the pilot against forming hoop stress; narrowing toward the tip
    # it prints support-free (the bridge prints show face down).
    ckx, cky = click_screw_xy()
    part += Pos(ckx, cky, 11.6) * Cone(CLICK_BOSS_TIP_R, CLICK_BOSS_ROOT_R,
                                       14.7 - 11.6 + 0.01,
                                       align=BOTTOM)        # under-web boss
    part -= Pos(ckx, cky, 11.6 - 0.01) * Cylinder(0.9, 16.0 - 11.6 + 0.02,
                                                  align=BOTTOM)  # pilot
    return part
