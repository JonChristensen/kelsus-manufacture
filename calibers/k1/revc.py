"""Caliber K1 rev C — the flat movement (log 0016 expert brief).

DISCIPLINE FIRST: nothing here is geometry. This module is the
whole-movement model — swept volumes, energy, and the layout solver.
Parts get modeled only after a layout passes check_all() and Jon's
massing gate.
"""
from math import cos, sin, pi, hypot

from movement.solver import Sweep, check_sweeps
from movement.springs import spring_model

RIM = 83.0
PLATE_T = 6.5


MESH_PAIRS = {frozenset(p) for p in [
    ("drum_gear", "min_p"), ("drum", "min_p"), ("min_w", "third_p"), ("third_w", "fourth_p"),
    ("ratchet", "crown_w"), ("ratchet", "b_arbor"), ("crown_w", "stem"),
    ("ratchet", "click_zone"), ("b_arbor", "click_zone"),
    ("drum_gear", "stem"),   # real clearance asserted analytically
    ("fourth_w", "esc_p"), ("esc_w", "lever_hub"), ("esc_w", "lever_fork"),
    ("lever_fork", "roller"), ("lever_fork", "ring"), ("lever_hub", "ring"),
    ("lever_fork", "spring"), ("lever_hub", "spring"),
    # intra-escapement: hub/fork are ONE part, and hub-to-roller spacing
    # is a constant of the mechanism (all on the escape->balance line) —
    # enforced by the escapement probe at part level, not the layout
    ("lever_hub", "lever_fork"), ("lever_hub", "roller"),
]}


def check_all(sweeps, clearance=2.0):
    """THE global test, K1 binding: rim 83, K1's mesh-pair exemptions,
    and the stem exempt from the rim check (it EXITS toward the crown).
    The machinery lives in movement.solver.check_sweeps."""
    return check_sweeps(sweeps, clearance=clearance, rim=RIM,
                        mesh_pairs=MESH_PAIRS, rim_exempt=("stem",))


# --- energy model: spring_model re-exported from movement.springs -------------

def runtime_hours(turns, drum_ratio_to_center):
    """drum period = 1h * ratio (center wheel is exactly 60 min)."""
    return turns * drum_ratio_to_center


# --- the layout solver --------------------------------------------------------
# Chain: drum(Zd) -> [intermediate Zi/pi] -> center(Zc/pc at ORIGIN) ->
# third -> fourth -> escape -> lever span -> balance. Planes A/B alternate
# by mesh parity; escapement+lever plane E above B; ring in the well.

PLANES = {"A": (7.0, 10.5), "B": (11.0, 14.5)}
# Jon's massing note, watch-true: the balance lives ON THE PLATE in its
# own bay — lowest resident, everything steps over it. Escape wheel
# drops to plane A on an extended arbor to meet the lever down there.
# Escapement bay RECESSED 2.5 into the plate (Jon's note; real watches
# do this). Constraint carried to the dial-side solve: no dial pocket
# may share plan-area with this recess (web >= 1.2).
ROLLER_Z = (4.2, 6.7)        # roller + lever + escape wheel, IN the recess
RING = (7.6, 11.0)           # ring just over the plate (0.6 air over the
                             # pallet strap — the flat-movement squeeze)
SPRING_Z = (11.7, 14.2)
BRIDGE = (14.7, 17.7)        # ONE bridge, well over the bay
COCK = (14.7, 17.7)          # coplanar cock — nothing higher
BAY_FLOOR = 4.0              # escapement recess floor (2.5 into the plate)
STRAP_PILOT_Z = 2.5          # strap M2 pilot floor: the dial-side solver's
                             # cap under the near foot (B2 pockets 1.9 deep +
                             # 0.6 web); the strap's 1.7 foot bosses lift the
                             # M2x6 head so its tip lands 0.3 above this
STRAP_FEET_R = 20.8          # feet from P along the strap: O4 screw heads on
                             # r2.2 bosses clear the balance rim (r26) by 0.25
                             # — at the old 19.5 a Ø4 head overlapped it 0.5
STRAP_BOSS_H = 1.7           # foot boss height (log 0026)


def _station_sweeps(kind, x, y, counts):
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = counts
    drum_r = (Zd + 6) / 2
    dh = 4.8 + 6.0
    S = {
        # drum body tucked INSIDE its gear roots, and RECESSED into the
        # mainplate (real-watch move) so its body clears plane B above
        "barrel": [Sweep("drum", x, y, Zd/2 - 1.5, 2.2, 11.0),
                   Sweep("drum_gear", x, y, Zd/2 + 1, *PLANES["A"]),
                   Sweep("b_arbor", x, y, 2.85, 11.0, BRIDGE[1])],
        "minute": [Sweep("min_p", x, y, pm/2 + 1, *PLANES["A"]),
                   Sweep("min_w", x, y, Zm/2 + 1, *PLANES["B"])],
        "third": [Sweep("third_p", x, y, p3/2 + 1, *PLANES["B"]),
                  Sweep("third_w", x, y, Z3/2 + 1, *PLANES["A"])],
        "fourth": [Sweep("fourth_p", x, y, p4/2 + 1, *PLANES["A"]),
                   Sweep("fourth_w", x, y, Z4/2 + 1, *PLANES["B"])],
        "escape": [Sweep("esc_p", x, y, pe/2 + 1, *PLANES["B"]),
                   Sweep("esc_w", x, y, 17, *ROLLER_Z)],
        "balance": [Sweep("roller", x, y, 7, *ROLLER_Z),
                    Sweep("ring", x, y, 26, *RING),
                    Sweep("spring", x, y, 26, *SPRING_Z)],
    }
    return S[kind]


