#!/bin/bash
#SBATCH --job-name=coverage_MEFHC_200
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=21-200%30
#SBATCH --output=coverage_MEFHC_200_%a_%A.out
#SBATCH --error=coverage_MEFHC_200_%a_%A.err

# Stage-2 plan deliverable #5 — coverage toys scale-up 20 -> 200.
#
# Reuses the existing toy framework from sbatch_coverage_toys_MEFHC.sh
# (toys 1-20 already on disk under uq/coverage/). This array adds
# toys 21-200. The skip-if-exists guard makes re-runs idempotent.
#
# At N=200, per-bin coverage resolution drops from ~10% (N=20) to ~3.3%,
# letting per-bin coverage be asserted rather than only the population
# mean.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

SEED=$((SLURM_ARRAY_TASK_ID + 1000))
XSEC_OUT="${DOCS}/uq/coverage/2d_xsec_MEFHC_5iter_lgbm_coverage_toy${SLURM_ARRAY_TASK_ID}.root"

if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq/coverage"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] seed:  ${SEED}"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile        "${OMNIFILE}" \
  --mcfile          "${FLUX_MC}" \
  --iters           5 \
  --use-weights \
  --estimator       lgbm \
  --closure \
  --bootstrap-seed  "${SEED}" \
  --seed            "${SEED}" \
  --out             "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
