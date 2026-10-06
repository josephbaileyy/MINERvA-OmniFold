#!/bin/bash
#SBATCH --job-name=cov2d_fixedtruth
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --output=/pscratch/sd/j/josephrb/coverage-2d-20261005/logs/toy_%a_%A.out
#SBATCH --error=/pscratch/sd/j/josephrb/coverage-2d-20261005/logs/toy_%a_%A.err

# Fixed-truth 2D coverage toys. The array index is the toy index:
#   pilot  sbatch --array=9001-9003 sbatch_fixed_truth_toys.sh
#   full   sbatch --array=1-200%<N> sbatch_fixed_truth_toys.sh
# Pre-registration: docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md.
# CODE must be a clean checkout of the pre-registered commit; the environment and
# the OmniFold backend are the production ones (main checkout, read only).

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

PROD="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE="${COVERAGE_CODE:-/pscratch/sd/j/josephrb/MINERvA-OmniFold-2d-coverage-20261005}"
OUTROOT="${COVERAGE_OUT:-/pscratch/sd/j/josephrb/coverage-2d-20261005}"
OMNIFILE="${PROD}/2d-unfolding/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${PROD}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
T="${SLURM_ARRAY_TASK_ID:?run as an array; the index is the toy index}"
if (( T >= 9000 )); then OUTDIR="${OUTROOT}/pilot"; else OUTDIR="${OUTROOT}/toys"; fi
OUT="${OUTDIR}/toy${T}.root"

source "${CODE}/lib/resume_guard.sh"
rg_skip_if_complete "${OUT}" && exit 0

if [[ -n "$(git -C "${CODE}" status --porcelain --untracked-files=no)" ]]; then
  echo "[FAIL] ${CODE} has uncommitted changes" >&2; exit 3
fi
source "${PROD}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"

echo "[sbatch] node=$(hostname) job=${SLURM_JOB_ID} toy=${T} qos=${SLURM_JOB_QOS:-?}"
echo "[sbatch] code=${CODE} head=$(git -C "${CODE}" rev-parse HEAD)"
echo "[sbatch] start $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
rg_run "${OUT}" python "${CODE}/2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py" \
  --toy "${T}" --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
  --iters 5 --estimator lgbm --seed 1 --out "${OUT}"
echo "[sbatch] done $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
