#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# RS1 full run, resumed under RS1-BINDING-2 addendum A1, in a fresh root staged by rs1_a1_plan.py (submit with
# --time=4:30:00). It runs the plan's todo tasks only, on 8 lanes, with the teardown guard; sbatch_rs1.sh and the bound
# modules are unchanged. Usage: sbatch_rs1_a1.sh <deploy> <pin> <root> <a1-tools> <a1-pin>.
# The tasks run from <deploy> at <pin>, the bound RS1 code (the dry run's pin, so RS1-C1's one-code rule and the bound
# analysis's dry = full pin rule hold); rs1_a1_plan.py comes from <a1-tools>, a clean clone at the addendum's <a1-pin>.
# sbatch runs a copy of this script, so neither path is derived from its own location.
# The guard: a task exits 1, never 255, so xargs keeps launching. A task whose process exits non-zero AFTER every product
# and sidecar it declares exists (``rs1_a1_plan.py expect``) is a teardown crash: <id>.teardown records the exit code,
# its files move to runs-teardown/<id>/, and the task is recomputed once; the re-run's files are used and a bitwise
# comparison of xsec_flat and xtrue_flat is recorded. A failure before every file exists, or a second crash, is a
# failure (<id>.failed). Only a run in which every queue task is done (staged and verified) or ended writes DONE.
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?root}"; A1="${4:?a1 tools}"; A1PIN="${5:?a1 pin}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[rs1-a1] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
a1_sha=$(git -C "$A1" rev-parse HEAD 2>/dev/null)
a1_dirty=$(git -C "$A1" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$a1_sha" != "$A1PIN" ] || [ "$a1_dirty" -ne 0 ] || [ ! -f "$A1/nd-unfolding/rs1_a1_plan.py" ]; then
    echo "[rs1-a1] refusing: a1 tools HEAD=$a1_sha (pinned $A1PIN), $a1_dirty modified tracked files" >&2; exit 2
fi
PLANPY="$A1/nd-unfolding/rs1_a1_plan.py"
P=8
Q="$OUT/queue.tsv"; PLAN="$OUT/plan.tsv"; L="$OUT/log-full"
[ -s "$Q" ] && [ -s "$PLAN" ] || { echo "[rs1-a1] refusing: no queue or plan in $OUT" >&2; exit 2; }
[ ! -e "$L" ] || { echo "[rs1-a1] refusing: $L exists" >&2; exit 2; }
[ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/FAILED" ] || { echo "[rs1-a1] refusing: no DONE receipt from the dry run" >&2; exit 2; }
dry_pin=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("pin", ""))' "$OUT/log-dry/DONE" 2>/dev/null)
[ "$dry_pin" = "$PIN" ] || { echo "[rs1-a1] refusing: the dry run ran at pin '$dry_pin', not $PIN" >&2; exit 2; }
n_q=$(grep -vc '^#' "$Q"); n_p=$(grep -vc '^#' "$PLAN")
[ "$n_q" -eq "$n_p" ] || { echo "[rs1-a1] refusing: the plan has $n_p tasks, the queue $n_q" >&2; exit 2; }
# Every rs1_a1_plan.py call runs under the job's own environment, never under the system python3, which is 3.6 on
# the cluster (A1 connect 1 stopped on it, 2026-11-07). The source's log is moved into $L once $L exists.
ENVLOG=$(mktemp); trap 'rm -f "$ENVLOG"' EXIT
source "$D/setup_salloc_env.sh" > "$ENVLOG" 2>&1
python3 "$PLANPY" verify --root "$OUT" > /dev/null \
    || { echo "[rs1-a1] refusing: a staged file no longer verifies" >&2; exit 2; }
mkdir -p "$L/tasks"
mv "$ENVLOG" "$L/env.log"
python3 -c "import lightgbm, scipy, numpy, sys; print('lightgbm', lightgbm.__version__, 'numpy', numpy.__version__, 'python', sys.version.split()[0])" >> "$L/env.log" 2>&1 \
    || { echo "[rs1-a1] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
awk -F "\t" '!/^#/ && $2 == "todo" {print $1}' "$PLAN" > "$L/todo.txt"
echo "[rs1-a1] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=$P todo=$(wc -l < "$L/todo.txt") start=$(date -u +%FT%TZ)"
TIME_BIN="${RS1_TIME_BIN:-/usr/bin/time}"  # GNU time on the cluster; the local test substitutes a stand-in
export D Q L TIME_BIN OUT PLANPY
xargs -P "$P" -I{} bash -c '
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
            python3 "$PLANPY" expect "${cols[@]:3}" 2>> "$L/tasks/$id.log")
        all=1; [ "${#files[@]}" -gt 0 ] || all=0
        for f in "${files[@]}"; do [ -e "$f" ] || all=0; done
        if [ "$all" -ne 1 ]; then echo "rc=$rc before every product was written" > "$L/$id.failed"; exit 1; fi
        echo "exit=$rc after all ${#files[@]} files were written" > "$L/$id.teardown"
        T="$OUT/runs-teardown/$id"; mkdir -p "$T"
        for f in "${files[@]}"; do mv "$f" "$T/" || { echo "could not move $f aside" > "$L/$id.failed"; exit 1; }; done
        run_task ".rerun"; rc=$?
        if [ "$rc" -ne 0 ]; then echo "rc=$rc on the re-run after a teardown crash" > "$L/$id.failed"; exit 1; fi
        for f in "${files[@]}"; do
            case "$f" in *.npz) ;; *) continue ;; esac
            python3 -c "import sys, numpy as np
