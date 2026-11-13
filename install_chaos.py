#!/usr/bin/env python3
"""Installs (or removes) the playable Chaos in an installed Dissidia 012 recomp game. Needs Python 3.11+ (the game's tools make their own
environment with numpy and Pillow the first time, one download of about 60 MB).

    install_chaos.py [--game DIR] [--uninstall] [--art DIR]

DIR is the game's install folder (the one with disc0/ and ms0/; the wizard's default is ~/Games/Dissidia012). With no --game the usual
places are tried and, failing that, you are asked. The script builds Chaos into DIR/mods from the game's own data in DIR/disc0 and the
game's own tools in DIR/tools; nothing from the game is stored in this package. It can be run again at any time (it updates in place);
--uninstall takes Chaos out again, and the game's other mods are left alone. Start the game afterwards: Chaos is the last tile of the
third row on the Quick Battle character select.

Needs the game's tools to be from release v0.1.8 or newer (earlier ones cannot repoint abilities)."""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CODE, SLOT = "chs100", 35
PAD = 2600000                       # bytes: above the retail model staging block (2,506,752) so the game raises its budget to this
PAGE = "https://github.com/schindlershadow/dissidia-chaos"
# menu pictures (fan wiki artwork, not shipped in this package): head and shoulders, full body, logo plate
ART_URLS = {
    "chaos_head.png": "https://dissidia.wiki/images/5/54/012_Chaos_Art.png",
    "chaos_full.png": "https://static.wikia.nocookie.net/finalfantasy/images/b/be/DissidiaChaos.png/revision/latest?cb=20101002233636",
    "chaos_logo.png": "https://static.wikia.nocookie.net/finalfantasy/images/0/0f/Dissidia_Chaos.png/revision/latest?cb=20090521145146",
}


def candidates():
    home = os.path.expanduser("~")
    out = [os.path.join(home, "Games", "Dissidia012"), os.path.join(home, "Dissidia012"), os.path.join(home, "Games", "Dissidia 012"),
           os.path.join(home, "Documents", "Dissidia012")]
    for var in ("LOCALAPPDATA", "APPDATA", "ProgramFiles"):
        if os.environ.get(var):
            out.append(os.path.join(os.environ[var], "Dissidia012"))
    return out


def is_game(d):
    return os.path.isfile(os.path.join(d, "disc0", "PSP_GAME", "USRDIR", "DATA", "PACKAGE.BIN"))


def find_tools(game):
    for d in (os.path.join(game, "tools"), os.path.join(game, "game", "tools"), os.path.join(game, "..", "game", "tools")):
        if os.path.isfile(os.path.join(d, "new_character.py")):
            return os.path.abspath(d)
    return None


def fetch_art(dst):
    """Downloads the menu pictures that are not in the art folder; any that fail stay Feral Chaos's. -> folder with what exists"""
    import urllib.request
    os.makedirs(dst, exist_ok=True)
    for name, url in ART_URLS.items():
        path = os.path.join(dst, name)
        if os.path.isfile(path):
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "dissidia-chaos-installer"})
            with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
                f.write(r.read())
            print("  picture: %s" % name)
        except Exception as e:                                   # offline, moved, blocked: keep the placeholder
            print("  picture %s not downloaded (%s): the menus keep Feral Chaos's" % (name, e))
    return dst


