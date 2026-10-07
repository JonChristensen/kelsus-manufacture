"""Rev C parts port gates: the proven rev B probes, re-aimed at
REVC_LAYOUT. Every mesh phase-aligned, the lever gating the wheel at
the new geometry, every part inside its z-band, and the flat-movement
service contracts (bay strap, hanging barrel, dial web)."""
from math import atan2, cos, degrees, hypot, pi, radians, sin

import pytest
from shapely.geometry import Point
from build123d import Align, Cylinder, Pos, Rot

from calibers.k1.revc import (BAY_FLOOR, PLATE_T, REVC_LAYOUT, RING,
                             STRAP_BOSS_H, ZC, bay_stations,
                             bridge_pillar_xy, cock_layout_c, lever_layout_c,
                             mesh_ideals, revc_sweeps)
from calibers.k1 import revc_parts as rp


def _d(a, b):
    return hypot(b[0] - a[0], b[1] - a[1])


def test_revc_mesh_distances_exact():
    """Center distances vs module-1 ideals: slack up to 0.06 is fine
    (cycloidal + 0.3 backlash), interference beyond 0.02 is not."""
    for name, a, b, ideal in mesh_ideals():
        err = _d(REVC_LAYOUT[a], REVC_LAYOUT[b]) - ideal
        assert -0.02 <= err <= 0.06, f"{name}: center distance err {err:+.3f}"


def _mesh_pair(A0, B0, a_xy, b_xy, za, zb):
    th = degrees(atan2(b_xy[1] - a_xy[1], b_xy[0] - a_xy[0]))
    rot_a = th - round(th / (360 / za)) * (360 / za)
    th_b = th + 180
    rot_b = (th_b - round(th_b / (360 / zb)) * (360 / zb)) + 180 / zb
    A = Pos(a_xy[0], a_xy[1], 0) * Rot(0, 0, rot_a) * A0
    B = Pos(b_xy[0], b_xy[1], 0) * Rot(0, 0, rot_b) * B0
    inter = A & B
    assert (inter.volume if inter else 0) < 0.5, "interferes at true centers"
    d = _d(a_xy, b_xy)
    B2 = Pos((a_xy[0] - b_xy[0]) / d, (a_xy[1] - b_xy[1]) / d, 0) * B
    inter2 = A & B2
    assert (inter2.volume if inter2 else 0) > 0.8, "teeth don't reach"


def test_revc_train_meshes_phase_aligned():
    """All four meshes: zero interference at true distance, real
    engagement 1mm closer — with a tooth phased into a gap."""
    L = REVC_LAYOUT
    Zd, pm, Zm, p3, Z3, p4, Z4, pe = L["counts"]
    drum, minute = rp.drum_c(), rp.minute_arbor_c()
    third, fourth, esc = rp.third_arbor_c(), rp.fourth_arbor_c(), rp.escape_arbor_c()
    _mesh_pair(drum, minute, L["barrel"], L["minute"], Zd, pm)
    _mesh_pair(minute, third, L["minute"], L["third"], Zm, p3)
    _mesh_pair(third, fourth, L["third"], L["fourth"], Z3, p4)
    _mesh_pair(fourth, esc, L["fourth"], L["escape"], Z4, pe)


def test_revc_lever_gates_the_escape_wheel():
    """The escapement contract, measured (log 0027 — Jon filmed the fork
    flopping banking to banking under wind: the stones had no lock).
    tools/probe_escapement.report runs it on the built solids, as
    drawn and with the tooth corners rounded r0.1 (what a 0.4 nozzle
    leaves). At each banking:
      - the wheel rests on THAT stone, tip on its locking face;
      - unlocking makes the wheel RECOIL (draw — the push holds the
        fork on its pin), and the tip stays on the face for a real
        unlock angle before it reaches the impulse ramp;
      - a half-swing then advances the wheel exactly half a pitch,
        with a bounded free drop and never a jam or a runaway;
      - the other stone stands clear of the wheel.
    Plus: the gate at any fixed fork angle never opens half a pitch,
    each banking leaves a free window wider than a printed tooth, and
    the stones' load path survives 0.5 mm of erosion.
    History: the old gate asserted 'draw' with a torque heuristic whose
    sign was wrong, never looked at the lock depth, and so passed a
    design whose locking face the solver had shrunk to 0.04 mm."""
    from calibers.k1.variants import active_variant
    if active_variant().name == "metal":
        pytest.skip("metal escapement angles await the DFM retune (0017)")
    from tools.probe_escapement import Scene, report
    for tip_round in (0.0, 0.1):
        sc = Scene(tip_round=tip_round)
        tag = f"(tips rounded {tip_round})"
        lr = max(sc.lv["lock_reserves"])
        assert lr >= 0.5, f"{tag} lock reserve solved down to {lr:.2f}"
        r = report(sc)
        for side in ("entry", "exit"):
            assert r[f"{side}_rest_d"] < 0.05, \
                f"{tag} {side}: wheel does not rest on its stone"
            assert r[f"{side}_rest_r"] > 16.0 - lr - 0.05, \
                f"{tag} {side}: rest at r{r[f'{side}_rest_r']:.2f} is not " \
                f"on the locking face"
            assert r[f"{side}_other_d"] > 0.25, \
                f"{tag} {side}: the other stone is only " \
                f"{r[f'{side}_other_d']:.2f} from the wheel"
            assert r[f"{side}_recoil_at_1deg"] > 0.10, \
                f"{tag} {side}: no draw — wheel moves " \
                f"{-r[f'{side}_recoil_at_1deg']:+.2f} deg as the fork " \
                f"unlocks 1 deg"
            u = r[f"{side}_unlock_deg"]
            assert u is not None and 1.5 <= u <= 4.0, \
                f"{tag} {side}: unlock after {u} deg of fork travel"
            assert not r[f"{side}_events"], f"{tag} {side}: {r[f'{side}_events']}"
            assert abs(abs(r[f"{side}_half_adv"]) - sc.pitch / 2) < 0.5, \
                f"{tag} {side}: half-swing advanced {r[f'{side}_half_adv']:.2f}"
            assert r[f"{side}_free_run"] < 7.5, \
                f"{tag} {side}: {r[f'{side}_free_run']:.1f} deg of free drop"
        assert r["max_free_window_any_fork_angle"] < 10.0, \
            f"{tag} gate opens {r['max_free_window_any_fork_angle']:.1f} deg"
        assert min(r["window_at_+bank"], r["window_at_-bank"]) >= 2.5, \
            f"{tag} free window at a banking under 2.5 deg"
    eroded = sc.lever_outline.buffer(-0.5)
    pieces = [g for g in getattr(eroded, "geoms", [eroded])
              if g.area > 0.05]
    assert len(pieces) == 1, \
        f"lever section separates into {len(pieces)} pieces at 0.5mm " \
        f"erosion — a stone (or horn) hangs on a sub-1mm neck"


