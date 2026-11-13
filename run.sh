#!/bin/bash
# Run the game with the Chaos mod. The bigger menu pack / main.bin need the raised model budget.
HERE=$(cd "$(dirname "$0")" && pwd)
export PSPRECOMP_MODS=${PSPRECOMP_MODS:-$HERE/mods}
export PSPRECOMP_ROSTER_EXPERIMENTAL=1
export PSPRECOMP_MODEL_BUDGET=${PSPRECOMP_MODEL_BUDGET:-2600000}
exec "${DISSIDIA_REPO:-$HOME/code/dissidia/psprecomp/games/dissidia}/tools/run.sh" "${WORK:-$HOME/Games/Dissidia012}" "$@"
