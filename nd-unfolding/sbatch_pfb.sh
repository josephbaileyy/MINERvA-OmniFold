#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --time=0:50:00
#SBATCH --job-name=pfb_run
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# PILOT-FB's one job (PILOT-FB-DECLARATION.md rev 3 §4, §5.1, §7; PILOT-FB-BINDING-1 rulings 2-3).
# Usage: sbatch_pfb.sh <deploy> <pin> <stage> <root>
#   <stage> holds the connect's O_NOATIME copies: a0-refs/ (RS1's A0 products) and assess_receipt.json (the sigma
#           receipt), and smoke-edges/INDEX.json from the login-node prep-only smoke (0 node-h) that precedes the job;
#   <root>  is the declared run root, /pscratch/sd/j/josephrb/pfb-20261117; it must NOT exist (§4, a fresh root): the
#           job creates it. A refusal is recorded as <stage>/job-<id>.refused.json, so no stale record can be read.
# The hard cap (§7, binding ruling 2): --time=0:50:00 is in this script, and the job refuses unless Slurm's TimeLimit for
# it is at most that (3,000 s = 0.833 node-h on one exclusive node, under 0.9) and its name is in the pfb_ family.
# The order: the prep step (G0, before any fit) writes <root>/edges and must reproduce the smoke's INDEX.json; round 1
# runs A0R, E1/E2/E3's bases and E1's jitters 1-4 on 8 lanes; then, in this order: a task's exit 4 (an input digest) is
# INPUTS CHANGED, exit 5 (a changed grid membership) is RUN REFUSED, any other failure is an operational interruption
# (INCOMPLETE); only a clean round reaches the round-1 gate (G4, G1, bindings, J, G2, G3, identity) and the wall
# projection (3 x round 1 <= 2,900 s); rounds 2-3 (E1's jitters 5-20) are classified the same way.
# job-status.json starts as "the job did not finish", so a time-limit kill reads INCOMPLETE; a deliberate stop after a
# round-1 gate failure is recorded as that, not as an interruption (§5.2).
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; STAGE="${3:?stage}"; OUT="${4:?root}"
ROOT_DECLARED=/pscratch/sd/j/josephrb/pfb-20261117
JOB="${SLURM_JOB_ID:-local}"
refuse() { mkdir -p "$STAGE"; echo "{\"refused\": \"$1\", \"job\": \"$JOB\"}" > "$STAGE/job-$JOB.refused.json"; echo "[pfb] RUN REFUSED: $1" >&2; exit 2; }
if [ -z "$PFB_LOCAL_TEST" ]; then
    [ "$OUT" = "$ROOT_DECLARED" ] || refuse "the root $OUT is not the declared $ROOT_DECLARED"
    case "$SLURM_JOB_NAME" in pfb_*) ;; *) refuse "the job name '$SLURM_JOB_NAME' is not in the pfb_ family" ;; esac
fi
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[pfb] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
[ -d "$STAGE/a0-refs" ] && [ -f "$STAGE/assess_receipt.json" ] && [ -f "$STAGE/smoke-edges/INDEX.json" ] \
    || refuse "the stage $STAGE lacks a0-refs/, assess_receipt.json or smoke-edges/INDEX.json"
