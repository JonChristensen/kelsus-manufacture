"""Kinematic probe of the rev C escapement (log 0026).

Sections the ACTUAL solids (club_escape_wheel_c, swiss_lever_c) at the
shared z-band into 2D polygons, then simulates the tick: the wheel is
torque-butted CCW against whatever blocks it while the fork sweeps
banking to banking, with recoil against draw allowed. This is the
ground truth the gate test asserts against — the static pose checks
that preceded it PASSED on geometry that could not tick (the bench
caught it; see docs/log/0026).

Run:  python tools/probe_escapement.py        (report + renders in out/)
Import: build_scene() -> Scene with free/pen/simulate/contact helpers.
"""
import os
import sys
from math import atan2, cos, degrees, hypot, radians, sin

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from build123d import Box, Pos  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.geometry import Point, Polygon  # noqa: E402
from shapely.ops import nearest_points  # noqa: E402


def _outline(part, z=1.5):
    """Largest XY cross-section outer boundary as a shapely Polygon
    (tessellate + union: ~1000x faster than sampling the wire)."""
    from shapely import union_all
    slab = Pos(0, 0, z) * Box(300, 300, 0.02)
    sec = part & slab
    faces = [f for f in sec.faces() if abs(f.normal_at(f.center()).Z) > 0.99]
    f = max(faces, key=lambda f: f.area)
    verts, tris = f.tessellate(0.008)
    u = union_all([Polygon([(verts[i].X, verts[i].Y) for i in t])
                   for t in tris]).buffer(0)
    u = max(getattr(u, "geoms", [u]), key=lambda g: g.area)
    return Polygon(u.exterior).simplify(0.004)


