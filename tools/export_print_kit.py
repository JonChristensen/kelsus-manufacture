"""The FDM print kit: every part as its own STL + a manifest with
print profiles, orientation and support maps. Jon prints from exports/k1/print/.

The MANIFEST is GENERATED here — edit THIS file, never the .md by hand.
`python tools/export_print_kit.py --manifest-only` rewrites just the
manifest (fast check that the .md in git matches this source).

Orientation + support notes are bench-proven (July 2026 first build):
see docs/k1/printing-guide.md for the reasoning behind each rule.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEADER = """\
# Caliber K1 rev C — print kit (movement r6)

Assembly, stage by stage with inspection gates:
[docs/k1/assembly-guide.md](../../docs/k1/assembly-guide.md)

## Hardware (not printed)

- **M3 + nuts** (hex nuts drop into dial-side pockets, 2.4 deep): **M3×18 ×6**
  (bridge pillars ×4, cock feet ×2 — stack is 17.7 minus the pocket) and
  **M3×20 ×3** (stand feet — plate 6.5 + foot 14). *An earlier note said
  M3×8 ×7 — that was wrong; ×8 doesn't reach any nut in this stack.*
- **M2×6 thread-forming ×6** — ONE screw for every M2 hole (bay strap ×2,
  click ×1, dial platform ×3): **McMaster-Carr 94209A343** (steel Phillips
  pan-head Taptite®, tri-lobular thread-former, pkg 100). Every M2 pilot is
  sized to it (log 0026). Not sheet-metal self-tappers, not machine screws.
- **M3 hex nuts ×16** — balance timing weights, pressed flush into the
  pockets in the balance wheel's rim (on top of the 9 nuts the M3 screws
  use). They set the 0.53 Hz rate and are the bench rate-trim: take them
  out in opposite pairs to speed the beat. *(Six M3×8 screws were
  specified here until log 0027 — they cannot fit: the rim has 0.7 mm
  of air above it and 0.5 below.)*
- Super Lube (PTFE grease) on every pivot at assembly.

## Print profiles (Bambu Studio; 0.4 nozzle, textured PEI)

| class | parts | settings |
|---|---|---|
| **A** — big flats | mainplate, bridge_wave, dial_platform, dial_sheet | 0.20 layers, 20% gyroid (bridge_wave **40% gyroid, 5 top/bottom layers** — was 100%: skins + 4 walls do the work on a 3mm plate; washer under any M3 head that dimples its boss), walls 4/4/4, brim 5 |
| **B** — gears, arbors, small | everything not listed elsewhere | 0.12 layers, 4 walls, **100% infill**, outer wall 50 mm/s, first layer 220°/rest 215°, bed 55°. *Exception: the four TRAIN ARBORS may run **40% gyroid** (+0.16 layers if speed matters) — at 4 walls everything Ø≤3.4 is solid wall anyway; only the wheel webs change. balance_wheel stays 100% (its infill is timing mass) and escape_wheel stays 100% (all walls regardless)* |
| **C** — flexures | mainspring, hairspring, click, transfer_pinion, stem_clip | **PETG** (Bambu PETG HF profile), 0.12 layers, 4 walls |
| **D** — register pins | center_post, arbor_post_*, balance_staff | PLA vertical, or swap for Ø3/Ø2 steel rod (press-fit either way) |

**Supports — the anti-scar recipe (learned the hard way on the first arbor batch):**
Tree (**manual**), painted ONLY where a row below says so. Top Z distance **0.2**,
top interface layers **2**, top interface **spacing 0.4–0.5** (a dense 0.2 interface
WELDS to the part), support/object XY distance **0.4**, on build plate only.
Never support a ring hovering ≤1 mm above the disc below it — no room to remove;
the sag self-heals. Cup-shaped parts print closed-face DOWN so the interior
needs no support at all.

**THE ARBOR ORIENTATION RULE (in plain sight, after three bench rounds
of breakage): big wheel HIGH, longest skinny feature at the plate,
small pivot tips UP.** Every arbor break so far was a small feature
printed at the BOTTOM underneath a big disc. Self-check on the print:
support scarring belongs only on disc UNDERSIDES, in rings; a fully
scarred wheel face with a mangled tip at its center = the part printed
upside-down. NOTE: "pinion up" is NOT the rule — it happens to be
right for third(inverted) and escape, and WRONG for minute and fourth.