def test_revc_parts_stay_in_their_bands():
    """Every part's actual metal inside the massing Jon approved —
    BOTH ends of every bounding box, every part, single solids only."""
    eps = 0.02
    table = [  # (part, z_lo_min, z_hi_max)
        (rp.mainplate_c(), -0.01, 6.5),
        (rp.drum_c(), 2.2, 11.0),
        (rp.barrel_arbor_c(), 0.8, rp.ARBOR_SQUARE_TOP),
        (rp.drum_cover_c(), 9.6 - rp.SPRING_C["pin_len"], 11.0),   # pin hangs into the drum
        (rp.mainspring_c(), 3.5, 9.5),             # inside the drum, 0.1 off floor and cover
        (rp.ratchet_c(), *rp.RATCHET_Z),           # 1.8 proud of the bridge
        (rp.click_c(), 14.95, 19.5),               # pawl works above it
        (rp.minute_arbor_c(), 1.6, 16.25),
        (rp.third_arbor_c(), 3.6, 16.25),
        (rp.fourth_arbor_c(), 3.6, 16.25),
        (rp.escape_arbor_c(), 2.3, 16.25),
        (rp.club_escape_wheel_c(), 0.0, 2.4),      # local; seat at 4.3
        (rp.swiss_lever_c(), -2.0, 3.0),           # local; body at 4.2
        # strap: band + its two r2.2 head bosses (log 0026 — they lift
        # the M2x6 heads over the dial-capped near pilot; posed-clash
        # gate below proves the boss zone empty)
        (rp.bay_strap_c(), ZC["strap"][0], ZC["strap"][1] + STRAP_BOSS_H),
        (rp.winding_pinion_c(), 0.0, 3.6),         # local; on the stem tip
        (rp.roller_c(), ZC["roller_saf"][0], ZC["roller_imp"][1]),
        (rp.balance_staff_c(), 2.3, 16.1),
        (rp.balance_wheel_c(), ZC["ring"][0], ZC["ring"][1]),
        (rp.hairspring_c(), ZC["spring"][0], ZC["spring"][1]),
        (rp.balance_cock_c(), 6.5, 17.7),
        (rp.bridge_c(), 6.5, 17.7),
    ]
    for part, lo, hi in table:
        bb = part.bounding_box()
        assert bb.min.Z >= lo - eps and bb.max.Z <= hi + eps, \
            f"band violation: {bb.min.Z:.2f}..{bb.max.Z:.2f} vs {lo}..{hi}"
        n = len(part.solids())
        assert (n == 1) if part is not table[-1][0] else (1 <= n <= 5), \
            f"wrong solid count {n}"


def test_drum_cover_lands_on_lugs():
    """The drop-in cover must drop INSIDE the wall yet still overlap the
    three lug shelves — the fit that a 56t->60t drum revision once broke
    by leaving the cover radius hard-coded to the old wall."""
    wall_o = rp._drum_wall_o()
    wall_i = wall_o - 1.5                    # inner wall face
    lug_inner = wall_o - 2.2 - 1.4           # how far the lugs reach inward
    cover_r = rp.drum_cover_c().bounding_box().max.X   # clean disc -> = radius
    assert cover_r < wall_i - 0.1, \
        f"cover r{cover_r:.2f} won't drop inside wall r{wall_i:.2f}"
    assert cover_r > lug_inner + 0.5, \
        f"cover r{cover_r:.2f} misses the lug shelf (inner r{lug_inner:.2f})"


def test_revc_bay_service_contracts():
    """The strap lifts out under the ring; its feet sit beyond the bay
    walls on solid plate; the dial-face web under every bay cup >= 1.5."""
    lv = lever_layout_c()
    assert ZC["strap"][1] <= RING[0] - 0.5, "strap rubs the ring"
    from calibers.k1.revc import bay_band
    bpath, bhw = bay_band()
    for f in lv["strap_feet"]:
        # the HEAD radius, not the shank: a Ø4 M2 pan head on its r2.2
        # boss must clear the r26 balance rim (log 0026 — the old 1.1
        # shank check let a head sit 0.5 under the rim)
        assert _d(f, lv["B"]) > 26.0 + 2.2 + 0.2, "screw head under the ring"
        for (cx, cy), wall_r in bay_stations():
            assert _d(f, (cx, cy)) > wall_r + 1.1 + 0.4, "M2 breaks the wall"
        # perpendicular web to the E-P band wall
        (e, p) = bpath
        ex, ey = e; px, py = p
        L2 = (px - ex) ** 2 + (py - ey) ** 2
        t = ((f[0] - ex) * (px - ex) + (f[1] - ey) * (py - ey)) / L2
        t = max(0.0, min(1.0, t))
        d_line = _d(f, (ex + t * (px - ex), ey + t * (py - ey)))
        assert d_line > bhw + 1.1 + 0.4, "M2 breaks the bay band wall"
    assert (BAY_FLOOR - 1.8) >= 1.5, "bay cups too deep for the dial web"
    # banking pins flank the fork inside the hub sweep — part-level fact
    for p in lv["bank_pins"]:
        assert _d(p, lv["E"]) > 16.0 + 1.0, "pin scrapes the wheel tips"