def solve_layout(step=12):
    """Staged placement, pruned. The minute wheel is FREE (hands reach
    the central cannon via a 1:1 dial-side transfer pair — indirect
    minute, classic practice). Chain: drum(A)->minP(A); minW(B)->
    thirdP(B); thirdW(A)->fourthP(A); fourthW(B)->escP(B); escW(E).
    Exactness: minute wheel = 60 min via drum ratio; fourth = 60 s;
    escape = 30 s (30t at 1 Hz). Barrel azimuth fixed (symmetry)."""
    from math import radians
    menu = [
        # (Zd, pm, Zm, p3, Z3, p4, Z4, pe): (Zm/p3)*(Z3/p4) == 60 exact;
        # Z4/pe == 2 (30s escape). Minute wheel CAPPED at 56t so its tip
        # (r29) clears the barrel center (mesh d 35) by the arbor column
        # + air — Jon's NH35 catch: the ratchet belongs on the MOVEMENT
        # side, so the barrel arbor must rise to the bridge.
        # 60/10 drum = 6h/rev (MORE spring room: ~17h runtime); minute
        # pinion r6 clears the coplanar third wheel; minute wheel r29
        # clears the barrel arbor column. (56/7)(45/6) = 60.000 exact.
        (60, 10, 56, 7, 45, 6, 36, 18),
    ]
    best = None
    for counts in menu:
        Zd, pm, Zm, p3, Z3, p4, Z4, pe = counts
        if abs((Zm / p3) * (Z3 / p4) - 60) > 1e-9 or Z4 != 2 * pe:
            continue
        d_bm = (Zd + pm) / 2
        d_mt, d_tf, d_fe = (Zm + p3) / 2, (Z3 + p4) / 2, (Z4 + pe) / 2
        def ring_pts(cx, cy, d):
            for az in range(0, 360, step):
                yield (cx + d * cos(radians(az)),
                       cy + d * sin(radians(az)))

        b_max = int(RIM - 1 - (Zd + 6) / 2)
        # dial-side reservation: the drum recess plan edge must stay
        # >= 10.7 from the ORIGIN (the moon pinion's pocket lives there)
        b_min = int(Zd / 2 - 1 + 10.7) + 1
        for b_r in range(b_max, b_min - 1, -4):
          bx, by = 0.0, float(b_r)
          base = _station_sweeps("barrel", bx, by, counts)
          for mx, my in ring_pts(bx, by, d_bm):
              s1 = base + _station_sweeps("minute", mx, my, counts)
              if check_all(s1):
                  continue
              for tx, ty in ring_pts(mx, my, d_mt):
                  s2 = s1 + _station_sweeps("third", tx, ty, counts)
                  if check_all(s2):
                      continue
                  for fx, fy in ring_pts(tx, ty, d_tf):
                      s3 = s2 + _station_sweeps("fourth", fx, fy, counts)
                      if check_all(s3):
                          continue
                      for ex, ey in ring_pts(fx, fy, d_fe):
                          s4 = s3 + _station_sweeps("escape", ex, ey, counts)
                          if check_all(s4):
                              continue
                          for Bx, By in ring_pts(ex, ey, 40.0):
                              s5 = s4 + _station_sweeps("balance", Bx, By, counts)
                              ux, uy = (Bx - ex) / 40.0, (By - ey) / 40.0
                              s5.append(Sweep("lever_hub", ex + 20.6*ux,
                                              ey + 20.6*uy, 13, *ROLLER_Z))
                              s5.append(Sweep("lever_fork", ex + 34.0*ux,
                                              ey + 34.0*uy, 5, *ROLLER_Z))
                              if check_all(s5):
                                  continue
                              reach = max(hypot(s.x, s.y) + s.r for s in s5)
                              cand = (reach, dict(
                                  counts=counts, barrel=(bx, by),
                                  minute=(round(mx,1), round(my,1)),
                                  third=(round(tx,1), round(ty,1)),
                                  fourth=(round(fx,1), round(fy,1)),
                                  escape=(round(ex,1), round(ey,1)),
                                  balance=(round(Bx,1), round(By,1))))
                              if best is None or cand[0] < best[0]:
                                  best = cand
    return best


# --- THE REV C LAYOUT (solver output, frozen; Jon's massing gate next) -------
REVC_LAYOUT = {
    # Zd, pm, Zm, p3, Z3, p4, Z4, pe: 60/10 drum (6h/rev), 56t minute
    # (clears the barrel ARBOR COLUMN - Jon's NH35 catch: the ratchet
    # lives on the MOVEMENT side, recessed flush in the bridge top),
    # 45/6 third, 36/18 fourth/escape. (56/7)(45/6) = 60.000 exact.
    "counts": (60, 10, 56, 7, 45, 6, 36, 18),
    "barrel": (0.0, 41.0),                   # drum recessed z2.2-11.0;
    "minute": (-30.3, 23.5),                 #  y>=40: dial reservation
    "third": (-46.1, -3.8),
    "fourth": (-41.6, -28.9),
    "escape": (-14.6, -28.9),
    "balance": (25.4, -28.9),
    "lever_span": 40.0,
    "drum_ratio": 6.0,                       # 6 h/rev x ~2.8 turns = ~17 h
    # v4: movement-side ratchet architecture; bay recessed; clearance
    # 2.0 everywhere; stack still tops at COCK z1 = 17.7
}