**The sunk-arbor trap (cost two third-arbor prints):** an arbor must
stand on the tiny O2.5 end of its shaft with EVERY gear disc floating
mid-air on its painted trees. "Lay on face" / auto-orient picks the big
wheel face, which rests the wheel on the bed and sinks the shaft BELOW
the plate — the slicer silently discards everything underground and
prints a bare gear. The subtler form (caught by Jon's side-view
screenshot): ROTATING a part in Bambu pivots it about its center and
leaves it partially sunk — always click "Place on plate" after any
rotation. The check is a number, not a vibe: the third arbor's wheel
underside hovers exactly 3.65 above the plate (collar 0.35 + pivot
3.3); a shaft visibly crossing the plate surface is being amputated.

**Brim:** type *Outer brim only*, width 5, gap 0.1 — on every vertical part and
the Class A flats. **Elephant-foot compensation ≥0.15** on; deburr and dry-fit
every plate-end pivot in its bushing before assembly (0.11 mm running clearance
— ladder-measured, log 0025 — is the whole budget, and printed pivots vary
~±0.03 r part-to-part: spin-test each arbor, spares absorb the outliers).

## Parts

| part | qty | cls | orientation / supports |
|---|---|---|---|
"""

# (file, builder, qty, class, orientation + support notes)
KIT = [
    ("mainplate", "mainplate_c", 1, "A",
     "dial face DOWN; tree supports in the dial pockets only. **Measure it "
     "before printing mates:** bushing Ø2.82, center bore Ø3.02, barrel recess "
     "Ø58.0, thickness 6.5 → set X-Y hole comp to the shortfall"),

    ("drum", "drum_c", 1, "B",
     "**floor DOWN, cup mouth UP** — the interior (where the spring rides) "
     "prints clean with zero support; auto-tree ≥50° catches the outside "
     "gear-band ledge + 3 cover lugs. *(Band-down buries the interior in "
     "support — don't.)*"),
    ("drum_cover", "drum_cover_c", 1, "B",
     "flat, PIN UP (flat face on the plate), no supports. **Re-cut in log "
     "0028: a O2.5 pin on the underside drops into the mainspring tab's "
     "hole — it is what keeps the spring's outer end on the rib.** An old "
     "flat cover lets the spring slide off the rib at the first turn"),
    ("barrel_arbor", "barrel_arbor_c", 1, "B",
     "vertical, square end UP; brim. The square is SOLID and 3.4 tall "
     "since log 0027 (the hollow 1.6 one let the ratchet climb off under "
     "half a turn of spring) — it stands 1.7 above the bridge, inside "
     "the ratchet"),
    ("mainspring", "mainspring_c", 1, "C",
     "**PETG ONLY**, flat, HOLE SIDE UP on the bed, 100% infill, walls "
     "only (the 1.7 strip is 4 walls; let any remainder be gap fill). "
     "**Re-cut in log 0028 — discard the 2.2 strip with the inner C-loop: "
     "it was the other hand and it broke.** This one is a solid inner "
     "ring keyed to the arbor rib, a tapered root, and a tab that sits "
     "against the drum rib under the cover's pin (reprint the cover); it "
     "packs solid at 1.14 turns and cannot be overwound. "
     "Two more strip thicknesses (1.4, 2.0) are in bench/ — print all "
     "three, the bench picks; picture docs/k1/img/mainspring-in-drum.png"),
    ("ratchet", "ratchet_c", 1, "B",
     "flat, the face with the CHAMFERED bore mouth on the plate. 3.45 "
     "thick since log 0027: the top 1.8 stands proud of the bridge, "
     "where the click now works. Bore is a snug 4.15 on the 4.0 square "
     "— if it will not start, ease the mouth with a knife; do not open "
     "the whole bore"),
    ("click", "click_c", 1, "C",
     "**PETG ONLY** — it is a pull-pawl with a 0.8 flexure neck (log "
     "0027). Print FLAT SIDE DOWN, pegs UP: the plate and the curved "
     "pawl both lie on the bed, no supports. Afterwards the pawl must "
     "swing freely on its neck — cut any strings in the 0.8 gap "
     "between pawl and plate. Print 2"),
    ("crown_wheel", "crown_wheel_c", 1, "B", "slots UP (top face down)"),
    ("crown_stud", "crown_stud_c", 1, "B", "head DOWN"),
    ("stem_and_crown", "stem_c", 1, "B",
     "crown face DOWN, axis vertical (no pinion on it since coda 5 "
     "rev 4 — no supports needed beyond the brim)"),
    ("winding_pinion", "winding_pinion_c", 1, "B",
     "flat. **Assembly order matters:** stem in from OUTSIDE first, "
     "then this presses onto the D-tip from inside until it butts the "
     "tunnel face, then the C-clip"),
    ("stem_clip", "stem_clip_c", 1, "C", "PETG preferred; flat; print 3"),
    ("minute_arbor", "minute_arbor_c", 2, "B",
     "vertical, **long dial stub at the PLATE, 56t wheel HIGH, short "
     "top pivot UP** (Jon's bench, coda 5 rev 7: printed pinion-up = "
     "upside-down, the wheel face rode a full support bed and the top "
     "pivot — the bridge-shelf thrust tip — printed at the bottom and "
     "snapped). Brim. Paint under the 10-leaf pinion + under the 56t "
     "wheel *outside the pinion's footprint*; skip the ring directly "
     "over the pinion"),
    ("third_arbor", "third_arbor_c", 2, "B",
     "vertical, **INVERTED: top pivot DOWN** (7-leaf pinion low, 45t "
     "wheel high). Shaft-down, this is the ONLY arbor whose biggest "
     "disc (the O47 wheel) lands directly on the naked O2.5 bottom "
     "column — the nozzle wobbles the flagpole while sweeping the big "
     "disc and the junction bonds one layer deep (leaned 5 deg and "
     "snapped at a touch, Jon's bench; every other arbor stacks a "
     "small pinion on its column first, and all proved sturdy). "
     "Inverted = the fourth's topology: 2.0 column, widening neck, "
     "pinion on plate trees, wheel on a braced core. Brim. Paint under "
     "the pinion + under the wheel outside the pinion footprint. "
     "Deburr the plate-side pivot end face (the shelf thrust face)"),
    ("fourth_arbor", "fourth_arbor_c", 2, "B",
     "vertical, **long lower shaft at the PLATE, 36t wheel HIGH, short "
     "top pivot UP** (NOT pinion-up — that flips it); brim. Paint under "
     "the 6-leaf pinion + under the 36t wheel outside the pinion "
     "footprint"),
    ("escape_arbor", "escape_arbor_c", 2, "B",
     "vertical, bay pivot DOWN; brim. Paint under the 18t pinion — the trees "
     "double as bracing for the tall post"),
    ("escape_wheel", "club_escape_wheel_c", 3, "B",
     "flat. **Teeth re-cut in log 0027 — discard every earlier wheel.** "
     "It goes on ONE way up: looking down from the bridge side, the "
     "tooth TIPS POINT COUNTER-CLOCKWISE — the way the wheel turns, like "
     "a saw blade's teeth pointing into the cut; each tip overhangs its "
     "own root (picture: docs/k1/img/escape-wheel-direction.png). Printed "
     "as exported, that is bed face DOWN toward the plate. Earlier wheels "
     "have no overhang. Upside down, or an old wheel, has no lock and the "
     "fork flops"),
    ("pallet_fork", "swiss_lever_c", 3, "B",
     "**Fork re-cut twice in log 0027 — discard every earlier fork** "
     "(two straight prongs = the oldest; flared horns with a POINTED "
     "finger underneath = current; the stones changed with the escape "
     "wheel, so print the fork and the wheel together from the same "
     "export). The pointed guard finger under the horn end is thin: "
     "support it like the rest of the underside and peel gently. Body "
     "flat, **long (2.0) pivot DOWN** — the body hovers 2 mm on the "
     "pivot tip. Paint the ENTIRE body underside; never the pivot. Peel "
     "supports away from the pivot, holding the body. The stone fins "
     "are the working faces: no support contact, no cleanup sanding"),
    ("bay_strap", "bay_strap_c", 2, "B", "flat"),
    ("roller", "roller_c", 2, "B",
     "flat, crescent side down. The impulse pin is O1.8 since log 0027 "
     "(was O2.5) — it and the fork end were redesigned together; an old "
     "roller will not enter a new fork"),
    ("balance_staff", "balance_staff_c", 1, "D",
     "vertical; or cut 13.8 from Ø3 metal rod (13.6-14.0; never longer), "
     "both ends squared, deburred and slightly rounded"),
    ("balance_wheel", "balance_wheel_c", 1, "B",
     "flat, **hex pockets UP**, no supports; then press an M3 nut into "
     "each of the 16 pockets until it is below the rim's face — NOTHING "
     "may stand proud of either face (the hairspring passes 0.7 above, "
     "the pallet strap 0.5 below). A loose nut gets a drop of "
     "superglue; the small hole under each is for pushing it back out"),
    ("hairspring", "hairspring_c", 1, "C",
     "**PETG ONLY** — flat; 0.45 walls = single-line: tune flow first; "
     "print 3 spares"),
    ("balance_cock", "balance_cock_c", 1, "B",
     "arm flat, columns UP; paint supports under the stud post. The "
     "blind cup in the arm is the staff's upper bearing AND its "
     "endstone (printed since log 0027 — no cabochon): keep supports "
     "out of it and check its floor is clean"),
    ("stand_foot", "stand_foot_c", 3, "B", "vertical"),
]

# dial-side parts build from revc_dial_parts
KIT_DIAL = [
    ("center_post", "center_post_d", 1, "D", "vertical; or Ø3 steel rod"),
    ("cannon", "cannon_d", 1, "B", "pipe vertical, hand-seat UP"),
    ("hour_wheel", "hour_wheel_d", 1, "B", "pipe vertical"),
    ("motion_arbor", "motion_arbor_d", 1, "B", "vertical"),
    ("moon_w1", "w1_d", 1, "B", "flat"),
    ("moon_w2", "w2_d", 1, "B", "vertical shaft"),
    ("moon_disc", "moon_disc_d", 1, "B",
     "moons DOWN (two-color swap at 0.3 if using AMS)"),
    ("transfer_pinion", "xfer_pinion_d", 1, "C",
     "PETG preferred; flat; slit collet is the hand-setting slip; print 2"),
    ("transfer_idler", "idler_d", 2, "B", "flat"),
    ("dial_platform", "dial_platform_d", 1, "A", "flat, proud face down"),
    ("dial_sheet", "dial_sheet_d", 1, "A",
     "face color! face DOWN; engraved markers paint-fill at the bench"),
    ("minute_hand", "minute_hand_d", 2, "B", "hand color; flat"),
    ("hour_hand", "hour_hand_d", 2, "B", "hand color; flat"),
]

BRIDGE_ROW = ("bridge_wave", "bridge_c", 1, "A",
              "show face — pick a color! SHOW FACE DOWN (pillars up); 40% "
              "gyroid, 5 top/bottom (profile A); supports only in the "
              "ratchet pocket + stem tunnel; brim. The click screw's "
              "under-web boss is a CONE (root O11 on the web, O6 tip — "
              "coda 5 rev 8): it points up in this orientation and needs "
              "no support")

POST_NOTE = "vertical; or Ø2 steel pin"


def manifest_rows():
    from calibers.k1.revc_dial import post_specs
    rows = [(n, q, c, note) for n, _, q, c, note in KIT + KIT_DIAL]
    rows.append((BRIDGE_ROW[0], BRIDGE_ROW[2], BRIDGE_ROW[3], BRIDGE_ROW[4]))
    rows += [(f"arbor_post_{n}", 1, "D", POST_NOTE)
             for (n, x, y, tip, top) in post_specs()]
    return rows


def write_manifest():
    with open("exports/k1/print/MANIFEST.md", "w") as f:
        f.write(HEADER)
        for name, qty, cls, note in manifest_rows():
            f.write(f"| {name} | {qty} | {cls} | {note} |\n")


def export_stls():
    from build123d import export_stl
    from calibers.k1 import revc_parts as rp
    from calibers.k1 import revc_dial_parts as dp
    from calibers.k1.revc_dial import post_specs

    builders = [(n, getattr(rp, fn)) for n, fn, *_ in KIT]
    builders += [(n, getattr(dp, fn)) for n, fn, *_ in KIT_DIAL]
    builders.append((BRIDGE_ROW[0], getattr(rp, BRIDGE_ROW[1])))
    builders += [(f"arbor_post_{n}", (lambda L=(top - 0.1 - tip): dp.arbor_post_d(L)))
                 for (n, x, y, tip, top) in post_specs()]
    for name, fn in builders:
        export_stl(fn(), f"exports/k1/print/{name}.stl", tolerance=0.02)
    return len(builders)


if __name__ == "__main__":
    os.makedirs("exports/k1/print", exist_ok=True)
    if "--manifest-only" in sys.argv:
        write_manifest()
        print(f"MANIFEST.md rewritten ({len(manifest_rows())} rows)")
    else:
        n = export_stls()
        write_manifest()
        print(f"print kit: {n} part files + MANIFEST.md")
