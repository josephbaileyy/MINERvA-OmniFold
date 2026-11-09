#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# FD-PRR (state/measurement-paper/5d-community-20261024/FD-PRR-DECLARATION.md §10). One node, 8 lanes, CPU only.
#   sbatch --job-name=prr_<mode> --time=<prr_probe.py limit <mode>> sbatch_prr.sh <mode> <deploy> <pin> <OUT>
#   dry:  stage every shared input once through O_NOATIME, with stat records before and after (prr_probe.py stage),
#         then the dry queue, then C-PAIR and C-MASK (prr_probe.py pair). DONE only if all three pass.
#   iter, cap, misc: after a clean dry run only; the staged copies are re-verified, the dry run's timings copied in,
#         and every task starts only through the gate (the projection, tail included, within 0.9 of this job's --time;
#         every level priced at its dry-run rate).
#   ibu:  route 2 (prr_ibu.py), after a clean dry run.
# The job's name must be prr_<mode> and its Slurm TimeLimit at most the declared limit (prr_probe.py limit), or it
# refuses before anything is written. A refused gate or a failed task exits 255, so xargs starts nothing further;
# Slurm's --time bounds the charge whatever happens. Writes only under <OUT>; refuses if this mode's log exists, so a
# stopped run is not resumed by re-running it (only an addendum the director binds continues it).
set -o pipefail   # NOT set -u
MODE="${1:?dry|iter|cap|misc|ibu}"; D="${2:?deploy}"; PIN="${3:?pin}"; OUT="${4:?out}"
PY="$D/nd-unfolding/prior_retention/prr_probe.py"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[prr] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
case "$MODE" in
    dry|iter|cap|misc|ibu) ;;
    *) echo "[prr] refusing: mode $MODE" >&2; exit 2 ;;
esac
# Addendum A1: the environment first. The login node's /usr/bin/python3 is 3.6.15, where prr_probe.py's
# `from __future__ import annotations` is a SyntaxError (RS1 A1, #905), so every python3 call runs after this source.
source "$D/setup_salloc_env.sh" > /dev/null 2>&1
# The job's identity and limit, as Slurm holds them (a smoke test outside Slurm sets PRR_SMOKE and PRR_TIMELIMIT)
LIMIT=$(python3 "$PY" limit "$MODE") || { echo "[prr] refusing: no declared limit for $MODE" >&2; exit 2; }
if [ -n "$SLURM_JOB_ID" ]; then
    NAME="$SLURM_JOB_NAME"; TL=$(squeue -h -j "$SLURM_JOB_ID" -o %l 2>/dev/null)
elif [ -n "$PRR_SMOKE" ]; then
    NAME="prr_$MODE"; TL="${PRR_TIMELIMIT:-$LIMIT}"
else
    echo "[prr] refusing: not inside a Slurm job" >&2; exit 2
fi
[ "$NAME" = "prr_$MODE" ] || { echo "[prr] refusing: job name $NAME is not prr_$MODE" >&2; exit 2; }
# Addendum A3: the limit in every form Slurm prints it (squeue's %l gives "30:00" for half an hour), and an unreadable
# limit refused as such: 0 within the limit, 4 above it, 3 unreadable; any other rc is a failed check.
python3 - "$TL" "$LIMIT" <<'EOF'
import sys
def sec(t):
    """Seconds in a Slurm time: M, M:SS or H:MM:SS without a day; D-H, D-H:MM or D-H:MM:SS with one."""
    d, dash, rest = t.partition("-")
    f = rest.split(":") if dash else t.split(":")
    if (dash and not d.isdigit()) or not all(x.isdigit() for x in f) or len(f) > 3:
        raise ValueError(t)
    f = [int(x) for x in f]
    if dash:  # D-H, D-H:MM, D-H:MM:SS
        h, m, s = f + [0] * (3 - len(f))
        return int(d) * 86400 + h * 3600 + m * 60 + s
    if len(f) == 1:  # M
        return f[0] * 60
    if len(f) == 2:  # M:SS
        return f[0] * 60 + f[1]
    return f[0] * 3600 + f[1] * 60 + f[2]  # H:MM:SS
try:
    tl, lim = sec(sys.argv[1]), sec(sys.argv[2])
except ValueError:
    sys.exit(3)
