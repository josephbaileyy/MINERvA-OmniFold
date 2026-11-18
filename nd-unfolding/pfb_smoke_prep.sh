#!/bin/bash
# PILOT-FB's login-node prep-only smoke (the code audits' request, the director's ruling of 2026-11-18): the prep step
# alone, on a login node, before any job. 0 node-h: no sbatch, no srun, no fit (prep stops before the first fit).
# Usage: pfb_smoke_prep.sh <deploy> <pin> <stage>, with <stage> the declared /pscratch/sd/j/josephrb/pfb-20261117-stage
# (created if absent; its parent must exist at that physical path). Everything it writes is under <stage>:
#   smoke-edges/ (the twelve forced-bins files and INDEX.json) or, on INFEASIBLE, smoke-edges.g0.json (G0's record);
#   smoke-receipt.json (stage, pin, mode, INDEX.json's sha256), which the job requires;
#   smoke-env.log, smoke.log, and the runner's empty smoke-unused/.
# Python never writes bytecode (PYTHONDONTWRITEBYTECODE=1), and the deploy's git index is read, never refreshed.
# setup_salloc_env.sh must be at its pinned sha256; it is sourced as the job sources it.
# Exit codes: 0 edges and receipt written; 6 INFEASIBLE; 4 an input digest; 2 a refusal (nothing written); 9 the
# receipt could not be written; other: the prep step's own. Local tests set PFB_LOCAL_TEST (any absolute stage outside
# /pscratch and /global; PFB_SETUP_SHA for a stub setup file).
set -o pipefail
export PYTHONDONTWRITEBYTECODE=1
D="${1:?deploy}"; PIN="${2:?pin}"; STAGE="${3:?stage}"
STAGE_DECLARED=/pscratch/sd/j/josephrb/pfb-20261117-stage
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
no() { echo "[pfb-smoke] refusing: $1" >&2; exit 2; }
[ -z "${SLURM_JOB_ID:-}" ] || no "this is a login-node step and runs outside any Slurm job"
LOCAL=false
if [ -n "${PFB_LOCAL_TEST+x}" ]; then
    LOCAL=true
    case "$STAGE" in /pscratch/*|/global/*) no "a local test never names a cluster path: $STAGE" ;; esac
    [ -n "${PFB_SETUP_SHA:-}" ] && SETUP_SHA="$PFB_SETUP_SHA"
else
    [ "$STAGE" = "$STAGE_DECLARED" ] || no "the stage $STAGE is not the declared $STAGE_DECLARED"
fi
case "$STAGE" in /*) ;; *) no "the stage must be an absolute path: $STAGE" ;; esac
case "$STAGE" in *//*|*/./*|*/../*|*/.|*/..) no "the stage path is not canonical: $STAGE" ;; esac
PARENT=$(dirname "$STAGE")
[ "$(cd "$PARENT" 2>/dev/null && pwd -P)" = "$PARENT" ] || no "the stage's parent $PARENT is not an existing directory at that path"
[ ! -L "$STAGE" ] || no "the stage $STAGE is a symlink"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git --no-optional-locks -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
[ "$head_sha" = "$PIN" ] && [ "$dirty" -eq 0 ] || no "deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files"
setup_sha=$(sha256sum "$D/setup_salloc_env.sh" 2>/dev/null | cut -d' ' -f1)
[ "$setup_sha" = "$SETUP_SHA" ] || no "setup_salloc_env.sh is not the pinned one (sha256 $setup_sha)"
for x in smoke-edges smoke-edges.g0.json smoke-receipt.json smoke-unused smoke.log smoke-env.log; do
    [ ! -e "$STAGE/$x" ] && [ ! -L "$STAGE/$x" ] || no "a smoke result exists: $STAGE/$x"
done
[ -d "$STAGE" ] || mkdir "$STAGE" || no "cannot create $STAGE"
[ "$(cd "$STAGE" && pwd -P)" = "$STAGE" ] || no "the stage $STAGE resolves elsewhere"
GUARD="$D|$PIN|$STAGE|$LOCAL"
unset PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONUSERBASE
source "$D/setup_salloc_env.sh" > "$STAGE/smoke-env.log" 2>&1
src=$?
export PYTHONDONTWRITEBYTECODE=1
[ "$src" -eq 0 ] || no "setup_salloc_env.sh returned $src"
[ "$GUARD" = "$D|$PIN|$STAGE|$LOCAL" ] || no "setup_salloc_env.sh changed the smoke's own variables"
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
RATIO="$D/$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import rounding_mechanism_probe as r; print(r.STABILITY["ratio"])' "$D/nd-unfolding")"
( cd "$D" && python3 nd-unfolding/fb_pilot_probe.py prep --edges-out "$STAGE/smoke-edges" -- \
    --npz "$NPZ" --bkg "$BKG" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 --config R --iters 5 \
    --threads 32 --construction pseudo --truth eavail_shape --amplitude 1.0 --eavail-ratio "$RATIO" --pseudo-seed 990000 \
    --pairs=-:- --tag pfb_smoke --out "$STAGE/smoke-unused" ) > "$STAGE/smoke.log" 2>&1
rc=$?
echo "[pfb-smoke] prep rc=$rc"
[ "$rc" -eq 0 ] || exit "$rc"
python3 "$D/nd-unfolding/fb_pilot_analyze.py" smoke-receipt write --stage "$STAGE" --pin "$PIN" --local "$LOCAL" || exit 9
echo "[pfb-smoke] receipt written: the job requires its own prep to reproduce $STAGE/smoke-edges/INDEX.json byte for byte"
