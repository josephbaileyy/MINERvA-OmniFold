#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# PV ladder preparation (DECLARATION.md §2): each rung's cell sets (pvl_cells.py) and vertex reweights
# (pvl_ratios.py), from a clean deploy at <pin>, into <OUT>/prep/. No unfolding.
#   sbatch --qos=debug --time=0:20:00 --job-name=pvl_prep --output=<OUT>/logs/%x_%j.out \
#          sbatch_pvl_prep.sh <deploy> <pin> <OUT> <rung> [<rung> ...]
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; shift 3
[ "$#" -gt 0 ] || { echo "[pvl] name at least one rung" >&2; exit 2; }
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(( $(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l) + \
         $(git -C "$D" status --porcelain --untracked-files=all -- nd-unfolding 3d-unfolding/genie 2d-unfolding/pv2d 2>/dev/null | wc -l) ))
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[pvl] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty changed or untracked files" >&2
    exit 2
fi
V="$D/nd-unfolding/pv-ladder"
mkdir -p "$OUT/logs" "$OUT/prep/cells" "$OUT/inventory"
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > "$OUT/logs/env-prep-${SLURM_JOB_ID}.log" 2>&1
case "$(python -V 2>&1)" in
    *3.11*) ;;
    *) echo "[pvl] refusing: environment did not activate ($(python -V 2>&1))" >&2; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
rc=0
for rung in "$@"; do
    for step in cells ratios; do
        if [ "$step" = cells ]; then args=(--rung "$rung" --out "$OUT/prep/cells/$rung.json")
        else args=(--rung "$rung" --out "$OUT/prep/ratios"); fi
        python "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$OUT/inventory/prep-$step-$rung.jsonl" \
            --label "pvl:prep-$step-$rung" -- "$V/pvl_$step.py" "${args[@]}" || { echo "[pvl] $step $rung failed" >&2; rc=1; }
    done
done
(cd "$OUT/prep" && find . -type f -name '*.json' | sort | xargs sha256sum)
echo "[pvl] prep rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
