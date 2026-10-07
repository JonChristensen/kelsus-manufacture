# 0028 — The spring was wound backwards

Oct 6, 2026. Jon could not feel the mainspring holding energy, opened
the drum, and found the spring broken: the inner C-loop snapped off
where the spiral left it (IMG_4063). He asked whether the reprint was
the moment to fix the spring properly. It was — and his photo showed
the first fault before the fracture did.

## Three faults, one spring

**1. The wrong hand.** Look into the open drum from the cover side
(bridge view). The broken spring's strip runs outward
*counter-clockwise* from the arbor. The arbor winds *counter-clockwise*
(the click blocks clockwise; coda 4 derived it from the train's
chirality, and Jon's bench confirmed the click holds that way). Turn
the inner end of a spiral the way its coils run and you *unwind* it:
the same strip has to span fewer degrees, so it moves out, not in.
Every counter-clockwise wind pressed the coils out against the drum
wall. That is why it went "heavy at half a turn, solid under one" — the
packing arithmetic of log 0027 predicted 1.14 turns to solid the
*right* way round, so the number agreed by accident and hid this.

`mainspring_c()` drew that hand (angle rising with radius), the guide
said "spiral as printed", and a flat spiral turned over is its own
mirror image. Nobody said which face up because nobody had checked the
hand against the winding direction.

**2. A notch at the root.** The inner end was a C-loop at r6.6 with
the spiral leaving it tangentially. Where the strip's inner edge parts
from the loop the two faces meet at a near-zero angle: a crack starter
at exactly the point carrying the full torque. The fracture is there.

**3. Too much strain.** A spiral strip under a pure moment strains
uniformly, ε = π · turns · t / L. At 2.2 thick, 425 long, 1.14 turns
to solid: 1.85% — and at the hub the first coil, printed at r6.9 and
wound onto r5.5, sees 4%. PETG yields around 2.5%. Wound the right
way, this strip would have broken on its own schedule.

## The spring now

`SPRING_C` / `mainspring_c(t)` / `mainspring_layout(t)` in
`calibers/k1/revc_parts.py`:

- **Hand:** outward CLOCKWISE in bridge view, so a counter-clockwise
  arbor tightens it. Gate: `test_revc_mainspring_is_the_hand_the_click_winds`
  checks material along the designed centreline on the built solid and
  that its angle falls as the radius grows.
- **Which way up:** the blind hole in the outer tab's top face. Hole
  toward the cover; print hole side up.
- **Inner end:** a solid ring (r5.65–8.5) over the arbor's r5.5 hub with
  a keyway for the hub's existing 2.4 mm rib — the arbor is unchanged.
  The strip grows out of the ring through a root 1.6 t thick that
  tapers to t over 115°, its inner face peeling off the ring on a
  smooth curve and its back rising out of the ring on a ramp. No loop,
  no notch; the ring takes the rib's push in bearing.
- **Outer end:** a 5 mm tab from inside the last coil to 0.4 off the
  wall, its counter-clockwise face 0.3 off the drum rib's clockwise
  face, which takes the tangential pull — and a Ø2.8 blind hole in its
  top for a **Ø2.5 pin on the underside of the drum cover**, which takes
  the inward pull. See "Jon's second finding" below for why the pin
  exists. The last coil stays inside r24.6 so the top millimetre of the
  strip clears the three cover lugs at r24.9 — the old spring's r26.3
  outer coil did not, and sat pushed in by them.
- **Sizing rule:** the coils pack solid on the ring — the only stop a
  going barrel has — at or under 1.5% strain (30 MPa). So the
  instruction is "wind until it stops", and it cannot be overwound.
  For the kit's 1.7 strip: pitch 3.62, 4.0 printed coils, 414 mm,
  solid at 1.14 turns (27 ratchet teeth), 75 N·mm per turn, 85 N·mm at
  solid, 1.48%.

## The torque question is still open

The number that sizes this spring is what the train needs at the drum
with the balance running, and we do not have it. Two estimates bracket
it badly: the bare train ran on under half a turn of the old spring
(< 80 N·mm), while an energy budget for the balance (pivot friction
~0.003–0.012 N·mm, lever efficiency ~0.35, 418:1 from escape wheel to
drum, ~0.5 through four printed meshes) lands anywhere from 100 to
700 N·mm. If the high end is real, no PETG strip in this drum delivers
it for more than a fraction of a turn: a spiral strip's torque is
bounded by σ·h·t²/6, and the turns available by the difference between
coils packed on the ring and coils as printed, which this drum caps
near 1.5 regardless of length.

So the spring is a ladder: `MAINSPRING_LADDER = (1.4, 1.7, 2.0)`.
Same ring, keyway, root and tab; only the strip changes.

| strip | turns to solid | teeth | N·mm/turn | N·mm at solid | strain |
|---|---|---|---|---|---|
| 1.4 | 1.39 | 33 | 35 | 49 | 1.26% |
| 1.7 (kit) | 1.14 | 27 | 75 | 85 | 1.48% |
| 2.0 | 0.97 | **stop at 20** | 141 | 136 (120 at 20) | 1.70% |

Jon prints all three, starts on 1.7, and reports which run and for how
long from solid. If 2.0 is the only one that runs, rev D needs a
different answer — a smaller drum ratio than 6 h/rev (more turns per
hour of running), or a steel strip, which stores ~1000× the energy per
volume and is the one place metal buys the most.

## Jon's second finding: why the tab popped off

Jon had in fact tried the right hand first. His words: "when I put it
the other direction, it would just pop out of the nub that was supposed
to hold it in place, so you couldn't build torque." So he turned it
over, and the wrong hand *held* — because a spring wound the wrong way
expands, pressing its outer end out against the wall and onto the rib.

The right hand does the opposite, and it is not a detail. A relaxed
printed spiral, wound, draws its coils in toward the ring; the outer
coil lifts off the wall and the strip leaves the anchor on a chord
toward the pack, pulling the anchor *inward* at roughly 0.6 of the
strip tension (about 2 N on the kit spring). A real mainspring never
sees that pull: its free shape is reverse-curved so the outer coils
press outward on the barrel wall even fully wound, and a plain hook
suffices. Ours has no such pre-stress, and a drum wall has no surface
that faces outward: the wall faces in, the rib faces in and sideways.
No hook, pocket or dovetail on the tab can be retained by them against
an inward pull — I drew one (a pocket over the rib) before working
that out. The only outward-facing surfaces in the barrel are the
arbor's, and the floor and cover's.

So the anchor is vertical: the **drum cover carries a Ø2.5 pin, 2.5
long, that drops into a Ø2.8 blind hole in the tab** (`cover_pin_xy()`,
`SPRING_C["pin_*"]`). The rib still takes the tangential load on the
tab's counter-clockwise face, 0.3 away; the pin takes the inward pull
(2–4 N in shear on a PLA pin — nothing) and, as a side effect, stops
the cover rotating. The cover's lift is limited to under a millimetre
by the bridge web above it, so the pin stays engaged. The cover
reprints (Class B, pin up); the drum does not. Gate:
`test_revc_mainspring_lives_in_the_drum` now pulls the spring 0.6 mm
inward and 1° each way and demands a collision each time.

## Bench consequences

- Discard the 2.2 spring. The arbor and drum stay; the **cover reprints**
  (it carries the spring's anchor pin).
- `exports/k1/print/mainspring.stl` is the 1.7; `bench/mainspring_t1.4.stl`
  and `bench/mainspring_t2.0.stl` are the rungs; the bench README has
  the table and the stop for each.
- Assembly guide Stage 1 rewritten around the ring, the rib, the hole
  and the cover pin; the Stage 1 gate names the direction that should
  resist.
  The "18 teeth" rule in Stage 5 and the bench README is replaced by
  "wind until it goes solid" (and 20 teeth for the 2.0 strip).
- The STEP now poses the spring with the arbor's rib in its keyway.
- Gates: `test_revc_mainspring_is_the_hand_the_click_winds`,
  `test_revc_mainspring_lives_in_the_drum[t]` (no overlap with drum,
  cover or keyed arbor; rib fits only the keyway; tab reaches the rib;
  coils print ≥ 0.8 apart), `test_revc_mainspring_cannot_be_overwound[t]`,
  and the spring joined the z-band table.

## What this says about the earlier bench rounds

Not what I first wrote. A wrong-hand spring still releases the drum
the right way: whatever the coils do, a counter-clockwise twist of the
inner end relative to the outer unwinds as a counter-clockwise drum.
So the half-turn that "ran the bare train for 15 seconds" ran it
forward, and the fork-flop video of log 0027 was taken with the wheel
turning the right way. What was contaminated is the torque: a spiral
jammed outward against the wall delivers its energy through wall
friction, on a curve nobody can predict, with its root at the notch
carrying all of it. The lock redesign stands on its own measurement
(the solver had shrunk the locking face to 0.04 mm); what the bench
saw it under is anyone's guess. The first clean torque the escapement
will ever see is this spring's.
