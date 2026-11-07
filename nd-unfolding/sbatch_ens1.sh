#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# ENS1 (state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/ensemble/ENS1-DECLARATION.md §8).
# One node, 8 lanes, one queue file:
#   dry <stage>:        <OUT>/stage<stage>/dry.tsv      (submit with --time=0:45:00)
#   shard <stage> <i>:  <OUT>/stage<stage>/shard<i>.tsv (stage 1 --time=9:00:00, stage 2 --time=7:30:00; only after the
#                       director accepts the dry run's projection, and never without the stage's dry DONE at this pin)
# The cap binds through Slurm's --time on one exclusive node. A failed task exits 255, so xargs starts nothing further.
# Only a run whose every task ended with rc 0 writes its DONE receipt. Writes only under <OUT>; refuses if this run's
# log exists (no resume without the director). Runs only from a clean deploy at <pin>.
set -o pipefail   # NOT set -u
MODE="${1:?dry|shard}"; STAGE="${2:?stage}"
if [ "$MODE" = shard ]; then I="${3:?shard index}"; shift; fi
D="${3:?deploy}"; PIN="${4:?pin}"; OUT="${5:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[ens1] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
case "$STAGE" in 1|2) ;; *) echo "[ens1] refusing: stage $STAGE" >&2; exit 2 ;; esac
SD="$OUT/stage$STAGE"
case "$MODE" in
    dry)   Q="$SD/dry.tsv"; L="$SD/log-dry" ;;
    shard) case "$I" in [0-5]) ;; *) echo "[ens1] refusing: shard $I" >&2; exit 2 ;; esac
           Q="$SD/shard$I.tsv"; L="$SD/log-shard$I" ;;
    *)     echo "[ens1] refusing: mode $MODE" >&2; exit 2 ;;
esac
P=8
[ -s "$Q" ] || { echo "[ens1] refusing: no queue $Q" >&2; exit 2; }
[ ! -e "$L" ] || { echo "[ens1] refusing: $L exists" >&2; exit 2; }
if [ "$MODE" = shard ]; then  # checked before anything is written, so a refusal leaves no trace
    [ -s "$SD/log-dry/DONE" ] && [ ! -e "$SD/log-dry/FAILED" ] || { echo "[ens1] refusing: no DONE receipt from the stage-$STAGE dry run" >&2; exit 2; }
    dry_pin=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("pin", ""))' "$SD/log-dry/DONE" 2>/dev/null)
    [ "$dry_pin" = "$PIN" ] || { echo "[ens1] refusing: the dry run ran at pin '$dry_pin', not $PIN" >&2; exit 2; }
fi
mkdir -p "$L/tasks"
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
python3 -c "import lightgbm, scipy, numpy, sys; print('lightgbm', lightgbm.__version__, 'numpy', numpy.__version__, 'python', sys.version.split()[0])" >> "$L/env.log" 2>&1 \
    || { echo "[ens1] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
echo "[ens1] mode=$MODE stage=$STAGE shard=${I:--} job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=$P start=$(date -u +%FT%TZ)"
TIME_BIN="${ENS1_TIME_BIN:-/usr/bin/time}"  # GNU time on the cluster; the local test substitutes a stand-in
export D Q L TIME_BIN
grep -v '^#' "$Q" | cut -f1 | xargs -P "$P" -I{} bash -c '
    id="$1"
    cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F "\t" -v id="$id" \
        '"'"'$1 == id { for (i = 1; i <= NF; i++) print $i }'"'"' "$Q")
    [ "${#cols[@]}" -gt 3 ] || exit 255
    python3 -c "import time; print(time.time())" > "$L/$id.start"
    ( cd "$D" && "$TIME_BIN" -v -o "$L/tasks/$id.time" python3 "nd-unfolding/${cols[2]}" "${cols[@]:3}" ) \
        > "$L/tasks/$id.log" 2>&1 || exit 255
    python3 -c "import time; print(time.time())" > "$L/$id.end.tmp" && mv "$L/$id.end.tmp" "$L/$id.end"' _ {}
rc=$?
echo "[ens1] queue rc=$rc end=$(date -u +%FT%TZ)"
# Pinned whatever the outcome: every complete product under runs/ at this moment
( cd "$OUT" && find runs -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[ens1] STOP: a task failed (rc=$rc)" >&2; exit 1; }
n_q=$(grep -vc '^#' "$Q"); n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq "$n_q" ] || { echo "ended=$n_end of $n_q" > "$L/FAILED"; echo "[ens1] STOP: $n_end of $n_q tasks ended" >&2; exit 1; }
echo "{\"mode\": \"$MODE\", \"stage\": $STAGE, \"shard\": \"${I:--}\", \"tasks\": $n_q, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\"}" > "$L/DONE"
