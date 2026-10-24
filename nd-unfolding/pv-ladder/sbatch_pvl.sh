#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# PV ladder: every task of one declared job (tasks.tsv column 7) at once, one srun step of 42 CPUs each
# (--cpu-bind=cores, as RE-1's re1-nd), through mnv_guarded_run.py (OI-136) from a clean deploy at <pin>, in RE-1's
# environment ($A/setup_salloc_env.sh, `python`). Every task is validated before any step starts. A job other than
# J1 runs only if <OUT>/gates/<job>.ok exists and names this pin: the director's rule that a rung runs only after
# its nominal control passes, written after pvl_analyze.py reads J1 (and, for F, after a NOT_POWERED verdict).
# The reweights are the prep job's files under <OUT>/prep/ratios (read-only), each checked against the committed
# prep-SHA256SUMS before any step starts; that sha256 is the one the unfold is told to expect.
#   sbatch --qos=regular --time=<limit> --job-name=pvl_<job> --output=<OUT>/logs/%x_%j.out \
#          sbatch_pvl.sh <deploy> <pin> <OUT> <job>
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; JOB="${4:?job}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
stray=$(git -C "$D" status --porcelain --untracked-files=all -- nd-unfolding 2d-unfolding/pv2d 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ] || [ "$stray" -ne 0 ]; then
    echo "[pvl] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files, $stray untracked" >&2
    exit 2
fi
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
V="$D/nd-unfolding/pv-ladder"
RD="$OUT/prep/ratios"
want_sha() {  # want_sha <path relative to prep/>: the committed sha256, or nothing
    awk -v f="./$1" '$2 == f {print $1}' "$V/prep-SHA256SUMS"
}
if [ "$JOB" != J1 ]; then
    G="$OUT/gates/$JOB.ok"
    [ -f "$G" ] && grep -qx "pin=$PIN" "$G" || { echo "[pvl] refusing: $G is missing or does not name pin $PIN" >&2; exit 2; }
fi
mapfile -t LINES < <(grep -v '^#' "$V/tasks.tsv" | awk -F'\t' -v j="$JOB" '$7 == j')
[ "${#LINES[@]}" -gt 0 ] || { echo "[pvl] no tasks for job $JOB" >&2; exit 2; }
mkdir -p "$OUT/logs"
source "$A/setup_salloc_env.sh" > "$OUT/logs/env-${SLURM_JOB_ID}.log" 2>&1
case "$(python -V 2>&1)" in
    *3.11*) ;;
    *) echo "[pvl] refusing: environment did not activate ($(python -V 2>&1))" >&2; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR" "$OUT/inventory" "$OUT/products" "$OUT/logs"
cfg() {  # cfg <rung> <key: npz|bkg> <field: path|sha256>
    python -c "import json,sys; print(json.load(open(sys.argv[1]))['rungs'][sys.argv[2]][sys.argv[3]][sys.argv[4]])" \
        "$V/config.json" "$1" "$2" "$3"
}
# validate every task first, so a refusal never leaves steps running
for line in "${LINES[@]}"; do
    IFS=$'\t' read -r task rung _ _ vertex _ _ _ <<< "$line"
    w=$(want_sha "ratios/$rung/$vertex.json")
    [ -n "$w" ] && [ "$(sha256sum "$RD/$rung/$vertex.json" | cut -d' ' -f1)" = "$w" ] \
        || { echo "[pvl] refusing: $RD/$rung/$vertex.json is missing or differs from prep-SHA256SUMS" >&2; exit 2; }
    [ ! -e "$OUT/products/$task.npz" ] || { echo "[pvl] refusing: $OUT/products/$task.npz exists" >&2; exit 2; }
done
# each step gets an equal share of 95 % of the job's memory, so all of them start at once (steps whose --mem
# sum exceeds the allocation serialize silently); sacct's step Start times are the check
MEM=$(( ${SLURM_MEM_PER_NODE:?} * 95 / 100 / ${#LINES[@]} ))
# 42 CPUs per step as RE-1's re1-nd, fewer when more than six steps share the node (LightGBM's num_threads is fixed
# at 32 by the s5 estimator configuration either way)
CPS=$(( ${SLURM_CPUS_ON_NODE:?} / ${#LINES[@]} )); [ "$CPS" -gt 42 ] && CPS=42
[ "$CPS" -ge 32 ] || { echo "[pvl] refusing: $CPS CPUs per step is below LightGBM's 32 threads" >&2; exit 2; }
echo "[pvl] job=$JOB slurm=$SLURM_JOB_ID node=$(hostname) tasks=${#LINES[@]} mem_per_step=${MEM}M cpus_per_step=$CPS start=$(date -u +%FT%TZ)"
pids=(); names=()
for line in "${LINES[@]}"; do
    IFS=$'\t' read -r task rung arm features vertex mode _ _ <<< "$line"
    RF="$RD/$rung/$vertex.json"
    SHA=$(want_sha "ratios/$rung/$vertex.json")
    PROD="$OUT/products/$task.npz"
    extra=(); [ "$mode" = closure ] && extra=(--closure)
    srun -n1 -c "$CPS" --mem="${MEM}M" --exact --cpu-bind=cores \
        python "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$OUT/inventory/$task.jsonl" \
        --label "pvl:$task" -- "$V/pvl_unfold.py" --rung "$rung" --arm "$arm" --features "$features" \
        --ratio "$RF" --expect-ratio-sha256 "$SHA" "${extra[@]}" \
        --npz "$(cfg "$rung" npz path)" --expect-npz-sha256 "$(cfg "$rung" npz sha256)" \
        --bkg "$(cfg "$rung" bkg path)" --expect-bkg-sha256 "$(cfg "$rung" bkg sha256)" \
        --estimator-seed 42 --threads 32 --iters 5 --out "$PROD" > "$OUT/logs/$task.log" 2>&1 &
    pids+=("$!"); names+=("$task")
done
rc=0
for i in "${!pids[@]}"; do
    if wait "${pids[$i]}"; then
        sha256sum "$OUT/products/${names[$i]}.npz"
    else
        echo "[pvl] task ${names[$i]} failed; see $OUT/logs/${names[$i]}.log" >&2; rc=1
    fi
done
echo "[pvl] job=$JOB rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