class Scene:
    """2D world-frame escapement: wheel ring + lever split entry/exit.

    tip_round: print-realism — round the escape teeth's convex corners
    by this radius (a 0.4 nozzle leaves ~r0.1-0.2 on a sharp/flat tip).
    The gate runs the contract at 0 AND at 0.1: a design that only
    locks on a mathematically sharp corner is not a design."""

    def __init__(self, tip_round=0.0):
        import calibers.k1.revc_parts as rp
        from calibers.k1.revc import lever_layout_c
        from calibers.k1.variants import active_variant

        self.variant = active_variant()
        self.lv = lever_layout_c()
        self.E, self.P = self.lv["E"], self.lv["P"]
        self.ang, self.bank = self.lv["ang"], self.lv["bank_deg"]
        self.pitch = 360.0 / self.variant.esc_teeth

        wheel_part = rp.club_escape_wheel_c()
        lever_part = rp.swiss_lever_c()
        n_bodies = len(lever_part.solids())
        if n_bodies != 1:
            raise RuntimeError(
                f"swiss_lever_c is {n_bodies} disconnected solids — the "
                f"stone weld failed; _outline would silently drop the "
                f"stones and every sim result would be fiction")
        wheel_local = _outline(wheel_part)
        if tip_round > 0:
            wheel_local = wheel_local.buffer(-tip_round, join_style=2) \
                                     .buffer(tip_round, join_style=1)
        lever_local = _outline(lever_part)
        # full mid-body section, kept for structural (erosion) checks
        self.lever_outline = lever_local
        E_l = (-self.lv["a"], 0.0)
        clip = Point(E_l).buffer(19.5, quad_segs=64)
        near = lever_local.intersection(clip)
        h = 60.0
        top = Polygon([(-h, 0), (h, 0), (h, h), (-h, h)])
        bot = Polygon([(-h, 0), (h, 0), (h, -h), (-h, -h)])
        self._lever_pieces = (near, near.intersection(top),
                              near.intersection(bot))
        ring = Point(0, 0).buffer(17.5, quad_segs=64).difference(
            Point(0, 0).buffer(12.4, quad_segs=64))
        self._wheel_ring = wheel_local.intersection(ring)
        self._wcache, self._lcache = {}, {}

    def wheel(self, th):
        key = round(th, 4)
        if key not in self._wcache:
            g = affinity.rotate(self._wheel_ring, th, origin=(0, 0))
            self._wcache[key] = affinity.translate(g, self.E[0], self.E[1])
        return self._wcache[key]

    def lever(self, sw):
        """(full, entry_side, exit_side) world polys at fork swing sw."""
        key = round(sw, 4)
        if key not in self._lcache:
            out = []
            for g in self._lever_pieces:
                gg = affinity.rotate(g, degrees(self.ang) + sw, origin=(0, 0))
                out.append(affinity.translate(gg, self.P[0], self.P[1]))
            self._lcache[key] = tuple(out)
        return self._lcache[key]

    def free(self, sw, th):
        return not self.lever(sw)[0].intersects(self.wheel(th))

    def pen(self, a, b):
        """Signed clearance: +distance apart, -sqrt(area) overlapped."""
        if a.intersects(b):
            return -np.sqrt(a.intersection(b).area)
        return a.distance(b)

    def butt(self, sw, th0, dth=0.02, max_run=None):
        """Advance the wheel CCW from th0 until contact; (th, run)."""
        cap = self.pitch + 2 if max_run is None else max_run
        th, run = th0, 0.0
        while self.free(sw, th + dth) and run < cap:
            th += dth
            run += dth
        return th, run

    def contact(self, sw, th):
        """Per-side nearest-feature report at a pose."""
        out = {}
        w = self.wheel(th)
        for name, g in zip(("entry", "exit"), self.lever(sw)[1:]):
            if g.is_empty:
                continue
            p1, p2 = nearest_points(g, w)
            out[name] = {
                "d": g.distance(w),
                "lever_r": hypot(p1.x - self.E[0], p1.y - self.E[1]),
                "lever_az": degrees(atan2(p1.y - self.E[1],
                                          p1.x - self.E[0])) % 360,
                "wheel_r": hypot(p2.x - self.E[0], p2.y - self.E[1]),
                "wheel_az": degrees(atan2(p2.y - self.E[1],
                                          p2.x - self.E[0])) % 360,
            }
        return out

    def simulate(self, sw_from, sw_to, th0, dsw=0.05, dth=0.02,
                 recoil_budget=4.0):
        """Sweep the fork with the wheel butted CCW. Returns (rows,
        events, max_free_run): rows = (sw, th, entry_clr, exit_clr)."""
        step = dsw if sw_to > sw_from else -dsw
        sws = np.arange(sw_from, sw_to + step / 2, step)
        th = th0
        rows, events = [], []
        max_free_run = 0.0
        for sw in sws:
            back = 0.0
            while not self.free(sw, th) and back < recoil_budget:
                th -= dth
                back += dth
            if back >= recoil_budget:
                events.append(("JAM", sw, th,
                               f"fork stuck at sw={sw:+.2f}: wheel cannot "
                               f"recoil clear within {recoil_budget} deg"))
                rows.append((sw, th, np.nan, np.nan))
                break
            th, run = self.butt(sw, th, dth)
            max_free_run = max(max_free_run, run)
            _, lent, lexi = self.lever(sw)
            w = self.wheel(th)
            rows.append((sw, th, self.pen(lent, w), self.pen(lexi, w)))
            if run >= self.pitch:
                events.append(("RUNAWAY", sw, th,
                               "wheel ran a full pitch free"))
                break
        return np.array(rows), events, max_free_run

    def rest(self, sw, th_seed=0.0):
        """Butted rest state at a fixed fork angle, from a free seed."""
        th = th_seed
        while not self.free(sw, th):
            th += 0.11
            if th - th_seed > 2 * self.pitch + 1:
                raise RuntimeError(
                    f"no free wheel pose at sw={sw:+.2f}: the lever "
                    f"blocks every rotation (arm/stone intrusion)")
        th, _ = self.butt(sw, th, max_run=3 * self.pitch)
        return th

    # ------------------------------------------------------------ render
    def snapshot(self, sw, th, fname, title, zoom=None):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 9))
        w = self.wheel(th)
        _, lent, lexi = self.lever(sw)
        full = self.lever(sw)[0]
        for g, c, lab in ((w, "#4a90d9", "escape wheel"),
                          (lent, "#d94a4a", "entry side"),
                          (lexi, "#d9884a", "exit side")):
            for gg in getattr(g, "geoms", [g]):
                if gg.is_empty or not hasattr(gg, "exterior"):
                    continue
                x, y = gg.exterior.xy
                ax.fill(x, y, alpha=0.45, color=c, label=lab)
                lab = None
        if full.intersects(w):
            ov = full.intersection(w)
            for gg in getattr(ov, "geoms", [ov]):
                if gg.is_empty or not hasattr(gg, "exterior"):
                    continue
                x, y = gg.exterior.xy
                ax.fill(x, y, color="black", label="OVERLAP")
        ax.plot(*self.E, "k+", ms=10)
        ax.plot(*self.P, "k+", ms=10)
        ax.set_aspect("equal")
        ax.legend(loc="lower right")
        ax.set_title(title)
        if zoom:
            cx, cy, r = zoom
            ax.set_xlim(cx - r, cx + r)
            ax.set_ylim(cy - r, cy + r)
        else:
            ax.set_xlim(self.E[0] - 19, self.E[0] + 19)
            ax.set_ylim(self.E[1] - 19, self.E[1] + 19)
        fig.savefig(fname, dpi=110, bbox_inches="tight")
        plt.close(fig)


