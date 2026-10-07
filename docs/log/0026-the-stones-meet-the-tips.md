# 0026 — The stones meet the tips: rebuilding the pallets for the wheel we actually print

**August 11, 2026.** Bench photo from Jon: pallet fork and escape wheel
assembled on the plate, one stone in a tooth gap, "not enough clearance
for the mechanism to *tick* back the other direction when one prong is
engaged." The exit stone is sitting ON TOP of a tooth — tip to tip.

## The probe that replaced squinting

Volume-threshold pose checks had passed this geometry, so the first
move was a better instrument: `tools/probe_escapement.py` sections the
real solids into 2D polygons and *runs the tick* — wheel torque-butted
CCW against the lever while the fork sweeps banking to banking, recoil
allowed. Ground truth per pose, ~40 s per run.

First run, old geometry: the tooth released the entry stone at 4.8 deg
into the 13 deg fork swing, and from there **neither stone gated the
wheel** — it free-ran more than a full pitch (the probe measured 24.5
deg) with the exit stone still 1.7 mm away. A free-running wheel lands
at random phase; sometimes that phase is a tooth top under the exit
stone, which is exactly Jon's photo.

## Root cause: 0024 changed the contact, the stones never heard

The July tooth re-cut (log 0024) made the wheel touch stones with
**tips only** at r16. But `lever_layout_c` still placed the stones by
the flank-era rule — working faces at `r_esc - sin(lock) - 0.4` ≈ r15,
a full millimetre INSIDE the tip circle, where a tooth tip can never
rest. The tips butted the stones' radial *backs*, the lock was
accidental, and the deadbeat handoff didn't exist. The old gate test
actively asserted the defect: "at neutral the wheel passes free" — a
free wheel at neutral IS the open gate.

## What the rebuild learned (each item probe-caught, in order)

1. **Embrace re-phased to the half-integer.** Contact azimuths now sit
   3.5 tooth pitches apart (±39.375 deg at 16t). P does not move — the
   plate survives; only the lever reprints.
2. **The deadbeat direction here is radial.** E–contact–P is ~94 deg,
   so an arc about P (the classic deadbeat locking face) is nearly
   radial about E. The locking face is that chord, draw-tilted, crossing
   the tip circle at the contact.
3. **The arm had to move.** Tip-contact stones sit ~1 mm closer in; the
   old straight boss-to-stone arm chord put its band edge INSIDE the tip
   circle — the wheel butted the *arm* 10 deg before the face. The arm
   now routes to a waypoint at r18.4 **in the engaged frame** (the
   banking swing plunges the whole side ~1.5 mm; a route laid out at
   neutral dips into the wheel at the banking) and welds at the face
   top. A weld hull that merely *touched* the corner left the stones as
   disconnected solids; the weld point now sits 0.45 inside the body.
4. **The impulse ramp is a trace, clipped by the real tooth.** The ramp
   is the path of the tooth tip in the stone frame under a chosen
   schedule (fork rides 6.5 deg past unlock, wheel advances 1.25 deg
   per fork deg). The printed tooth's hook back is a 3-chord polyline
   that bulges above the smooth t^0.6 form — the nose had to tuck
   2.64 deg downstream of the rest azimuth to clear it, and the ramp's
   coupling was flattened until the trace hugs the hook with ~0.15 mm
   to spare.
5. **The catch lands on the ramp, and that's the budget.** With lift at
   0.228 mm/deg and teeth only 2.8 mm deep, the wheel cannot stay
   coupled to within 1.7 deg of the far banking — a free flight is
   structural. The half-pitch spends as: ~2.6 deg face creep during
   unlock, ~8.1 deg coupled ride, ~5.8 deg flight, then the catch eases
   the wheel BACK ~6 deg as the fork seats (the plunging ramp pushes
   the caught tooth upstream). That retrograde is the efficiency debt
   of this architecture — cheap on the bench (back-driving the train
   is nearly free), a real question for the balance-driven stage.

## Jon's second catch: the stones were about to snap off