def test_revc_statics_clear_the_sweeps():
    """Cock feet, bridge pillars and the stud post vs every rotating
    sweep they share z with — the statics obey the same 2.0 rule."""
    sweeps = revc_sweeps()
    ck = cock_layout_c()
    posts = [(x, y, 4.0, PLATE_T, ZC["bridge"][0]) for x, y in bridge_pillar_xy()]
    posts += [(x, y, 5.0, PLATE_T, ZC["bridge"][0]) for x, y in ck["feet"]]
    for px, py, pr, z0, z1 in posts:
        for s in sweeps:
            if s.z1 <= z0 or s.z0 >= z1:
                continue
            assert hypot(s.x - px, s.y - py) >= s.r + pr + 2.0 - 1e-6, \
                f"post ({px:.0f},{py:.0f}) vs {s.name}"
    # stud post: intentionally 1.0 inside the spring's breathing sweep
    # (it PINS the coil end) — assert it's there, and clear of the ring
    sx, sy = ck["stud"]
    assert _d((sx, sy), ck["B"]) == pytest.approx(27.2, abs=0.01)
    assert 11.9 >= RING[1] + 0.5, "stud post reaches the ring band"


def test_revc_bridge_and_cock_are_disjoint():
    """Coplanar neighbors: the cock nestles in the bridge's cutout with
    a real gap (the NH35 composition), no boolean contact."""
    inter = rp.bridge_c() & rp.balance_cock_c()
    assert (inter.volume if inter else 0) < 1e-6


# --- assembled-pose gates (the review's structural blind spot, closed) ---------

def _builder():
    import tools.build_revc_movement as m
    return m


def test_revc_assembled_movement_no_interference():
    """The exported STEP itself: every meshing pair phase-chained clean,
    lever/plate/roller/spring/cock/strap all disjoint AT THEIR POSES.
    This is the gate that would have shipped three collisions."""
    m = _builder()
    parts = {k.label: k for k in m.kids}
    get = lambda s: next(v for k, v in parts.items() if s in k)
    mesh_pairs = [("barrel drum", "minute arbor"), ("minute arbor", "third arbor"),
                  ("third arbor", "fourth arbor"), ("fourth arbor", "escape arbor")]
    for a, b in mesh_pairs:
        inter = get(a) & get(b)
        v = inter.volume if inter else 0
        assert v < 0.5, f"assembled mesh {a} x {b} interferes ({v:.2f})"
    disjoint = [("stem + crown", "crown wheel stud"),
                ("pallet fork", "mainplate"), ("pallet fork", "roller"),
                ("pallet fork", "bay strap"), ("bay strap", "mainplate"),
                ("hairspring", "balance cock"), ("hairspring", "balance wheel"),
                ("ratchet", "minute arbor"), ("barrel drum", "mainplate"),
                ("barrel arbor", "barrel drum"),
                ("balance wheel", "bay strap")]
    for a, b in disjoint:
        inter = get(a) & get(b)
        v = inter.volume if inter else 0
        assert v < 0.05, f"assembled {a} x {b} interferes ({v:.2f})"
    # the click's hook is 1.7 into the ratchet teeth by design: across
    # one tooth pitch there must be a SETTLED phase (hook in a gullet —
    # the window is under a degree wide, so step finely) and a BITING
    # phase (the rigid hook truly stands in a tooth's way)
    from build123d import Pos as P2, Rot as R2
    from calibers.k1.revc import REVC_LAYOUT as _L
    click = get("click (")
    r0 = rp.ratchet_c()
    bites = []
    for k in range(30):
        ratchet = P2(*_L["barrel"], 0) * R2(0, 0, 0.5 * k) * r0
        ic = click & ratchet
        bites.append(ic.volume if ic else 0)
    assert min(bites) < 0.05, f"click never settles into a gap ({min(bites):.2f})"
    assert max(bites) > 0.3, f"click never bites the teeth ({max(bites):.2f})"


def test_revc_m2_screws_touch_only_what_they_fasten():
    """The six M2x6 screws AT THEIR POSES (log 0026): each may overlap
    only the parts it fastens (thread engagement in the plate/bridge is
    the point; passing through the strap/click is by design) and must
    be disjoint from every moving or neighboring part. Born from a
    latent bug: the strap-feet service check measured the SHANK radius
    against the balance rim, so a Ø4 pan head sat 0.5 under the balance
    and no gate saw it — a fastener is a part, so it is in the STEP now.
    Also asserts each screw actually THREADS: the shank (r1.0) in its
    pilot (r0.9 plate/bridge, r0.8 platform) leaves an interference
    annulus; overlap volume / annulus area = engaged length, >= 3.5mm
    in the plate. The CLICK screw is held to 3.0: its head seats in the
    click's counterbore at z17.75 (log 0027), and the 6.0 shank spends
    1.6 in the click and 1.3 in a web the peg holes break open, leaving
    2.95 full-circle in the under-web boss. More would need pegs clear
    of the pilot — a bridge change."""
    m = _builder()
    parts = {k.label: k for k in m.kids}
    screws = {k: v for k, v in parts.items() if k.startswith("M2x6")}
    assert len(screws) == 6, f"expected 6 M2 screws in the build, got {len(screws)}"
    fastens = {  # what each screw is allowed to intersect
        "strap": ("bay strap", "mainplate"),
        "click": ("click (", "wave bridge"),
        "platform": ("dial platform", "mainplate"),
    }
    anchors = {"strap": ("mainplate", 0.9), "click": ("wave bridge", 0.9),
               "platform": ("mainplate", 0.8)}
    others = {k: v for k, v in parts.items() if not k.startswith("M2x6")}
    from math import pi
    for label, screw in screws.items():
        kind = next(k for k in fastens if k in label)
        allowed = fastens[kind]
        for pl, part in others.items():
            inter = screw & part
            v = inter.volume if inter else 0
            if any(a in pl for a in allowed):
                continue
            assert v < 0.02, f"{label} x {pl}: {v:.2f} mm^3 (a fastener " \
                             f"in a part it does not fasten)"
        aname, pilot_r = anchors[kind]
        anchor = sum((screw & p).volume for pl, p in others.items()
                     if aname in pl and (screw & p))
        engaged = anchor / (pi * (1.0 ** 2 - pilot_r ** 2))
        need = 3.0 if kind == "click" else 3.5
        assert engaged > need, \
            f"{label}: only {engaged:.2f} mm of thread in the {aname}"


