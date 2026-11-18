#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# PILOT-FB's one job (PILOT-FB-DECLARATION.md rev 3 §4, §5.1, §7; PILOT-FB-BINDING-1). Submit with --time=0:50:00.
# Usage: sbatch_pfb.sh <deploy> <pin> <root>. <root> holds a0-refs/ (the connect's O_NOATIME copies of RS1's A0
# products) and nothing else; runs/, edges/ and logs/ must not exist (a fresh root, §4).
# The order: the prep step (G0, before any fit) writes edges/; round 1 runs A0R, E1/E2/E3's bases and E1's jitters 1-4 on
# 8 lanes; the round-1 gate (fb_pilot_analyze.py round1: G4, G1, J, G2, G3, identity) and the wall projection
# (3 x round 1 <= 2,900 s) decide whether rounds 2-3 (E1's jitters 5-20) run.
# job-status.json starts as "the job did not finish", so a time-limit kill or an interruption reads INCOMPLETE; a
# deliberate stop after a round-1 gate failure is recorded as that, not as an interruption (§5.2).
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?root}"
ST="$OUT/job-status.json"
status() { python3 -c 'import json, sys; json.dump(json.loads(sys.argv[2]), open(sys.argv[1], "w"), indent=1)' "$ST" "$1"; }
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[pfb] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
[ -d "$OUT/a0-refs" ] || { echo "[pfb] refusing: no $OUT/a0-refs" >&2; exit 2; }
for x in runs edges logs job-status.json; do
    if [ -e "$OUT/$x" ]; then
        echo "{\"refused\": \"the root is not fresh: $x exists\", \"job\": \"$SLURM_JOB_ID\"}" > "$OUT/job-status.refused.json"
        echo "[pfb] RUN REFUSED: $OUT/$x exists" >&2; exit 2
    fi
done
L="$OUT/logs"; mkdir -p "$L/tasks"
ENVLOG="$L/env.log"
source "$D/setup_salloc_env.sh" > "$ENVLOG" 2>&1
status "{\"interrupted\": \"the job did not finish (time limit or interruption)\", \"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\"}"
python3 -c "import lightgbm, numpy, sys; print('lightgbm', lightgbm.__version__, 'numpy', numpy.__version__, 'python', sys.version.split()[0]); assert lightgbm.__version__ == '4.6.0'" >> "$ENVLOG" 2>&1 \
    || { status "{\"refused\": \"the environment's LightGBM is not 4.6.0\", \"job\": \"$SLURM_JOB_ID\"}"; exit 7; }
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
RATIO="$D/$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import rounding_mechanism_probe as r; print(r.STABILITY["ratio"])' "$D/nd-unfolding")"
COMMON=(--npz "$NPZ" --bkg "$BKG" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f
        --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 --config R --iters 5
        --threads 32 --construction pseudo --truth eavail_shape --amplitude 1.0 --eavail-ratio "$RATIO" --pseudo-seed 990000)
SHM="/dev/shm/pfb-$SLURM_JOB_ID"; mkdir -p "$SHM"; trap 'rm -rf "$SHM"' EXIT
echo "[pfb] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN start=$(date -u +%FT%TZ)"
# the prep step: G0, before any fit
( cd "$D" && python3 nd-unfolding/fb_pilot_probe.py prep --edges-out "$OUT/edges" -- "${COMMON[@]}" --pairs=-:- \
    --tag pfb_prep --out "$OUT/prep-unused" ) > "$L/prep.log" 2>&1
rc=$?
if [ "$rc" -eq 6 ]; then
    status "{\"prep\": \"INFEASIBLE\", \"prep_detail\": $(python3 -c 'import json, sys; print(json.dumps(open(sys.argv[1]).read()[-2000:]))' "$L/prep.log"), \"job\": \"$SLURM_JOB_ID\"}"
    echo "[pfb] INFEASIBLE (G0)"; exit 0
elif [ "$rc" -ne 0 ]; then
    echo "[pfb] STOP: the prep step exited $rc" >&2; exit 1   # job-status.json keeps "did not finish"
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
run_round() {  # ids on stdin; 8 lanes
    xargs -P 8 -I{} bash -c '
        id="$1"; COMMON=($COMMON_STR)
        argv=(); while IFS= read -r x; do argv+=("$x"); done < <(task_cmd "$id")
        python3 -c "import time; print(time.time())" > "$L/$id.start"
        ( cd "$D" && /usr/bin/time -v -o "$L/tasks/$id.time" python3 "${argv[@]}" ) >> "$L/tasks/$id.log" 2>&1
        rc=$?
        [ "$rc" -eq 0 ] || echo "rc=$rc" > "$L/$id.failed"
        python3 -c "import time; print(time.time())" > "$L/$id.end"
        exit 0' _ {}
}
R1="A0R E1_- E2_- E3_- E1_1 E1_2 E1_3 E1_4"
t0=$(date +%s)
printf '%s\n' $R1 | run_round
w1=$(( $(date +%s) - t0 ))
echo "[pfb] round 1 wall ${w1}s"
python3 "$D/nd-unfolding/fb_pilot_analyze.py" round1 --runs "$OUT" --a0-refs "$OUT/a0-refs" > "$L/round1.json" 2>> "$L/round1.err"
g=$?
if [ "$g" -ne 0 ]; then
    status "{\"round1\": \"STOP\", \"round1_detail\": $(cat "$L/round1.json" 2>/dev/null || echo null), \"round1_wall_s\": $w1, \"job\": \"$SLURM_JOB_ID\"}"
    echo "[pfb] round-1 gate STOP (deliberate; the gate names the outcome)"
    ( cd "$OUT" && find runs edges -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
    exit 0
fi
if [ $(( 3 * w1 )) -gt 2900 ]; then
    status "{\"interrupted\": \"the round-1 wall projection: 3 x ${w1}s > 2,900 s\", \"round1\": \"PASS\", \"job\": \"$SLURM_JOB_ID\"}"
    echo "[pfb] INCOMPLETE: the wall projection stops the run"; exit 0
fi
printf '%s\n' E1_{5..20} | run_round
( cd "$OUT" && find runs edges -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
failed=$(cd "$L" && ls *.failed 2>/dev/null | sed 's/\.failed$//' | tr '\n' ' ')
status "{\"round1\": \"PASS\", \"round1_wall_s\": $w1, \"failed_tasks\": \"$failed\", \"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\", \"done\": true}"
echo "{\"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\", \"failed\": \"$failed\", \"end\": \"$(date -u +%FT%TZ)\"}" > "$L/DONE"
echo "[pfb] DONE end=$(date -u +%FT%TZ) failed=[$failed]"