Same day, from the *render*: "how are those teeth connected to the
fork? They look like they might break right off." He was right, twice
over. The first weld hull touched the stone at a single geometric
point — OCC fused it into "one solid" that was two parts in every way
that matters. The fix-of-the-fix pulled a weld point 0.45 mm inside
the stone, which passed the one-solid check but necked to **under
0.1 mm** — sub-nozzle, unprintable, unsnappable only because there was
nothing there to snap. A second attempt with two pad points left a
0.6 mm isthmus.

The instrument that settled it: an **erosion probe** — shrink the
mid-body cross-section inward until it separates; twice the surviving
radius is the narrowest load path. The shape that passes: the stone's
back is now a **convex bulge from fin peak to face top at r17.4-18.0**,
territory the tooth tips (r16.0 exactly) can never reach at any pose,
and pose-safe against the bay wall because |pad − P| never changes.
The arm hull welds onto two anchors inside that bulge. Narrowest
bridge: **1.3 mm** plan × 2.1 thick ≈ 2.7 mm² — versus tenths-of-a-
newton working loads, and safe against tweezers and support-peeling.
The one-solid check and the tick sim both stand unchanged.

## The numbers, frozen (print variant, probe-verified)

Rest: tooth land-corner ON the locking face at r15.95, 0.2 deg off the
designed azimuth. Advance per half-swing: **11.24 / 11.26 deg** against
a half pitch of 11.25. Longest free run 5.8 deg; catch retrograde 6.2;
no jam, no runaway, cycle repeats at exactly one pitch. The gate test
now runs this simulation as the contract (shapely added to
requirements); the neutral-free assertion is inverted — at neutral the
wheel must butt within one pitch.

## Coda: one M2 screw for the whole movement (Aug 15)

