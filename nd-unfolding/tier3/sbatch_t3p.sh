#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# T3 (state/measurement-paper/5d-community-20261024/fd/tier3-20261110/T3-PIPELINE-TESTS-DECLARATION.md §9). One node,
# 8 lanes x 32 threads, CPU only. Runs only after the LL5D readout, on the director's go for each connect.
#   sbatch --job-name=t3p_<mode> --time=<t3p_probe.py limit <mode>> sbatch_t3p.sh <mode> <deploy> <pin> <OUT>
#   dry:   refuses unless <OUT>/fence.txt names the job-name prefixes the director fenced and none of them is queued
#          or running; stages every shared input once through O_NOATIME (t3p_probe.py stage), runs the six A7 GiBUU
#          arms on the primary split, then C-PAIR and C-X (t3p_probe.py pair --job dry). DONE only if both pass.
#   q3, floor: after a clean dry run only; the staged copies are re-verified, the dry run's timings copied in, every
#          task starts through the gate (every arm priced at its dry-run rate), then the job's own C-PAIR and C-X.
# The job's name must be t3p_<mode> and its Slurm TimeLimit at most the declared limit, or it refuses before anything
# is written. A refused gate or a failed task exits 255, so xargs starts nothing further. Writes only under <OUT>;
# refuses if this mode's log exists (a stopped run is continued only by an addendum the director binds).
set -o pipefail   # NOT set -u
MODE="${1:?dry|q3|floor}"; D="${2:?deploy}"; PIN="${3:?pin}"; OUT="${4:?out}"
PY="$D/nd-unfolding/tier3/t3p_probe.py"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[t3p] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
case "$MODE" in
    dry|q3|floor) ;;
    *) echo "[t3p] refusing: mode $MODE" >&2; exit 2 ;;
esac
source "$D/setup_salloc_env.sh" > /dev/null 2>&1   # FD-PRR A1: the environment before any python3 call
LIMIT=$(python3 "$PY" limit "$MODE") || { echo "[t3p] refusing: no declared limit for $MODE" >&2; exit 2; }
if [ -n "$SLURM_JOB_ID" ]; then
    NAME="$SLURM_JOB_NAME"; TL=$(squeue -h -j "$SLURM_JOB_ID" -o %l 2>/dev/null)
elif [ -n "$T3P_SMOKE" ]; then
    NAME="${T3P_NAME:-t3p_$MODE}"; TL="${T3P_TIMELIMIT:-$LIMIT}"
else
    echo "[t3p] refusing: not inside a Slurm job" >&2; exit 2
fi
[ "$NAME" = "t3p_$MODE" ] || { echo "[t3p] refusing: job name $NAME is not t3p_$MODE" >&2; exit 2; }
# FD-PRR A3: the limit in every form Slurm prints it; 0 within, 4 above, 3 unreadable
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
    tl, lim = sec(sys.argv[1]), sec(sys.argv[2])
except ValueError:
    sys.exit(3)
sys.exit(0 if tl <= lim else 4)
EOF
trc=$?
[ "$trc" -ne 3 ] || { echo "[t3p] refusing: could not read the Slurm TimeLimit '$TL'" >&2; exit 2; }
[ "$trc" -ne 4 ] || { echo "[t3p] refusing: Slurm TimeLimit $TL exceeds the declared $LIMIT" >&2; exit 2; }
[ "$trc" -eq 0 ] || { echo "[t3p] refusing: the TimeLimit check failed (rc $trc)" >&2; exit 2; }
LIMIT_H=$(python3 -c "import sys; h,m,s=(int(x) for x in sys.argv[1].split(':')); print(h+m/60+s/3600)" "$LIMIT")
L="$OUT/log-$MODE"
[ ! -e "$L" ] || { echo "[t3p] refusing: $L exists" >&2; exit 2; }
if [ "$MODE" = dry ]; then
    [ -s "$OUT/manifest.json" ] || { echo "[t3p] refusing: no $OUT/manifest.json" >&2; exit 2; }
    [ ! -e "$OUT/stage" ] || { echo "[t3p] refusing: $OUT/stage exists" >&2; exit 2; }
    # §9.4: the director's go names the fenced families; nothing is staged or written while any is queued or running.
    # Fails closed: no fence file, an empty one, or a squeue that cannot answer refuses.
    [ -s "$OUT/fence.txt" ] || { echo "[t3p] refusing: no $OUT/fence.txt naming the fenced job-name prefixes" >&2; exit 2; }
    sq=$(squeue -h -u "${USER:-josephrb}" -o '%j|%T' 2>/dev/null) || { echo "[t3p] refusing: squeue failed" >&2; exit 2; }
    while IFS= read -r pre; do
        [ -n "$pre" ] || continue
        hit=$(printf '%s\n' "$sq" | grep -F -- "$pre" | awk -F'|' -v p="$pre" 'index($1, p) == 1')
        [ -z "$hit" ] || { echo "[t3p] refusing: fenced jobs ($pre*) are queued or running: $hit" >&2; exit 2; }
    done < "$OUT/fence.txt"
