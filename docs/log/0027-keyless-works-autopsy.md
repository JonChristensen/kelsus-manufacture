# 0027 — The keyless works: an autopsy

Oct 1, 2026. The train finally spins on a touch of the drum — the
endshake and tooth-form work of log 0026 landed. Jon moved on to
winding and reported that the crown and stem do nothing at all: the
crown wheel sits loose on its stud and drifts out of the ratchet, and
even held down by hand the stem's pinion "just slides underneath it".
His question was whether this form of winding can work on a printed
movement or whether we bail.

This entry is the measurement, not the fix. Nothing in the winding
train was changed; one bench tool was added.

## What was measured

Three faults, each independent, each enough on its own.

**1. The ratchet and crown wheel cannot mesh over the crown wheel's
full height.** Both are 24-tooth saw wheels, r13 tips, at centre
distance 24. Sectioned in plan and tried at every phase:

| height | result |
|---|---|
| z16.05–17.15 (through the underside slots) | nests — 28 of 30 ratchet phases have a free crown phase |
| z17.15–17.65 (above the slot roof) | never nests; least overlap 0.35 mm² at the best phase |

The pair only interleaves where the pinion slots happen to carve
clearance out of the crown wheel's teeth. The top 0.5 mm is the full
saw profile, and that needs the wheels more than 0.5 mm further apart
(overlap is still 0.05 mm² at 24.5, zero by 25.0). On the bench the
crown wheel gets shoved outward by that slab — which is exactly "loses
engagement with the ratchet". The gate that should have caught it,
`_mesh_pair`, tolerates 0.5 mm³ of overlap at one pose; this collision
is 0.30 mm³ there and passed.

A second finding from the same trace: the crown wheel's cliffs face
counter-clockwise, and it winds by turning clockwise. So it pushes the
ratchet with the sloped backs of its teeth, not cliff-to-cliff as the
comments claim. The drive still transmits; it also pushes the wheels
apart harder than it should.

**2. The crown wheel's axle is barely attached.** The stud is a 0.03
radial press over 0.91 mm of full diameter (1.31 with the lead-in) in
a web 1.3 thick. It has to resist the ratchet mesh's side load 0.85
above the pocket floor and whatever lift the pinion produces. It
cannot; fault 1 supplies the side load.

**3. The stem pinion never properly enters the crown wheel.** Stem
axis z12.8, pinion tip radius 4.13 (pitch radius 3.5 plus a 0.63
semicircular nose), wheel underside z16.05:

| | reach into the wheel |
|---|---|
| leaf at top dead centre | 0.88 mm |
| half a pitch later, at hand-over | 0.47 mm for both leaves |

The pinion's pitch line sits 0.25 above the land bottoms, so all of
that engagement is rounded nose. Tips on a 4.13 circle are 3.71 apart;
the slots are 3.14 apart at r12. Drawn at hand-over, the two leaves
sit under the lands either side of a slot, not in one: the next leaf
arrives bearing upward on a land's underside. With fault 2, upward is
free. That is "slides underneath".

## The number nobody has

Sizing a replacement turned up something bigger than geometry. The
mainspring as drawn — PETG, 2.2 x 6.0 strip, 425 long — works out to
about 160 N.mm per turn of wind (E taken as 2.0 GPa). That is 13 N on
one ratchet tooth per turn, 26 N at two. A module-1 PLA tooth 1.6 wide
is near its limit around 20 N. So are the click's wedge, the arbor's
hollow square (0.7 wall around the key socket) and the stem's Ø3
D-tip. `SPRING_C` has carried "TORQUE FLAG: bench-validate" since the
port; it has never been validated because the movement has never been
wound.

A crown-and-stem train that fits the present bridge window and stem
height can be made to mesh correctly, but only with a face 1.2–2 mm
wide at module ~0.85. By the same tooth-stress estimate that is fine
at a fraction of a turn of this spring and marginal by one. Sized for
the spring as drawn it would want something like module 1.25 teeth, a
wider window in the web, and taller wheels standing proud of the
bridge — a bridge change, sketched but not yet simulated. Which of
those is right depends on how much torque the train actually needs,
and that is a bench number.

## What was built