Jon's fastener box turned out to be M3; the six M2s were never
ordered. The docs said "M2 self-tap ×6" — three lengths across three
parts, and the wrong *type* if bought literally: the pilots (Ø1.6–1.8)
want a **thread-former** that displaces plastic, not a sheet-metal
self-tapper that shaves it. Finding one at retail was the surprise:
genuine M2 PT/Delta-PT screws for plastic are a 5,000-per-carton
world (Fastener SuperStore, Monster Bolts) or dried-up 100-packs (US
Micro Screw's Amazon storefront). McMaster's M2 shelf holds only
Taptite® — thread-forming *for soft metal* — but a tri-lobular
Taptite is a thread-former, and in 6 mm of printed plate the narrower
flank is irrelevant. **McMaster 94209A343, M2×6, pkg 100, $9.** Ordered.

It comes in ×6 only. Rather than three lengths and a "which goes
where" trap, the parts were made to fit the screw:

- **dial platform** ×3: plate pilots 2.0 → **5.5 deep** (three sites
  probed solid to depth; 1.0 roof, tip air 0.3).
- **click** ×1: the bridge web is 1.3 thick — the click's screw only
  ever had 1.3 mm of thread. A **r2.4 boss now hangs under the web**
  to z11.6 (0.6 over the drum top; no plane-B sweep reaches that XY —
  probed) and the pilot runs through: **4.4 mm of thread**, tip flush.
- **bay strap** ×2: the interesting one. The near foot's pilot is
  **capped at z2.5 by the dial-side solver** (moon B2 pockets 1.9 deep
  + 0.6 web — the old 2.5 was never arbitrary), so the plate could not
  be deepened there. And investigating headroom found a latent bug:
  the old service test checked the screw *shank* radius (1.1) against
  the balance rim, not the *head* — a Ø4 pan head at the old feet
  (r27.5 from B) sat **0.5 mm inside the r26 balance rim**. Both feet
  moved to **20.8 from P** (r28.45 from B) and grew **r2.2 × 1.7 head
  bosses**: heads clear the rim by 0.25, and the raised bearing face
  lets the ×6 land 0.3 above the capped pilot. The service test now
  checks the head radius. Strap and plate reprint together.

The fasteners are now **parts in the build**: `m2x6_screw_c()` posed at
all six sites goes into the STEP, and a new gate asserts each screw
touches only what it fastens and threads ≥3.5 mm into its anchor. That
gate immediately found the second latent issue: the three platform
screw heads stand 1.4 proud of the platform's dial face, straight
through the 1.0 dial sheet. The sheet now has Ø4.6 clearance holes;
**three pan heads show 0.3 proud in the dial face** — the honest cost
of holding the platform from the dial side with the plate 6.5 thick.
A flush dial wants countersunk heads and a thicker sheet: aesthetics
pass, Jon's call.

## Coda 2 (Aug 19): the fork that parks anywhere — and why

Jon's video: the Aug-16 fork assembled, wheel spinning **free with the
fork parked at neutral**. The probe had passed it. Both things are
true, and tracing why took the day.

1. **The mid-swing gate was closed by 0.3 mm** — the gate test asserted
   a sign, not a margin; the 0.11 pivot fit erases 0.3 mm. Lesson
   taken: the test now measures intrusion.
2. **Far worse: the escapement has no draw.** New probe check — butt
   the wheel at a banking, move the fork 0.1° off its pin — shows the
   wheel advancing *freely* at both bankings. Nothing pulls the fork
   home; that is *why* it parks anywhere, and it means a balance would
   never keep it running. The tick sim drives the fork externally (like
   tweezers) and never asked whether it stays put.
3. **Root cause, found by stepping the wheel into the stone and naming
   the first contact:** it is the **hook-back of the approaching tooth,
   6° ahead of its tip**, landing on the stone's ramp at r14.3 — before
   the tip ever reaches the locking face. The tooth's back sweeps
   forward ~13° from the land down to the root, so **anything the stone
   dips below r16 downstream of its face is met by the tooth's back
   first.** Envelope, measured: 0.5 mm max intrusion 2° downstream,
   1 mm at 4°, 1.8 mm at 8°. Every ramp I built (ride 4–10, couple
   0.4–1.25, floor 13.8–15.3, both draw signs, narrow and wide) violated
   it near the face; the "lock" in every variant was the stone's belly
   on a tooth back — an impulse-direction surface, hence zero draw and
   a hair-thin free window.
4. And the mid-swing gap follows from the same envelope: a ramp that
   respects it at banking sits ~1.5 mm higher at neutral (lift ×6.5°),
   i.e. at or outside r16. **With this tooth form one stone cannot both
   respect the hook-back and reach the wheel at neutral.**

Two smaller bugs fixed on the way: the nose was a separate tucked point
that made the stone's underside a V (flank-on-apex catch) — it now lies
on the face line; and the fin lean is capped so narrow stones don't
self-intersect.

**Open design point — Jon's call, not taken here:** (A) reshape the
tooth (steeper back right behind the land) — wheel + fork reprint, real
margins on draw, window, and mid-swing; (B) keep the wheel, build the
ramp to the envelope — face lock with draw, but ~0.2–0.3 mm mid-swing
reach and a fork that parks free on the bench; (C) both. Recommended C.
ESC_TUNE is held at the Aug-16 printed values as the baseline until
then; the probe carries the new draw/window/depth instruments.

## Coda 3 (Aug 19, later): Option C — the tooth was backwards

Jon chose C (reshape the tooth too). What followed corrected coda 2
in three places, and they're worth stating plainly because each one
cost hours:

1. **The tooth was mirrored.** The July wheel's raked locking face
   was on the tooth's *trailing* side (rising from the gullet up to
   the tip, in the direction of travel) with the land and back
   *ahead* of the tip. A stone waiting ahead of the tooth is therefore
   always met by the tooth's back first and its tip last. "Steepen
   the back" (coda 2's plan) can't fix that; only putting the face on
   the **leading** side can. Done: in travel order the tooth is now
   tip → 20°-raked face falling to the root → root → steep back rising
   → next tip. The tip leads; nothing of the tooth is ahead of it.

2. **Draw is a force, not a trap.** My draw test asked "does the
   fork have to make the wheel recoil to leave its pin?" — no working
   escapement satisfies that (the fork must unlock). It returned zero
   for every geometry including ones that were correct, and sent me
   chasing face angles for an hour. The right test is the torque of
   the resting tooth's push on the locking face about P: it must carry
   the fork into its banking. `Scene.draw_torque` now; +3.4 on both
   stones.

