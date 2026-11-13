#!/bin/bash
# Builds the playable Chaos (roster slot 35, code chs100) into a mods folder from YOUR OWN Dissidia 012 data.
#
#   DISSIDIA_REPO=~/code/dissidia/psprecomp/games/dissidia  (the Dissidia recomp's games/dissidia folder)
#   WORK=~/dissidia/work         (a work folder with disc0/, as made by setup_from_iso.py)
#   MODS=./mods                  (output; run the game with PSPRECOMP_MODS pointing here)
#   ART=./art                    (optional pictures: chaos_head.png, chaos_full.png, chaos_logo.png; without them the menus use Feral Chaos's)
#
# No game files are stored in this repository: the model, costume file, voice bank and the boss' move set are read from WORK/disc0.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
H=${DISSIDIA_REPO:-$HOME/code/dissidia/psprecomp/games/dissidia}
WORK=${WORK:-$HOME/dissidia/work}
MODS=${MODS:-$HERE/mods}
ART=${ART:-$HERE/art}
D=$WORK/disc0
CODE=chs100
T=$H/tools
[ -f "$T/new_character.py" ] || { echo "DISSIDIA_REPO=$H has no tools/new_character.py"; exit 1; }
[ -f "$D/PSP_GAME/USRDIR/DATA/PACKAGE.BIN" ] || { echo "$D has no PACKAGE.BIN (WORK needs disc0)"; exit 1; }
get() { python3 "$T/package_extract.py" "$D" get "$1" "$2" >/dev/null; }
mkdir -p "$MODS"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

# the boss' third form: model, costume data, moves
get obj/p_org200_s_hard.gmo  "$TMP/body.gmo"
get obj/p_org200_s_hard.cosx "$TMP/body.cosx"
get obj/p_org200_02.objx     "$TMP/boss.objx"
get menu/jp/battle/chara_image/p_org200_normal.gim "$TMP/hud.gim"
python3 "$HERE/tools/make_objx.py" "$T" "$TMP/boss.objx" "$TMP/p_chaos.objx"
python3 "$HERE/tools/make_hud.py" "$T" "$TMP/hud.gim" "$TMP/hud.png"

cp "$HERE/extra_abilities.json" "$MODS/extra_abilities.json"
ARGS=()
[ -f "$ART/chaos_head.png" ]  && ARGS+=(--portrait "$ART/chaos_head.png")
[ -f "$ART/chaos_full.png" ]  && ARGS+=(--slidein "$ART/chaos_full.png")
[ -f "$ART/chaos_logo.png" ]  && ARGS+=(--logo "$ART/chaos_logo.png")
python3 "$T/new_character.py" --work "$WORK" --mods "$MODS" --slot 35 --code $CODE --like org210 --name Chaos \
  --series "FINAL FANTASY" "${ARGS[@]}" --model "$TMP/body.gmo" --objx "$TMP/p_chaos.objx" >/dev/null

# the boss' costume data names the voice-bank suffix (_s_hard); the bank, face strip, encounter banner and talk portraits are his too
for v in 1p 2p zako; do cp "$TMP/body.cosx" "$MODS/obj/p_${CODE}_$v.cosx"; done
rm -f "$MODS"/voice/en/battle/voice_p_${CODE}_*.scd
get voice/en/battle/voice_p_org200_s_hard.scd "$MODS/voice/en/battle/voice_p_${CODE}_s_hard.scd"
printf 'VOLD\x14\x08\x10\x20\x00\x00\x00\x00\x00\x00\x00\x00' > "$MODS/voice/en/voice_load_p_$CODE.bin"   # empty cue table
python3 - "$T" "$MODS" "$TMP/hud.png" "$CODE" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import gim_encode as ge
from PIL import Image
mods, png, code = sys.argv[2:5]
img = Image.open(png)
base = "%s/menu/jp/battle/chara_image/p_%s_" % (mods, code)
tmpl = open(base + "1p.gim", "rb").read()
for v in ("1p", "2p", "zako"):
    open(base + v + ".gim", "wb").write(ge.encode(tmpl, img))
PY
get menu/jp/common/chara_face_in_name/p_org200_face_in_name.gim "$MODS/menu/jp/common/chara_face_in_name/p_${CODE}_face_in_name.gim"
get menu/en/battle/encount/encount_text_tim2/encount_org200.gim "$MODS/menu/en/battle/encount/encount_text_tim2/encount_${CODE}.gim"
mkdir -p "$MODS/menu/jp/talkevent/tim2/chara"
get menu/jp/talkevent/tim2/chara/b_talk_org200.gim "$MODS/menu/jp/talkevent/tim2/chara/b_talk_${CODE}.gim"
get menu/jp/talkevent/tim2/chara/t_talk_org200.gim "$MODS/menu/jp/talkevent/tim2/chara/t_talk_${CODE}.gim"
echo "built into $MODS"
