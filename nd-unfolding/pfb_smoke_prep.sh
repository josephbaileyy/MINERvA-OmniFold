#!/usr/bin/env -S -u BASH_ENV -u ENV /bin/bash --noprofile --norc
# PILOT-FB's login-node prep-only smoke (the code audits' request, the director's ruling of 2026-11-18): the prep step
# alone, on a login node, before any job. 0 node-h: no sbatch, no srun, no fit (prep stops before the first fit).
# Usage: pfb_smoke_prep.sh <deploy> <pin> <stage>, with <stage> the declared /pscratch/sd/j/josephrb/pfb-20261117-stage.
# The smoke CREATES the stage, which must not exist (code 4: fresh and empty, so nothing is pre-placed in it; the connect
# copies a0-refs/ and the sigma receipt in afterwards). Its parent must exist at that physical path. Everything it
# writes is under <stage>, each file created new (O_CREAT|O_EXCL|O_NOFOLLOW):
#   smoke-edges/ (the twelve forced-bins files and INDEX.json) or, on INFEASIBLE, smoke-edges.g0.json (G0's record);
#   smoke-receipt.json (stage, pin, mode, INDEX.json's sha256 and the setup's sourced-file closure), which the job
#   requires; smoke-env.log (the setup's output and xtrace), smoke.log, and the runner's empty smoke-unused/.
# It runs in the job's own environment (the environment block below), so a missing tool or a broken import shows here
# at 0 node-h. Python never writes bytecode, and the deploy's git index is read, never refreshed.
# Exit codes: 0 edges and receipt written; 6 INFEASIBLE; 4 an input digest; 2 a refusal (before the stage is created,
# nothing is written; after, only under the new stage); 9 the receipt could not be written; other: the prep step's own.
# Local tests set PFB_LOCAL_TEST (any absolute stage outside /pscratch and /global; PFB_SETUP_SHA for a stub setup).
# --- the environment: identical in sbatch_pfb.sh and pfb_smoke_prep.sh (code 4-5, the director's rulings) ---
# The reviewed launch starts the first shell clean: the smoke as
#   env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin /bin/bash --noprofile --norc <deploy>/nd-unfolding/pfb_smoke_prep.sh ...
# and the job through `env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin sbatch <deploy>/nd-unfolding/sbatch_pfb.sh ...`
# (no SBATCH_EXPORT can reach sbatch), whose first shell is this file's shebang: env -S -u BASH_ENV -u ENV, so no
# BASH_ENV runs before this line. The script then re-executes itself under `env -i` with only the variables it names.
# Whatever the marker says, the names AND the values are checked: HOME, PATH, USER, LOGNAME, SCRATCH, LC_ALL and
# PYTHONDONTWRITEBYTECODE must be the declared ones (a local test, PFB_LOCAL_TEST outside Slurm only, keeps its own
# HOME and PATH). After the setup, a denied variable (BASH_ENV, ENV, PYTHONHOME, PYTHONSTARTUP, PYTHONPYCACHEPREFIX,
# PYTHONUSERBASE, PYTHONINSPECT, GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE) refuses, and the smoke records the set of
# names the setup leaves, which the job must reproduce.
if [ "${PFBCLEAN:-}" != 1 ]; then
    if [ -n "${SLURM_JOB_ID:-}" ] && [ -n "$(compgen -v PFB_)" ]; then
        echo "[pfb] refusing: PFB_ variables are set inside a Slurm job: $(compgen -v PFB_ | tr '\n' ' ')" >&2; exit 2
    fi
    keep=(PFBCLEAN=1 LC_ALL=C PYTHONDONTWRITEBYTECODE=1)
    if [ -n "${PFB_LOCAL_TEST+x}" ] && [ -z "${SLURM_JOB_ID:-}" ]; then
        keep+=("HOME=${HOME:-/}" "PATH=${PATH:-/usr/bin:/bin}")
        for v in $(compgen -e PFB_); do keep+=("$v=${!v}"); done
    else
        keep+=(HOME=/global/homes/j/josephrb USER=josephrb LOGNAME=josephrb PATH=/usr/bin:/bin SCRATCH=/pscratch/sd/j/josephrb)
        for v in SLURM_JOB_ID SLURM_JOB_NAME SLURM_JOB_NUM_NODES SLURM_EXPORT_ENV; do
            [ -n "${!v:-}" ] && keep+=("$v=${!v}")
        done
    fi
    exec /usr/bin/env -i "${keep[@]}" /bin/bash --noprofile --norc "$0" "$@"
