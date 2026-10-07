"""K1's binding of the shared cycloidal gear engine (movement.gears).

Same public API this package has always had — module, backlash and
addendum default to K1's TRAIN parameters — so every call site in the
caliber stays unchanged. The tooth-form math lives in movement/gears.py.
"""

from movement import gears as _engine

from .parameters import TRAIN


def wheel_face(teeth: int, mate_teeth: int, module: float = None,
               backlash: float = None, addendum: float = None):
    # BS978 practice (and the engine docstring's own advice, finally
    # applied — coda 4): wheels driving LOW-LEAF pinions get a 0.85
    # addendum. A full 1.0 ogive on a 6-7 leaf mate makes approach-side
    # contact before the line of centers — the scraping Jon feels as a
    # sticky train. Mates with 11+ teeth keep the full addendum.
    if addendum is None:
        addendum = 0.85 if mate_teeth <= 10 else TRAIN.wheel_addendum
    return _engine.wheel_face(
        teeth, mate_teeth,
        module=module if module is not None else TRAIN.module,
        backlash=backlash if backlash is not None else TRAIN.backlash,
        addendum=addendum,
        dedendum=TRAIN.wheel_dedendum)


def pinion_face(teeth: int, module: float = None, backlash: float = None):
    return _engine.pinion_face(
        teeth,
        module=module if module is not None else TRAIN.module,
        backlash=backlash if backlash is not None else TRAIN.backlash,
        dedendum=TRAIN.wheel_dedendum)


def center_distance(z1: int, z2: int, module: float = None) -> float:
    return _engine.center_distance(
        z1, z2, module if module is not None else TRAIN.module)