sys.exit(0 if tl <= lim else 4)
EOF
trc=$?
[ "$trc" -ne 3 ] || { echo "[prr] refusing: could not read the Slurm TimeLimit '$TL'" >&2; exit 2; }
[ "$trc" -ne 4 ] || { echo "[prr] refusing: Slurm TimeLimit $TL exceeds the declared $LIMIT" >&2; exit 2; }
[ "$trc" -eq 0 ] || { echo "[prr] refusing: the TimeLimit check failed (rc $trc)" >&2; exit 2; }
LIMIT_H=$(python3 -c "import sys; h,m,s=(int(x) for x in sys.argv[1].split(':')); print(h+m/60+s/3600)" "$LIMIT")
L="$OUT/log-$MODE"
[ ! -e "$L" ] || { echo "[prr] refusing: $L exists" >&2; exit 2; }
if [ "$MODE" = dry ]; then
    [ -s "$OUT/manifest.json" ] || { echo "[prr] refusing: no $OUT/manifest.json" >&2; exit 2; }
    [ ! -e "$OUT/stage" ] || { echo "[prr] refusing: $OUT/stage exists" >&2; exit 2; }
    # The director's sharing ruling (FD-PRR §10.4): ENS1 reads the same inputs in place, so nothing is staged or
    # written while any ens1_* job is queued or running. Fails closed: if squeue cannot answer, the dry run refuses.
    sq=$(squeue -h -u "${USER:-josephrb}" -o '%j|%T' 2>/dev/null) || { echo "[prr] refusing: squeue failed; cannot check for ens1_* jobs" >&2; exit 2; }
    ens=$(printf '%s\n' "$sq" | grep '^ens1_')
    [ -z "$ens" ] || { echo "[prr] refusing: ens1_* jobs are queued or running: $ens" >&2; exit 2; }
else  # checked before anything is written, so a refusal leaves no trace
    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] || { echo "[prr] refusing: no DONE receipt from the dry run" >&2; exit 2; }
    for id in $(grep -v '^#' "$OUT/queues/dry.tsv" | cut -f1); do
        [ -e "$OUT/log-dry/$id.end" ] || { echo "[prr] refusing: dry-run task $id never ended" >&2; exit 2; }
    done
fi
Q="$OUT/queues/$MODE.tsv"
[ "$MODE" = ibu ] || [ -s "$Q" ] || { echo "[prr] refusing: no queue $Q" >&2; exit 2; }
mkdir -p "$L/tasks"
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
python3 -c "import lightgbm, scipy, numpy" >> "$L/env.log" 2>&1 || { echo "[prr] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
if [ "$MODE" = dry ]; then
    ( cd "$D" && python3 "$PY" stage --manifest "$OUT/manifest.json" --dest "$OUT/stage" --out "$OUT/stage.json" ) \
        > "$L/stage.log" 2>&1 || { echo "stage rc=$?" > "$L/STOP"; echo "[prr] STOP: staging refused; see $L/stage.log" >&2; exit 1; }
else
    ( cd "$D" && python3 "$PY" verify-stage --stage "$OUT/stage.json" ) > "$L/verify-stage.log" 2>&1 \
        || { echo "verify-stage failed" > "$L/STOP"; echo "[prr] STOP: a staged copy changed" >&2; exit 1; }
fi
if [ "$MODE" = ibu ]; then
    echo "[prr] mode=ibu job=$SLURM_JOB_ID host=$(hostname) pin=$PIN start=$(date -u +%FT%TZ)"
    ( cd "$D" && python3 nd-unfolding/prior_retention/prr_ibu.py run --queue-dir "$OUT/queues" --stage "$OUT/stage.json" \
        --out "$OUT/route2" ) > "$L/ibu.log" 2>&1
    rc=$?
    [ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[prr] STOP: route 2 failed (rc=$rc)" >&2; exit 1; }
    ( cd "$OUT" && sha256sum route2/route2.npz route2/route2.json ) > "$L/SHA256SUMS"
    echo "{\"mode\": \"ibu\", \"rc\": 0, \"job\": \"$SLURM_JOB_ID\"}" > "$L/DONE"
    echo "[prr] done"; exit 0
fi
if [ "$MODE" != dry ]; then
    cp "$OUT"/log-dry/*.start "$OUT"/log-dry/*.end "$L/" || { echo "[prr] refusing: dry-run timings missing" >&2; exit 2; }
    GMODE=full
else
    GMODE=dry
fi
T0=$(python3 -c "import time; print(time.time())")  # the same clock and resolution as the gate's starts and ends
echo "[prr] mode=$MODE job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=8 limit=$LIMIT start=$(date -u +%FT%TZ)"
TIME_BIN="${PRR_TIME_BIN:-/usr/bin/time}"  # GNU time on the cluster; the local smoke test substitutes a stand-in
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
echo "[prr] queue rc=$rc end=$(date -u +%FT%TZ)"
( cd "$OUT" && find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
[ -e "$L/STOP" ] && { echo "[prr] STOP: $(cat "$L/STOP")" >&2; exit 1; }
[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[prr] STOP: a task failed (rc=$rc)" >&2; exit 1; }
n_q=$(grep -vc '^#' "$Q"); n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq "$n_q" ] || { echo "ended=$n_end of $n_q" > "$L/FAILED"; echo "[prr] STOP: $n_end of $n_q tasks ended" >&2; exit 1; }
if [ "$MODE" = dry ]; then  # C-PAIR and C-MASK gate the full jobs
    ( cd "$D" && python3 "$PY" pair --stage "$OUT/stage.json" --runs "$OUT/runs" --out "$L/pair.json" ) > "$L/pair.log" 2>&1
    pc=$?
    [ "$pc" -eq 0 ] || { echo "pair rc=$pc" > "$L/STOP"; echo "[prr] STOP: C-PAIR or C-MASK did not pass (rc=$pc)" >&2; exit 1; }
fi
echo "{\"mode\": \"$MODE\", \"tasks\": $n_q, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\"}" > "$L/DONE"
echo "[prr] done"
