"""2D probe of the roller <-> pallet fork interface (log 0027), on the
BUILT solids, at two heights: the slot level (impulse pin vs notch and
horns) and the guard level (guard dart vs safety roller).

Pallet frame: fork pivot P at the origin, balance axis at (D, 0).
Fork angle `a`: + = horn end toward +y. Roller phase `rph`: 0 = the
impulse pin pointing at P; + = pin toward -y.

    from tools.probe_fork import study
    study()      # -> dict, see the keys in its docstring
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from shapely import affinity

import calibers.k1.revc_parts as rp
from calibers.k1.revc import ZC, lever_layout_c
from tools.probe_escapement import _outline


def outlines():
    """(fork slot level, fork guard level, roller impulse tier, roller
    safety tier, D, banking angle)."""
    lv = lever_layout_c()
    lever, roller = rp.swiss_lever_c(), rp.roller_c()
    mid = lambda band: (ZC[band][0] + ZC[band][1]) / 2
    return (_outline(lever, z=1.5), _outline(lever, z=0.5),
            _outline(roller, z=mid("roller_imp")),
            _outline(roller, z=mid("roller_saf")),
            lv["fork_len"], lv["bank_deg"])


def make_hit(fat=0.0):
    """hit(a, rph) -> 's' / 'g' / None for the fork at angle a and the
    roller at phase rph. `fat` grows every outline (print realism;
    negative = printed thin)."""
    fs, fg, rs, rg, D, bank = outlines()
    if fat:
        fs, fg, rs, rg = (p.buffer(fat) for p in (fs, fg, rs, rg))

    def roll(poly, rph):
        return affinity.translate(
            affinity.rotate(poly, 180 + rph, origin=(0, 0)), D, 0)

    def hit(a, rph):
        if affinity.rotate(fs, a, origin=(0, 0)).intersects(roll(rs, rph)):
            return "s"
        if affinity.rotate(fg, a, origin=(0, 0)).intersects(roll(rg, rph)):
            return "g"
        return None
    return hit, bank


def one_pass(hit, bank, unlock=1.5, step=0.5, da=0.05):
    """The pin travels from the +y side to the -y side. The fork starts
    at +bank. Until it has been pushed `unlock` deg off its banking,
    draw holds it as near +bank as the pin allows; after that the
    escape wheel drives it as near -bank as the pin allows."""
    a, unlocked, log = bank, False, []
    for rph in np.arange(-80, 80.01, step):
        if not unlocked:
            c = bank
            while hit(c, rph) and c > -bank - 1e-9:
                c -= da
            if hit(c, rph) or c < a - 3.0:
                return {"jam": float(rph), "log": log}
            a = c
            unlocked = a <= bank - unlock
        if unlocked:
            c = -bank
            while hit(c, rph) and c < bank + 1e-9:
                c += da
            if hit(c, rph):
                return {"jam": float(rph), "log": log}
            a = c
        log.append((float(rph), round(a, 2)))
    first = next((r for r, x in log if x < bank - 0.01), None)
    home = next((r for r, x in log if x <= -bank + 0.01), None)
    clean = home is not None and all(x <= -bank + 0.01
                                     for r, x in log if r > home)
    return {"jam": None, "first_push": first, "home": home,
            "exit_clean": clean, "log": log}


def shake(hit, bank, phases=np.arange(-180, 180.01, 2.5)):
    """Fork resting at +bank with the balance at each phase: how far
    toward centre can a knock move it before the guard dart or a horn
    stops it? Returns (lowest angle reached, phases where the PARKED
    fork already collides with the roller outside the engagement arc)."""
    low, parked = bank, []
    for rph in phases:
        if hit(bank, rph):
            if abs(rph) > 20:
                parked.append(float(rph))
            continue
        a = bank
        while a > -bank and not hit(a - 0.1, rph):
            a -= 0.1
        low = min(low, a)
    return low, parked


def study(fat=0.0, unlock=1.5):
    """Keys:
      jam          roller phase at which the pin is blocked, or None
      first_push   phase at which the pin first moves the fork
      home         phase at which the fork reaches the far banking
      lift_deg     home - first_push: the balance arc spent on the fork
      exit_clean   the pin leaves without touching the fork again
      knock_floor  the lowest angle a knock can move the parked fork to
                   (it must stay well on its own side of 0)
      parked       phases where the parked fork fouls the roller
    """
    hit, bank = make_hit(fat)
    r = one_pass(hit, bank, unlock=unlock)
    out = {"jam": r["jam"]}
    if r["jam"] is None:
        out.update(first_push=r["first_push"], home=r["home"],
                   lift_deg=r["home"] - r["first_push"],
                   exit_clean=r["exit_clean"])
    out["knock_floor"], out["parked"] = shake(hit, bank)
    return out


if __name__ == "__main__":
    for fat in (-0.05, 0.0, 0.08, 0.10):
        print(f"printed {fat:+.2f}:", study(fat))
