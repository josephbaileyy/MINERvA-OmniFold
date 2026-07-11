#!/bin/bash
#SBATCH --job-name=unfold_uni_nw_CV
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --output=unfold_MEFHC_uni_full_CV_%j.out
#SBATCH --error=unfold_MEFHC_uni_full_CV_%j.err

# Companion CV unfold for the Stage-2 full lateral+vertical universe sweep.
# This must match sbatch_unfold_2d_MEFHC_5iter_universes_full.sh in every
# non-universe setting: same full universe omnifile, lgbm backend, seed,
# iteration count, weights, and flux input. The final universe covariance
# rollup subtracts this file from each universe output.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC_universes_full.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
XSEC_OUT="${DOCS}/uq/negweight_uni/2d_xsec_MEFHC_5iter_lgbm_nw_uni_CV.root"

if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] flux mc:  ${FLUX_MC}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator lgbm \
  --seed      42 \
  --bkg-mode  negweight \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
