#!/usr/bin/env -S -u BASH_ENV -u ENV /bin/bash --noprofile --norc
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --time=0:50:00
#SBATCH --job-name=pfb_run
#SBATCH --export=NIL
#SBATCH --output=/pscratch/sd/j/josephrb/pfb-20261117-stage/slurm-%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/pfb-20261117-stage/slurm-%j.err
# PILOT-FB's one job (PILOT-FB-DECLARATION.md rev 3 §4, §5.1, §7; PILOT-FB-BINDING-1 rulings 2-3).
# Usage: sbatch_pfb.sh <deploy> <pin> <stage> <root>
#   <stage> is the declared /pscratch/sd/j/josephrb/pfb-20261117-stage (Slurm's own logs go there too). It holds RS1's
#           A0 products (a0-refs/) and the sigma receipt (assess_receipt.json), copied by the connect, and the
#           login-node prep-only smoke's smoke-edges/INDEX.json and smoke-receipt.json (0 node-h; it precedes the job);
#   <root>  is the declared run root, /pscratch/sd/j/josephrb/pfb-20261117; it must NOT exist (§4, a fresh root): the
#           job creates it.
# Preflight, all before the root is created, so a refusal never spends it: inside Slurm, any PFB_ variable refuses (the
# local-test switch cannot reach a real job), the allocation must be one node, the name in the pfb_ family, the root
# and stage the declared paths, physically (no symlink); the deploy at the pin, clean (read without refreshing its git
# index); setup_salloc_env.sh at its pinned sha256, sourced with PYTHONPATH, PYTHONHOME, PYTHONSTARTUP and PYTHONUSERBASE
# unset, its return status checked, and the job's own variables unchanged by it; Slurm's TimeLimit at most
# --time=0:50:00 (3,000 s = 0.833 node-h on one exclusive node, under 0.9); the stage's copies and the smoke's receipt
# (this pin, this mode, its INDEX); LightGBM 4.6.0. A preflight refusal is <stage>/job-<id>.refused.json with
# "preflight_refused" (no outcome: nothing ran); an existing root is "refused" (RUN REFUSED, §5.2). A refusal before the
# stage is validated writes nothing but stderr. Python never writes bytecode (PYTHONDONTWRITEBYTECODE=1).
# Code 4-6: --export=NIL (code 6), and the script re-executes itself under env -i with a named variable list (the environment
# block below); every file it creates in the stage is created new (O_CREAT|O_EXCL|O_NOFOLLOW), so nothing pre-placed is
# written through; the stage must hold only what the smoke created and the copies (stage-check), and the setup's
# sourced-file closure (from its xtrace) must equal the smoke's; untracked .py files in the deploy's nd-unfolding/
# refuse. Slurm itself opens slurm-%j.out/.err before the script runs; stage-check refuses them if they are links.
# Local tests run outside Slurm with PFB_LOCAL_TEST set; they may name other absolute paths, never under /pscratch or
# /global, and may give PFB_SETUP_SHA for their stub setup file.
# The order after preflight: the prep step (G0, before any fit) writes <root>/edges and must reproduce the smoke's
# INDEX.json; round 1 runs A0R, E1/E2/E3's bases and E1's jitters 1-4 on 8 lanes; then, in this order: a task's exit 4
# (an input digest) is INPUTS CHANGED, exit 5 (a changed grid membership) is RUN REFUSED, any other failure is an
# operational interruption (INCOMPLETE); only a clean round reaches the round-1 gate (G4, G1, bindings, the products'
# job, J, G2, G3, identity) and the wall projection (3 x round 1 <= 2,900 s); rounds 2-3 (E1's jitters 5-20) are
# classified the same way.
# job-status.json starts as "the job did not finish", so a time-limit kill reads INCOMPLETE; a deliberate stop after a
# round-1 gate failure is recorded as that, not as an interruption (§5.2). Every status names the job, pin and root.
# --- the environment: identical in sbatch_pfb.sh and pfb_smoke_prep.sh (code 4-7, the director's rulings) ---
# The reviewed launches are the only approved entry. The smoke, on a login node (the guard refuses inside an
# allocation before the environment is cleared):
#   [ -z "${SLURM_JOB_ID-}" ] && /usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin /bin/bash --noprofile --norc <deploy>/nd-unfolding/pfb_smoke_prep.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage
# The job (no SBATCH_EXPORT can reach sbatch; #SBATCH --export=NIL creates no login environment on the node):
#   /usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin sbatch <deploy>/nd-unfolding/sbatch_pfb.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage /pscratch/sd/j/josephrb/pfb-20261117
# The job's first shell is this file's shebang (env -S -u BASH_ENV -u ENV). The script re-executes itself under
# `env -i` with only the variables it names, and checks the names AND the values whatever the marker says: HOME, PATH,
# USER, LOGNAME, SCRATCH, LC_ALL, PYTHONDONTWRITEBYTECODE=1, PYTHONNOUSERSITE=1 (no user site in any python3),
# GIT_CONFIG_NOSYSTEM=1 and GIT_CONFIG_GLOBAL=/dev/null (every git call also runs -c core.fsmonitor=false). A local
# test (PFB_LOCAL_TEST, outside Slurm only) keeps its own HOME and PATH. After the setup, a denied variable refuses,
# the declared Python and git values are restored, and setup_env_text records the values the setup leaves (PATH,
# PYTHONPATH, LD_LIBRARY_PATH, LD_PRELOAD, CONDA_PREFIX, CONDARC, PYTHONNOUSERSITE, every GIT_CONFIG_*): the smoke
# writes them, and the job must reproduce them exactly before it runs any setup-selected tool.
if [ "${PFBCLEAN:-}" != 1 ]; then
    if [ -n "${SLURM_JOB_ID:-}" ] && [ -n "$(compgen -v PFB_)" ]; then
        echo "[pfb] refusing: PFB_ variables are set inside a Slurm job: $(compgen -v PFB_ | tr '\n' ' ')" >&2; exit 2
    fi
    keep=(PFBCLEAN=1 LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null)
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
envwant PFBCLEAN 1; envwant LC_ALL C; envwant PYTHONDONTWRITEBYTECODE 1; envwant PYTHONNOUSERSITE 1
envwant GIT_CONFIG_NOSYSTEM 1; envwant GIT_CONFIG_GLOBAL /dev/null
if [ -z "${PFB_LOCAL_TEST+x}" ] || [ -n "${SLURM_JOB_ID:-}" ]; then
    envwant HOME /global/homes/j/josephrb; envwant PATH /usr/bin:/bin; envwant USER josephrb
    envwant LOGNAME josephrb; envwant SCRATCH /pscratch/sd/j/josephrb
