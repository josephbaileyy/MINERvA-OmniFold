#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# RS1 (state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/RS1-DECLARATION.md §7). One node.
#   dry:  the nine one-unfold DRY tasks on 8 lanes (submit with --time=0:45:00).
#   full: the whole queue on 8 lanes (submit with --time=7:15:00, and only after the director accepts the dry run's
#         projection). The dry run's ends are copied in first, so its tasks are skipped and its products stand.
# The cap binds through Slurm's --time on one exclusive node. A failed task exits 255, so xargs starts nothing further.
# Only a run whose every task ended with rc 0 writes its DONE receipt; the full run refuses without the dry run's.
# Writes only under <OUT>; refuses if this mode's log exists (no resume without the director). Runs only from a clean
# deploy at <pin>.
set -o pipefail   # NOT set -u
MODE="${1:?dry|full}"; D="${2:?deploy}"; PIN="${3:?pin}"; OUT="${4:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[rs1] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
case "$MODE" in
    dry)  Q="$OUT/dry.tsv" ;;
    full) Q="$OUT/queue.tsv" ;;
    *)    echo "[rs1] refusing: mode $MODE" >&2; exit 2 ;;
esac
P=8
[ -s "$Q" ] || { echo "[rs1] refusing: no queue $Q" >&2; exit 2; }
L="$OUT/log-$MODE"
[ ! -e "$L" ] || { echo "[rs1] refusing: $L exists" >&2; exit 2; }
if [ "$MODE" = full ]; then  # checked before anything is written, so a refusal leaves no trace
    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/FAILED" ] || { echo "[rs1] refusing: no DONE receipt from the dry run" >&2; exit 2; }
    # RS1-C1: the dry products carry into the full run only at the same deploy pin
    dry_pin=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("pin", ""))' "$OUT/log-dry/DONE" 2>/dev/null)
    [ "$dry_pin" = "$PIN" ] || { echo "[rs1] refusing: the dry run ran at pin '$dry_pin', not $PIN" >&2; exit 2; }
    for id in $(grep -v '^#' "$OUT/dry.tsv" | cut -f1); do
        [ -e "$OUT/log-dry/$id.end" ] || { echo "[rs1] refusing: dry-run task $id never ended" >&2; exit 2; }
    done
fi
mkdir -p "$L/tasks"
if [ "$MODE" = full ]; then
    cp "$OUT"/log-dry/*.end "$L/" || { echo "[rs1] refusing: dry-run ends missing" >&2; exit 2; }
fi
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
python3 -c "import lightgbm, scipy, numpy, sys; print('lightgbm', lightgbm.__version__, 'numpy', numpy.__version__, 'python', sys.version.split()[0])" >> "$L/env.log" 2>&1 \
    || { echo "[rs1] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
echo "[rs1] mode=$MODE job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=$P start=$(date -u +%FT%TZ)"
TIME_BIN="${RS1_TIME_BIN:-/usr/bin/time}"  # GNU time on the cluster; the local test substitutes a stand-in
export D Q L TIME_BIN
grep -v '^#' "$Q" | cut -f1 | xargs -P "$P" -I{} bash -c '
    id="$1"
    [ -e "$L/$id.end" ] && exit 0      # ended in the dry run: its product stands
    cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F "\t" -v id="$id" \
        '"'"'$1 == id { for (i = 1; i <= NF; i++) print $i }'"'"' "$Q")
    [ "${#cols[@]}" -gt 3 ] || exit 255
    python3 -c "import time; print(time.time())" > "$L/$id.start"
    ( cd "$D" && "$TIME_BIN" -v -o "$L/tasks/$id.time" python3 "nd-unfolding/${cols[2]}" "${cols[@]:3}" ) \
        > "$L/tasks/$id.log" 2>&1 || exit 255
    python3 -c "import time; print(time.time())" > "$L/$id.end.tmp" && mv "$L/$id.end.tmp" "$L/$id.end"' _ {}
rc=$?
echo "[rs1] queue rc=$rc end=$(date -u +%FT%TZ)"
# Pinned whatever the outcome: products and their trace sidecars
( cd "$OUT" && find runs -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[rs1] STOP: a task failed (rc=$rc)" >&2; exit 1; }
n_q=$(grep -vc '^#' "$Q"); n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq "$n_q" ] || { echo "ended=$n_end of $n_q" > "$L/FAILED"; echo "[rs1] STOP: $n_end of $n_q tasks ended" >&2; exit 1; }
echo "{\"mode\": \"$MODE\", \"tasks\": $n_q, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\"}" > "$L/DONE"