def test_revc_winding_knob_drops_in_for_the_ratchet():
    """The bench winding knob (log 0027) must be the ratchet up to the
    ratchet's top — identical section where the click and the arbor
    square meet it — and everything it adds above must stand clear of
    the click, the crown wheel and the bridge at the ratchet's pose."""
    from tools.probe_escapement import _outline
    knob0 = rp.ratchet_knob_c()
    assert len(knob0.solids()) == 1
    a, b = _outline(rp.ratchet_c(), z=18.7), _outline(knob0, z=18.7)
    assert a.symmetric_difference(b).area < 0.01, \
        "the knob's lower section is not the ratchet's"
    m = _builder()
    bx, by = REVC_LAYOUT["barrel"]
    bot = (Align.CENTER, Align.CENTER, Align.MIN)
    from build123d import Box
    upper = (Pos(bx, by, 0) * knob0) & (Pos(bx, by, rp.RATCHET_Z[1] + 0.01)
                                         * Box(60, 60, 20, align=bot))
    for name in ("click (", "crown wheel (", "wave bridge", "M2x6 click"):
        part = next(k for k in m.kids if name in k.label)
        gap = upper.distance_to(part)
        assert gap >= 0.4, f"knob clears {name!r} by only {gap:.2f}"
    # and the pawl has room to lift under the flare: at full lift the
    # hook's outer edge is still inside the flare's shadow
    assert rp.CLICK_Z["pawl"][1] <= rp.RATCHET_Z[1]


def test_revc_balance_weights_sit_inside_the_rim():
    """The timing weights (log 0027 — Jon's bench: six M3x8 screws stood
    3.0 proud of one rim face and 4.6 of the other and could not pass
    the cock; they had never been in the assembly, so no gate saw it).
    At their radius the hairspring passes 0.7 above the rim and the
    pallet strap 0.5 below. So: every weight is a posed part, each lies
    wholly within the rim's own z-band, each fits its pocket, and the
    ring they sweep — at the rim's full height — meets nothing else."""
    m = _builder()
    nuts = [k for k in m.kids if k.label.startswith("M3 nut, balance")]
    assert len(nuts) == rp.BALANCE_WEIGHTS["n"]
    wheel = next(k for k in m.kids if k.label == "balance wheel")
    lo, hi = ZC["ring"]
    for nut in nuts:
        bb = nut.bounding_box()
        assert lo <= bb.min.Z and bb.max.Z <= hi, \
            f"{nut.label}: z {bb.min.Z:.2f}..{bb.max.Z:.2f} leaves the rim"
        iv = nut & wheel
        assert (iv.volume if iv else 0) < 0.05, f"{nut.label} misses its pocket"
    bx, by = REVC_LAYOUT["balance"]
    r = rp.BALANCE_WEIGHTS["r"]
    bot = (Align.CENTER, Align.CENTER, Align.MIN)
    sweep = Pos(bx, by, lo + 0.02) * (
        Cylinder(r + 3.2, hi - lo - 0.04, align=bot)
        - Cylinder(r - 3.2, hi - lo - 0.04, align=bot))
    for k in m.kids:
        if k is wheel or k in nuts:
            continue
        iv = sweep & k
        assert (iv.volume if iv else 0) < 0.02, \
            f"the weights' path meets {k.label}"


# --- the keyless works as measured on Jon's bench (log 0027) -----------------
# Three independent faults, each enough to stop the crown winding the
# barrel. They are recorded as STRICT expected failures: the redesign
# is done when all three flip to passing, and not before.

@pytest.mark.xfail(strict=True, reason="log 0027: above the slot roof "
                   "(z17.15-17.65) the crown wheel's full saw profile "
                   "cannot interleave with the ratchet at any phase")
def test_keyless_crown_wheel_nests_with_the_ratchet_at_every_height():
    """Plan-view nesting at centre distance 24, checked ABOVE the
    underside slots as well as through them. The old gate (_mesh_pair)
    allowed 0.5 mm^3 of overlap at one pose; the top 0.5 mm slab
    collides by 0.35 mm^2 at its best phase and slipped under it."""
    import numpy as np
    from shapely import affinity
    from tools.probe_escapement import _outline
    rat, crown = rp.ratchet_c(), rp.crown_wheel_c()
    for z in (16.6, 17.4):
        o, c = _outline(rat, z=z), _outline(crown, z=z)
        for th in np.arange(0, 15, 1.0):
            a = affinity.rotate(o, th, origin=(0, 0))
            least = min(a.intersection(affinity.translate(
                affinity.rotate(c, ph, origin=(0, 0)), 24.0, 0)).area
                for ph in np.arange(0, 15, 0.1))
            assert least < 1e-6, \
                f"z{z}: ratchet phase {th:.0f} deg has no free crown " \
                f"phase (least overlap {least:.3f} mm^2)"


@pytest.mark.xfail(strict=True, reason="log 0027: the stem pinion's tips "
                   "reach 0.88 into the crown wheel and only 0.47 at "
                   "tooth hand-over — all of it rounded nose")
def test_keyless_pinion_stays_engaged_through_hand_over():
    """Half a tooth pitch away from top dead centre is where one leaf
    hands the drive to the next: BOTH are at their shallowest there.
    Below ~0.8 the next leaf arrives under a land instead of in a slot
    and lifts the wheel (Jon's bench: 'they just slide underneath')."""
    from math import cos, pi
    from calibers.k1.revc import WINDING
    from tools.probe_escapement import _outline
    pin = _outline(rp.winding_pinion_c(), z=1.8)
    rs = [hypot(x, y) for x, y in pin.exterior.coords]
    tip, mid = max(rs), (max(rs) + min(rs)) / 2
    leaves = sum(1 for i in range(len(rs) - 1)
                 if rs[i] < mid <= rs[i + 1])
    underside = rp.crown_wheel_c().bounding_box().min.Z
    reach = WINDING["stem_z"] + tip - underside
    handover = WINDING["stem_z"] + tip * cos(pi / leaves) - underside
    assert reach >= 1.2, f"deepest reach only {reach:.2f}"
    assert handover >= 0.8, \
        f"{leaves} leaves: only {handover:.2f} engaged at hand-over"


