#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# IBU-1: run lines <first>..<last> of tasks.tsv CONCURRENTLY on one node, one srun step each (Slurm queues the
# steps that do not fit), every one through mnv_guarded_run.py (OI-136) from a clean deploy at <pin>:
#   sbatch --qos=<regular|debug> --time=<limit> --job-name=ibu1_<k> --output=<OUT>/logs/%x_%j.out \
#          sbatch_ibu1.sh <deploy> <pin> <OUT> <cpus per task> <mem per task> <first> <last>
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; CPT="${4:?cpus}"; MEM="${5:?mem}"; FIRST="${6:?first}"; LAST="${7:?last}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[ibu1] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2
    exit 2
fi
source "$D/setup_salloc_env.sh" > "$OUT/logs/env-${SLURM_JOB_ID}.log" 2>&1
case "$(python3 -V 2>&1)" in
    *3.11*) ;;
    *) echo "[ibu1] refusing: environment did not activate ($(python3 -V 2>&1))" >&2; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR" "$OUT/inventory" "$OUT/products"
TABLE="$D/nd-unfolding/ibu1/tasks.tsv"
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
cd "$D" || exit 2
pids=()
for i in $(seq "$FIRST" "$LAST"); do
    line=$(grep -v '^#' "$TABLE" | sed -n "$((i + 1))p")
    [ -z "$line" ] && { echo "[ibu1] no task line $i" >&2; exit 2; }
    name=$(printf '%s' "$line" | cut -f1); unit=$(printf '%s' "$line" | cut -f2); seeds=$(printf '%s' "$line" | cut -f3)
    extra=(); [ -n "$seeds" ] && extra=(--seeds "$seeds")
    srun --exclusive -n1 -c "$CPT" --mem="$MEM" --job-name="$name" \
        python3 "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$OUT/inventory/$name.jsonl" \
        --label "ibu1:$name" -- "$D/nd-unfolding/ibu1/ibu1.py" --npz "$NPZ" --bkg "$BKG" --out "$OUT/products" \
        --unit "$unit" "${extra[@]}" > "$OUT/logs/task-$name-${SLURM_JOB_ID}.log" 2>&1 &
    pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "[ibu1] tasks $FIRST..$LAST done rc=$rc"
exit $rc