3. **A sharp tip is not a tip.** The design passed everything with a
   mathematically sharp tooth and then, with a print-realistic r0.2
   rounding, the round slid *under* the face: rest fell to r15.26 and
   draw went *negative*. The tip is a **0.2 mm flat** now (prints
   faithfully, gives the face a defined edge), the gate runs the whole
   contract again on an r0.1-rounded wheel, and the stone's lock
   depth below the tip circle is *solved* against the tooth envelope
   (`hook_back_r`, which now correctly describes both sides of the
   tip) instead of guessed — it resolves to 0.04: the flat locks on
   the face right at the tip circle, the 2.4 mm of stone inside the
   wheel at banking is the real lock depth. Any deeper face puts the
   foot where the tooth's flank arrives first (probe-verified: forced
   0.45 → flank-on-foot, fragile).

Also: `face_rake 20°` (was 38; the 0.33 mm/° fall at 38 reached any
sub-r16 stone material 1.2° ahead of the tip), stone impulse bevel
built as the tip trace *clipped to the tooth envelope* (hugs the tooth
from outside at banking; the tip climbs it as the fork lifts),
`ride 10.5 / couple 0.9` (probe knee: 9 → mid +0.34, 10.5 → +0.41,
12 → the bevel turns anti-impulse and drives the wheel backward).

**Frozen (probe, print-realistic r0.1):** tip on the face at r15.96 ·
draw +3.38 / +3.42 · mid-swing intrusion +0.40 (was 0.28 on Jon's
fork, 0.3 mm of which the 0.11 pivot fit ate) · free window at banking
9–10° (was 0–1) · tick 11.24 / 11.26 per half-swing against 11.25 ·
robust to r0.1 corner rounding (same numbers). Tooth 0.8 mm wide at
mid-depth, 2.4 thick — prints at 0.4; it is a ratchet-style sawtooth,
which is what a deadbeat wheel looks like.

## Coda 4 (Aug 22): the winding stage was never a ratchet, and the
## train gets its textbook teeth

Jon, at Stage 5: which way does it wind? And two bugs: the click
cannot stop the ratchet, and the crown wheel's underside teeth are
hollow at 9 o'clock, solid at 3.

**Direction, derived not guessed:** the documented train chain puts
the drum at CCW (bridge view) running, so the spring torques the
arbor CW and the click must block CW. **Winding = ratchet CCW seen
from the bridge**; the crown knob, viewed from above, also turns
counter-clockwise. Now in the assembly guide.

