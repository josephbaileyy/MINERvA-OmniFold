#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# E96-DATA (state/measurement-paper/5d-community-20261024/fd/e96-data-20261110/E96D-DECLARATION.md, draft), adapted
# from nd-unfolding/sbatch_ens1.sh: the same lanes, teardown guard, receipts and refusals; one queue per stage.
#   dry:   <OUT>/dry.tsv   (the control and k = 1; submit with --job-name=e96data_dry --time=0:30:00)
#   full:  <OUT>/full.tsv  (F64 and k = 2..96; --job-name=e96data_full --time=3:00:00; only after the director accepts
#                           the dry run's projection, and never without the dry DONE at this pin)
# Nothing runs before the LL5D readout and the director's go. The cap binds through Slurm's --time on one exclusive
# node. A failed task exits 255, so xargs starts nothing further. Only a run whose every task ended with rc 0 writes its
# DONE receipt. Writes only under <OUT>; refuses if this run's log exists (no resume without the director). Runs only
# from a clean deploy at <pin>.
set -o pipefail   # NOT set -u
MODE="${1:?dry|full}"
D="${2:?deploy}"; PIN="${3:?pin}"; OUT="${4:?out}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[e96data] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
case "$MODE" in
    dry)  Q="$OUT/dry.tsv";  L="$OUT/log-dry" ;;
    full) Q="$OUT/full.tsv"; L="$OUT/log-full" ;;
    *)    echo "[e96data] refusing: mode $MODE" >&2; exit 2 ;;
esac
P=8
[ -s "$Q" ] || { echo "[e96data] refusing: no queue $Q" >&2; exit 2; }
[ ! -e "$L" ] || { echo "[e96data] refusing: $L exists" >&2; exit 2; }
if [ "$MODE" = full ]; then  # checked before anything is written, so a refusal leaves no trace
    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/FAILED" ] || { echo "[e96data] refusing: no DONE receipt from the dry run" >&2; exit 2; }
    dry_pin=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("pin", ""))' "$OUT/log-dry/DONE" 2>/dev/null)
    [ "$dry_pin" = "$PIN" ] || { echo "[e96data] refusing: the dry run ran at pin '$dry_pin', not $PIN" >&2; exit 2; }
fi
mkdir -p "$L/tasks"
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
python3 -c "import lightgbm, scipy, numpy, sys; print('lightgbm', lightgbm.__version__, 'numpy', numpy.__version__, 'python', sys.version.split()[0])" >> "$L/env.log" 2>&1 \
    || { echo "[e96data] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
echo "[e96data] mode=$MODE job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=$P start=$(date -u +%FT%TZ)"
TIME_BIN="${E96D_TIME_BIN:-/usr/bin/time}"  # GNU time on the cluster; the local test substitutes a stand-in
export D Q L TIME_BIN OUT
# The teardown guard, ENS1's unchanged (RS1-BINDING-2 addendum A1, the director's ruling 5 for ENS1). A task exits 1, never 255, so xargs
# keeps launching. A task whose process exits non-zero AFTER every product it declares exists (``<script> expect``) is a
# teardown crash: <id>.teardown records the exit code, its products move to runs-teardown/<id>/, and the task is
# recomputed once; the re-run's products are used and a bitwise comparison of xsec_flat and xtrue_flat is recorded. A
# failure before every product exists, or a second crash, is a failure (<id>.failed).
grep -v '^#' "$Q" | cut -f1 | xargs -P "$P" -I{} bash -c '
    id="$1"
    cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F "\t" -v id="$id" \
        '"'"'$1 == id { for (i = 1; i <= NF; i++) print $i }'"'"' "$Q")
    [ "${#cols[@]}" -gt 3 ] || { echo "malformed queue line" > "$L/$id.failed"; exit 1; }
    run_task() { ( cd "$D" && "$TIME_BIN" -v -o "$L/tasks/$id.time$1" python3 "nd-unfolding/${cols[2]}" "${cols[@]:3}" ) \
        >> "$L/tasks/$id.log" 2>&1; }
    python3 -c "import time; print(time.time())" > "$L/$id.start"
    run_task ""; rc=$?
    if [ "$rc" -ne 0 ]; then
        files=(); while IFS= read -r f; do [ -n "$f" ] && files+=("$f"); done < <(cd "$D" && \
            python3 "nd-unfolding/${cols[2]}" expect "${cols[@]:3}" 2>> "$L/tasks/$id.log")
        all=1; [ "${#files[@]}" -gt 0 ] || all=0
        for f in "${files[@]}"; do [ -e "$f" ] || all=0; done
        if [ "$all" -ne 1 ]; then echo "rc=$rc before every product was written" > "$L/$id.failed"; exit 1; fi
        echo "exit=$rc after all ${#files[@]} products were written" > "$L/$id.teardown"
        T="$OUT/runs-teardown/$id"; mkdir -p "$T"
        for f in "${files[@]}"; do mv "$f" "$T/" || { echo "could not move $f aside" > "$L/$id.failed"; exit 1; }; done
        run_task ".rerun"; rc=$?
        if [ "$rc" -ne 0 ]; then echo "rc=$rc on the re-run after a teardown crash" > "$L/$id.failed"; exit 1; fi
        for f in "${files[@]}"; do
            python3 -c "import sys, numpy as np
a, b = np.load(sys.argv[1]), np.load(sys.argv[2])
same = all(np.array_equal(a[k], b[k]) for k in (\"xsec_flat\", \"xtrue_flat\") if k in a.files or k in b.files)
print(sys.argv[2].rsplit(\"/\", 1)[-1], \"bitwise_identical\" if same else \"DIFFERS\")" "$T/${f##*/}" "$f" >> "$L/$id.teardown" \
                || echo "${f##*/} comparison failed" >> "$L/$id.teardown"
        done
    fi
    python3 -c "import time; print(time.time())" > "$L/$id.end.tmp" && mv "$L/$id.end.tmp" "$L/$id.end"' _ {}
rc=$?
echo "[e96data] queue rc=$rc end=$(date -u +%FT%TZ)"
# Pinned whatever the outcome: every complete product under runs/ at this moment
( cd "$OUT" && find runs -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
failed=$(cd "$L" && ls *.failed 2>/dev/null | sed 's/\.failed$//' | tr '\n' ' ')
teardown=$(cd "$L" && ls *.teardown 2>/dev/null | sed 's/\.teardown$//' | tr '\n' ' ')
[ -z "$failed" ] && [ "$rc" -eq 0 ] || { echo "rc=$rc failed=$failed" > "$L/FAILED"; echo "[e96data] STOP: failed tasks: $failed (rc=$rc)" >&2; exit 1; }
n_q=$(grep -vc '^#' "$Q"); n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq "$n_q" ] || { echo "ended=$n_end of $n_q" > "$L/FAILED"; echo "[e96data] STOP: $n_end of $n_q tasks ended" >&2; exit 1; }
echo "{\"mode\": \"$MODE\", \"tasks\": $n_q, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\", \"teardown\": \"$teardown\"}" > "$L/DONE"