@pytest.mark.xfail(strict=True, reason="log 0027: the crown wheel's stud "
                   "is a 0.03 press over 0.91 mm in a 1.3 mm web")
def test_keyless_crown_wheel_axle_is_anchored():
    """The axle takes the ratchet mesh's side load 0.85 above the pocket
    floor and the pinion's lift. Whatever holds it — a long press, a
    screw — needs at least 3 mm of grip below that floor."""
    grip = 16.0 - rp.crown_stud_c().bounding_box().min.Z
    assert grip >= 3.0, f"axle grips only {grip:.2f} mm of bridge"


def test_revc_click_boss_root_outruns_the_peg_holes():
    """The click screw's under-web boss carries the thread-former's
    driving torque into a 1.3 web that the two click-peg holes pierce
    1.6 and 2.1 from the screw axis (log 0026 coda 5 rev 8 — Jon's
    bench: the r2.4 stub hung from 8.3 mm^2 of web and twisted off).
    Asserts the boss meets the web over a root far wider than the peg
    holes, that the web it lands on is actually there, and that the
    free end keeps >= 2.0 of wall around the pilot."""
    from math import pi
    from build123d import Pos, Cylinder, Align
    bot = (Align.CENTER, Align.CENTER, Align.MIN)
    bridge = rp.bridge_c()
    x, y = rp.click_screw_xy()
    R, r_tip, pilot = rp.CLICK_BOSS_ROOT_R, rp.CLICK_BOSS_TIP_R, 0.9

    def area(z, r, t=0.02):
        s = bridge & (Pos(x, y, z) * Cylinder(r, t, align=bot))
        return s.volume / t if s else 0.0

    boss_side = area(14.66, R)      # just under the web: the boss root
    web_side = area(14.74, R)       # just inside the web: what it bonds to
    assert boss_side > 0.97 * pi * ((R - 0.03) ** 2 - pilot ** 2), \
        f"boss root is {boss_side:.1f} mm^2 — not a full r{R} section"
    assert web_side > 75, \
        f"only {web_side:.1f} mm^2 of web under the boss root (peg " \
        f"holes or a wave opening ate it; the old stub had 8.3)"
    tip = area(11.62, r_tip + 0.5)
    assert r_tip - pilot >= 2.0 and \
        tip > 0.97 * pi * (r_tip ** 2 - pilot ** 2), \
        f"tip section {tip:.1f} mm^2 — under 2.0 of wall around the pilot"


def test_revc_arbors_float_on_shoulders_not_faces():
    """Endshake contract (log 0026 coda 5 — Jon's bench: wheel faces
    rubbing the bridge/plate were a major friction source; on the desk
    stand the axis is horizontal, so gravity doesn't pick an end and
    every arbor wanders its full float). Metal movements bound axial
    float with the pivot shoulder against the jewel at tiny radius —
    now so do we: stepped bridge bearings + reduced arbor tips.
    Asserts, per train arbor, in each axial direction:
      - float before contact <= endshake + rest offset + margin;
      - the stopping contact sits ON-AXIS (centroid within r2.0 of the
        arbor axis) and is SMALL (< 1.5 mm^3 at 0.05 overshoot) — a
        shoulder or nose tip, never a wheel face (the minute wheel
        face used to land on the bridge web with 52 mm^3)."""
    from math import hypot
    from build123d import Pos
    from calibers.k1.variants import active_variant
    es = active_variant().endshake
    L = REVC_LAYOUT
    plate = rp.mainplate_c()
    bridge = rp.bridge_c()
    posed = {
        "drum": Pos(*L["barrel"], 0) * rp.drum_c(),
        "cover": Pos(*L["barrel"], 0) * rp.drum_cover_c(),
        "minute": Pos(*L["minute"], 0) * rp.minute_arbor_c(),
        "third": Pos(*L["third"], 0) * rp.third_arbor_c(),
        "fourth": Pos(*L["fourth"], 0) * rp.fourth_arbor_c(),
        "escape": Pos(*L["escape"], 0) * rp.escape_arbor_c(),
    }
    scene = {"plate": plate, "bridge": bridge}
    for name in ("minute", "third", "fourth", "escape"):
        part = posed[name]
        ax, ay = L[name]
        others = {**scene, **{n: p for n, p in posed.items() if n != name}}
        base = {n: (part & p).volume if (part & p) else 0
                for n, p in others.items()}
        for sgn in (+1, -1):
            lo, hi = 0.0, 2.0
            for _ in range(9):
                mid = (lo + hi) / 2
                m = Pos(0, 0, sgn * mid) * part
                if any(((m & p).volume if (m & p) else 0) - base[n] > 0.05
                       for n, p in others.items()):
                    hi = mid
                else:
                    lo = mid
            assert lo <= es + 0.25, \
                f"{name} {'up' if sgn > 0 else 'down'}: floats {lo:.2f} " \
                f"(endshake {es}) — an axial stop is missing"
            m = Pos(0, 0, sgn * (lo + 0.05)) * part
            for n, p in others.items():
                iv = m & p
                v = (iv.volume if iv else 0) - base[n]
                if v > 0.05:
                    c = iv.center()
                    r = hypot(c.X - ax, c.Y - ay)
                    assert r < 2.0 and v < 1.5, \
                        f"{name} {'up' if sgn > 0 else 'down'} stops on " \
                        f"{n} at r={r:.1f} v={v:.1f} — a FACE RUB, not " \
                        f"a shoulder (coda 5)"


