#!/bin/bash
#SBATCH --job-name=cov2d_equiv
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-2
#SBATCH --output=/pscratch/sd/j/josephrb/coverage-2d-20261005/logs/equiv_%a_%A.out
#SBATCH --error=/pscratch/sd/j/josephrb/coverage-2d-20261005/logs/equiv_%a_%A.err

# Equivalence check for fixed_truth_toy.py: task 1 runs the production driver
# (--closure --use-weights, lgbm, --seed 1, no bootstrap); task 2 runs
# fixed_truth_toy.py --no-fluctuation with the same settings. compare_equivalence.py
# then requires identical hXSec2D and truth histograms.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

PROD="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE="${COVERAGE_CODE:-/pscratch/sd/j/josephrb/MINERvA-OmniFold-2d-coverage-20261005}"
OUTDIR="${COVERAGE_OUT:-/pscratch/sd/j/josephrb/coverage-2d-20261005}/equivalence"
OMNIFILE="${PROD}/2d-unfolding/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${PROD}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"

source "${CODE}/lib/resume_guard.sh"
if [[ -n "$(git -C "${CODE}" status --porcelain --untracked-files=no)" ]]; then
  echo "[FAIL] ${CODE} has uncommitted changes" >&2; exit 3
fi
source "${PROD}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${CODE}/2d-unfolding"
echo "[sbatch] node=$(hostname) job=${SLURM_JOB_ID} task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] code=${CODE} head=$(git -C "${CODE}" rev-parse HEAD)"
echo "[sbatch] start $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
case "${SLURM_ARRAY_TASK_ID}" in
  1) OUT="${OUTDIR}/production_closure.root"
     rg_skip_if_complete "${OUT}" && exit 0
     rg_run "${OUT}" python unfold_2d_omnifold_unbinned.py \
       --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" --iters 5 --use-weights \
       --estimator lgbm --closure --seed 1 --out "${OUT}" ;;
  2) OUT="${OUTDIR}/toy_driver_nofluct.root"
     rg_skip_if_complete "${OUT}" && exit 0
     rg_run "${OUT}" python uq/coverage_fixed_truth/fixed_truth_toy.py --no-fluctuation \
       --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" --iters 5 --estimator lgbm \
       --seed 1 --out "${OUT}" ;;
  *) echo "[FAIL] unknown task" >&2; exit 2 ;;
esac
echo "[sbatch] done $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