# --- the winding station (Jon's NH35 catch, completed): ratchet + click
# flush in the bridge-top pocket, crown wheel outboard toward 12, stem
# entering over the rim like a pocket-watch pendant. The stem's pinion
# must clear the crown wheel's top: the pendant boss stands proud of the
# bridge at the rim — THE open question for Jon's massing gate.
# WINDING DIRECTION (derived, coda 4): the direction chain (revc_dial:
# minute CW in bridge view) puts the DRUM at CCW (bridge view) when
# running, so the spring torques the arbor CW and the click must BLOCK
# CW. Winding = ratchet CCW seen from the bridge side (soft clicks);
# crown wheel then turns CW, and the crown knob, viewed from directly
# above the crown looking down the stem, turns COUNTER-clockwise.
WINDING = {
    # 6498-true: the crown wheel is ONE flat wheel at the ratchet plane
    # with 23 bevel SLOTS cut into its UNDERSIDE annulus; the winding
    # pinion meshes it FROM BELOW (rev B's proven face-slot pair,
    # flipped — the height cost becomes a height savings). Stem axis
    # z12.8, dead in the corridor; nothing above the bridge (Jon's
    # section-view catch).
    "ratchet_r": 13.6, "pocket_z": (16.05, 17.65),
    "crown_wheel": (0.0, 65.0),              # 24t x 24t m1: exactly 24
    "slot_ring": (9.5, 13.0),                # spans the pinion tip chord
    "slots": 24,                             # = m1 pitch at ring r12.0.
    #   24, NOT 23 (coda 4): 23 slots against the rim's 24 teeth drift
    #   0.65 deg/tooth — one full moire cycle per revolution, so slots
    #   pass from under-gap (solid teeth) to under-tooth (hollowed:
    #   Jon's bottom-view screenshot, 9 o'clock vs 3 o'clock). 24 slots
    #   phase-locked under the gullets leave every tooth identical and
    #   solid; the pitch-true working ring moves 11.5 -> 12.0, so
    "stem_z": 12.8,                          # pinion tip dips 1.1 into
    "pinion_y": 77.0,                        #  the slots from below.
    #   (was 76.5; the printed bridge's web window spans y72.3-80.7 and
    #   the moved pinion needs 73.9-80.1 — old bridges still fit)
    "stem_y": (74.7, 94.5),
    "module_bay": (56.0, 18.0, 18.0),        # reserved: metronome barrel
}


def winding_sweeps():
    """The winding station + reservations as gate-covered volumes."""
    bx, by = REVC_LAYOUT["barrel"]
    cw = WINDING["crown_wheel"]
    z0, z1 = WINDING["pocket_z"]
    s = [Sweep("ratchet", bx, by, WINDING["ratchet_r"], z0, z1),
         Sweep("crown_w", cw[0], cw[1], WINDING["ratchet_r"], z0, z1),
         Sweep("click_zone", bx + 14.3, by - 1.3, 9.5, z0, z1,
               rotating=False),
         # the winding pinion's swept cylinder + the stem run. Vertical
         # cans over-approximate a horizontal cylinder, so drum_gear x
         # stem is whitelisted and the REAL cylinder-to-tip clearance
         # (>=2.0) is asserted analytically in the test suite.
         Sweep("stem", 0.0, WINDING["pinion_y"], 4.6,
               WINDING["stem_z"] - 4.4, WINDING["stem_z"] + 4.4),
         Sweep("stem", 0.0, 81.0, 2.7, WINDING["stem_z"] - 2.5,
               WINDING["stem_z"] + 2.5),
         Sweep("stem", 0.0, 87.0, 2.7, WINDING["stem_z"] - 2.5,
               WINDING["stem_z"] + 2.5)]
    mx, my, mr = WINDING["module_bay"]
    s.append(Sweep("module_bay", mx, my, mr, 7.0, 14.5, rotating=False))
    return s


# --- THE COMPONENT INVENTORY: everything that lives in the movement.
# The massing BUILDS from this list and a test fails if it forgets one —
# Jon's rule: no massing without reciting the full cast first.
INVENTORY = [
    # (label, source): sweeps come from the gate model; zones are static
    ("mainplate", "plate"), ("bridge", "zone"), ("balance cock", "zone"),
    ("pallet strap", "zone"), ("drum", "sweep"), ("drum_gear", "sweep"),
    ("b_arbor", "sweep"), ("min_p", "sweep"), ("min_w", "sweep"),
    ("third_p", "sweep"), ("third_w", "sweep"), ("fourth_p", "sweep"),
    ("fourth_w", "sweep"), ("esc_p", "sweep"), ("esc_w", "sweep"),
    ("lever_hub", "sweep"), ("lever_fork", "sweep"), ("roller", "sweep"),
    ("ring", "sweep"), ("spring", "sweep"),
    ("ratchet", "sweep"), ("crown_w", "sweep"), ("click_zone", "sweep"),
    ("stem", "sweep"),
    ("dial works", "dial"), ("dial platform", "dial"),
]