def test_revc_winding_is_one_way():
    """The click's contract (log 0027 — Jon's bench: "the click does not
    hold at all"; the first click was a thin flexure the ratchet pushed
    INTO its anchor, in a pocket that let it lift 0.64 of the 1.70 a
    tooth needs). Run on the built solids by tools/probe_click, with the
    pawl pivoting on its neck, as drawn AND printed 0.08 fat:
      - letdown (ratchet CW, bridge view) PULLS the pawl: the push
        points away from the pivot, so the neck is in tension;
      - that push has a moment about the pivot that swings the hook
        INTO the tooth with no help from friction (the draw);
      - the faces meet on the ratchet's cliff (< 30 deg off radial);
      - winding (CCW) lifts the pawl over every tooth without a jam,
        by less than the neck can flex, and it drops back each time;
      - nothing but the hook comes near the teeth, and the pawl never
        touches its own plate.
    Directions are DERIVED: drum runs CCW (bridge view) per the
    documented train chain, so the spring torques the arbor CW and the
    click must block CW. Winding is CCW at the bridge — confirmed on
    Jon's bench."""
    from tools.probe_click import study
    for fat in (0.0, 0.08):
        r = study(fat)
        tag = f"(fat {fat})"
        assert r["tension"] > 0.9, \
            f"{tag} letdown pushes the pawl toward its pivot " \
            f"({r['tension']:+.2f}) — a strut, not a pull-pawl"
        assert r["draw_lever"] < -1.0, \
            f"{tag} draw lever {r['draw_lever']:+.2f} mm — load does " \
            f"not pull the hook into the tooth"
        assert r["lock_face_deg"] < 30, \
            f"{tag} locks on a {r['lock_face_deg']:.0f} deg face"
        assert r["wind_jam"] is None, \
            f"{tag} winding jams at ratchet {r['wind_jam']}"
        assert r["lift_deg"] <= 9.0 and r["drops_back"], \
            f"{tag} lift {r['lift_deg']:.1f} deg / drops back " \
            f"{r['drops_back']}"
        assert r["rest_lift_deg"] <= 1.5, \
            f"{tag} hook cannot seat ({r['rest_lift_deg']:.1f} deg proud)"
        assert r["gap_tips"] >= 0.45 and r["gap_plate_lifted"] >= 0.45, \
            f"{tag} gaps: tips {r['gap_tips']:.2f}, plate " \
            f"{r['gap_plate_lifted']:.2f}"
    # the neck: pivot and return spring. Lift strain and letdown stress
    # from its section (PETG: ~4% yield strain, ~45 MPa)
    w, ln = rp.CLICK_NECK
    h = rp.CLICK_Z["pawl"][1] - rp.CLICK_Z["pawl"][0]
    from math import radians as _rad
    strain = (w / 2) * _rad(r["lift_deg"]) / ln
    assert strain < 0.025, f"neck strain {strain:.1%} at full lift"
    one_turn = 158.0 / 12.0                     # N on the hook, log 0027
    assert one_turn / (w * h) < 15.0, "neck stress at one turn of wind"


def test_revc_crown_wheel_turns_the_ratchet_through_the_slots():
    """What still holds of the crown wheel (see the test_keyless_*
    expected failures for what does not): in the height band of its
    underside slots, turned CW it carries the ratchet CCW ~1:1 without
    jamming. Kept from the old winding contract so the redesign has
    the 2D drive check to hand."""
    from shapely import affinity
    from tools.probe_escapement import _outline
    Z = 16.8
    ratchet = _outline(rp.ratchet_c(), z=Z)
    crown = _outline(rp.crown_wheel_c(), z=Z)

    def rot(th):
        return affinity.rotate(ratchet, th, origin=(0, 0))

    def crown_at(phi):
        return affinity.translate(affinity.rotate(crown, phi, origin=(0, 0)),
                                  24.0, 0)
    th_r, phi0 = 0.0, 0.0
    while rot(th_r).intersects(crown_at(phi0)):
        phi0 -= 0.1
        assert phi0 > -15.5, "no free crown phase at ratchet phase 0"
    adv0 = th_r
    for step in range(1, 81):
        guard = 0.0
        while rot(th_r).intersects(crown_at(phi0 - 0.25 * step)) \
                and guard < 20:
            th_r += 0.05
            guard += 0.05
        assert guard < 20, f"crown drive JAMS at {0.25*step:.1f} deg"
    assert th_r - adv0 > 15, \
        f"crown 20 deg -> ratchet only {th_r - adv0:.1f} (needs ~1:1)"


def test_revc_lever_swings_free_of_the_plate():
    """Across the banking range the fork touches nothing in the plate."""
    from build123d import Pos, Rot
    from math import degrees
    lv = lever_layout_c()
    plate = rp.mainplate_c()
    lever0 = rp.swiss_lever_c()
    ang = degrees(lv["ang"])
    for sw in (-6.5, -4, 0, 4, 6.5):
        lever = Pos(*lv["P"], 4.2) * Rot(0, 0, ang + sw) * lever0
        ip = lever & plate
        assert (ip.volume if ip else 0) < 0.05, f"lever x plate at {sw} deg"


def test_revc_roller_passes_through_the_fork():
    """The roller/fork contract (log 0027 — Jon, looking at the parts
    before printing the balance: would that end really control the
    fork?). The old gate posed the fork and roller in a handful of
    static states and paired the fork with the banking AWAY from the
    pin — the one pairing that never happens — so it never saw that
    the returning pin butted the flat end of a horn 42 deg before
    centre and stopped dead. This one runs the pass, on the built
    solids (tools/probe_fork), as drawn, printed thin and printed fat:
      - the pin, arriving at a fork parked at its banking, gets INTO
        the notch, carries the fork across, and leaves the far side
        without touching it again;
      - the balance arc that takes (the lift) stays under 40 deg;
      - the parked fork fouls the roller at no phase;
      - and a knock cannot move the parked fork across centre: the
        guard dart on the safety roller, or a horn on the pin, stops
        it while it is still well on its own side."""
    from tools.probe_fork import study
    for fat in (-0.05, 0.0, 0.08):
        r = study(fat)
        tag = f"(printed {fat:+.2f})"
        assert r["jam"] is None, \
            f"{tag} the pin is stopped by the fork at phase {r['jam']}"
        assert r["exit_clean"], f"{tag} the pin strikes the fork leaving"
        assert -20 < r["first_push"] < -8 and 8 < r["home"] < 20, \
            f"{tag} push {r['first_push']}, home {r['home']}"
        assert r["lift_deg"] < 40, f"{tag} lift {r['lift_deg']} deg"
        assert not r["parked"], \
            f"{tag} parked fork fouls the roller at {r['parked'][:4]}"
        assert r["knock_floor"] > 2.0, \
            f"{tag} a knock moves the fork to {r['knock_floor']:+.1f} deg"


