# Playable Chaos for Dissidia 012 (recomp)

Normal Chaos (the final boss) as a playable roster character for the [Dissidia 012 native build](https://github.com/schindlershadow/dissidia).
Roster slot 35, code `chs100`, built from **your own game data**: this repository holds no Square Enix files (no models, voice banks,
move files or pictures). `build.sh` reads them from your extracted disc and writes a mods folder.

## Use

```
DISSIDIA_REPO=~/code/dissidia/psprecomp/games/dissidia \
WORK=~/dissidia/work \          # work folder with disc0/ (setup_from_iso.py)
ART=./art \                     # optional: chaos_head.png, chaos_full.png, chaos_logo.png (menu pictures; without them Feral Chaos's are used)
./build.sh                      # -> ./mods
WORK=~/Games/Dissidia012 ./run.sh   # runs the game with PSPRECOMP_MODS=./mods, PSPRECOMP_ROSTER_EXPERIMENTAL=1, PSPRECOMP_MODEL_BUDGET=2600000
```

Chaos is the last tile of the third row of the Quick Battle grid. Both players of a multiplayer match need the same mod folder
(nothing checks it; a player without it has no character 35).

## What it is

- Body, costume data, voice and moves are the boss' third form (`obj/p_org200_s_hard.*`, `obj/p_org200_02.objx`): the most complete
  animation set of the three. `tools/make_objx.py` gives the one move without an animation (Demonsdance) a stand-in, clears the
  boss-phase tags on Earthcrusher's steps and lowers `KICK_2` from 30 to 16.
- `extra_abilities.json`: the kit, 8 brave (Darkflame Talon, Earthwalker, Earthcrusher, Onslaught; Darkflame Fang, Darkflame Blast,
  The Fall, Negashock) and 5 HP (Condemn, Scarlet Rain, Divine Punishment, Soul of Oblivion ground and midair) with names from the
  Final Fantasy Wiki's move list matched against the animation data. Demonsdance and the Utter Chaos pieces are left out.
- `tools/make_hud.py`: the boss' picture as a compact HUD cut-out that clears the HP bar and EX gauge.
- Details, measurements and known gaps (EX Burst, victory pose, camera): [docs/chaos.md](docs/chaos.md).

Needs the dissidia fork's `tools/` (`new_character.py`, `charmod_objx.py`, `gim_encode.py`, `package_extract.py`) with the `set_cmd`
ability option (`roster_mainbin.py`, on `main`), and Pillow / numpy (the fork's `pydeps` installs them).