def revc_sweeps():
    """The frozen layout as swept volumes — THE global gate."""
    L = REVC_LAYOUT
    counts = L["counts"]
    s = []
    for k in ("barrel", "minute", "third", "fourth", "escape", "balance"):
        kind = "minute" if k == "minute" else k
        s += _station_sweeps(kind, *L[k], counts)
    s += winding_sweeps()
    ex, ey = L["escape"]
    Bx, By = L["balance"]
    ux, uy = (Bx - ex) / 40.0, (By - ey) / 40.0
    s.append(Sweep("lever_hub", ex + 20.6*ux, ey + 20.6*uy, 15.5, *ROLLER_Z))
    s.append(Sweep("lever_fork", ex + 34.0*ux, ey + 34.0*uy, 5, *ROLLER_Z))
    return s


# --- part-level z-map (parts port; all ABSOLUTE, dial face = z0) -------------
# Derived from the frozen bands above; parts assert against these.
REVC_BACKLASH = 0.30
ZC = {
    "bay_cup_floor": BAY_FLOOR - 1.8,        # lower pivot cups in the bay
    "esc_wheel": (4.2, 6.6),                 # club wheel t2.4
    "lever": (4.2, 6.3),                     # fork body t2.1, pivots +-
    "roller_saf": (4.2, 5.15),               # safety tier == guard band
    "roller_imp": (5.15, 6.7),               # impulse tier == slot band
    "strap": (6.55, 7.1),                    # removable pallet strap
    "planeA": (7.25, 10.25),                 # gear metal inside PLANES["A"]
    "planeB": (11.25, 14.25),                # gear metal inside PLANES["B"]
    "ring": (7.6, 11.0),
    "spring": (11.7, 14.1),
    "bridge": BRIDGE,
    "bush_floor": PLATE_T - 3.0,             # train lower bushings (blind)
    "drum": (2.2, 11.0),
}


def mesh_ideals(layout=None):
    """(name, station_a, station_b, ideal_center_distance) for the four
    train meshes at module 1.0 — the exactness gate."""
    L = layout or REVC_LAYOUT
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = L["counts"]
    return [("drum-minute", "barrel", "minute", (Zd + pm) / 2),
            ("minute-third", "minute", "third", (Zm + p3) / 2),
            ("third-fourth", "third", "fourth", (Z3 + p4) / 2),
            ("fourth-escape", "fourth", "escape", (Z4 + pe) / 2)]


# The escape wheel's tooth and the pallet stones are designed together:
# the tooth profile below is the one source for the printed wheel AND
# for the stone solver's clearance test (log 0027).
TOOTH = {"r_tip": 16.0, "r_root": 13.2, "face_rake_deg": 28.0,
         "back_rake_deg": 42.0, "tip_flat_mm": 0.15}
#   THE TOOTH LEANS BACK (log 0027, Jon's video of the fork flopping
#   under wind). Its tip is the foremost point. Its LEADING face runs
#   from the tip down to the root receding UPSTREAM at face_rake_deg;
#   its back does the same, steeper, at back_rake_deg; the body is
#   the blade between them, wholly behind the tip. Ahead of the tip,
#   below r16, there is nothing.
#   Why: a locking face with DRAW leans upstream from the tooth's rest
#   point (the wheel must recoil to unlock — that is what holds the
#   fork on its banking). It can only do that if the tooth's own body
#   is further upstream still at every depth — i.e. face_rake >
#   draw. The coda-3 tooth leaned FORWARD (face falling ahead of the
#   tip), so every draw-tilted face ran into its body and the lock
#   solver silently shrank the face to 0.04 mm: no lock, no draw.
#   tip_flat: a 0.4-nozzle corner prints ~r0.2; a small flat keeps the
#   contact where it is drawn.


def tooth_profile_pts(teeth):
    """Outline of the whole escape wheel's toothed rim, CCW, as the
    wheel is modelled (one source for the part and for the stone
    solver). Rakes are angles off radial at the mean engagement radius
    (14.6), so they hold at any tooth count."""
    from math import cos, pi, radians, sin, tan
    t = TOOTH
    r_tip, r_root = t["r_tip"], t["r_root"]
    depth = r_tip - r_root
    w = 2 * pi / teeth
    tf = t["tip_flat_mm"] / r_tip / 2
    face_run = depth * tan(radians(t["face_rake_deg"])) / 14.6
    back_run = depth * tan(radians(t["back_rake_deg"])) / 14.6
    pts = []
    for k in range(teeth):
        a = 2 * pi * k / teeth
        for u in (0.0, 0.5):                     # the back, rising to the tip
            th = a - tf - back_run * (1 - u)
            rr = r_root + depth * u
            pts.append((rr * cos(th), rr * sin(th)))
        pts.append((r_tip * cos(a - tf), r_tip * sin(a - tf)))
        pts.append((r_tip * cos(a + tf), r_tip * sin(a + tf)))
        for u in (0.5, 1.0):                     # the leading face, receding
            th = a + tf - face_run * u
            rr = r_tip - depth * u
            pts.append((rr * cos(th), rr * sin(th)))
        th_next = a + w - tf - back_run          # root floor to the next back
        pts.append((r_root * cos(th_next - 0.01), r_root * sin(th_next - 0.01)))
    return pts