[ ! -e "$OUT" ] || refuse "the root is not fresh: $OUT exists"
mkdir -p "$OUT" || refuse "cannot create $OUT"
ST="$OUT/job-status.json"
status() { python3 -c 'import json, sys; json.dump(json.loads(sys.argv[2]), open(sys.argv[1], "w"), indent=1)' "$ST" "$1"; }
L="$OUT/logs"; mkdir -p "$L/tasks"
ENVLOG="$L/env.log"
source "$D/setup_salloc_env.sh" > "$ENVLOG" 2>&1
status "{\"interrupted\": \"the job did not finish (time limit or interruption)\", \"job\": \"$JOB\", \"pin\": \"$PIN\"}"
if [ -z "$PFB_LOCAL_TEST" ]; then
    TL=$(scontrol show job "$JOB" 2>/dev/null | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
    python3 "$D/nd-unfolding/fb_pilot_analyze.py" slurm-limit --timelimit "$TL" \
        || { status "{\"refused\": \"Slurm's TimeLimit '$TL' exceeds --time=0:50:00 (the 0.9 node-h cap)\", \"job\": \"$JOB\"}"; exit 2; }
fi
python3 -c "import lightgbm, numpy, sys; print('lightgbm', lightgbm.__version__, 'numpy', numpy.__version__, 'python', sys.version.split()[0]); assert lightgbm.__version__ == '4.6.0'" >> "$ENVLOG" 2>&1 \
    || { status "{\"interrupted\": \"the environment's LightGBM is not 4.6.0\", \"job\": \"$JOB\"}"; exit 7; }
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
    6) status "{\"prep\": \"INFEASIBLE\", \"prep_detail\": $(cat "$OUT/edges.g0.json" 2>/dev/null || echo null), \"job\": \"$JOB\"}"
       echo "[pfb] INFEASIBLE (G0)"; exit 0 ;;
    4) status "{\"inputs_changed\": \"the prep step's input digest check (exit 4)\", \"job\": \"$JOB\"}"; exit 0 ;;
    *) status "{\"interrupted\": \"the prep step exited $rc\", \"job\": \"$JOB\"}"; exit 1 ;;
esac
if ! cmp -s "$OUT/edges/INDEX.json" "$STAGE/smoke-edges/INDEX.json"; then
    status "{\"inputs_changed\": \"the job's edges differ from the login-node smoke's (INDEX.json)\", \"job\": \"$JOB\"}"; exit 0
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
    if [ -n "$bad4" ]; then status "{\"inputs_changed\": \"input digest exit 4 in:$bad4\", \"job\": \"$JOB\"}"; return 1; fi
    if [ -n "$bad5" ]; then status "{\"refused\": \"grid-membership exit 5 in:$bad5\", \"job\": \"$JOB\"}"; return 1; fi
    if [ -n "$bad" ]; then status "{\"interrupted\": \"tasks failed:$bad\", \"task_failures\": \"$bad\", \"job\": \"$JOB\"}"; return 1; fi
    return 0
}
sums() { ( cd "$OUT" && find runs edges -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"; }
R1="A0R E1_- E2_- E3_- E1_1 E1_2 E1_3 E1_4"
t0=$(date +%s)
printf '%s\n' $R1 | run_round
w1=$(( $(date +%s) - t0 ))
echo "[pfb] round 1 wall ${w1}s"
classify $R1 || { sums; exit 0; }
python3 "$D/nd-unfolding/fb_pilot_analyze.py" round1 --runs "$OUT" --stage "$STAGE" --deploy "$D" --pin "$PIN" \
    > "$L/round1.json" 2>> "$L/round1.err"
g=$?
if [ "$g" -ne 0 ]; then
    status "{\"round1\": \"STOP\", \"round1_detail\": $(cat "$L/round1.json" 2>/dev/null || echo null), \"round1_wall_s\": $w1, \"job\": \"$JOB\"}"
    echo "[pfb] round-1 gate STOP (deliberate; the gate names the outcome)"; sums; exit 0
fi
if [ $(( 3 * w1 )) -gt 2900 ]; then
    status "{\"interrupted\": \"the round-1 wall projection: 3 x ${w1}s > 2,900 s\", \"round1\": \"PASS\", \"job\": \"$JOB\"}"
    echo "[pfb] INCOMPLETE: the wall projection stops the run"; sums; exit 0
fi
R23=$(printf 'E1_%s ' {5..20})
printf '%s\n' $R23 | run_round
sums
classify $R23 || exit 0
status "{\"round1\": \"PASS\", \"round1_wall_s\": $w1, \"job\": \"$JOB\", \"pin\": \"$PIN\", \"done\": true}"
echo "{\"job\": \"$JOB\", \"pin\": \"$PIN\", \"end\": \"$(date -u +%FT%TZ)\"}" > "$L/DONE"
echo "[pfb] DONE end=$(date -u +%FT%TZ)"