`ratchet_knob_c` / `tools/export_bench_tools.py` →
`exports/k1/print/bench/winding_knob.stl`: the ratchet with a fluted
finger knob on top. Below z17.65 it is the ratchet, section for
section; above, it clears the click by 0.70, the crown wheel by 0.60
and the bridge by 1.66. It winds the barrel directly through the click
that is already there, and it is the instrument for the torque number.

Three tests now record the faults as strict expected failures
(`test_keyless_*`). The redesign is done when they pass.

## What was learned about the gates

- A volume tolerance on one pose is not a nesting check. Two toothed
  wheels need a free phase at every height, in section.
- "Overlaps when the wheel is turned half a slot" proved the pinion
  touches the wheel, not that it drives it. The hand-over depth is the
  number.
- None of the winding gates ever asked what force the teeth carry.

## Bench round 1 (Oct 2) — and what it changed

Jon printed the knob, held the escape wheel, and wound.

| what he saw | what the model says |
|---|---|
| "significant tension at about half a revolution" | ~79 N.mm, 6.6 N on one ratchet tooth |
| "not quite one full revolution before it gets very very tight" | 425 mm of 2.2 strip packs solid on the hub at 5.39 coils; it is printed at 4.25. **1.14 turns** and it is a solid puck. The "2.8 usable turns" in `SPRING_C` was never true |
| the arbor's square "slips out of" the ratchet, "even as I am pressing down quite firmly" | the square was 1.6 tall, hollowed by a 2.6 key socket to a 0.7 wall, in a bore with 0.15 a side of play |
| "the click does not hold at all" | two faults. In its pocket the click could lift 0.64 before the arm met the wall; a tooth needs 1.70. And the ratchet pushed the arm INTO its anchor (direction cosine +0.97): a 1.3-wide, 19-long kinked PETG strut in compression |
| released at half a turn, "the whole gear train moves, and the escape wheel turns very rapidly for about 15 seconds" | the first time this movement has run on its own spring |
| winds counter-clockwise | as derived |

Three parts changed. The bridge did not.

**Barrel arbor.** Solid 4.0 square, 3.4 tall (z16.0–19.4). 4.0 is the
largest square whose diagonal passes the bridge's web bearing.

**Ratchet.** 3.45 thick: the lower 1.6 in the pocket as before, 1.8
proud of the bridge. Bore 4.15 with a chamfered mouth (it prints on
the bed; an elephant-footed mouth is a taper that helps the square
climb). The knob grows from the new top.

**Click.** A pull-pawl, working in the open air above the bridge top.
The mounting is untouched — same block pocket, same two pegs, same
screw into the cone boss — but the block now carries a plate that
seats on the bridge's top surface, and from the plate a 0.8 x 3.0
flexure neck leads to a curved pawl that wraps a sixth of the way
round the ratchet to a hook. The pivot is on the far side of the
contact and 18 deg inside the tangent there, so the tooth PULLS the
pawl (tension cosine 0.98) and the pull has a 2.5 mm lever swinging
the hook into the tooth with no help from friction. The hook's lock
face leans 8.3 deg like the ratchet's cliff, so they meet flat. Lift
to pass a tooth: 7.2 deg, 1.76 mm, 1.7% strain in the neck; nothing
above the bridge is in its way. Printed 0.08 fat on both parts the
hook seats 0.9 deg proud and everything else holds. `tools/probe_click`
runs this on the built solids and `test_revc_winding_is_one_way` is
now that contract.

Not changed, and why: the mainspring. It is far stiffer than the bare
train needs and it has one turn in it, not three — but what the
escapement needs is the number that sizes it, and the balance is not
in yet. Until it is: wind 18 teeth at most.

The crown-and-stem redesign waits on the same number.

## Bench round 2 (Oct 2) — the balance goes in, almost

With the new arbor, knob and click: the click holds. Jon went to
install the balance and found three more things.

**The timing screws never fitted.** Six M3x8 steel screws through the
rim at r23 were the rate weights. A socket-head M3x8 stands 3.0 proud
of one face of a 3.4 rim and 4.6 of the other. Swept round the balance
axis, that radius has the hairspring's outer coil 0.7 above the rim
and the pallet strap 0.5 below. The screws were hardware in a
docstring; they were never posed in the assembly, so no gate ever met
them. The weights are now 16 M3 nuts pressed flush into hex pockets at
r22.5 — measured from the solids, that lands the balance at about 5500
g.mm^2, the inertia the six screws were meant to give (the bare wheel
is 2200). They are posed parts now, with a gate on their path. Trim is
by count, in opposite pairs.