def tooth_clearance_test(E, phi_tip, margin):
    """f(pt) -> True if pt stays `margin` clear of the teeth around the
    one whose tip sits at azimuth phi_tip (radians about E): the wheel
    at rest on that tooth. Built from the real profile, so it assumes
    nothing about which way the tooth leans."""
    from math import cos, sin
    from shapely.geometry import Point, Polygon
    from .variants import active_variant
    pts = tooth_profile_pts(active_variant().esc_teeth)
    c, s_ = cos(phi_tip), sin(phi_tip)
    wheel = Polygon([(E[0] + x * c - y * s_, E[1] + x * s_ + y * c)
                     for x, y in pts]).buffer(0)
    tip = Point(E[0] + TOOTH["r_tip"] * c, E[1] + TOOTH["r_tip"] * s_)
    grown = wheel.intersection(tip.buffer(14.0)).buffer(margin)
    return lambda pt: not grown.intersects(Point(pt))


# Escapement stone tune (print variant; probe-swept Aug 2026, log 0026).
# One dict so tools/probe_escapement.py can sweep candidates in place.
ESC_TUNE = {
    "lock_reserve": 0.60,   # locking face below the rest point (log 0027:
    #   a 0.4-nozzle tip prints ~r0.1 and lands 0.3 lower on the face;
    #   0.60 leaves it 1.9 deg of unlock with draw, 0.45 left ~1.1 and
    #   almost no recoil)
    "draw_deg": 15.0,       # the locking face's lean off the P-chord,
    #   inner end upstream — recoil ~0.2 deg per fork deg while unlocking
    "face_over": 0.90,      # face above the rest point (catch slop).
    #   A longer face does NOT extend the catch window (probe-tested at
    #   1.9): the segment slides outward along its own line as the
    #   stone swings, vacating the tip-circle crossing regardless of
    #   length — the mid-swing catch always lands on the ramp, whose
    #   plunge then eases the wheel back ~6 deg while the fork seats
    #   (the accepted efficiency debt of this lift-rate architecture)
    # Option C (Aug 19, log 0026 coda 3): tooth back steepened (TOOTH)
    # and the ramp built to the hook-back envelope — the tip always wins
    # the race to the face. Values probe-gated on draw + banking window
    # + mid-swing depth + tick; see tests/test_revc_parts.
    "ride_deg": 10.0,       # fork travel the impulse bevel is traced for.
    #   log 0027 (tooth leaning back, lock 0.60): 10 — at 10.5+ the
    #   OTHER stone's lifted ramp tail reaches the tip circle at this
    #   banking and the wheel rests on it instead of on the lock.
    #   Coda 5 bench (Jon): "a third of a millimetre more stone and
    #   we're perfect" — probe-swept: 10.5 gave mid-swing gate +0.41,
    #   12/0.85/floor-13.4 gives +0.54 (the knee: at ride 13+ the ramp
    #   tail wraps into the NEXT tooth's approach — rest falls on the
    #   tail, draw inverts, the tick runs backward. 12 is the ceiling).
    #   Probe-swept Aug 19: 9.0 -> mid-swing +0.34; 10.5 -> +0.41 with
    #   the tick still clean (exit half: flight 1.5, retro 0.1 — better
    #   coupling); 12 -> +0.48 but the bevel turns anti-impulse and the
    #   first half-swing drives the wheel BACKWARD. 10.5 is the knee.
    "ramp_floor_r": 13.4,   # absolute floor (root 13.2 + air)
    "couple": 0.85,         # wheel deg advanced per fork deg on the bevel
    "env_margin": 0.10,     # stone material stays this far clear of the
    #   tooth at rest (tooth_clearance_test): the locking face below
    #   the tip runs between the radial line and the tooth's receding
    #   face, 0.45 (tan 28 - tan 12) = 0.14 behind it at the foot
    "fin_out": 1.6,         # fin closure: outward reach ...
    "fin_back": 0.55,       # ... and upstream lean off the drop edge
}