def run(args, **kw):
    r = subprocess.run([sys.executable] + args, **kw)
    if r.returncode:
        sys.exit("failed: %s (exit %d)" % (" ".join(os.path.basename(a) for a in args[:2]), r.returncode))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game", help="the game's install folder (has disc0/)")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--no-download", action="store_true", help="do not download the menu pictures (Feral Chaos's stay)")
    ap.add_argument("--art", help="folder with chaos_head.png, chaos_full.png, chaos_logo.png (menu pictures; default: art/ next to this script)")
    a = ap.parse_args()

    game = a.game
    if not game:
        game = next((d for d in candidates() if is_game(d)), None)
    while not game or not is_game(game):
        if game:
            print("%s has no disc0/PSP_GAME/USRDIR/DATA/PACKAGE.BIN: not an installed game folder." % game)
        try:
            game = input("Path of your Dissidia 012 install folder (the one with disc0): ").strip().strip('"')
        except EOFError:
            sys.exit("no game folder given (use --game DIR)")
    game = os.path.abspath(os.path.expanduser(game))
    tools = find_tools(game)
    if not tools:
        sys.exit("%s/tools has no new_character.py: reinstall the game with the wizard (release v0.1.8 or newer)." % game)
    sys.path.insert(0, tools)
    import pydeps                      # numpy / Pillow at the versions the game's tools pin (made once in tools/.venv; needs Python 3.11+)
    pydeps.require()
    mods = os.path.join(game, "mods")
    os.makedirs(mods, exist_ok=True)
    print("game: %s\ntools: %s\nmods: %s" % (game, tools, mods))

    if a.uninstall:
        run([os.path.join(tools, "new_character.py"), "--work", game, "--mods", mods, "--slot", str(SLOT), "--remove"])
        for rel in ("voice/en/voice_load_p_%s.bin" % CODE, "menu/jp/talkevent/tim2/chara/b_talk_%s.gim" % CODE,
                    "menu/jp/talkevent/tim2/chara/t_talk_%s.gim" % CODE):
            try:
                os.remove(os.path.join(mods, *rel.split("/")))
            except OSError:
                pass
        battle = os.path.join(mods, "voice", "en", "battle")
        if os.path.isdir(battle):
            for f in os.listdir(battle):
                if f.startswith("voice_p_%s_" % CODE):
                    os.remove(os.path.join(battle, f))
        import json
        p = os.path.join(mods, "extra_abilities.json")
        if os.path.isfile(p):
            names = json.load(open(p, encoding="utf-8"))
            names.pop(CODE, None)
            if names:
                json.dump(names, open(p, "w", encoding="utf-8"), indent=1)
            else:
                os.remove(p)
        print("Chaos removed.")
        return

    art = a.art or os.path.join(HERE, "art")
    get_py = os.path.join(tools, "package_extract.py")
    with tempfile.TemporaryDirectory() as tmp:
        if not a.no_download and not a.art:
            print("menu pictures ...")
            art = fetch_art(os.path.join(tmp, "art")) if not all(os.path.isfile(os.path.join(art, n)) for n in ART_URLS) else art
        def get(path, dst):
            run([get_py, os.path.join(game, "disc0"), "get", path, dst], stdout=subprocess.DEVNULL)

        print("reading the boss' files from your game ...")
        get("obj/p_org200_s_hard.gmo", os.path.join(tmp, "body.gmo"))
        get("obj/p_org200_s_hard.cosx", os.path.join(tmp, "body.cosx"))
        get("obj/p_org200_02.objx", os.path.join(tmp, "boss.objx"))
        get("menu/jp/battle/chara_image/p_org200_normal.gim", os.path.join(tmp, "hud.gim"))
        run([os.path.join(HERE, "tools", "make_objx.py"), tools, os.path.join(tmp, "boss.objx"), os.path.join(tmp, "p_chaos.objx")])
        run([os.path.join(HERE, "tools", "make_hud.py"), tools, os.path.join(tmp, "hud.gim"), os.path.join(tmp, "hud.png")])

        # the kit's names and help texts: merged into the mods folder's own extra_abilities.json (other characters keep theirs)
        import json
        names = {}
        p = os.path.join(mods, "extra_abilities.json")
        if os.path.isfile(p):
            names = json.load(open(p, encoding="utf-8"))
        names[CODE] = json.load(open(os.path.join(HERE, "extra_abilities.json"), encoding="utf-8"))[CODE]
        json.dump(names, open(p, "w", encoding="utf-8"), indent=1)

        args = [os.path.join(tools, "new_character.py"), "--work", game, "--mods", mods, "--slot", str(SLOT), "--code", CODE,
                "--like", "org210", "--name", "Chaos", "--series", "FINAL FANTASY",
                "--model", os.path.join(tmp, "body.gmo"), "--objx", os.path.join(tmp, "p_chaos.objx")]
        for flag, name in (("--portrait", "chaos_head.png"), ("--slidein", "chaos_full.png"), ("--logo", "chaos_logo.png")):
            if os.path.isfile(os.path.join(art, name)):
                args += [flag, os.path.join(art, name)]
        print("building the character ...")
        run(args, stdout=subprocess.DEVNULL)

        # The game raises its model memory budget only when a model file in mods/obj is bigger than a retail one, and the bigger menu
        # pack of an extra character needs that raise (without it the battle never finishes loading). The manikin body is never used
        # by a player, so it carries the padding (trailing zeros are ignored by the model loader).
        zako = os.path.join(mods, "obj", "p_%s_zako.gmo" % CODE)
        if os.path.getsize(zako) < PAD:
            with open(zako, "ab") as f:
                f.write(bytes(PAD - os.path.getsize(zako)))
        # the boss' own costume data (it names the voice-bank suffix), voice bank, face strip, banner and talk portraits
        for v in ("1p", "2p", "zako"):
            shutil.copy(os.path.join(tmp, "body.cosx"), os.path.join(mods, "obj", "p_%s_%s.cosx" % (CODE, v)))
        battle = os.path.join(mods, "voice", "en", "battle")
        os.makedirs(battle, exist_ok=True)
        for f in os.listdir(battle):
            if f.startswith("voice_p_%s_" % CODE):
                os.remove(os.path.join(battle, f))
        get("voice/en/battle/voice_p_org200_s_hard.scd", os.path.join(battle, "voice_p_%s_s_hard.scd" % CODE))
        with open(os.path.join(mods, "voice", "en", "voice_load_p_%s.bin" % CODE), "wb") as f:   # empty cue table
            f.write(b"VOLD\x14\x08\x10\x20" + bytes(8))
        sys.path.insert(0, tools)
        import gim_encode as ge
        from PIL import Image
        img = Image.open(os.path.join(tmp, "hud.png"))
        base = os.path.join(mods, "menu", "jp", "battle", "chara_image", "p_%s_" % CODE)
        tmpl = open(base + "1p.gim", "rb").read()
        for v in ("1p", "2p", "zako"):
            open(base + v + ".gim", "wb").write(ge.encode(tmpl, img))
        for path, dst in (("menu/jp/common/chara_face_in_name/p_org200_face_in_name.gim", "menu/jp/common/chara_face_in_name/p_%s_face_in_name.gim"),
                          ("menu/en/battle/encount/encount_text_tim2/encount_org200.gim", "menu/en/battle/encount/encount_text_tim2/encount_%s.gim"),
                          ("menu/jp/talkevent/tim2/chara/b_talk_org200.gim", "menu/jp/talkevent/tim2/chara/b_talk_%s.gim"),
                          ("menu/jp/talkevent/tim2/chara/t_talk_org200.gim", "menu/jp/talkevent/tim2/chara/t_talk_%s.gim")):
            out = os.path.join(mods, *(dst % CODE).split("/"))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            get(path, out)
    print("\nDone. Start the game: Chaos is the last tile of the third row of the Quick Battle character select.")
    print("Both players of a multiplayer match need Chaos installed. Remove it with:  install_chaos.py --uninstall")
    print(PAGE)


if __name__ == "__main__":
    main()