**The staff would not enter the wheel.** Jon's rod is brass, O2.96.
The wheel's bore was O2.90 where the roller and collet use O2.94; it
now uses the same press as they do.

**The cabochon would not stay in its pocket.** The garnet endstone
pressed into a O3.95 hole from above; on Jon's print it was loose. The
cock's blind cup now has a flat printed floor at z16.3 that does the
same job — the same 0.30 of endshake over a 13.8 staff — and, with the
cock printed arm-down, that floor is a clean top-of-layer surface. The
stone was a nice idea that depended on a press fit nobody had tested.

## Before printing the balance: the fork end (Oct 2)

Jon, looking at the roller and the fork's end before committing hours
of plastic: "I'm just not entirely certain that that little three
prong area under the fork is going to allow that thing to control it
well." He was right, and the existing gate could not have told him.

Run as a pass, from the solids (`tools/probe_fork`):

- **The pin could not get in.** The fork's end was two straight prongs
  reaching 0.7 past the pin's centre, the pin O2.5 on a 5.5 orbit, the
  fork swinging +-6.5 deg at 13.9 from its pivot — a sideways throw of
  1.57 for a pin of radius 1.25. With the fork parked at its banking
  the returning pin met the flat END of the near prong at 42.5 deg
  before centre. A push on that face turns the fork INTO its banking.
  Dead stop.
- **It could not get out either.** Released from centre, the pin met
  the same prong again 10 deg after it.
- **The guard finger guarded nothing.** It stopped 0.3 short of the
  safety roller measured AT CENTRE, so its tip never came within 0.3
  of the roller at any fork angle: a knock could carry the parked fork
  clean across at 115 of 145 balance phases.

The old test posed fork and roller in eleven static states. For the
phases near the pass it paired the fork with the banking AWAY from the
pin ("after exit, draw holds the away-side bank"). The fork follows
the pin; that pairing never occurs, and it is the only one that is
clear.

Flaring the horns alone does not fix it. With a O2.5 pin the approach
sweeps through x' 13.6 in the fork's frame — inside the place the
notch wall has to stand to hold the pin at centre (13.91). The pin is
too fat for the throw. So three changes, together:

| | was | now |
|---|---|---|
| impulse pin | O2.5 | O1.8 |
| notch | 3.1 wide, parallel walls to the prong ends | 2.2 wide; walls stop 0.36 short of the pin's centre-line position, then horns flare at 60 deg |
| guard | square finger, 3.5 from the balance axis | pointed dart, tip centre 3.16 from the axis, r0.3 |

As drawn the pin first moves the fork 12.5 deg before centre and the
fork is home on the far side 13 deg after: 25.5 deg of lift, and the
pin leaves clean. Printed 0.05 thin to 0.10 fat it still passes
(23.5 to 29.5 deg of lift). A knock moves the parked fork no further
than +3.7 deg (+2.8 thin) before the dart meets the safety roller or a
horn meets the pin. One honest limit: the escape wheel begins to
advance after about 1.25 deg of fork travel, so a hard knock can still
trip a tooth before the dart lands — the fork then leans on the roller
until the notch comes round. It cannot cross.

Reprint: pallet_fork, roller. `test_revc_roller_passes_through_the_fork`
is the contract now.

## Hairspring stiffness and the pivot-friction budget (Oct 2)

Jon, twisting the printed hairspring on the bench: "very very soft —
a 30-40 degree arc where even the friction of sitting on smooth
plastic stops it returning." From the drawing: 1307 mm of 0.45 x 1.75
PETG, k = 0.020 N.mm per radian (E taken as 2.0 GPa) — 0.012 N.mm at
35 deg, 0.064 at 180. The spring's own weight dragging on a table at
r16 is about 0.06 N.mm. So the observation is the design, not a
defect: a hairspring never has to beat table friction, only the
staff's ends.

Which is the real number to worry about. The balance is 13.9 g with
its sixteen nuts, on O3 ends:

| position | friction torque at the staff (mu 0.15-0.3) | compare: spring at 100 / 180 deg |
|---|---|---|
| lying flat, rounded tip, contact ~r0.3 | 0.006-0.012 | 0.036 / 0.064 |
| lying flat, flat-cut tip | 0.02-0.04 | |
| standing on the desk stand (journal on O3) | 0.03-0.06 | |

Impulse from the train at 12 teeth of wind is ~0.011 mJ per beat; the
energy stored at 180 deg is 0.10 mJ. Lying flat with a rounded tip the
loss per half-swing is ~0.025 mJ at 180 — the balance should run at
100-200 deg. Standing up the journal loss is 0.13-0.25 mJ per
half-swing: more than the balance holds. It will not sustain.

First tick is therefore a lying-flat test. Standing up needs a lighter
balance, a stiffer spring with less inertia, or pivots far smaller
than O3 — the rev D conversation. Expected beat with all sixteen nuts:
~0.31 Hz (3.3 s per full swing), not the 0.53 the docstrings carried;
the balance alone, no nuts, would be ~0.48. The nuts are the trim.

## The escapement had no lock (Oct 2–3)

Jon, with a little wind on the barrel and the balance out: "the pallet
fork is too loose. It freely flops back and forth, letting the energy
out of the system." Right diagnosis, wrong suspect. A fork that flops
under wind has nothing holding it: the escapement has no lock and no
draw.

**Measured.** With the fork parked at its banking the solver had
shrunk the stone's locking face to **0.04 mm** — silently: the
coda-3 lock gate checked the contact's azimuth and a "draw torque"
whose sign rule was wrong, and never the lock depth or what happens
when the fork moves. Run as kinematics, moving the fork off its
banking moved the wheel FORWARD from the first tenth of a degree. The
tooth rested on a ramp, so the wheel pushed the fork off its pin, the
fork crossed, the next tooth did the same from the other side. That
is the flop.

**Why the solver gave up the lock.** A locking face with draw leans
UPSTREAM from the tooth's rest point: lifting the stone then makes the
tooth back up along the face, so the wheel recoils and its torque
holds the fork on the pin. Such a face can only exist in the space
behind the tooth's tip — and the coda-3 tooth leaned FORWARD, its body
ahead of the tip, with a stone face behind the tip running straight
into the body of the next approaching tooth. (The first two hours of
this fix went the other way, with the tooth leaning back but the face
chosen downstream; that gave a face but no recoil. The kinematics are
in `lever_layout_c`'s draw comment now, derived rather than guessed.)

**Changed, together:**

| | was | now |
|---|---|---|
| escape tooth | leaning forward, face falling ahead of the tip | leaning BACK: tip foremost, leading face receding 28 deg behind it, back at 42 deg; `tooth_profile_pts` is the one source for the wheel and the solver |
| stone locking face | through the tip's centre, 0.45 reserve (solved to 0.04) | through the tip flat's downstream corner, 0.60 reserve, 15 deg of draw with the inner end upstream |
| clearance rule | an analytic "hook-back" envelope that assumed the old tooth | a point-in-tooth test on the real profile, 0.10 margin |
| impulse ramp | ride 12 deg | ride 10 (at 10.5+ the other stone's lifted ramp tail reached the tip circle and the wheel rested on it) |
| the gate | contact azimuth + a torque heuristic | `probe_escapement.report`: rest on the right stone, recoil, unlock angle, half-pitch advance, drop, gate, windows — sharp AND r0.1-rounded tips |

As drawn: the wheel rests tip-on-face on both stones; moving the fork
1 deg off its banking backs the wheel up 0.22 deg; the tip stays on
the face for 3.3 deg of fork travel, then the ramp takes it and a
half-swing advances exactly half a pitch with 4.6 / 3.4 deg of free
drop. With the tooth corners rounded r0.1: unlock after 1.9 deg, recoil
0.20, drop 5.8 / 2.6. The old "step in a rapid buzz without a balance"
in the assembly guide was the fault described as a feature; the gate
now says the wheel must lock and stay.

Reprint: escape_wheel and pallet_fork — the same pair as this
morning's horn fix, so nothing extra if those are not printed yet.