def lever_layout_c(variant=None):
    """Swiss lever on rev C coordinates. E, P, B colinear; strap feet
    flank P; banking pins rise from the bay floor. P is PLATE-FROZEN at
    a = r_esc/cos(39 deg) = 20.59 (rev B proportions) — bay cups, strap
    holes and banking pins all measure from it.

    STONES FOR A TIPS-ONLY WHEEL (bench-caught Aug 2026, log 0026): the
    0024 tooth re-cut made the wheel touch stones with TIPS at r16, but
    the stones kept their flank-era placement — faces ~1mm INSIDE the
    tip circle, where a tooth tip can never rest. Tips butted the
    stones' radial backs, released 4.8 deg into the 13 deg swing, and
    from there NEITHER stone gated the wheel: it free-ran over a full
    pitch and landed at random phase (the bench bind). Rebuilt from
    contact kinematics:

    - embrace: the contact azimuths sit a HALF-INTEGER number of tooth
      pitches apart (deadbeat alternation), nearest the frozen 78 deg:
      +-39.375 at 16t, +-39.0 at 30t. P does NOT move — the plate
      survives; only the lever reprints.
    - at this architecture the E-contact-P angle is ~94 deg, so an arc
      about P (the true deadbeat locking direction) is nearly RADIAL
      about E. The locking face is that chord crossing the tip circle,
      draw-tilted (sign picked numerically so tooth pressure torques
      the fork INTO its banking); the tooth rests on it AT r16 with
      lock_reserve of face below the rest point = ~2 deg unlock swing.
    - the impulse ramp is the TRACE of the tooth tip in the stone frame
      over the ride schedule (fork rides ride_deg past unlock while the
      wheel advances couple*ride_deg CCW): the exact face that keeps
      wheel and fork coupled through mid-swing. Sized so each side
      releases only AFTER the other side's ramp already intrudes
      through the tip circle — the gate is never open.
    - each stone is drawn at its ENGAGED pose (fork at its own banking)
      then pre-rotated to neutral about P (July's deadbeat retiming,
      kept — engagement depth is reached at the banking, not neutral).

    Cycle budget at 16t (probe-verified, tools/probe_escapement.py):
    unlock ~2 + ride 6 of the 13 deg fork swing, wheel couples 4.5 deg,
    flies ~2.5 free, catches on the far ramp, draw-seats: half a pitch
    (11.25 deg) per half-swing exactly."""
    from math import atan2, cos, sin, radians, hypot, degrees
    if variant is None:
        from .variants import active_variant
        variant = active_variant()
    E = REVC_LAYOUT["escape"]
    B = REVC_LAYOUT["balance"]
    span_mm = REVC_LAYOUT["lever_span"]
    ang = atan2(B[1] - E[1], B[0] - E[0])
    r_esc = 16.0
    a = r_esc / cos(radians(39))                 # 20.59, plate-frozen
    u = (cos(ang), sin(ang))
    P = (E[0] + a * u[0], E[1] + a * u[1])
    bank_deg = 6.5
    pitch = 360.0 / variant.esc_teeth
    n_half = round(78.0 / pitch - 0.5) + 0.5     # half-integer pitches
    span_half = n_half * pitch / 2.0             # 39.375 @16t, 39.0 @30t

    lock_reserve = ESC_TUNE["lock_reserve"]  # radial face below the rest
    face_over = ESC_TUNE["face_over"]        # face above it (catch slop)
    ride_deg = ESC_TUNE["ride_deg"]          # fork travel riding the ramp
    ramp_floor_r = ESC_TUNE["ramp_floor_r"]  # ramp depth cap at banking
    env_margin = ESC_TUNE["env_margin"]      # clearance off the tooth back
    couple = ESC_TUNE["couple"]              # wheel deg per fork deg:
    #   the trace must stay DOWNSTREAM of the tooth's hook-back envelope
    #   (which recedes ~ 13*(d/2.75)^1.667 deg past the tip at depth d,
    #   superlinear — so a deeper, further-swept ramp clears it while a
    #   shallow steep one fouls); probe-swept, see tools/probe_escapement
    fin_out, fin_back = ESC_TUNE["fin_out"], ESC_TUNE["fin_back"]

    def _about_P(pt, dth_deg):
        dth = radians(dth_deg)
        dx, dy = pt[0] - P[0], pt[1] - P[1]
        return (P[0] + dx * cos(dth) - dy * sin(dth),
                P[1] + dx * sin(dth) + dy * cos(dth))

    stones, contacts, lifts, arm_vias, arm_welds = [], [], [], [], []
    lock_reserves = []
    for s in (+1, -1):
        phi = ang + s * radians(span_half)       # the resting tooth's tip CENTRE
        # the stone's face passes through the tip flat's DOWNSTREAM
        # corner — that corner is what touches it (log 0027: drawn
        # through the centre, the face sat 0.075 inside the flat and
        # the clearance walk below it never found its margin)
        phi_c = phi + TOOTH["tip_flat_mm"] / 2 / r_esc
        T = (E[0] + r_esc * cos(phi_c), E[1] + r_esc * sin(phi_c))
        n_out = (cos(phi_c), sin(phi_c))
        tg = (-n_out[1], n_out[0])               # CCW tangent = tooth travel
        # lift rate: mm the stone rises off E per fork deg AWAY from bank
        dd = 0.01
        Td = _about_P(T, -s * dd)
        lift = (hypot(Td[0] - E[0], Td[1] - E[1]) - r_esc) / dd
        # deadbeat chord (perp to P-radius), outward, then draw-tilted so
        # the tooth's push on the face torques the fork INTO this banking
        vP = (T[0] - P[0], T[1] - P[1])
        lP = hypot(*vP)
        q = (-vP[1] / lP, vP[0] / lP)
        if q[0] * n_out[0] + q[1] * n_out[1] < 0:
            q = (-q[0], -q[1])
        # DRAW (log 0027): the face is the P-chord rotated so that its
        # INNER end lies UPSTREAM of the contact. Unlocking lifts the
        # stone outward along the P-arc; the face slides past the
        # tooth's tip, and because the face leans upstream going in,
        # the tip has to back up to stay on it: the wheel RECOILS, and
        # its torque holds the fork against its banking. That face is
        # only possible because the tooth's own body recedes upstream
        # faster (TOOTH face_rake > draw). (The old rule picked the
        # sense by a torque heuristic whose sign was wrong, against a
        # tooth that leaned forward: the solver gave up the lock
        # entirely.) tools/probe_escapement measures the recoil; the
        # gate asserts it.
        f = None
        for sgn in (+1, -1):
            dth = radians(sgn * ESC_TUNE["draw_deg"])
            fc = (q[0] * cos(dth) - q[1] * sin(dth),
                  q[0] * sin(dth) + q[1] * cos(dth))
            fr_ = fc[0] * n_out[0] + fc[1] * n_out[1]
            inward = (-fc[0] / fr_, -fc[1] / fr_)        # along the face, in
            if inward[0] * tg[0] + inward[1] * tg[1] < 0:    # ... upstream
                f = fc
        if f is None:                            # zero draw: radial chord
            f = q
        fr = f[0] * n_out[0] + f[1] * n_out[1]   # radial gain along face
        # the locking face must run BELOW r16 (that's where a tooth tip
        # lives): it continues the draw-tilted line lock_reserve
        # radially down from T to the NOSE, and the ramp starts there.
        # (Bench-caught Aug 19, Jon's video: the old nose was a separate
        # point tucked downstream at r16-lock_reserve, which turned the
        # stone's underside into a V — face down to an apex, then back
        # up to the tucked nose. A tooth's hook-back slid under that V
        # and CAUGHT the apex: flank-on-foot, the contact the July
        # redesign was meant to kill. No tip ever touched the face; no
        # draw on either stone; the fork parked anywhere and the wheel
        # ran free at mid-swing. With the nose ON the face line the
        # underside is one straight wall the tip butts, and the ramp's
        # own first trace point (downstream by construction) provides
        # the hook-back clearance the tuck was for.)
        # THE LOCK (coda 3, the structural find): any stone material
        # below r16 DOWNSTREAM of the contact is reached by the tooth's
        # leading surface (at depth d it sits D(d) deg ahead of the tip)
        # before the tip reaches the face. So the face's foot may dip
        # below r16 only as far as the tooth's leading face allows at
        # the foot's own downstream offset — solved here, not guessed:
        # walk the face down from T until it would come within env_margin
        # margin. Draw comes from the face ANGLE at the contact, not
        # from depth below the tip.
        clear = tooth_clearance_test(E, phi, env_margin)

        def _env_ok(pt):
            return (hypot(pt[0] - E[0], pt[1] - E[1]) >= ramp_floor_r
                    and clear(pt))
        lr = lock_reserve
        nose = (T[0] - f[0] * lr / fr, T[1] - f[1] * lr / fr)
        while ESC_TUNE.get("solve_lock", True) and lr > 0.04 and not _env_ok(nose):
            lr -= 0.01
            nose = (T[0] - f[0] * lr / fr, T[1] - f[1] * lr / fr)
        unlock_deg = lr / lift                   # fork deg to clear the face
        lock_reserves.append(lr)
        top = (T[0] + f[0] * face_over / fr,
               T[1] + f[1] * face_over / fr)
        # IMPULSE FACE: from the nose, DOWNSTREAM across the tip circle.
        # Not a trace into the gullet (that was the July ramp — it dips
        # where the tooth's leading face already is). It is the path of
        # the tip in the stone frame while the fork LIFTS: built as the
        # trace but clipped to the tooth envelope at every point, so at
        # banking it hugs the tooth's leading face from outside and the
        # tip climbs it only as the stone rises. ride_deg/couple set its
        # length and slope; n points keep it faithful after simplify.
        w0 = _about_P(nose, -s * unlock_deg)     # tip world at unlock end
        azi0 = atan2(w0[1] - E[1], w0[0] - E[0])
        ramp = []
        n_ramp = 10
        for k in range(1, n_ramp + 1):
            t = k / n_ramp
            th_w = azi0 + radians(couple * ride_deg * t)
            wpt = (E[0] + r_esc * cos(th_w), E[1] + r_esc * sin(th_w))
            pt = _about_P(wpt, s * (unlock_deg + ride_deg * t))
            a_pt = atan2(pt[1] - E[1], pt[0] - E[0])
            r_pt = hypot(pt[0] - E[0], pt[1] - E[1])
            r_min = max(ramp_floor_r, r_pt)
            while not clear((E[0] + r_min * cos(a_pt), E[1] + r_min * sin(a_pt))) \
                    and r_min < r_esc:
                r_min += 0.05                    # lift the point out of the tooth
            if r_min > r_pt:
                pt = (E[0] + r_min * cos(a_pt), E[1] + r_min * sin(a_pt))
            ramp.append(pt)
        drop = ramp[-1]
        # fin closure off the ramp end: outward, with an upstream lean
        # capped so it can never cross back over the locking face (a
        # fixed 0.55 lean self-intersected once the ramp got narrower
        # than ~3 deg of arc — the narrow-stone redesign, Aug 19)
        drop_az = atan2(drop[1] - E[1], drop[0] - E[0])
        arc_mm = (drop_az - phi) * r_esc               # ramp arc at r16
        lean = max(0.0, min(fin_back, 0.5 * arc_mm - 0.1))
        peak = (drop[0] + fin_out * n_out[0] - lean * tg[0],
                drop[1] + fin_out * n_out[1] - lean * tg[1])
        # back pad: a CONVEX bulge over the stone's whole back, from the
        # fin peak to the face top, all at r17.4-18.0 — tooth tips fly
        # at exactly r16.0, so material out here can never be touched
        # at any pose, and |pad - P| is pose-invariant so it stays
        # inside the bay's P-circle at every swing. It exists so the
        # arm weld grabs a wide solid back: two earlier shapes fused
        # into one solid on screen and snapped in the hand — a corner
        # weld necked at <0.1mm, then a jagged two-point pad pinched a
        # 0.6mm isthmus (Jon called the first from the render, the
        # erosion probe measured both; log 0026). Weld anchors are
        # built HERE (engaged frame) and pre-rotated with the stone.
        pads = [(E[0] + r_p * cos(phi + radians(a_p)),
                 E[1] + r_p * sin(phi + radians(a_p)))
                for r_p, a_p in ((17.8, 5.2), (18.0, 3.2), (17.4, 1.4))]
        poly = [T, nose] + ramp + [peak] + pads + [top]  # top->T->nose = face
        stones.append([_about_P(p, -s * bank_deg) for p in poly])  # face
        anchors = [(E[0] + 17.0 * cos(phi + radians(2.5)),
                    E[1] + 17.0 * sin(phi + radians(2.5))),
                   (E[0] + 16.9 * cos(phi + radians(4.2)),
                    E[1] + 16.9 * sin(phi + radians(4.2)))]
        arm_welds.append([_about_P(a, -s * bank_deg) for a in anchors])
        contacts.append(_about_P(T, -s * bank_deg))
        lifts.append(lift)
        # arm waypoint, ENGAGED frame like everything else: the banking
        # swing plunges this whole side ~1.5mm toward E, so a route laid
        # out at neutral dips its band edge INSIDE the tip circle at the
        # banking (probe-caught: a tooth butted the arm, not the stone).
        # r18.4 engaged keeps the P->W chord edge >16.6 at worst pose.
        phi_v = phi + radians(3.0)
        via = (E[0] + 18.4 * cos(phi_v), E[1] + 18.4 * sin(phi_v))
        arm_vias.append(_about_P(via, -s * bank_deg))

    perp = (-u[1], u[0])
    feet = [(P[0] + s * STRAP_FEET_R * perp[0], P[1] + s * STRAP_FEET_R * perp[1])
            for s in (+1, -1)]                   # strap feet, on solid plate
    # banking pins: neck half 2.4 + pin r1.0 + swing room at the 8mm station
    from math import tan
    bank_off = 2.4 + 1.0 + 8 * tan(radians(6.5))
    pins = [(P[0] + 8 * u[0] + s * bank_off * perp[0],
             P[1] + 8 * u[1] + s * bank_off * perp[1]) for s in (+1, -1)]
    return {"E": E, "P": P, "B": B, "ang": ang, "a": a, "r_esc": r_esc,
            "bank_deg": bank_deg, "esc_pitch": pitch,
            "contacts": contacts, "stones": stones, "lift_rates": lifts,
            "arm_vias": arm_vias, "arm_welds": arm_welds,
            "lock_reserves": lock_reserves,
            "span_deg": 2 * span_half, "ride_deg": ride_deg,
            "couple": couple, "lock_reserve": lock_reserve,
            "lock_deg": variant.lock_deg, "draw_deg": variant.draw_deg,
            "fork_len": span_mm - a, "strap_feet": feet, "bank_pins": pins}


