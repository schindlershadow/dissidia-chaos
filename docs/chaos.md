# Playable Chaos (normal Chaos, the final boss)

Normal Chaos (`org200`) is a boss in retail: three objects (`P_ORG200_NORMAL` / `_HARD` / `_S_HARD`, object type 6) that are only
ever opponents. This documents how he is made playable as an extra roster character (slot 35, code `chs100`, scaffolded with
`new_character.py --like org210`, so the roster / ability / menu plumbing is Feral Chaos's).

## What the retail files give

| Boss form | Move set (objx) | Model | Costume file (`.cosx`) | Voice bank |
|---|---|---|---|---|
| 1 | `obj/p_org200_00.objx` | `p_org200_normal.gmo` | `_normal` | `voice/en/battle/voice_p_org200_normal.scd` |
| 2 | `obj/p_org200_01.objx` | `p_org200_hard.gmo` | `_hard` | `..._hard.scd` |
| 3 | `obj/p_org200_02.objx` | `p_org200_s_hard.gmo` | `_s_hard` | `..._s_hard.scd` |

- The objx of all three have the same `comb` (17 commands, ids `0x218`-`0x228`) and the same `plya` actions. Only the **script -> motion
  table** (`p_se` type 7) differs: each form's model only holds the animations of that boss phase, and the table has rows only for those.
  An action whose script has no row does nothing (`[TEST] ... NOT started`). Form 3 (`s_hard`) is the most complete.
- The costume file carries the voice-bank suffix (`_s_hard`), so the bank is `voice_p_<code>_s_hard.scd` (not `_00`).
- The boss objx has no player-only sections: the move-detail caption image (`spec` type 3), the EX Burst sequence (`spec` type 17) and
  the script rows `1200` / `1210` (EX Burst) are missing. See "Known gaps".

## The kit

`extra_abilities.json` (`<mods>/`, key `chs100`) points the cloned Feral Chaos ability records at Chaos's commands
(`set_cmd`, added to `roster_mainbin.py`) and adds one with `copy`.

| Ability | Command | Notes |
|---|---|---|
| Darkflame Talon (ground brave) | `0x218` | claw combo |
| Earthwalker / Earthcrusher (ground) | `0x219` / `0x21A` | fire wave; Earthcrusher chains it three times (button chain not verified) |
| Onslaught (ground) | `0x21F` | teleport + uppercut x3 (shared scripts 36 / 38 resolve to rows `10021`-`10023` of this form) |
| Darkflame Fang / Blast, The Fall, Negashock (midair) | `0x21B` / `0x21C` / `0x21D` / `0x21E` | |
| Condemn (ground HP) | `0x220` | |
| Scarlet Rain (ground HP) | `0x225` | script `10085` (phase 3 only on the boss) |
| Divine Punishment (midair HP) | `0x221` | |
| Soul of Oblivion (midair / ground HP) | `0x222` / `0x223` | scripts `10082` -> `10083` |

Left out: Demonsdance (`0x224`, script `10084`, only form 2 has an animation), `0x226` (ends at once), `0x227` / `0x228` (the start of
Utter Chaos, teleports the fighter 30-90 m). Hits: `KICK_2` 30 -> 16 (everything else is inside the retail ranges).
The move names are from the Final Fantasy Wiki move list matched against the animation data (hit names `CLAW`, `FANG`, `KICK`, projectile
counts); Divine Punishment / Soul of Oblivion are the least certain.

## How the installer works (`install_chaos.py`)

It reads the boss' model / costume file / voice bank / move file / portrait from `<game>/disc0`, patches the move file and portrait
(`tools/make_objx.py`, `tools/make_hud.py`), runs the game's own `tools/new_character.py` into `<game>/mods` (slot 35, `chs100`, like
Feral Chaos for the menu plumbing), then swaps in the boss' costume data, voice bank (`voice_p_chs100_s_hard.scd`), face strip, banner and
talk portraits. `extra_abilities.json` (the kit) is merged into the mods folder's own file. Nothing from the game is stored in the package.

**Memory budget.** An extra character makes the menu pack and `main.bin` bigger than retail, and the battle then fails to load in the
game's main heap (`[MODELS] heap ... alloc(...) FAILED`, "Now Loading" for good) unless the model budget is raised. The runtime raises it
only when a file in `mods/obj/` is bigger than a retail model (2,506,752 B), or with `PSPRECOMP_MODEL_BUDGET`. The installer therefore
pads the manikin body `p_chs100_zako.gmo`, which no player ever uses, with zeros to 2,600,000 B, which has the same effect as
`PSPRECOMP_MODEL_BUDGET=2600000` and needs no launch setting.

## Known gaps

- **EX Burst**: Chaos has no EX Burst assets (caption, sequence, rows `1200` / `1210`). Entering EX Mode works; the burst itself is untested.
- Victory pose and camera: untested. Boss-sized model: camera distance / lock-on untested.
- Alternate costumes are the same body (the three boss models have different animation lists, so they cannot share one objx).
- Grid tile, slide-in, VS face and logo plate are generated from pictures by `new_character.py`; the in-battle portrait is the boss's own
  picture framed with `gim_encode.frame_hud`.

## Multiplayer

Nothing in the runtime checks that both players have the same mods or roster (`docs/multiplayer.md`: "do not mix a modded roster with an
unmodded one"). A player without the mod has no charId 35 in `chrp` / `objentry` / `ablt` and no `chs100` files. Expect a desync or a
failed battle load for that player if the other one picks Chaos; both must run the same mod folder.

## Automated tests

`tools/battle_test.py actions --char chaos ...` starts every action directly and reports which scripts play (`docs/testing.md`). The
harness knows the Chaos grid cell (row 3, column 3) and charId; run with `PSPRECOMP_MODS`, `PSPRECOMP_ROSTER_EXPERIMENTAL=1` and
`PSPRECOMP_MODEL_BUDGET=2600000` (the bigger menu pack overflows the main heap otherwise). On a shared machine set `PSPRECOMP_BIN` /
`PSPRECOMP_TEST_XVFB` to renamed copies so another session's `pkill` cannot reach them.
