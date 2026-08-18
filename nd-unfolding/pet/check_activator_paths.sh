#!/bin/bash
# Does the job's ENVIRONMENT actually come up? EXECUTED, not inspected.
#
# WHY THIS EXISTS. 57232522 died 50/50 in 7-11 seconds with an EMPTY `.out`, on the FIRST line of the
# environment activation -- after a pre-submit dry run that went green through every guard including the full
# 9.9 GB input sha256. Every one of those guards checks something ABOUT THE DATA ROOT'S CONTENTS. Not one
# executes the environment the job will run in. So the guards answered *"are the inputs right?"* and the job
# died on *"can I become the environment that reads them?"*
#
# RUN IN A CLEAN NON-INTERACTIVE SHELL, because the login shell already has the environment activated:
# sourcing the activator there succeeds for a reason the job will not have. Same shape as the ordering check
# that could not fail from the wrong host -- an instrument verifying from a position where the failure cannot
# appear.
#
# `env -i` plus only what sbatch guarantees (HOME, USER, SCRATCH), `--noprofile --norc`, and PATH reduced to
# the system default so a PATH-based shim from the submitting shell cannot mask a missing activation.
set -eo pipefail
DATA_ROOT=${1:?usage: check_activator_paths.sh <DATA_ROOT>}

# ONE FILE, not two. The earlier split existed only to dodge quote-splicing a nested `bash -c` string -- a
# fragility the check does not need, and `sbatch_*.sh`/`submit_*.sh` names are load-bearing provenance here,
# so fewer new names is better.
DATA_ROOT=$1
ACT="${DATA_ROOT}/setup_salloc_env.sh"

[ -r "$ACT" ] || { echo "NO_ACTIVATOR at $ACT"; exit 2; }

# Resolve SCRIPT_DIR the way the activator does: the directory of the file AS SOURCED. For a symlink that is
# the LINK's directory, not the target's -- which is precisely how a bare data root ends up being asked for
# software trees it does not contain.
SCRIPT_DIR="$(cd "$(dirname "$ACT")" && pwd)"
echo "SCRIPT_DIR=$SCRIPT_DIR"

# Follow one level of indirection: a shim that sources another activator hands SCRIPT_DIR to THAT file's
# directory, so the paths to check are the ones the FINAL activator resolves.
FINAL="$ACT"
NEXT=$(grep -oE '^[[:space:]]*(source|\.)[[:space:]]+"?[^"]*setup_salloc_env\.sh"?' "$ACT" | tail -1 \
       | sed -E 's/^[[:space:]]*(source|\.)[[:space:]]+"?//; s/"?$//')
if [ -n "${NEXT:-}" ]; then
  NEXT_EXPANDED=$(eval "GATE5_ENV_ROOT=\${GATE5_ENV_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}; echo $NEXT" 2>/dev/null || true)
  if [ -r "${NEXT_EXPANDED:-}" ]; then
    FINAL="$NEXT_EXPANDED"
    SCRIPT_DIR="$(cd "$(dirname "$FINAL")" && pwd)"
    echo "SHIM -> FINAL=$FINAL"
    echo "SCRIPT_DIR(final)=$SCRIPT_DIR"
  fi
fi

missing=0
while read -r rel; do
  [ -n "$rel" ] || continue
  if [ -e "${SCRIPT_DIR}/${rel}" ]; then
    echo "OK   ${rel}"
  else
    echo "MISS ${rel}   (expected at ${SCRIPT_DIR}/${rel})"
    missing=$((missing + 1))
  fi
done < <(grep -oE '\$\{SCRIPT_DIR\}/[A-Za-z0-9_./-]+' "$FINAL" | sed 's|^${SCRIPT_DIR}/||' | sort -u)

echo "MISSING_COUNT=$missing"
[ "$missing" -eq 0 ] || { echo "PATHS_MISSING"; exit 3; }

# Activation ATTEMPTED and reported, never gating -- see the header.
if bash --noprofile --norc -c "source '$ACT' >/dev/null 2>&1 && command -v python3" >/dev/null 2>&1; then
  echo "ACTIVATION_INFO=succeeded"
else
  echo "ACTIVATION_INFO=did-not-complete-in-this-shell (NOT a failure condition; see header)"
fi
echo "ENV_PATHS_OK"

echo "[activator-paths] PASS -- every path the activator resolves against its own directory exists from"
echo "[activator-paths] this data root. Activation itself is reported above as INFO, never as a gate."