def bay_stations():
    """Centers + wall radii of the escapement bay recess (plan outline =
    resident sweeps + 1.5 wall). Shared by the mainplate and the tests."""
    Lv = lever_layout_c()
    E, P, B = Lv["E"], Lv["P"], Lv["B"]
    u = (cos(Lv["ang"]), sin(Lv["ang"]))
    fork = (E[0] + 34.0 * u[0], E[1] + 34.0 * u[1])
    return [(E, 17 + 1.5), (P, 15.5 + 1.5), (fork, 5 + 1.5), (B, 7 + 1.5)]


def bay_band():
    """The E-P connecting band of the recess (same wall as the P circle):
    without it a concave cusp of solid plate survives between the two wall
    circles — the lever's exit-arm cap swings through that wedge."""
    Lv = lever_layout_c()
    return ([Lv["E"], Lv["P"]], 15.5 + 1.5)


def cock_layout_c():
    """Balance cock: coplanar with the bridge, feet columns to the PLATE
    (rim side of the balance), stud post at the hairspring's outer end."""
    from math import atan2, cos, sin, radians
    B = REVC_LAYOUT["balance"]
    az = atan2(B[1], B[0])                       # toward the rim
    feet = [(B[0] + 33.5 * cos(az + radians(s)),
             B[1] + 33.5 * sin(az + radians(s))) for s in (26, -26)]
    stud_az = az                                 # centered between the arms,
    stud = (B[0] + 27.2 * cos(stud_az),          # on its own finger off the
            B[1] + 27.2 * sin(stud_az))          # boss (clear of the columns)
    return {"B": B, "feet": feet, "stud": stud, "az": az, "stud_az": stud_az}


# 4 hold-downs: the minimum that still ENCLOSES every loaded pivot and
# keeps the max unsupported rim-hoop span at 113 deg (identical to the
# old 6; the dropped 55/165 were redundant intermediates). 3 can't
# enclose the pivots with rim-only holes. Azimuths 38/145/200/285
# bracket the winding (top) + the left-side train cluster; the 113 deg
# open span is the load-free balance side (its cock self-anchors).
BRIDGE_PILLARS = [(37.8, 73.4), (145, 74.0), (200, 74.0), (285, 74.0)]


def bridge_pillar_xy():
    from math import cos, sin, radians
    return [(r * cos(radians(az)), r * sin(radians(az)))
            for az, r in BRIDGE_PILLARS]