def main():
    out = os.path.join(os.path.dirname(__file__), "..", "out",
                       "escapement_probe")
    os.makedirs(out, exist_ok=True)
    sc = Scene()
    bank, pitch = sc.bank, sc.pitch
    print(f"variant={sc.variant.name} teeth={sc.variant.esc_teeth} "
          f"pitch={pitch} span={sc.lv['span_deg']}")

    th0 = sc.rest(bank)
    c = sc.contact(bank, th0)
    print(f"\nentry-banked rest: th={th0:.2f} (mod pitch "
          f"{th0 % pitch:.2f})")
    for side, d in c.items():
        print(f"  {side}: d={d['d']:.3f} lever(r={d['lever_r']:.2f},"
              f"az={d['lever_az']:.1f}) wheel(r={d['wheel_r']:.2f},"
              f"az={d['wheel_az']:.1f})")
    sc.snapshot(bank, th0, os.path.join(out, "rest_entry.png"),
                f"entry banked sw=+{bank}, th={th0:.2f}")
    ct = c.get("entry")
    sc.snapshot(bank, th0, os.path.join(out, "rest_entry_zoom.png"),
                "entry rest contact zoom",
                zoom=(sc.E[0] + ct["lever_r"] * cos(radians(ct["lever_az"])),
                      sc.E[1] + ct["lever_r"] * sin(radians(ct["lever_az"])),
                      4.0))

    for half, (a, b) in (("entry->exit", (bank, -bank)),
                         ("exit->entry", (-bank, bank))):
        tr, ev, run = sc.simulate(a, b, th0)
        adv = tr[-1][1] - tr[0][1]
        print(f"\n== {half}: wheel {tr[0][1]:.2f} -> {tr[-1][1]:.2f} "
              f"(advance {adv:.2f}, longest free run {run:.2f})")
        for e in ev:
            print("  EVENT:", e)
        for i, side in ((2, "entry"), (3, "exit")):
            j = int(np.nanargmin(tr[:, i]))
            print(f"  min {side} clearance {np.nanmin(tr[:, i]):+.3f} "
                  f"at sw={tr[j, 0]:+.2f}")
        th0 = tr[-1][1]
        tag = half.replace("->", "_")
        worst = np.nanmin(tr[:, 2:4], axis=1)
        iw = int(np.nanargmin(worst))
        sc.snapshot(tr[iw, 0], tr[iw, 1],
                    os.path.join(out, f"pinch_{tag}.png"),
                    f"{half} tightest: sw={tr[iw, 0]:+.2f} "
                    f"th={tr[iw, 1]:.2f} clr={worst[iw]:+.3f}")
        if ev:
            sc.snapshot(tr[-1, 0], tr[-1, 1],
                        os.path.join(out, f"event_{tag}.png"),
                        f"{half} {ev[0][0]} at sw={tr[-1, 0]:+.2f}")
            break
    print(f"\nrenders in {out}")


if __name__ == "__main__":
    main()


def report(sc, drop_limit=6.0):
    """The escapement's contract as numbers (log 0027). For each banking:
    the wheel rests on THAT stone's locking face; unlocking makes the
    wheel RECOIL (draw) until the tip clears the face (the unlock
    angle); then a half-swing advances the wheel half a pitch with a
    bounded free drop. Returns a flat dict; `ok` summarises."""
    bank, pitch = sc.bank, sc.pitch
    out, ok = {}, True
    th = sc.rest(bank)
    for side, a, b in (("entry", bank, -bank), ("exit", -bank, bank)):
        th0 = sc.rest(a, th_seed=th)
        c = sc.contact(a, th0)
        own, other = c[side], c["exit" if side == "entry" else "entry"]
        out[f"{side}_rest_d"] = own["d"]
        out[f"{side}_rest_r"] = own["wheel_r"]
        out[f"{side}_other_d"] = other["d"]
        if own["d"] > 0.05 or own["wheel_r"] < 16.0 - max(sc.lv["lock_reserves"]) - 0.05:
            ok = False
        rows, ev, run = sc.simulate(a, a + (-1 if a > 0 else 1) * 4.0, th0, dsw=0.1)
        wheel = [r[1] - th0 for r in rows]
        out[f"{side}_recoil_at_1deg"] = -wheel[10]
        unlock = next((abs(r[0] - a) for r in rows if r[1] - th0 > 0.02), None)
        out[f"{side}_unlock_deg"] = unlock
        if wheel[10] > -0.08 or unlock is None or not (0.8 <= unlock <= 3.5):
            ok = False
        rows2, ev2, run2 = sc.simulate(a, b, th0, dsw=0.25)
        adv = rows2[-1][1] - th0
        out[f"{side}_half_adv"] = adv
        out[f"{side}_free_run"] = run2
        out[f"{side}_events"] = [e[0] for e in ev2]
        if ev2 or abs(adv - pitch / 2) > 0.5 or run2 > drop_limit:
            ok = False
        th = rows2[-1][1]
    # the gate at every fixed fork angle: the longest free run of the wheel
    worst = 0.0
    for sw in np.arange(-bank, bank + 0.01, 0.5):
        full, _, _ = sc.lever(sw)
        free = [not full.intersects(sc.wheel(t)) for t in np.arange(0, pitch, 0.1)]
        # longest circular run of free poses, in degrees
        s = free + free
        best, cur = 0, 0
        for f in s:
            cur = cur + 1 if f else 0
            best = max(best, cur)
        worst = max(worst, min(best, len(free)) * 0.1)
    out["max_free_window_any_fork_angle"] = worst
    if worst > drop_limit:
        ok = False
    for sw in (bank, -bank):
        full, _, _ = sc.lever(sw)
        win = sum(not full.intersects(sc.wheel(t)) for t in np.arange(0, pitch, 0.05)) * 0.05
        out[f"window_at_{'+' if sw > 0 else '-'}bank"] = win
        if win < 3.0:
            ok = False
    out["ok"] = ok
    return out