fi
for v in $(compgen -e); do
    case "$v" in
        PFBCLEAN|LC_ALL|PYTHONDONTWRITEBYTECODE|PYTHONNOUSERSITE|GIT_CONFIG_NOSYSTEM|GIT_CONFIG_GLOBAL) ;;
        HOME|USER|LOGNAME|PATH|SCRATCH) ;;
        SLURM_JOB_ID|SLURM_JOB_NAME|SLURM_JOB_NUM_NODES|SLURM_EXPORT_ENV|PWD|OLDPWD|SHLVL|_|PFB_*) ;;
        *) echo "[pfb] refusing: the environment holds $v, which the declared environment does not" >&2; exit 2 ;;
    esac
done
pgit() { git -c core.fsmonitor=false "$@"; }  # with GIT_CONFIG_NOSYSTEM=1 and GIT_CONFIG_GLOBAL=/dev/null above
newfile() {  # <path>: create it O_CREAT|O_EXCL|O_NOFOLLOW; fails on anything already there, a link included. The system
    # interpreter by absolute path, isolated and writing no bytecode (-I -S -B): a refusal after the setup never runs a
    # setup-selected python3
    /usr/bin/python3 -I -S -B -c 'import os, sys; os.close(os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644))' "$1" 2>/dev/null
}
traced_setup() {  # <log>: source the pinned setup with its xtrace (PS4 names each sourced file) into <log>; 97 if it
    local PS4='+@${BASH_SOURCE[0]}@ '                # exported a denied variable
    set -x
    source "$D/setup_salloc_env.sh" >> "$1" 2>&1
    local rc=$?
    { set +x; } 2>/dev/null
    export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null  # before the
    for v in BASH_ENV ENV PYTHONHOME PYTHONSTARTUP PYTHONPYCACHEPREFIX PYTHONUSERBASE PYTHONINSPECT GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE; do  # check
        [ -z "${!v+x}" ] || { echo "[pfb] the setup exported $v, which is denied" >> "$1"; echo "[pfb] the setup exported $v, which is denied" >&2; return 97; }
    done
    return "$rc"
}
setup_env_text() {  # the values the setup leaves, one record per name: the name, its status (exported, set, unset) and
    local v st d                                   # the value quoted by printf %q; bash builtins only
    for v in PATH PYTHONPATH LD_LIBRARY_PATH LD_PRELOAD CONDA_PREFIX CONDARC PYTHONNOUSERSITE $(compgen -v GIT_CONFIG_); do
        if [ -z "${!v+x}" ]; then printf '%s unset\n' "$v"; continue; fi
        d=$(declare -p "$v" 2>/dev/null); d=${d#declare -}; d=${d%% *}  # the attribute field: -x, -rx, -xr all export
        case "$d" in *x*) st=exported ;; *) st=set ;; esac
        printf '%s %s %q\n' "$v" "$st" "${!v}"
    done
}
# --- end of the environment block ---
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; STAGE="${3:?stage}"; OUT="${4:?root}"
ROOT_DECLARED=/pscratch/sd/j/josephrb/pfb-20261117
STAGE_DECLARED=/pscratch/sd/j/josephrb/pfb-20261117-stage
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
LGBM_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28  # setup_salloc_env.sh's ROOT628_PREFIX: LightGBM must be there
JOB="${SLURM_JOB_ID:-local}"
STAGE_OK=""; LOCAL=false
record() {  # <key> <why>: the stage's refusal record, created new, only once the stage is validated
    echo "[pfb] $1: $2" >&2
    [ -n "$STAGE_OK" ] && newfile "$STAGE/job-$JOB.refused.json" \
        && printf '{"%s": "%s", "job": "%s", "pin": "%s", "root": "%s"}\n' "$1" "$2" "$JOB" "$PIN" "$OUT" \
            >> "$STAGE/job-$JOB.refused.json"
}
preflight() { record preflight_refused "$1"; exit 2; }
canonical() {  # <path>: absolute, no . or .. or // components
    case "$1" in /*) ;; *) return 1 ;; esac
    case "$1" in *//*|*/./*|*/../*|*/.|*/..) return 1 ;; esac
}
if [ -n "${SLURM_JOB_ID:-}" ]; then
    [ -z "$(compgen -v PFB_)" ] || preflight "PFB_ variables are set inside a Slurm job: $(compgen -v PFB_ | tr '\n' ' ')"
    [ "${SLURM_JOB_NUM_NODES:-}" = 1 ] || preflight "the allocation has ${SLURM_JOB_NUM_NODES:-?} nodes, not 1"
    [ "${SLURM_EXPORT_ENV-}" = NIL ] \
        || preflight "the job's export mode is '${SLURM_EXPORT_ENV-<unset>}', not the approved NIL (an SBATCH_EXPORT override?)"
    case "${SLURM_JOB_NAME:-}" in pfb_*) ;; *) preflight "the job name '${SLURM_JOB_NAME:-}' is not in the pfb_ family" ;; esac
    [ "$OUT" = "$ROOT_DECLARED" ] || preflight "the root $OUT is not the declared $ROOT_DECLARED"
    [ "$STAGE" = "$STAGE_DECLARED" ] || preflight "the stage $STAGE is not the declared $STAGE_DECLARED"