def test_inventory_is_complete_in_the_gate():
    """Jon's rule: recite the full cast before massing. Every sweep-kind
    inventory item must appear in revc_sweeps(); the massing tool builds
    from the same list and asserts its own completeness."""
    from calibers.k1.revc import INVENTORY, revc_sweeps
    names = {s.name for s in revc_sweeps()}
    for item, kind in INVENTORY:
        if kind == "sweep":
            assert item in names, f"inventory sweep {item} not in the gate"


def test_winding_station():
    """The crown path: ratchet x crown wheel phase-aligned; the stem's
    pinion gates the crown wheel through the underside slots; the
    pinion's swept cylinder truly clears the drum gear's teeth (the
    analytic check the drum_gear x stem whitelist relies on); and the
    ratio winds the ~2.8-turn spring in under 15 crown turns."""
    from math import atan2, degrees
    from build123d import Pos, Rot
    from calibers.k1.revc import REVC_LAYOUT as _L, WINDING
    _mesh_pair(rp.ratchet_c(), rp.crown_wheel_c(),
               _L["barrel"], WINDING["crown_wheel"], 24, 24)
    # ASSEMBLY-PATH gate (the stray +0.35 lesson): the stud's widest
    # tail section must pass the crown wheel's bore on the way in, and
    # press the bridge bore within a sane interference band
    from calibers.k1.variants import active_variant as _av
    stud = rp.crown_stud_c()
    from build123d import Pos as _P, Cylinder as _Cyl, Align as _Al
    _B = (_Al.CENTER, _Al.CENTER, _Al.MIN)
    tail_slice = stud & (_P(0, 0, 15.0) * _Cyl(10, 0.9, align=_B))
    import math
    tail_r = math.sqrt(tail_slice.volume / 0.9 / math.pi)
    wheel_bore = 2.55 + _av().pivot_clearance
    assert tail_r < wheel_bore - 0.15, \
        f"stud tail r{tail_r:.2f} cannot pass the wheel bore r{wheel_bore:.2f}"
    assert 0.0 < tail_r - 2.35 <= 0.06, \
        f"stud tail r{tail_r:.2f} vs bridge bore r2.35: not a press fit"
    # slot mesh: clear at pose for SOME stem roll, engaged when the
    # crown wheel turns half a slot against a held stem
    cw = WINDING["crown_wheel"]
    wheel = Pos(*cw, 0) * rp.crown_wheel_c()
    # coda 5 rev 4: the pinion is its own part (the one-print stem was
    # never installable); roll IT for the slot mesh
    def posed_pinion(roll):
        return (Pos(0, WINDING["pinion_y"] - 1.8, WINDING["stem_z"])
                * Rot(-90, 0, 0) * Rot(0, 0, roll) * rp.winding_pinion_c())
    rolls = []
    for roll in range(0, 52, 4):
        i = posed_pinion(roll) & wheel
        rolls.append((i.volume if i else 0, roll))
    best_v, best_roll = min(rolls)
    assert best_v < 0.3, f"pinion can't settle into a slot ({best_v:.2f})"
    wheel2 = Pos(*cw, 0) * Rot(0, 0, 360 / 46) * rp.crown_wheel_c()
    i2 = posed_pinion(best_roll) & wheel2
    assert (i2.volume if i2 else 0) > 0.4, "slots don't gate the pinion"
    # assembly path: everything on the stem must pass the O5.4 tunnel
    stem_solid = rp.stem_c()
    from build123d import Axis as _Ax
    for y0 in (76.0, 78.0, 80.0):     # sections inboard of the tunnel
        sl = stem_solid & (Pos(0, y0, WINDING["stem_z"])
                           * Rot(-90, 0, 0) * Cylinder(20, 0.5,
                           align=(Align.CENTER, Align.CENTER, Align.MIN)))
        if sl and sl.volume > 0.01:
            import math
            r_eq = math.sqrt(sl.volume / 0.5 / math.pi)
            assert r_eq < 2.7 - 0.1, \
                f"stem section at y={y0} is r{r_eq:.2f} — cannot pass " \
                f"the O5.4 tunnel (the one-print-stem bug, again)"
    # analytic drum clearance (the whitelist's justification)
    drum_tip = REVC_LAYOUT["counts"][0] / 2 + 0.85
    gap = (WINDING["pinion_y"] - 1.8) - REVC_LAYOUT["barrel"][1] - drum_tip
    assert gap >= 2.0, f"pinion cylinder vs drum teeth: {gap:.2f}"
    assert 2.78 * WINDING["slots"] / 7 < 15   # crown turns to full wind


def test_revc_bridge_structural():
    """The wave bridge (however the art splits it): every connected
    plate held by >=2 screw anchors, every train pivot boss intact on
    exactly one plate, nothing shattered into slivers."""
    from build123d import Cylinder, Align
    from calibers.k1.revc import bridge_pillar_xy
    B = (Align.CENTER, Align.CENTER, Align.MIN)
    plates = [s for s in rp.bridge_c().solids() if s.volume > 200]
    assert 1 <= len(plates) <= 5
    for s in plates:
        anchors = sum(1 for px, py in bridge_pillar_xy()
                      if (s & (Pos(px, py, 15.0) * Cylinder(5.5, 1.5, align=B)))
                      and (s & (Pos(px, py, 15.0) * Cylinder(5.5, 1.5, align=B))).volume > 5)
        assert anchors >= 2, f"a bridge plate has only {anchors} anchor(s)"
    for k in ("minute", "third", "fourth", "escape"):
        x, y = REVC_LAYOUT[k]
        hits = sum(1 for s in plates
                   if (s & (Pos(x, y, 15.0) * Cylinder(5.0, 1.5, align=B)))
                   and (s & (Pos(x, y, 15.0) * Cylinder(5.0, 1.5, align=B))).volume > 40)
        assert hits == 1, f"{k} boss straddles a gap or is cut"


