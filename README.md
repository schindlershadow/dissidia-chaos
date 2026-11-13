# Playable Chaos for Dissidia 012 (recomp)

Normal Chaos, the final boss, as a playable character in the [Dissidia 012 native build](https://github.com/schindlershadow/dissidia):
8 brave attacks and 5 HP attacks (Darkflame Talon, Earthwalker, Earthcrusher, Onslaught, Darkflame Fang, Darkflame Blast, The Fall,
Negashock; Condemn, Scarlet Rain, Divine Punishment, Soul of Oblivion), his own model, voice and portrait.

## Install

You need the game installed with the recomp's setup wizard (release **v0.1.8 or newer**) and Python **3.11 or newer**.

1. Download `DissidiaChaos-<version>.zip` from the [Releases](https://github.com/schindlershadow/dissidia-chaos/releases) page and unzip it.
2. Run `install.bat` (Windows) or `./install.sh` (Linux). It finds your game folder (`~/Games/Dissidia012` by default) or asks for it.
   The first run downloads about 60 MB of Python packages for the game's tools, and three menu pictures.
3. Start the game. Chaos is the last tile of the third row on the Quick Battle character select.

To remove him again: `install.bat --uninstall` / `./install.sh --uninstall`. Other mods in your game's `mods` folder are left alone, and
running the installer again just updates Chaos.

**Multiplayer:** both players need Chaos installed (nothing in the game checks that; a player without him has no character 35 and the
match will desync or fail to load). Everyone in the match must also have the same game version.

Options: `--game DIR` (the install folder, the one with `disc0/`), `--no-download` (skip the menu pictures; Feral Chaos's are used),
`--art DIR` (your own `chaos_head.png`, `chaos_full.png`, `chaos_logo.png`).

## What is in it, and what is not

This package holds **no Square Enix files**: no models, voices, move files or pictures. The installer reads the boss' model, costume data,
voice bank and move set from your own game (`disc0/`), changes what needs changing and writes the result into the game's `mods` folder.
The menu pictures (character select tile, slide-in, logo) are fan wiki artwork that is downloaded when you install.

- Body, voice and moves are the boss' third form, the most complete of the three. `tools/make_objx.py` gives Demonsdance's slot an
  animation, clears boss-phase tags on Earthcrusher's steps and lowers `KICK_2` (The Fall) from 30 to 16. Demonsdance and the Utter Chaos
  pieces are left out.
- `tools/make_hud.py` frames his portrait as a compact HUD cut-out that clears the HP bar and the EX gauge.
- Known gaps: **EX Burst** (the boss has none; untested), victory pose and camera, alternate costumes are the same body.
  Details and measurements: [docs/chaos.md](docs/chaos.md).

## For developers

`build.sh` builds the same thing from a source checkout of the recomp (`DISSIDIA_REPO`, `WORK`, `MODS`, `ART`), `run.sh` starts the game with
the settings used while testing. `package.py` makes the release zip. The installer uses the game's own `tools/` (`new_character.py`,
`roster_mainbin.py` with the `set_cmd` ability option, `charmod_objx.py`, `gim_encode.py`, `package_extract.py`).

MIT licensed (scripts and text only; see `LICENSE`).
