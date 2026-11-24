#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# S2R (state/measurement-paper/5d-community-20261024/fd/s2r-20261124/S2R-DECLARATION.md). One node, 6 lanes x 32
# threads, CPU only, one job, on the director's go.
#   sbatch --job-name=s2r_run --time=<s2r_probe.py limit> sbatch_s2r.sh <deploy> <pin> <OUT>
# Refuses before writing anything unless: the deploy is <pin> and clean; the job is s2r_run with a Slurm TimeLimit
# within the declared limit (read from sacct); <OUT>/fence.txt names the fenced job-name prefixes and none is
# non-terminal in sacct; <OUT>/log, <OUT>/stage and <OUT>/runs do not exist. Then: the manifest from the deploy's
# committed receipts; staging through O_NOATIME (each copy refused unless it is its pin); the queue; six tasks through
# the gate; SHA256SUMS; C-PAIR / C-X / C-ONE; the read. DONE only if every step passed. A refused gate or a failed
# task exits 255, so xargs starts nothing further. Writes only under <OUT>. Job states from sacct only.
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"
PY="$D/nd-unfolding/s2r/s2r_probe.py"
RD="$D/nd-unfolding/s2r/s2r_read.py"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[s2r] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
source "$D/setup_salloc_env.sh" > /dev/null 2>&1   # FD-PRR A1: the environment before any python3 call
LIMIT=$(python3 "$PY" limit) || { echo "[s2r] refusing: no declared limit" >&2; exit 2; }
if [ -n "$SLURM_JOB_ID" ]; then
    NAME="$SLURM_JOB_NAME"; TL=$(sacct -X -n -P -j "$SLURM_JOB_ID" -o Timelimit 2>/dev/null | head -n 1)
elif [ -n "$S2R_SMOKE" ]; then
    NAME="${S2R_NAME:-s2r_run}"; TL="${S2R_TIMELIMIT:-$LIMIT}"
else
    echo "[s2r] refusing: not inside a Slurm job" >&2; exit 2
fi
[ "$NAME" = "s2r_run" ] || { echo "[s2r] refusing: job name $NAME is not s2r_run" >&2; exit 2; }
python3 - "$TL" "$LIMIT" <<'EOF'
import sys
def sec(t):
    d, dash, rest = t.partition("-")
    f = rest.split(":") if dash else t.split(":")
    if (dash and not d.isdigit()) or not all(x.isdigit() for x in f) or len(f) > 3:
        raise ValueError(t)
    f = [int(x) for x in f]
    if dash:
        h, m, s = f + [0] * (3 - len(f))
        return int(d) * 86400 + h * 3600 + m * 60 + s
    if len(f) == 1:
        return f[0] * 60
    if len(f) == 2:
        return f[0] * 60 + f[1]
    return f[0] * 3600 + f[1] * 60 + f[2]
try:
    tl, lim = sec(sys.argv[1].strip()), sec(sys.argv[2].strip())
except ValueError:
    sys.exit(3)
sys.exit(0 if tl <= lim else 4)
EOF
trc=$?
[ "$trc" -ne 3 ] || { echo "[s2r] refusing: could not read the Slurm TimeLimit '$TL'" >&2; exit 2; }
[ "$trc" -ne 4 ] || { echo "[s2r] refusing: Slurm TimeLimit $TL exceeds the declared $LIMIT" >&2; exit 2; }
[ "$trc" -eq 0 ] || { echo "[s2r] refusing: the TimeLimit check failed (rc $trc)" >&2; exit 2; }
LIMIT_H=$(python3 -c "import sys; h,m,s=(int(x) for x in sys.argv[1].split(':')); print(h+m/60+s/3600)" "$LIMIT")
L="$OUT/log"
for p in "$L" "$OUT/stage" "$OUT/runs"; do
    [ ! -e "$p" ] || { echo "[s2r] refusing: $p exists" >&2; exit 2; }