# --- the mainspring (log 0028) -------------------------------------------

def _vol(a, b):
    """Overlap volume; an empty boolean comes back as None in build123d."""
    x = a & b
    return x.volume if x is not None else 0.0

def test_revc_mainspring_is_the_hand_the_click_winds():
    """Jon's first spring broke (log 0028) and the photo showed why
    before the fracture did: its spiral ran outward COUNTER-clockwise in
    bridge view, and the click only lets the arbor wind counter-
    clockwise — which LOOSENS that hand (turn the inner end of a spiral
    the way it unwinds and the coils press out against the wall). The
    hand that tightens under a CCW arbor runs outward CLOCKWISE. This
    pins it on the built solid: material all along the designed
    centreline, whose position angle falls as the radius grows."""
    from shapely.geometry import Point
    from tools.probe_escapement import _outline
    o = _outline(rp.mainspring_c(), 6.5)
    cl = rp._mainspring_centreline()
    assert all(o.contains(Point(r * cos(radians(ph)), r * sin(radians(ph))))
               for u, r, ph in cl), "the strip is not where its centreline says"
    assert all(b[1] > a[1] and b[2] < a[2] for a, b in zip(cl, cl[1:])), \
        "the spiral must run outward CLOCKWISE (bridge view)"


@pytest.mark.parametrize("t", rp.MAINSPRING_LADDER)
def test_revc_mainspring_lives_in_the_drum(t):
    """Every rung of the ladder, relaxed, in the drum it will be laid
    into: one solid; no overlap with the drum (wall, rib, cover lugs),
    the cover with its pin in the tab's hole, or the arbor with its rib
    in the keyway; the keyway is the ONLY place the rib fits; and the
    tab is CAPTURED — pulled inward it meets the cover's pin, pulled
    counter-clockwise it meets the rib (Jon's bench: the first
    right-hand wind slid the old tab straight off the rib, because a
    wound spiral pulls its end inward and a wall rib faces only
    inward); neighbouring coils never print closer than 0.8."""
    from shapely.geometry import LineString
    from tools.probe_escapement import _outline
    sp = rp.mainspring_c(t)
    assert len(sp.solids()) == 1
    L = rp.mainspring_layout(t)
    key_deg = rp.SPRING_C["tab_deg"] + L["coils"] * 360 + 180
    arbor = rp.barrel_arbor_c()
    assert _vol(sp, rp.drum_c()) < 1e-6
    assert _vol(sp, rp.drum_cover_c()) < 1e-6
    assert (sp & (Rot(0, 0, key_deg) * arbor)).volume < 1e-6
    assert (sp & (Rot(0, 0, key_deg + 25) * arbor)).volume > 5.0
    bb = sp.bounding_box()
    r_max = max(abs(bb.min.X), bb.max.X, abs(bb.min.Y), bb.max.Y)
    assert 26.3 < r_max < 26.7                        # the tab, 0.4 off the wall
    cover, drum = rp.drum_cover_c(), rp.drum_c()
    px, py = rp.cover_pin_xy()
    pull_in = Pos(-0.6 * px / hypot(px, py), -0.6 * py / hypot(px, py), 0)
    assert _vol(pull_in * sp, cover) > 0.5        # the pin stops the inward pull
    assert _vol(Rot(0, 0, 1.0) * sp, drum) > 0.5  # the rib stops the CCW pull
    assert _vol(Rot(0, 0, 1.0) * sp, cover) > 0.5 # ... and so does the pin
    o = _outline(sp, 6.5)
    cl = rp._mainspring_centreline(t)
    gaps = []
    for u, r, ph in cl[::4]:
        if u > cl[-1][0] - 2 * pi:
            break
        d = (cos(radians(ph)), sin(radians(ph)))
        x = LineString([(d[0] * r, d[1] * r),
                        (d[0] * (r + L["pitch"] + t), d[1] * (r + L["pitch"] + t))]
                       ).intersection(o.boundary)
        rs = sorted(hypot(g.x, g.y) for g in getattr(x, "geoms", [x]) if not g.is_empty)
        if len(rs) >= 2:
            gaps.append(rs[1] - rs[0])
    assert min(gaps) >= 0.8, f"coils print {min(gaps):.2f} apart"


@pytest.mark.parametrize("t", rp.MAINSPRING_LADDER)
def test_revc_mainspring_cannot_be_overwound(t):
    """The sizing rule (log 0028): the coils pack solid on the ring —
    the only stop there is — at or under the PETG strain ceiling, so
    'wind until it stops' is safe. The 2.2 strip went solid at ~4%:
    past yield, which is the fracture in Jon's photo. The torque the
    train needs is still unmeasured, so the rungs must bracket what
    the old spring gave at half a turn (~80 N.mm) from both sides."""
    L = rp.mainspring_layout(t)
    assert 0.8 < L["turns"] < 2.0
    assert L["strain_full"] <= 1.15 * rp.SPRING_C["eps_full"]   # 2.0 stops 3 teeth short of solid
    assert L["turns_safe"] * 24 >= 18                          # ... and still gives 18+ teeth
    if t == rp.SPRING_C["strip_t"]:
        assert L["strain_full"] <= rp.SPRING_C["eps_full"]     # the kit spring: solid IS the stop
    lo, hi = (rp.mainspring_layout(x)["torque_safe"] for x in (min(rp.MAINSPRING_LADDER), max(rp.MAINSPRING_LADDER)))
    assert lo < 60 < 80 < hi
