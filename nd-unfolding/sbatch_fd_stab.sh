#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# FD-STAB (state/measurement-paper/5d-community-20261024/FD-STAB-DECLARATION.md §7 and §11). One node.
#   dry:  the eight DRY_TASKS on the full run's 8 lanes (submit with --time=0:45).
#   full: the whole queue on 8 lanes (submit with --time = the cap's remainder after the dry run, at most 7:15). The
#         dry run's log is copied in first, so its timings seed the projection and its products are skipped.
# Every task starts only through `estimator_stability_probe.py gate`: the node-hours charged so far plus the projected
# remainder of the whole run must stay within CAP_LEFT, and B2 within 2x the control's per-unfold time. A refused gate
# or a failed task exits 255, so xargs starts nothing further; Slurm's --time bounds the charge whatever happens.
# Only a run whose every task ended, with no STOP and rc 0, writes its DONE receipt; the full run refuses without the
# dry run's (a failed task, a STOP and a Slurm time-limit kill all leave none).
# Writes only under <OUT>; refuses if this mode's log exists. Runs only from a clean deploy at <pin>.
set -o pipefail   # NOT set -u
MODE="${1:?dry|full}"; D="${2:?deploy}"; PIN="${3:?pin}"; OUT="${4:?out}"; CAP_LEFT="${5:?node-hours left under the cap}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[stab] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
case "$MODE" in
    dry)  Q="$OUT/dry.tsv"; P=8 ;;
    full) Q="$OUT/queue.tsv"; P=8 ;;
    *)    echo "[stab] refusing: mode $MODE" >&2; exit 2 ;;
esac
[ -s "$Q" ] || { echo "[stab] refusing: no queue $Q" >&2; exit 2; }
L="$OUT/log-$MODE"
[ ! -e "$L" ] || { echo "[stab] refusing: $L exists" >&2; exit 2; }
if [ "$MODE" = full ]; then  # checked before anything is written, so a refusal leaves no trace
    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] || { echo "[stab] refusing: no DONE receipt from the dry run" >&2; exit 2; }
    for id in $(grep -v '^#' "$OUT/dry.tsv" | cut -f1); do
        [ -e "$OUT/log-dry/$id.end" ] || { echo "[stab] refusing: dry-run task $id never ended" >&2; exit 2; }
    done
fi
mkdir -p "$L/tasks"
if [ "$MODE" = full ]; then
    cp "$OUT"/log-dry/*.start "$OUT"/log-dry/*.end "$L/" || { echo "[stab] refusing: dry-run timings missing" >&2; exit 2; }
fi
source "$D/setup_salloc_env.sh" > "$L/env.log" 2>&1
# The environment is the dry run's to establish (§11): it must import what the production unfold imports.
python3 -c "import lightgbm, scipy, numpy" >> "$L/env.log" 2>&1 || { echo "[stab] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }
T0=$(python3 -c "import time; print(time.time())")  # the same clock and resolution as the gate's starts and ends
echo "[stab] mode=$MODE job=$SLURM_JOB_ID host=$(hostname) pin=$PIN lanes=$P cap_left=$CAP_LEFT start=$(date -u +%FT%TZ)"
TIME_BIN="${STAB_TIME_BIN:-/usr/bin/time}"  # GNU time on the cluster; the local smoke test substitutes a stand-in
export D Q L T0 CAP_LEFT TIME_BIN
grep -v '^#' "$Q" | cut -f1 | xargs -P "$P" -I{} bash -c '
    id="$1"
    python3 "$D/nd-unfolding/estimator_stability_probe.py" gate --task "$id" --queue "$Q" --log "$L" --t0 "$T0" \
        --cap "$CAP_LEFT"
    g=$?
    [ "$g" -eq 4 ] && exit 0      # finished in the dry run: its product and timing stand
    [ "$g" -eq 0 ] || exit 255
    cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F "\t" -v id="$id" \
        '"'"'$1 == id { for (i = 1; i <= NF; i++) print $i }'"'"' "$Q")
    [ "${#cols[@]}" -gt 3 ] || exit 255
    ( cd "$D" && "$TIME_BIN" -v -o "$L/tasks/$id.time" python3 "nd-unfolding/${cols[2]}" "${cols[@]:3}" ) \
        > "$L/tasks/$id.log" 2>&1 || exit 255
    python3 -c "import time; print(time.time())" > "$L/$id.end.tmp" && mv "$L/$id.end.tmp" "$L/$id.end"' _ {}  
rc=$?
echo "[stab] queue rc=$rc end=$(date -u +%FT%TZ)"
[ -e "$L/STOP" ] && { echo "[stab] STOP: $(cat "$L/STOP")" >&2; exit 1; }
[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[stab] STOP: a task failed (rc=$rc)" >&2; exit 1; }
n_q=$(grep -vc '^#' "$Q"); n_end=0
for id in $(grep -v '^#' "$Q" | cut -f1); do [ -e "$L/$id.end" ] && n_end=$((n_end + 1)); done
[ "$n_end" -eq "$n_q" ] || { echo "ended=$n_end of $n_q" > "$L/FAILED"; echo "[stab] STOP: $n_end of $n_q tasks ended" >&2; exit 1; }
( cd "$OUT" && find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 sha256sum ) > "$L/SHA256SUMS"
echo "{\"mode\": \"$MODE\", \"tasks\": $n_q, \"ended\": $n_end, \"rc\": 0, \"job\": \"$SLURM_JOB_ID\"}" > "$L/DONE"
echo "[stab] done"
