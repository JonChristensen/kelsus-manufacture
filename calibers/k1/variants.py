"""The variant switch: one geometry, two material worlds.

Set K1_VARIANT=metal (env) or pass variant= explicitly. Print and metal
share ALL layout coordinates and wheel counts; they differ only in the
dimension tables below — and every derived height (like the stem line)
is computed FROM these, so flipping the switch reflows the movement.

(Born in rev B, but it's a caliber-wide contract: rev C and the tests
consume it too — which is why it lives here and not in the attic.)
"""
from dataclasses import dataclass
import os as _os


@dataclass(frozen=True)
class Variant:
    name: str
    drum_h: float           # barrel drum height (spring volume driver)
    usable_turns: float
    pivot_clearance: float  # running fits
    endshake: float         # axial float per train arbor, shoulder-to-shelf
    #   (coda 5: finally CONSUMED — the stepped bridge bearings + arbor
    #   tip shoulders. Print 0.35 sits under the smallest face gap
    #   (0.45, minute wheel to bridge web) so shoulders always stop the
    #   arbor before any wheel face can touch a plate)
    spring: str             # mainspring spec
    escapement: str         # swiss_lever both worlds (log 0015); pin_pallet = fallback
    lock_deg: float         # pallet lock: deep for print error, fine for metal
    draw_deg: float
    backlash: float = 0.30  # train mesh backlash (probe-tuned print default)
    press_r: float = 0.03   # radial press-fit interference on the O3 staff
    esc_teeth: int = 30     # escape wheel teeth: beat = esc_teeth/30 Hz
    #   (arbor is train-fixed at 30 s/rev). print=16: chunky 22.5deg-pitch
    #   teeth a 0.4 nozzle renders faithfully, stately 0.53 Hz tick;
    #   metal=30: the 1 Hz watch beat the fine-toleranced world can hold.
    #   16 vs the fork's frozen +-39deg stones = 3.47 pitches, 0.03 off
    #   the deadbeat half-integer — absorbed in stone tuning (probe-OK).


VARIANTS = {
    # pivot_clearance 0.11: MEASURED, fit-ladder coupon on Jon's H2C
    # (Aug 2026, log 0025 — retired the 0.20 pre-measurement guess that
    # let arbors cock ~4deg and rub planes). Printed pivots vary
    # ~±0.03 r part-to-part at this size: bench-select, spares absorb
    # the outliers. Backlash stays 0.30 — lash was never the binder.
    "print": Variant("print", 17.0, 1.5, 0.11, 0.20,
                     "PETG strip 1.6x16", "swiss_lever", 2.0, 15.0,
                     backlash=0.30, press_r=0.03, esc_teeth=16),
    "metal": Variant("metal", 4.5, 7.0, 0.04, 0.10,
                     "steel 0.30x14 (spec at DFM pass)", "swiss_lever", 1.5, 13.0,
                     backlash=0.12, press_r=0.01),
}


def active_variant() -> Variant:
    return VARIANTS[_os.environ.get("K1_VARIANT", "print")]
