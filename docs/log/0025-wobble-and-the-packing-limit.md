# 0025 — Wobble, and the packing limit hiding in the third wheel

**August 3, 2026.** Bench report from the first train assembly: two
wheels spin, three sometimes, four locks — every time. Jon, watching
from the side: the wheels visibly wobble. Holding one wheel and rocking
its mate gives about a degree of play each way, and the barrel–minute
mesh is looser than minute–third.

## The numbers agree with his fingers

Designed backlash is 0.30 mm circumferential — about **0.6° total** at
the minute wheel. Jon feels ~2°. The extra ~1.4° ≈ 0.7 mm at the pitch
line, which is the bore clearances talking: 0.20 radial per pivot
(pre-measurement guesses, set before the printer's real accuracy was
known) → 0.4 mm diametral per arbor, two arbors per mesh. The
barrel–minute mesh is loosest because it stacks **three** interfaces:
drum-on-arbor, arbor in its 2.0-deep plate cup, arbor in the bridge.

Why length kills the train: over the ~12 mm plate-to-bridge span, 0.4 mm
per bore lets an arbor cock ~3–4°, swinging a Ø56 wheel rim **±1 mm
axially — against 0.25 mm of designed air between gear metal and its
plane band**. Every station added is a new neighbor for a tilted rim to
rub, while torque falls ÷360 by the fourth pinion. Two wheels shrug;
four stall.

## The recount that refused to pack

The obvious deeper fix: the 45/6 third–fourth mesh is the classic
low-leaf binder, and (56/7)·(60/8) = 60.000 exactly — an 8-leaf fourth
pinion with the fourth wheel, escapement, and 0024's sixteen teeth all
untouched. The layout solver said no. Not "no room at this azimuth" —
**zero placements at any grid step**, because the third wheel (plane A)
must clear the minute *pinion* (plane A) across the fixed minute–third
center distance:

    Z3/2 + 1  ≤  (Zm + p3)/2 − (pm/2 + 1) − 2   →   Z3 ≤ Zm + p3 − pm − 6 = 45

The train was already **at the packing limit**. 45/6 was never integer
convenience — it's the biggest third wheel this architecture holds at
module 1. Every ≥8-leaf recount pushes some wheel past 60t and hits the
same wall (or the barrel-arbor cap that froze Zm at 56). Filed under
things the solver knew before we did.

## The coupon kit (exports/k1/print/coupons/)

Measurement before commitment — `tools/export_fit_coupons.py`:

- **fit_ladder + fit_pin**: the real blind bushing (Ø2.6, 3.0
  engagement) at six clearances, 0.05–0.20. The tightest tick a pin
  spins dead-free in becomes the print `pivot_clearance`.
- **mesh_jig + six test gears**: 45/6, an 8-leaf 60/8 *reference*
  (packing-blocked as a recount, kept as the control), and 56/7 — each
  at center distance pinched −0.25 / nominal / spread +0.30. Pinch is
  what bore slop does dynamically; the decisive cell is pinch on the
  6-leaf.

Decision table: 45/6 fine at nominal, binds only at pinch → tightened
fits carry rev C. 45/6 binds at nominal while 60/8 stays sweet → leaf
count is the wall, a rev D architecture question. Everything binds at
pinch, even 8 leaves → module 1 itself is marginal on FDM and the
scale-up conversation reopens — as a *module* change in code with
clearances held absolute, never a slicer scale (which multiplies the
very slop we're chasing and breaks every M3 bore).

## Coupon results (same day — Jon's bench)

**Ladder:** tick 3 (0.11) spins dead-true for one pin; 0.14–0.20 wobble
visibly, with 0.20 falling out of its bore on a spin. The second pin ran
perfectly even at tick 1 — **printed pivots vary ~2 ticks (±0.03 r)
part-to-part**, so 0.11 is the design value and the bench rule is:
spin-test every arbor, spares absorb outliers.

**Mesh jig:** all nine cells turn smoothly — even pinch on the 6-leaf,
even fast. Spread shows lash and a whiff of jump-out, nothing more. Jon
then caught the instrument's flaw: with slack in the jig bores, drive
torque's separation force parks both pivots on the loose side, so a
drilled pinch relieves back toward nominal — the cell tests *entering*
pinched geometry, not sustained pinch. Caveat now lives in the jig
README. The same physics runs in the movement, and it points the right
way: a driven train self-biases toward spread, which the jig showed to
be benign.

**Verdict: the mesh was never guilty. The fits were.** And the plane-air
arithmetic agrees with the symptom pattern: cross-plane metal-to-metal
air is 1.0 mm; at 0.20 fits the ±1.05 mm tilt excursion just reaches the
neighboring plane (why three wheels *sometimes* ran), at 0.11 it's
±0.55 mm — clear by nearly half a millimeter.

`pivot_clearance` print = **0.11** (variants.py, measured comment
attached). All 91 gates pass; kit re-exported; plate bushings verified
Ø2.82 in the STL.

## Cost recorded honestly

The clearance lives in more bores than the plate: reprints are
**mainplate, wave bridge, drum + cover (arbor bores), crown wheel (stud
bore)** for the train, then **bay strap + balance cock** with the
escapement wave 0024 already ordered (escape wheel ×3, hairspring ×3,
balance wheel), and the dial-side gears whenever that stage assembles.
Train arbors are innocent — reprint only bench-culled outliers.
`Variant.endshake` turned out to be consumed by nothing in rev C —
axial float is baked into the ZC bands — so the pivot bore is the whole
fits story. The 0.20 guess is retired by measurement, which is how it
should have been born.