done
# The director's go names the fenced job-name prefixes; nothing stages, writes or runs while any of them is
# non-terminal in sacct. Fails closed: no fence file, an empty one, or a sacct that cannot answer refuses.
fence_check() {
    [ -s "$OUT/fence.txt" ] || { echo "[s2r] refusing: no $OUT/fence.txt naming the fenced job-name prefixes" >&2; exit 2; }
    rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || { echo "[s2r] refusing: sacct failed: $rows" >&2; exit 2; }
    while IFS= read -r pre; do
        [ -n "$pre" ] || continue
        hit=$(printf '%s\n' "$rows" | awk -F'|' -v p="$pre" '
            NF >= 3 { st = $3; sub(/ by [0-9]+$/, "", st)
                      if (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) next
                      if (index($2, p) == 1) print }')
        [ -z "$hit" ] || { echo "[s2r] refusing: fenced jobs ($pre*) are not terminal: $hit" >&2; exit 2; }
    done < "$OUT/fence.txt"
}
fence_check
if [ -z "$SLURM_JOB_ID" ] && [ -n "$S2R_SMOKE" ]; then echo "[s2r] smoke: past the fence, nothing staged or run" >&2; exit 0; fi
mkdir -p "$L/tasks"
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
python3 -c "import lightgbm, scipy, numpy" >> "$L/env.log" 2>&1 || { echo "[s2r] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
( cd "$D" && python3 "$PY" manifest --out "$OUT/manifest.json" ) > "$L/manifest.log" 2>&1 \
    || { echo "manifest failed" > "$L/STOP"; echo "[s2r] STOP: the manifest refused; see $L/manifest.log" >&2; exit 1; }
( cd "$D" && python3 "$PY" stage --manifest "$OUT/manifest.json" --dest "$OUT/stage" --out "$OUT/stage.json" ) \
    > "$L/stage.log" 2>&1 || { echo "stage refused" > "$L/STOP"; echo "[s2r] STOP: staging refused; see $L/stage.log" >&2; exit 1; }
( cd "$D" && python3 "$PY" tasks --out "$OUT/queues" --stage-dir "$OUT/stage" --runs "$OUT/runs" --stage-json "$OUT/stage.json" ) \
    > "$L/tasks.log" 2>&1 || { echo "tasks failed" > "$L/STOP"; echo "[s2r] STOP: the queue was not written" >&2; exit 1; }
Q="$OUT/queues/run.tsv"
[ "$(grep -vc '^#' "$Q")" -eq 6 ] || { echo "queue count" > "$L/STOP"; echo "[s2r] STOP: the queue does not hold six tasks" >&2; exit 1; }
T0=$(python3 -c "import time; print(time.time())")
echo "[s2r] job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=6 limit=$LIMIT start=$(date -u +%FT%TZ)"
TIME_BIN="${S2R_TIME_BIN:-/usr/bin/time}"
export D Q L T0 LIMIT_H TIME_BIN PY
grep -v '^#' "$Q" | cut -f1 | xargs -P 6 -I{} bash -c '
    id="$1"
    python3 "$PY" gate --task "$id" --queue "$Q" --log "$L" --t0 "$T0" --limit-h "$LIMIT_H"
    g=$?
    [ "$g" -eq 4 ] && exit 0
    [ "$g" -eq 0 ] || exit 255
    cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F "\t" -v id="$id" \
        '"'"'$1 == id { for (i = 1; i <= NF; i++) print $i }'"'"' "$Q")
    [ "${#cols[@]}" -gt 4 ] || exit 255
    ( cd "$D" && "$TIME_BIN" -v -o "$L/tasks/$id.time" python3 "nd-unfolding/${cols[3]}" "${cols[@]:4}" ) \
        > "$L/tasks/$id.log" 2>&1 || exit 255
    python3 -c "import time; print(time.time())" > "$L/$id.end.tmp" && mv "$L/$id.end.tmp" "$L/$id.end"' _ {}
rc=$?
echo "[s2r] queue rc=$rc end=$(date -u +%FT%TZ)"
( cd "$OUT" && find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 -r sha256sum ) > "$L/SHA256SUMS"
[ -e "$L/STOP" ] && { echo "[s2r] STOP: $(cat "$L/STOP")" >&2; exit 1; }
[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[s2r] STOP: a task failed (rc=$rc)" >&2; exit 1; }
n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq 6 ] || { echo "ended=$n_end of 6" > "$L/FAILED"; echo "[s2r] STOP: $n_end of 6 tasks ended" >&2; exit 1; }
( cd "$D" && python3 "$PY" pair --stage "$OUT/stage.json" --runs "$OUT/runs" --out "$L/pair.json" ) > "$L/pair.log" 2>&1
pc=$?
[ "$pc" -eq 0 ] || { echo "pair rc=$pc" > "$L/STOP"; echo "[s2r] STOP: C-PAIR, C-X or C-ONE did not pass (rc=$pc)" >&2; exit 1; }
( cd "$D" && python3 "$RD" --runs "$OUT/runs" --stage "$OUT/stage.json" --pair "$L/pair.json" --out "$OUT/read" ) > "$L/read.log" 2>&1
rdc=$?
[ "$rdc" -eq 0 ] || { echo "read rc=$rdc" > "$L/STOP"; echo "[s2r] STOP: the read refused (rc=$rdc)" >&2; exit 1; }
echo "{\"tasks\": 6, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\"}" > "$L/DONE"
echo "[s2r] done"
