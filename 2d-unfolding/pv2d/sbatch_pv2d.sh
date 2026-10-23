#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# PV-2D: one task line of tasks.tsv per job, through mnv_guarded_run.py (OI-136) from a clean deploy at <pin>.
# The unfold is E_U's (sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh): the same omnifile, flux file, 5
# iterations, --use-weights, --estimator lgbm, --seed 42, 128 threads; plus the task's PV-2D flags.
#   sbatch --qos=regular --time=<limit> --job-name=pv2d_<task> --output=<OUT>/logs/%x_%j.out \
#          sbatch_pv2d.sh <deploy> <pin> <OUT> <task>
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; TASK="${4:?task}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[pv2d] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2
    exit 2
fi
P="$D/2d-unfolding/pv2d"
line=$(grep -v '^#' "$P/tasks.tsv" | awk -F'\t' -v t="$TASK" '$1 == t')
[ -z "$line" ] && { echo "[pv2d] no task $TASK" >&2; exit 2; }
mode=$(printf '%s' "$line" | cut -f2); ratio=$(printf '%s' "$line" | cut -f3)
RF="$P/ratios/$ratio.json"
[ -f "$RF" ] || { echo "[pv2d] missing ratio file $RF" >&2; exit 2; }
SHA=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['vertices'][sys.argv[2]]['ratio_sha256'])" \
      "$P/ratios/projections.json" "$ratio") || exit 2
case "$mode" in
    prior)   extra=(--prior-ratio "$RF" --expect-prior-ratio-sha256 "$SHA") ;;
    closure) extra=(--closure --closure-ratio "$RF" --expect-closure-ratio-sha256 "$SHA") ;;
    *) echo "[pv2d] bad mode $mode" >&2; exit 2 ;;
esac
PROD="$OUT/products/$TASK.root"
[ -e "$PROD" ] && { echo "[pv2d] refusing to overwrite $PROD" >&2; exit 2; }
source "$D/setup_salloc_env.sh" > "$OUT/logs/env-${SLURM_JOB_ID}.log" 2>&1
case "$(python3 -V 2>&1)" in
    *3.11*) ;;
    *) echo "[pv2d] refusing: environment did not activate ($(python3 -V 2>&1))" >&2; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR" "$OUT/inventory" "$OUT/products"
R=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
cd "$OUT" || exit 2
echo "[pv2d] task=$TASK mode=$mode ratio=$ratio sha=$SHA node=$(hostname) job=${SLURM_JOB_ID} start=$(date -u +%FT%TZ)"
python3 "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$OUT/inventory/$TASK.jsonl" \
    --label "pv2d:$TASK" -- "$P/unfold_2d_pv2d.py" \
    --omnifile "$R/runEventLoopOmniFold_MEFHC_universes_full.root" \
    --mcfile "$R/baseline_flux/runEventLoopMC_MEFHC.root" \
    --iters 5 --use-weights --estimator lgbm --seed 42 \
    "${extra[@]}" --out "$PROD.part"
rc=$?
[ "$rc" -eq 0 ] && mv "$PROD.part" "$PROD" && sha256sum "$PROD"
echo "[pv2d] task=$TASK rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
