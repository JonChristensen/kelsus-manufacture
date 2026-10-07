# Handoff prompt — design the 36 mm metal base caliber

*Paste everything below the line into a new conversation that has this repo open. It was written on Oct 7 2026 at the end of a long session on the plastic K1; the plastic work continues in a separate conversation. Keep both from editing the same files — see "Working arrangement".*

---

You are taking over the design of an **open-source mechanical wristwatch caliber in metal** from a conversation that spent four months building its 5×-scale plastic prototype. This document is the whole context you have: the goal, what exists, what was learned, what was decided, what is still open, and the plan. Read it fully, then read the repo files it points to, before proposing anything.

## 1. Who you are working with

Jon (jon@kelsus.com) is a self-described CAD novice who directs, prints and tests; you drive the CAD. He owns a Bambu Lab H2C printer (350 × 320 mm bed) and builds in public (GitHub, website, TikTok). His construction instincts about real watches — from studying the NH35, ETA 2824 and 6497 — have repeatedly out-corrected the model's; when he says a real movement does it another way, verify yours against the real caliber before defending it. His eyes are a required gate: every design step ends with an "inspect this" checklist and a rendered picture he can judge.

The memory directory for this project (loaded automatically as `MEMORY.md`) holds the standing lessons. Read it; the entries `feedback-target-is-watch-scale`, `k1-rev-b-flatten`, `inspection-gates`, `cad-workflow-choice` and `k1-revc-status` matter most here.

## 2. The goal, stated plainly