fi
envwant() {  # <name> <value>: the variable must be set, to exactly that value
    [ "${!1-__unset__}" = "$2" ] || { echo "[pfb] refusing: $1 is '${!1-<unset>}', not the declared '$2'" >&2; exit 2; }
}
envwant PFBCLEAN 1; envwant LC_ALL C; envwant PYTHONDONTWRITEBYTECODE 1
if [ -z "${PFB_LOCAL_TEST+x}" ] || [ -n "${SLURM_JOB_ID:-}" ]; then
    envwant HOME /global/homes/j/josephrb; envwant PATH /usr/bin:/bin; envwant USER josephrb
    envwant LOGNAME josephrb; envwant SCRATCH /pscratch/sd/j/josephrb
fi
for v in $(compgen -e); do
    case "$v" in
        PFBCLEAN|LC_ALL|PYTHONDONTWRITEBYTECODE|HOME|USER|LOGNAME|PATH|SCRATCH) ;;
        SLURM_JOB_ID|SLURM_JOB_NAME|SLURM_JOB_NUM_NODES|SLURM_EXPORT_ENV|PWD|OLDPWD|SHLVL|_|PFB_*) ;;
        *) echo "[pfb] refusing: the environment holds $v, which the declared environment does not" >&2; exit 2 ;;
    esac
done
newfile() {  # <path>: create it O_CREAT|O_EXCL|O_NOFOLLOW; fails on anything already there, a link included
    python3 -c 'import os, sys; os.close(os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644))' "$1" 2>/dev/null
}
traced_setup() {  # <log>: source the pinned setup with its xtrace (PS4 names each sourced file) into <log>; 97 if it
    local PS4='+@${BASH_SOURCE[0]}@ '                # exported a denied variable
    set -x
    source "$D/setup_salloc_env.sh" >> "$1" 2>&1
    local rc=$?
    { set +x; } 2>/dev/null
    export PYTHONDONTWRITEBYTECODE=1
    for v in BASH_ENV ENV PYTHONHOME PYTHONSTARTUP PYTHONPYCACHEPREFIX PYTHONUSERBASE PYTHONINSPECT GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE; do
        [ -z "${!v+x}" ] || { echo "[pfb] the setup exported $v, which is denied" >> "$1"; echo "[pfb] the setup exported $v, which is denied" >&2; return 97; }
    done
    return "$rc"
}
# --- end of the environment block ---
set -o pipefail
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
[ ! -e "$STAGE" ] && [ ! -L "$STAGE" ] || no "the stage $STAGE exists: the smoke creates it, fresh and empty"
for t in git sha256sum python3; do command -v "$t" > /dev/null || no "the declared environment has no $t"; done
[ "$LOCAL" = true ] || command -v scontrol > /dev/null || no "the declared environment has no scontrol (the job needs it)"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git --no-optional-locks -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
[ "$head_sha" = "$PIN" ] && [ "$dirty" -eq 0 ] || no "deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files"
setup_sha=$(sha256sum "$D/setup_salloc_env.sh" 2>/dev/null | cut -d' ' -f1)
[ "$setup_sha" = "$SETUP_SHA" ] || no "setup_salloc_env.sh is not the pinned one (sha256 $setup_sha)"
mkdir "$STAGE" || no "cannot create $STAGE"
[ "$(cd "$STAGE" && pwd -P)" = "$STAGE" ] || no "the stage $STAGE resolves elsewhere"
newfile "$STAGE/smoke-env.log" && newfile "$STAGE/smoke.log" || no "cannot create the smoke's logs new"
GUARD="$D|$PIN|$STAGE|$LOCAL"
traced_setup "$STAGE/smoke-env.log"
src=$?
[ "$src" -eq 0 ] || no "setup_salloc_env.sh returned $src (97: it exported a denied variable)"
[ "$GUARD" = "$D|$PIN|$STAGE|$LOCAL" ] || no "setup_salloc_env.sh changed the smoke's own variables"
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
RATIO="$D/$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import rounding_mechanism_probe as r; print(r.STABILITY["ratio"])' "$D/nd-unfolding")"
( cd "$D" && python3 nd-unfolding/fb_pilot_probe.py prep --edges-out "$STAGE/smoke-edges" -- \
    --npz "$NPZ" --bkg "$BKG" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 --config R --iters 5 \
    --threads 32 --construction pseudo --truth eavail_shape --amplitude 1.0 --eavail-ratio "$RATIO" --pseudo-seed 990000 \
    --pairs=-:- --tag pfb_smoke --out "$STAGE/smoke-unused" ) >> "$STAGE/smoke.log" 2>&1
rc=$?
echo "[pfb-smoke] prep rc=$rc"
[ "$rc" -eq 0 ] || exit "$rc"
python3 "$D/nd-unfolding/fb_pilot_analyze.py" smoke-receipt write --stage "$STAGE" --pin "$PIN" --local "$LOCAL" \
    --trace "$STAGE/smoke-env.log" --exclude "$0" || exit 9
echo "[pfb-smoke] receipt written: the job requires its own prep to reproduce $STAGE/smoke-edges/INDEX.json byte for byte"