a, b = np.load(sys.argv[1]), np.load(sys.argv[2])
same = all(np.array_equal(a[k], b[k]) for k in (\"xsec_flat\", \"xtrue_flat\") if k in a.files or k in b.files)
print(sys.argv[2].rsplit(\"/\", 1)[-1], \"bitwise_identical\" if same else \"DIFFERS\")" "$T/${f##*/}" "$f" >> "$L/$id.teardown" \
                || echo "${f##*/} comparison failed" >> "$L/$id.teardown"
        done
    fi
    python3 -c "import time; print(time.time())" > "$L/$id.end.tmp" && mv "$L/$id.end.tmp" "$L/$id.end"' _ {} < "$L/todo.txt"
rc=$?
echo "[rs1-a1] queue rc=$rc end=$(date -u +%FT%TZ)"
( cd "$OUT" && find runs -type f ! -name '*.partial*' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
failed=$(cd "$L" && ls *.failed 2>/dev/null | sed 's/\.failed$//' | tr '\n' ' ')
teardown=$(cd "$L" && ls *.teardown 2>/dev/null | sed 's/\.teardown$//' | tr '\n' ' ')
[ -z "$failed" ] && [ "$rc" -eq 0 ] || { echo "rc=$rc failed=$failed" > "$L/FAILED"; echo "[rs1-a1] STOP: failed tasks: $failed (rc=$rc)" >&2; exit 1; }
n_done=$(awk -F "\t" '!/^#/ && $2 == "done" {n++} END {print n + 0}' "$PLAN"); n_ran=0
for id in $(cat "$L/todo.txt"); do [ -e "$L/$id.end" ] && n_ran=$((n_ran + 1)); done
[ $((n_done + n_ran)) -eq "$n_q" ] || { echo "done=$n_done ran=$n_ran of $n_q" > "$L/FAILED"; echo "[rs1-a1] STOP: not every task is done or ended" >&2; exit 1; }
echo "{\"mode\": \"full\", \"addendum\": \"A1\", \"tasks\": $n_q, \"ended\": $n_q, \"staged\": $n_done, \"ran\": $n_ran, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\", \"pin\": \"$PIN\", \"a1_pin\": \"$A1PIN\", \"teardown\": \"$teardown\"}" > "$L/DONE"