A **truly open, free-for-anyone wristwatch base caliber** — Jon's own design including the base, with no license strings, no branding requirement, no membership gate (OpenMovement's OM10 was considered and rejected on exactly those grounds). On that base, later, complications that do not exist in horology: a **haptic metronome** (Caliber K2's job; the metronome keeps its own barrel) and a **world-class tide indication**. The complications are years away and are not your job now. The base is.

"Open" for hardware means: every drawing free; every part either makeable from the drawings or a commodity anyone can buy from more than one source. Nobody — not independents, not most Swiss brands — makes hairsprings, jewels or mainsprings. So:

- **v1:** everything is Jon's except the regulating consumables, which are bought as a multi-source assortment.
- **v2:** Jon's own escapement and balance, once v1 keeps time.

## 3. Decisions already made (Oct 7 2026) — do not reopen without new evidence

| Decision | Value | Why |
|---|---|---|
| Size class | **36 mm** (6497-class), fits a 42 mm case at the floor, 43–44 comfortable | Complications need plate; main train stays near module 0.2; plastic model at a clean 5×; hand-fitting margin for a first-time maker |
| Beat | **4 Hz, 28,800 bph** | Industry sweet spot; the most open frequency on earth. 5 Hz was wanted and declined: f³ power cost, lubrication demands, and no multi-source 5 Hz assortment exists |
| Regulating organ, v1 | **ETA 2824-class assortment**: balance complete + hairspring, pallet fork, escape wheel, shock protection, jewels — made by ETA, cloned by Sellita (SW200) and Seagull (ST2130), stocked aftermarket | Design the balance cock, escapement positions and jewel seats so these parts drop in. A big plate with a small fast balance is normal manufacture practice |
| Power reserve | ≥ 40 h from a Ø16-class barrel; the metronome gets its own barrel later | 4 Hz with a big barrel lands 40–50 h |
| Thickness | base 5–6 mm; expect 13–15 mm cases once modules stack | Tell Jon before anything grows it |
| Plastic's role | a **5× kinematic model derived from the 1× design**, never the other way round | The old mistake was a print-first geometry with a "metal variant" that was the same Ø150 plate in brass — a clock nobody wanted |
| Source of truth | build123d code in git, parametric, with pytest gates and CI; export → render → look at the PNG before calling anything done | Memory: `cad-workflow-choice` |

## 4. What exists in the repo

Layout (`README.md` is current): `movement/` is the shared engine — `gears.py` (cycloidal wheel/pinion faces: `wheel_face`, `pinion_face`, hypocycloid gullets, BS978 addenda, backlash), `solver.py` (the station/sweep layout solver — read `docs/how-the-solver-works.md`), `springs.py`. `calibers/k1/` is the plastic K1 rev C (time + moon phase): `revc.py` (frozen layout, counts, `ESC_TUNE`, `TOOTH`, `WINDING`, the chirality chain), `revc_parts.py` (every part builder), `revc_dial.py`/`revc_dial_parts.py` (dial side: indirect minute via a 3-mesh transfer chain, motion works and a 59.0625-ratio moon train in dial-face recesses), `variants.py` (the print/metal dimension tables — see §6), `decor.py`, `wave_art.py`. `calibers/k2/` is the metronome caliber's brief and layout (Ø250 two-sided massing, winding link solved). `attic/` holds rev A/B. `tools/` holds the exporters (`export_print_kit.py` generates `exports/k1/print/MANIFEST.md` — never edit the .md), the STEP builder (`build_revc_movement.py`), and the **kinematic probes** that are the project's real instruments: `probe_escapement.py` (sections built solids to 2D with shapely and simulates the lock/unlock/tick with the wheel torque-butted), `probe_fork.py` (roller pin through the fork horns), `probe_click.py`, `probe_winding.py`. `tests/test_revc_parts.py` is ~100 gates run in CI (`.github/workflows/ci.yml`); as of Oct 7 the suite is 106 passed, 3 xfailed (the xfails record the broken keyless works).

Read, in this order: `README.md`, `docs/log/0016-rev-c-expert-brief.md` (how a brief is written and why top-down matters), `docs/log/0025`–`0028` (what the bench taught), `calibers/k1/revc.py`, `calibers/k1/variants.py`, `docs/how-the-solver-works.md`, `tests/test_revc_parts.py`.

## 5. The honest assessment of K1 as a watch caliber

**Architecture: right, keep it.** Two-plate construction; offset going barrel hanging from the plate with a bridge-web bearing; an interleaved two-plane train with a true 60 s fourth arbor; Swiss lever; keyless works with ratchet and crown wheel at the bridge plane; motion works and moon train in dial-side recesses with a retaining platform (only the hour wheel stands proud); a decorative bridge that is a real train bridge. Jon's corrections drove it there and it maps onto real construction.

**Proportions: plastic's, discard.** Every number was chosen to survive a 0.4 mm nozzle: module 1 teeth with 6- and 7-leaf pinions at the packing limit; a 16-tooth escape wheel at ~0.5 Hz on a 30 s/rev arbor; a 2:1 last stage; Ø2.5 pivots in printed cups and a shoulder-on-shelf endshake system with blind bridge bearings; a 14 g balance trimmed with M3 nuts; a fork with integral stones built to a print envelope; a PETG mainspring sized at PETG's strain limit; a pull-pawl click. None transfer.

**The gap: there is no 1× design yet.** `variants.py`'s "metal" entry is the Ø150 geometry with metal clearances and a 30-tooth escape wheel giving 1 Hz. A 1 Hz wristwatch is shock-sensitive and positionally unstable. The variant switch was meant to stop the project "getting married to the printable version and flying blind at the CNC handoff"; it never got a scale, so it guarded nothing. **Your first structural job is to make 1× the source of truth and derive the print model from it.**

**Train arithmetic you will redo.** K1 counts are `(60, 10, 56, 7, 45, 6, 36, 18)` = barrel 60 → center pinion 10 (6:1, center at 1 h/rev) → center wheel 56 → third pinion 7 (8:1) → third wheel 45 → fourth pinion 6 (7.5:1, fourth at 60 s/rev) → fourth wheel 36 → escape pinion 18 (2:1). Barrel-to-escape is 720:1. At 4 Hz the escape wheel's revolution time is set by the assortment's tooth count (take it from the real part — measure a 2824/SW200 or use published service data; do not trust memory for the 2824's counts, lift angle or center distances), and the barrel-to-escape ratio becomes roughly 4,000–6,000:1. Keep center at 1 h and fourth at 60 s; most of the new ratio lands in the fourth-to-escape stage, which real calibers run at a finer module than the rest of the train. Set a pinion leaf floor of 8. The K1's packing-limit lesson (log 0025: Z3 ≤ Zm + p3 − pm − 6 at module 1) was a module-1 problem; re-derive at the new modules with the same solver and gates.

## 6. What transfers from the plastic work (keep) and what does not (drop)

**Keep — scale-free:** the architecture; the solver and its station sweeps; `movement/gears.py`; the kinematic-probe method (section the built solids, simulate, assert on the simulation — never on a static pose or a volume tolerance); the gate discipline (global swept-volume collision gates before any part modeling; assembly-path gates; "would this ship in metal?" review at every milestone); the chirality chain and winding-direction derivation in `revc.py`; the keyless-works and motion-works mechanisms; the moon train ratio.

**Kinematic lessons that transfer verbatim:**
- Lever escapement draw rule (log 0027): draw exists iff the stone's locking face has its inner end *upstream* of the contact, which requires a tooth whose body sits behind its tip with face rake greater than the draw angle; the face must pass through the tip-flat's downstream corner; test clearance with a real point-in-tooth test, not an envelope radius. An escapement with "lock reserve 0.04 mm" is an escapement with no lock. With a bought assortment you inherit a correct escapement, but the probe is how you verify your plate puts it at the right centers.
- A click must be a pull-pawl (pivot on the far side of the contact, inside the tangent) or it will not hold (log 0027).
- A relaxed-printed spiral mainspring is the wrong model of a steel one — but two things carry: the spring's hand must match the arbor's winding direction (a spiral tightens when its inner end turns *against* the direction its coils run outward), and the outer anchor must resist an **inward** pull unless the spring is reverse-curved like a real one (log 0028). A steel mainspring is reverse-curved; a plain hook works. Still: design the barrel hook, not just the barrel.
- Pivots: nothing under Ø2 in plastic survives Jon's hands; at 1× the analog is "every pivot, shoulder and stop is a standard watch feature with a standard tool to make and measure it."
- Endshake and depthing are *adjusted at assembly* in metal; design the adjusters (bushings/jewel settings that can be moved, eccentric banking, movable stud) rather than freezing everything in plate geometry as the plastic did.

**Drop — plastic-only:** every dimension in `revc_parts.py`; `ESC_TUNE`, `TOOTH`; the printed-jewel endshake system; the 16/30-tooth escape wheel; the PETG spring ladder and the cover-pin anchor; the pull-pawl click's geometry (keep its principle); the nut-weighted balance; the cabochon/printed endstone; the keyless works as drawn (three measured faults, tracked by the `test_keyless_*` xfails).

## 7. The process lessons (these cost months — honor them)

1. **Design top-down from hard targets.** Rev B was built by accretion under per-screenshot corrections — locally right patches, globally wrong architecture (log 0016). Write the brief first: size, height, beat, reserve, assortment, jewel count, screw and stem standards, DFM rules. Then layout. Then parts. Gate everything behind a global collision test from day one.
2. **Never let a test fixture become architecture.** The M1 test-stand spider became rev A's frame.
3. **Measure before redesigning.** Every bench round that went well started by measuring the fault (coupons, probes, photos of the break); every one that went badly started with a guess. Keep the probe-first habit.
4. **Gates that don't simulate lie.** Static-pose gates, volume tolerances and sign-only heuristics each green-lit a real defect. A gate should run the mechanism.
5. **"One fused solid" is not "printable/machinable."** Point-contact welds and 0.6 mm isthmuses passed the solids==1 check. Add erosion/wall-thickness probes and, for metal, DFM gates (minimum wall, EDM inside radii, reamable holes, standard threads).
6. **Verify the edit landed.** Heredoc edits silently no-op'd more than once and the suite green-lit old geometry. After any geometry change, measure the built solid.
7. **Jon prints from saved slicer projects that embed old meshes** — the metal analog is vendor files: every quote package must be generated from the tagged code, never hand-edited.

## 8. The plan

**Phase 0 — the brief** (first deliverable, `docs/<caliber>/brief.md`, written like log 0016): 36 mm, ≤ 5.5 mm base height target, 4 Hz, 2824-class assortment with its real measured parameters, ≥ 40 h, barrel diameter, jewel count and sizes (standard jewel ranges — verify the standard, don't assume), shock protection unit, stem/crown thread standard, screw thread standard, plate and bridge materials (brass or nickel silver), DFM rules (minimum wall ≈ 0.3 mm in brass; wire-EDM inside radius from a 0.1 mm wire; reamed pivot holes; no feature a job shop can't quote), and a reserved footprint for the metronome module and its barrel (K2's brief in `docs/log/0020` and `calibers/k2/brief.py` say what it needs). Jon gates the brief.

**Phase 1 — the variant system gets a scale.** Restructure so the 1× geometry is primary and the print variant is "1× scaled by 5 with print fits and a print-tuned escapement end." The plastic model can't run 4 Hz in PLA; it validates the barrel, train to the fourth wheel, keyless and motion works at 5×; the escapement end is validated at 1× in metal with bought parts. CI builds and tests both.

**Phase 2 — train and layout** with the solver: new count set, pinion floor 8, finer module at the escape end, barrel sized for reserve, assortment placed by its real center distances. Global swept-volume gates before any part.

**Phase 3 — parts** in dependency order (plate and bridges, barrel and arbor, train arbors and wheels, keyless works, motion works, balance cock around the assortment), each with assembly-path gates and DFM gates. A 5× print of each subsystem as its kinematic first article.

**Phase 4 — the vendor loop.** Rented precision, not a factory: quick-turn laser/waterjet or photochemical etching for flat parts (cams, levers, springs in 0.1–0.5 mm stock); wire-EDM job shops for steel parts; micro-machining shops (medical-device suppliers) for brass plates/bridges in 5–50 piece runs. First purchase is one plate, one wheel and one lever sent three ways to learn the vendors (~$300). A desktop mill only if that round shows a weekly bottleneck. Jon also needs an ST36/6497 and a watchmaker's bench kit to learn stripping and fitting — the human half of the loop. Research the vendors with current prices and lead times before recommending any; the previous conversation gave ballparks only.

**Phase 5 — fitting and timing.** Assemble, adjust endshake and depthing, time on a timegrapher (rate, beat error, amplitude in six positions). Target ±20 s/day for v1; COSC-grade is a v2 ambition that depends on the regulating organ, not the plates.

## 9. Open decisions to settle with Jon in the first exchange

- Caliber name and directory (suggestion: a new `calibers/<name>/` with its own `docs/<name>/`; K1 stays the plastic lineage).
- Base height target and whether center seconds or small seconds (K1 has a 60 s fourth arbor; small seconds is simplest).
- Hand-wound only for v1 (yes, unless he says otherwise).
- Which real 2824-class movement to buy and measure for the assortment's parameters.
- Whether the moon phase stays on the base or becomes a module.

## 10. Working arrangement

Jon is continuing the **plastic K1 rev C** in a separate conversation on `main` — that is its own feat and not yours. **Work in a git branch or worktree** (e.g. `metal-caliber`) and add new directories rather than editing `calibers/k1/`, `tools/` K1 exporters or `tests/test_revc_parts.py`. You may extend `movement/` if K1's tests still pass. Commit or push only when Jon asks. Nothing from the plastic session was committed as of this handoff; ask Jon to commit `main` before branching so the worktree carries the current state. Memory lives in the per-project memory directory and is shared between the two conversations; note anything durable there under a name that says which caliber it concerns.

## 11. Todos handed over from the plastic session (not blockers; do them early)

1. **Stop tracking the STEP in git.** The rebuilt `exports/k1/revc/movement_r11.step` is 122 MB — over GitHub's 100 MB file limit — so it was left uncommitted; the committed copy is the older 66-component one (52 MB). Even at 52 MB it is a bad git citizen (every rebuild adds a tens-of-MB blob to a public repo's history forever). Add `exports/**/*.step` to `.gitignore` (keep the small `massing_r6.step` if wanted), keep exporting locally, and publish the STEP as a GitHub release asset or CI artifact. Regenerate it any time with `PYTHONPATH=. python tools/build_revc_movement.py`.
2. **Build gear-tooth flanks as splines in `movement/gears.py`.** Measured Oct 7: every toothed wheel is 8–11 MB of STEP because the coda-4 tooth form (24-point flanks, hypocycloid gullets) is a polyline — one planar face per point. One B-spline face per flank shrinks the STEP roughly tenfold, leaves the STLs unchanged within tolerance, and gives the metal caliber the smooth curves CAM wants. Shared engine: run the full suite (`python -m pytest tests/ -q`, ~12 min) and K2's tests after; coordinate with the plastic conversation, which owns K1's exports.
3. `exports/k1/print/barrel+winding-group-k1.3mf` is a slicer scratch project tracked from before the ignore rule (only curated plates in `exports/k1/print/plates/` are meant to be tracked). It is modified and uncommitted; either `git rm --cached` it per the rule or Jon says to keep it.