elif [ -n "${PFB_LOCAL_TEST+x}" ]; then
    LOCAL=true
    for p in "$OUT" "$STAGE"; do
        case "$p" in /pscratch/*|/global/*) preflight "a local test never names a cluster path: $p" ;; esac
    done
    [ -n "${PFB_SETUP_SHA:-}" ] && SETUP_SHA="$PFB_SETUP_SHA"
    [ -n "${PFB_LGBM_PREFIX:-}" ] && LGBM_PREFIX="$PFB_LGBM_PREFIX"
else
    preflight "outside a Slurm job without PFB_LOCAL_TEST: the job runs only under sbatch"
fi
canonical "$STAGE" && canonical "$OUT" || preflight "the stage and root must be canonical absolute paths"
[ -d "$STAGE" ] && [ ! -L "$STAGE" ] || preflight "the stage $STAGE is not an existing directory"
[ "$(cd "$STAGE" && pwd -P)" = "$STAGE" ] || preflight "the stage $STAGE resolves elsewhere"
STAGE_OK=1
[ "$(cd "$(dirname "$OUT")" 2>/dev/null && pwd -P)" = "$(dirname "$OUT")" ] || preflight "the root's parent is not an existing directory at that path"
head_sha=$(pgit -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(pgit --no-optional-locks -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
[ "$head_sha" = "$PIN" ] && [ "$dirty" -eq 0 ] || preflight "deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files"
extra_py=$(pgit --no-optional-locks -C "$D" ls-files --others -- 'nd-unfolding/*.py' 2>/dev/null | wc -l)
[ "$extra_py" -eq 0 ] || preflight "the deploy's nd-unfolding/ holds $extra_py untracked .py files (they would shadow imports)"
setup_sha=$(sha256sum "$D/setup_salloc_env.sh" 2>/dev/null | cut -d' ' -f1)
[ "$setup_sha" = "$SETUP_SHA" ] || preflight "setup_salloc_env.sh is not the pinned one (sha256 $setup_sha)"
ENVLOG="$STAGE/job-$JOB.env.log"
newfile "$ENVLOG" || preflight "cannot create $ENVLOG new (something is already there)"
GUARD="$D|$PIN|$STAGE|$OUT|$JOB|$LOCAL"
traced_setup "$ENVLOG"
src=$?
[ "$src" -eq 0 ] || preflight "setup_salloc_env.sh returned $src (97: it exported a denied variable)"
[ "$GUARD" = "$D|$PIN|$STAGE|$OUT|$JOB|$LOCAL" ] || preflight "setup_salloc_env.sh changed the job's own variables"
[ -f "$STAGE/smoke-setup-env.txt" ] && [ ! -L "$STAGE/smoke-setup-env.txt" ] \
    && [ "$(setup_env_text)" = "$(< "$STAGE/smoke-setup-env.txt")" ] \
    || preflight "the setup's environment values (PATH, PYTHONPATH, LD_*, CONDA_*, git config) are not the smoke's"
if [ "$LOCAL" = false ]; then
    TL=$(scontrol show job "$JOB" 2>/dev/null | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
    python3 "$D/nd-unfolding/fb_pilot_analyze.py" slurm-limit --timelimit "$TL" \
        || preflight "Slurm's TimeLimit '$TL' exceeds --time=0:50:00 (the 0.9 node-h cap)"
fi
python3 "$D/nd-unfolding/fb_pilot_analyze.py" stage-check --stage "$STAGE" 2>> "$ENVLOG" \
    || preflight "the stage holds something other than the smoke's files, the copies and the jobs' logs (see the env log)"
python3 "$D/nd-unfolding/fb_pilot_analyze.py" smoke-receipt check --stage "$STAGE" --pin "$PIN" --local "$LOCAL" \
    --trace "$ENVLOG" --exclude "$0" 2>> "$ENVLOG" \
    || preflight "the smoke receipt is not this pin's, this mode's, this INDEX's and this setup closure's (see the env log)"
[ ! -e "$OUT" ] && [ ! -L "$OUT" ] || { record refused "the root is not fresh: $OUT exists"; exit 2; }
( cd "$D/nd-unfolding" && python3 fb_pilot_analyze.py lgbm-check --prefix "$LGBM_PREFIX" ) >> "$ENVLOG" 2>&1 \
    || preflight "the environment's LightGBM is not 4.6.0 under $LGBM_PREFIX (see the env log)"
mkdir "$OUT" || preflight "cannot create $OUT"
ST="$OUT/job-status.json"
status() { python3 -c 'import json, os, sys; d = json.loads(sys.argv[2]); d.update(job=sys.argv[3], pin=sys.argv[4], root=sys.argv[5]); t = sys.argv[1] + ".partial-%d" % os.getpid(); fd = os.open(t, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644); os.write(fd, json.dumps(d, indent=1).encode()); os.close(fd); os.replace(t, sys.argv[1])' "$ST" "$1" "$JOB" "$PIN" "$OUT"; }
L="$OUT/logs"; mkdir -p "$L/tasks"
status "{\"interrupted\": \"the job did not finish (time limit or interruption)\"}"
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
RATIO="$D/$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import rounding_mechanism_probe as r; print(r.STABILITY["ratio"])' "$D/nd-unfolding")"
COMMON=(--npz "$NPZ" --bkg "$BKG" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f
        --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 --config R --iters 5
        --threads 32 --construction pseudo --truth eavail_shape --amplitude 1.0 --eavail-ratio "$RATIO" --pseudo-seed 990000)
SHM="/dev/shm/pfb-$JOB"; mkdir -p "$SHM"; trap 'rm -rf "$SHM"' EXIT
echo "[pfb] job=$JOB host=$(hostname) pin=$PIN start=$(date -u +%FT%TZ)"
# the prep step: G0, before any fit; it must reproduce the login-node smoke's edges
( cd "$D" && python3 nd-unfolding/fb_pilot_probe.py prep --edges-out "$OUT/edges" -- "${COMMON[@]}" --pairs=-:- \
    --tag pfb_prep --out "$OUT/prep-unused" ) > "$L/prep.log" 2>&1
rc=$?
case "$rc" in
    0) ;;
    6) status "{\"prep\": \"INFEASIBLE\", \"prep_detail\": $(cat "$OUT/edges.g0.json" 2>/dev/null || echo null)}"
       echo "[pfb] INFEASIBLE (G0)"; exit 0 ;;
    4) status "{\"inputs_changed\": \"the prep step's input digest check (exit 4)\"}"; exit 0 ;;
    *) status "{\"interrupted\": \"the prep step exited $rc\"}"; exit 1 ;;
esac
if ! cmp -s "$OUT/edges/INDEX.json" "$STAGE/smoke-edges/INDEX.json"; then
    status "{\"inputs_changed\": \"the job's edges differ from the login-node smoke's (INDEX.json)\"}"; exit 0
fi
task_cmd() {  # <id>: one task's command line, as argv lines
    local id="$1"
    case "$id" in
        A0R) printf '%s\n' nd-unfolding/rounding_mechanism_probe.py run --arm A0 --contract docs/orchestration/state/s5c/contract.json \
                 --h2-definition nd-unfolding/pv-ladder/readouts/h2_definition.json -- "${COMMON[@]}" "--pairs=-:-" --tag rs1_A0 \
                 --out "$OUT/runs/A0R" ;;
        E[123]_*) local s="${id%%_*}" j="${id#*_}"
             printf '%s\n' nd-unfolding/fb_pilot_probe.py run --set "$s" --edges "$OUT/edges" --workdir "$SHM" -- "${COMMON[@]}" \
                 "--pairs=-:$j" --tag "pfb_$s" --out "$OUT/runs/$s" ;;
    esac
}
export -f task_cmd; export D L OUT SHM; export COMMON_STR="${COMMON[*]}"
run_round() {  # ids on stdin; 8 lanes; each task's exit code in $L/<id>.rc
    xargs -P 8 -I{} bash -c '
        id="$1"; COMMON=($COMMON_STR)
        argv=(); while IFS= read -r x; do argv+=("$x"); done < <(task_cmd "$id")
        python3 -c "import time; print(time.time())" > "$L/$id.start"
        ( cd "$D" && /usr/bin/time -v -o "$L/tasks/$id.time" python3 "${argv[@]}" ) >> "$L/tasks/$id.log" 2>&1
        echo $? > "$L/$id.rc"
        python3 -c "import time; print(time.time())" > "$L/$id.end"
        exit 0' _ {}
}
classify() {  # <ids...>: exit 4 -> INPUTS CHANGED, exit 5 -> RUN REFUSED, other -> interrupted; returns 1 if any
    local bad4="" bad5="" bad=""
    for id in "$@"; do
        r=$(cat "$L/$id.rc" 2>/dev/null || echo missing)
        case "$r" in 0) ;; 4) bad4="$bad4 $id" ;; 5) bad5="$bad5 $id" ;; *) bad="$bad $id:$r" ;; esac
    done
    if [ -n "$bad4" ]; then status "{\"inputs_changed\": \"input digest exit 4 in:$bad4\"}"; return 1; fi
    if [ -n "$bad5" ]; then status "{\"refused\": \"grid-membership exit 5 in:$bad5\"}"; return 1; fi
    if [ -n "$bad" ]; then status "{\"interrupted\": \"tasks failed:$bad\", \"task_failures\": \"$bad\"}"; return 1; fi
    return 0
}
sums() { ( cd "$OUT" && find runs edges -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"; }
R1="A0R E1_- E2_- E3_- E1_1 E1_2 E1_3 E1_4"
t0=$(date +%s)
printf '%s\n' $R1 | run_round
w1=$(( $(date +%s) - t0 ))
echo "[pfb] round 1 wall ${w1}s"
classify $R1 || { sums; exit 0; }
python3 "$D/nd-unfolding/fb_pilot_analyze.py" round1 --runs "$OUT" --stage "$STAGE" --deploy "$D" --pin "$PIN" --job "$JOB" \
    > "$L/round1.json" 2>> "$L/round1.err"
g=$?
if [ "$g" -ne 0 ]; then
    status "{\"round1\": \"STOP\", \"round1_detail\": $(cat "$L/round1.json" 2>/dev/null || echo null), \"round1_wall_s\": $w1}"
    echo "[pfb] round-1 gate STOP (deliberate; the gate names the outcome)"; sums; exit 0
fi
if [ $(( 3 * w1 )) -gt 2900 ]; then
    status "{\"interrupted\": \"the round-1 wall projection: 3 x ${w1}s > 2,900 s\", \"round1\": \"PASS\"}"
    echo "[pfb] INCOMPLETE: the wall projection stops the run"; sums; exit 0
fi
R23=$(printf 'E1_%s ' {5..20})
printf '%s\n' $R23 | run_round
sums
classify $R23 || exit 0
status "{\"round1\": \"PASS\", \"round1_wall_s\": $w1, \"done\": true}"
echo "{\"job\": \"$JOB\", \"pin\": \"$PIN\", \"end\": \"$(date -u +%FT%TZ)\"}" > "$L/DONE"
echo "[pfb] DONE end=$(date -u +%FT%TZ)"