**The click bug was total:** `ratchet_c` built its teeth with
`wheel_face(24,24)` — a symmetric involute spur. No click locks
symmetric teeth; the wedge cams out both ways. And the crown moire
was a vernier: 23 underside slots against a 24-tooth rim drift 0.65
deg/tooth, so once around the wheel the slots pass from under-gap
(solid teeth) to under-tooth (hollowed). Both wheels are now a
matched SAW pair (tips r13, roots r10.7): tip flat, near-radial
cliff, ROOT LAND, then a CONVEX ramp — steep below r12 where the
crown tip nests, shallow (58 deg) above where the click rides. Three
probe-caught corrections en route: the first saw was mirrored
(slipped at letdown, jammed winding); without the root land the pair
could not nest at ANY phase (0.68 mm3 minimum overlap); a straight
ramp made winding stiff (30 deg at the click's riding depth). Slots:
24, phase-locked under the gullets — every tooth identical and
solid. The crown carries a -0.75 deg phase trim centering the
clean-nest plateau. Verified behaviors, now a permanent gate
(`test_revc_winding_is_one_way`): letdown butts a 7.7-deg cliff in
0.1 deg; winding cams a 58-deg ramp; crown CW drives ratchet CCW
59.5/60; reversed crown hard-stops within one tooth (by design —
the guide says don't force it).

**The train's fidelity pass** (Jon's bench: "still a little sticky",
plus his textbook cycloidal-pair diagram): movement/gears.py now cuts
TRUE hypocycloid dedendum flanks (the deep hollow gullets of the
reference — the old straight-radial shortcut needed a 0.35 root
relief to avoid scraping), 24-point flanks (12-point facet flats were
part of the friction), eased tip corners, FULL semicircular pinion
noses (the 0.65 squash undercut the roll), and BS978 addendum 0.85
on wheels driving 6-10 leaf pinions — the approach-side scrape Jon
felt is exactly what an oversized addendum on a low-leaf pinion does.
Same module, same center distances: no plate or layout change.

**The escape-skip worry, quantified:** stretching the fork away from
the wheel by the full worst-case bore-slop stack (+0.32 mm, both
pivots hard against their cup walls) costs the mid-swing gate only
0.41 -> 0.33 mm — no static skip. Residual risk is 3D arbor tilt +
dynamic bounce: bench rule is to spin-select the fattest-pivot fork
and escape arbor for those two stations; next plate revision drops
the E/P cup clearance to 0.06 (logged here so it isn't folklore).

## Coda 5 (Aug 23): Jon's question that found the missing half of the
## bearing architecture

"I've been surprised that a big source of friction is the gear plates
rubbing against each others' faces and/or the main plate or bridge. In
metal movements the gears were suspended by their pivots in jewels.
Does our design anticipate this?"

The probe's answer: partially, and the missing half was load-bearing.
Measured axial float per train arbor, and what stopped it: minute
0.45 mm up, stopping as the 56t WHEEL FACE flat on the bridge web
(52 mm^3 of contact); third/fourth/escape ~0.45 up onto the bridge,
~0.18 down onto the plate. On the desk stand the movement's axis is
horizontal — gravity doesn't even pick an end — so every arbor wanders
its full float until a wheel face leans on something at r10-28, which
costs ~40x the friction of a shoulder stop at r~1. The tell: the
variant system had carried an `endshake` parameter that log 0025
noted was consumed by NOTHING. The plane-band system kept gear faces
off other GEARS; nobody built the axial bearings.

The fix is the metal principle, printed — and not a restart:

- **stepped bridge bearings**: r1.35 guide bore to a SHELF, then
  r0.85 for a reduced arbor tip; the pivot's shoulder annulus meets
  the shelf = the up-stop at small radius. (First cut failed: the
  1.2-tall lead-in cone stayed wider than the guide bore for its full
  height and swallowed the shelf — probe-caught; the lead-in is now a
  0.5 chamfer.)
- **arbor tips**: Ø1.4 x 1.2 reduced top tips (shoulder at z15.0);
  Ø1.2 nose bosses on the lower pivots so the down-stop on the
  existing cup floors is near-axis; the minute arbor — the one with
  no cup floor, whose down-stop was WHEEL-ON-DRUM — gets a r1.9
  collar riding its plate bore mouth.
- **endshake CONSUMED at last**: print 0.35 (must sit under the
  smallest face gap, 0.45), metal 0.10 — same architecture, tighter
  numbers. That is the metal-transferability answer: yes, by
  construction now.

Verified: every arbor floats 0.38-0.41 total and stops ON-AXIS with
~0.2 mm^3 shoulder/nose contact, both directions. Permanent gate:
`test_revc_arbors_float_on_shoulders_not_faces` (it would have failed
the old design at every arbor). Barrel arbor left as-is: its 0.07
float is bounded inside the drum by design.

**Coda 5 addendum — the cabochon pocket was waiting.** Jon's "beads"
turned out to be Ø4 x 2.09 flat-back garnet CZ cabochons — and the
cock has carried a decorative "cabochon pocket" since rev B (the
docstring always said so; the old shopping list was never a mistake).
Now it's functional: the 0.5 web under the pocket is a Ø2.4 hole, the
cab rim-seats dome-down (self-centering; apex depth set by dome
curvature, 0.40 below the rim, so the 2.08-2.10 batch spread doesn't
matter), and the apex at z16.30 is the staff's upper endstone —
endshake 0.30 on glass instead of PLA. Bare (no cab) the staff stops
on the pocket shoulder: degraded but functional. Honest physics: on
the vertical desk stand the staff is loaded radially and the stone
carries little; it earns its keep dial-down, in handling, and as the
visible red jewel. The lower (plate-side) stone is logged for the
next plate revision with the E/P cup tightening. The cab is a posed
component in the STEP (50 total) so the gates see it.

**Coda 5, bench round 2 (Aug 22):** Jon's reprint findings. (1) The
escape wheel's D-bore had ~5 deg of rotational wiggle on its seat —
which is wheel PHASE slop, spent directly out of the gate margins.
The bore is now a press fit (variant press_r on both the round and
the flat); arbors unchanged — wheel-only reprint. (2) "A third of a
millimetre more stone and we're perfect": probe-swept the ramp
schedule — ride 12 / couple 0.85 / floor 13.4 takes the mid-swing
gate from +0.41 to **+0.54 mm** (the ceiling: at ride 13+ the ramp
tail wraps into the next tooth's approach, the rest falls on the
tail, draw inverts, and the tick runs backward — the probe caught
all three). Worst-case bore-slop stretch now leaves +0.46. Combined
with the D-fix killing the phase slop, the bench margin roughly
doubles. Reprint: escape_wheel + pallet_fork only.

**Coda 5, rev 2 (Aug 24) — the bench voted on the endshake tips.**
Jon broke both new features within days: the Ø1.4 reduced top tips
snapped off the minute and third arbors at a touch (a 1.5 mm^2 column
across layer lines — a print-fragile feature I designed), and the
Ø3.5 wheel-to-pinion necks tore in torsion on the minute and third
(the layer-adhesion fuse of every vertical-printed arbor). Fixes:

- Tips DELETED, not beefed: the bridge bearings are now BLIND — a
  shelf at pivot-end + endshake with only a Ø1.2 vent through. The
  plain pivot's flat end face is the up-stop (mean contact radius
  ~0.8, same physics, zero fragile features, simpler arbor). Pivots
  end at 16.1; the bands and the endshake gate moved with them.
- Necks get stepped cone-fillets sized per station against the real
  tooth corridors: minute r3.0-2.3-3.0 (drum tips pass 4.0 away),
  third 2.6 then 2.0 toward its 8-leaf pinion (minute-wheel tips at
  2.5 in the float zone), fourth 1.75 at the bottom (third-wheel
  corridor at 2.0, as always) fattening to 2.6 at its wheel. Waist
  areas up 31-73 percent, and every junction now lands on a step
  instead of a sharp corner — the corner was where both breaks began.
- Lower nose bosses 0.6 -> 0.8 while in there.

**Coda 5, rev 3 (Aug 24): the click, third time, and the pawl-back
lesson.** The saw-tooth rebuild's click still came up short on Jon's
bench — its ~0.95mm engagement kept evaporating into print shrink,
rounded tips and peg slop. Deepening the wedge to r11.3 (1.7mm into
the teeth) jammed the wind at first: below the ramp's convex knee the
tooth wall is near-radial, and a full-depth shallow ramp is
IMPOSSIBLE in a 15-deg pitch (2.3mm of rise at 57 deg needs 14.8 deg
of arc; the pitch has 8.25 free — a knee-scaling attempt folded the
polygon and OCC refused it). The classic answer: the PAWL cams on its
own angled back. The wedge's winding-side flank now runs tip ->
(6.2, 12.0) at ~54 deg off radial; the tooth's knee corner slides
along it and lifts the click regardless of the under-knee wall. Probe
(now measuring BOTH surfaces at the contact — corner-on-flank camming
is governed by whichever is the flank): letdown cliff 8.3 deg in
0.05; winding cams at 53.5; crown drive 59.7/60; reverse hard-stop.
Click is a Class C PETG reprint; ratchet/crown unchanged.

Also answered for the bench: the ratchet and crown wheel are MIRROR
images ("opposing") by necessity — an external mesh presents each
wheel to the other rotated 180 deg, so a pair that look identical
side by side meet ramp-to-cliff and slip (the probe rejected exactly
that pair in coda 4). Assembled view from the bridge: ratchet teeth
hook CCW, crown (slots down) hooks CW.

**Coda 5, rev 4 (Aug 25): the winding stage's assembly paths.** Two
bench failures in one evening, same root class — the pose gates never
walked the ASSEMBLY PATH. (1) The crown stud would not enter its
holes: a stray "+0.35" in the tail radius shipped a O5.34 tail
against the O4.70 bridge bore (10x a press fit) that could not even
pass the wheel's own O5.32 bore. Tail is now bore + press_r with a
lead-in cone. (2) Jon broke the stem tunnel boss forcing the stem in
— and the arithmetic shows the one-print stem was NEVER installable:
O9 pinion on one end, O13.6 crown on the other, a closed O5.4 tunnel
between. There was no legal move; the boss was the fuse. The stem is
now TWO PIECES, the real-keyless-works way: stem + crown with a
D-flat tip slides in from outside; a separate winding_pinion presses
onto the D from inside and butts the tunnel's inner face as its
thrust shoulder; the C-clip is unchanged. New gates walk the paths:
the stud's widest tail section must pass the wheel bore and press the
bridge bore within a sane band; every stem section inboard of the
tunnel must pass O5.4. Kit gains winding_pinion (45 parts); reprint =
crown_stud, stem_and_crown, winding_pinion, and the bridge Jon broke.

**Coda 5, rev 5 (Aug 26): bridge-landing bench round.** Four at once.
(1) Wheels still rubbed the bridge: the shoulder-stop margin was
face-gap 0.45 minus endshake 0.35 = 0.10 — one short-printed pivot
wide. Fixed on the ARBOR side so the printed bridge survives: top
pivots +0.15 (end 16.25), endshake 0.20, shelf formula re-anchored so
the shelves land where the printed bridge already has them; margin
0.25. (2) The stem must go into the bridge BEFORE the bridge mounts
(the pinion press needs finger room under the web) — now Stage 4 step
1. (3) The click's peg holes scar (the pocket prints face-down):
holes r1.35 + chamfered mouths for future prints, and a bench note —
twist a Ø2.5 bit through by hand on the current one. (4) The M2x6's
forming taper exited the under-web boss flush and the last threads
stripped: the click grew a 0.5 screw boss that keeps the tip captive.
Reprints: four train arbors + click; the bridge is UNCHANGED at the
bearings by construction.

**Coda 5, rev 8 (Sep 30): the click boss twists off.** Driving the
click's M2x6 sheared the r2.4 under-web cylinder clean off the web
(Jon's bench: "couldn't hold up to the rotational forces created by
the screw"). What the section measurement shows: the two click-peg
holes sit 1.6 and 2.1 from the screw axis, so the stub's root met the
web over 8.3 mm^2 — two crescents between three holes — where a full
annulus would have been 15.5. The boss is now a cone, root r5.5 on
the web tapering to r3.0 at the tip: the root ring lands on unbroken
web outside the peg holes (81.9 mm^2, and ~22x the first polar moment
about the screw axis), the tip keeps 2.1 of wall around the pilot,
and the peg holes become blind under it. The space was free all
along: nothing but the screw itself occupies r9 of that axis above
the drum top. A new gate measures the root section on both sides of
the web interface. Lesson for the fastener gates: "the screw threads
3.5 mm" was asserted; "the thing it threads into can carry the
driving torque" was not. Reprint: **bridge_wave** only — click,
screw and pegs are unchanged.

The section drawing that checked the cone also caught the gate
itself lying. Rev 5 raised the click's screw seat 0.5 (the captive-tip
boss) but the posed screw in the STEP stayed at z17.65, head buried
in that boss — so the thread gate measured 3.67 mm for a screw that
really has 3.17: 2.55 full-circle in the under-web boss plus 0.62
equivalent in a web whose pilot the peg holes break open. Pose fixed
(seat z18.15); the click's gate is set to 3.0 and says why. The
stack caps it — 6.0 of shank, 2.1 through the click, 1.3 of pierced
web — and the bridge cannot add thread. **Open item:** a click
revision with pegs clear of the pilot would close the web around the
screw (+0.7) and is the way to buy margin if this joint ever strips.

## Cost recorded honestly

Reprint: **escape_wheel** ×3 (mirrored tooth, flat tip) and
**pallet_fork** ×3 (envelope-built stones, third print — coda 2's
reasons plus coda 3's), **bay_strap** (feet moved, bosses),
**mainplate** (strap + platform pilots), **bridge_wave** (click boss).
The plate and bridge were already queued for the 0.11-fit wave, so
this rides along. Wheel and train untouched. Open items for the
balance-driven bench: catch retrograde, ~52 deg draw on the tucked
nose face.
