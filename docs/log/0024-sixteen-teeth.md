# 0024 — Sixteen teeth: the escape wheel meets the nozzle

**July 12, 2026.** Jon, holding the printed escapement: the 30t wheel's
teeth are too fine for a 0.4 nozzle, and a 12t wheel he found online
(a published printable clock) shows what forgiving plastic escapement
geometry looks like. He asked the right question: *do all escape wheels
have 30 teeth?*

They don't. Watches run 15/20; our 30 was integer convenience
(30t × 1 Hz = 30 s/rev = the seconds-true fourth), not a print decision.

## The discovery that made it cheap

The escape wheel meshes nothing — the train drives its arbor's 18t
pinion, so the wheel's tooth count is **beat rate only** (f = teeth/30
Hz). And the fork's stones, frozen ±39° in the printed plate, span 3.47
tooth-pitches at 16t — within 0.03 of the deadbeat half-integer. So 16
teeth drops in with **no mainplate, bridge, fork, or train changes**:
pitch 22.5°, tooth arc 6.3 mm — the same proportional tooth room as the
12t reference. Volume-probed: capture humps alternate at 0.48 pitch,
free margins wider than 30t ever had (60% vs 46% of cycle).

15t and 12t would need the pallet pivot moved — a plate reprint. 16 is
the only chunky count the existing plate supports. Taken.

## Paying for the beat: 0.53 Hz

f² ∝ k/I must shrink ×0.284. Split three ways, because each lever alone
runs out of room:

- **Hairspring ×0.55** — h 2.5→1.75, coils 11→13. More coils don't fit:
  past 13 the first coil walks onto the collet lip and the beat slit
  would sever it (found by arithmetic before it was found by bench).
- **Printed rim ×1.26** — whirlpool windows stop at r14 (was r20).
- **Timing screws ×~1.55** — 6× M3×8 steel in the r23 rim holes. The
  holes were always called "timing holes"; now they earn the name.
  Screw length/count = the bench rate trim, which a printed movement
  needs regardless — every spool's modulus is different.

Wired as `Variant.esc_teeth` (print 16, metal 30): the metal world keeps
its 1 Hz watch beat; plastic gets teeth it can actually print. The
escapement gate test now checks capture-hump alternation generically
(the old free-set-disjointness only held at 30t geometry).

## Cost recorded honestly

Jon's already-printed 1 Hz hairsprings are obsolete for the print
variant (tuned 3.5× too stiff), as is the light balance wheel. Reprint:
escape_wheel ×3, hairspring ×3, balance_wheel ×1. Tooth form and count
both derived by measuring the reference part — parameters, not mesh.