else
    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] || { echo "[t3p] refusing: no DONE receipt from the dry run" >&2; exit 2; }
    for id in $(grep -v '^#' "$OUT/queues/dry.tsv" | cut -f1); do
        [ -e "$OUT/log-dry/$id.end" ] || { echo "[t3p] refusing: dry-run task $id never ended" >&2; exit 2; }
    done
fi
Q="$OUT/queues/$MODE.tsv"
[ -s "$Q" ] || { echo "[t3p] refusing: no queue $Q" >&2; exit 2; }
mkdir -p "$L/tasks"
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
python3 -c "import lightgbm, scipy, numpy" >> "$L/env.log" 2>&1 || { echo "[t3p] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
if [ "$MODE" = dry ]; then
    ( cd "$D" && python3 "$PY" stage --manifest "$OUT/manifest.json" --dest "$OUT/stage" --out "$OUT/stage.json" ) \
        > "$L/stage.log" 2>&1 || { echo "stage rc=$?" > "$L/STOP"; echo "[t3p] STOP: staging refused; see $L/stage.log" >&2; exit 1; }
    GMODE=dry
else
    ( cd "$D" && python3 "$PY" verify-stage --stage "$OUT/stage.json" ) > "$L/verify-stage.log" 2>&1 \
        || { echo "verify-stage failed" > "$L/STOP"; echo "[t3p] STOP: a staged copy changed" >&2; exit 1; }
    cp "$OUT"/log-dry/*.start "$OUT"/log-dry/*.end "$L/" || { echo "[t3p] refusing: dry-run timings missing" >&2; exit 2; }
    GMODE=full
fi
T0=$(python3 -c "import time; print(time.time())")
echo "[t3p] mode=$MODE job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=8 limit=$LIMIT start=$(date -u +%FT%TZ)"
TIME_BIN="${T3P_TIME_BIN:-/usr/bin/time}"
export D Q L T0 LIMIT_H GMODE TIME_BIN PY
grep -v '^#' "$Q" | cut -f1 | xargs -P 8 -I{} bash -c '
    id="$1"
    python3 "$PY" gate --task "$id" --queue "$Q" --log "$L" --t0 "$T0" --limit-h "$LIMIT_H" --mode "$GMODE"
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
echo "[t3p] queue rc=$rc end=$(date -u +%FT%TZ)"
( cd "$OUT" && find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
[ -e "$L/STOP" ] && { echo "[t3p] STOP: $(cat "$L/STOP")" >&2; exit 1; }
[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[t3p] STOP: a task failed (rc=$rc)" >&2; exit 1; }
n_q=$(grep -vc '^#' "$Q"); n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq "$n_q" ] || { echo "ended=$n_end of $n_q" > "$L/FAILED"; echo "[t3p] STOP: $n_end of $n_q tasks ended" >&2; exit 1; }
( cd "$D" && python3 "$PY" pair --stage "$OUT/stage.json" --runs "$OUT/runs" --job "$MODE" --out "$L/pair.json" ) > "$L/pair.log" 2>&1
pc=$?
[ "$pc" -eq 0 ] || { echo "pair rc=$pc" > "$L/STOP"; echo "[t3p] STOP: C-PAIR or C-X did not pass (rc=$pc)" >&2; exit 1; }
echo "{\"mode\": \"$MODE\", \"tasks\": $n_q, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\"}" > "$L/DONE"
echo "[t3p] done"
