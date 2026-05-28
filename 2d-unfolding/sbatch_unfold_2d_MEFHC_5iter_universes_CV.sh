#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_uniCV
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --output=unfold_MEFHC_uniCV_%j.out
#SBATCH --error=unfold_MEFHC_uniCV_%j.err

# Companion CV unfold to sbatch_unfold_2d_MEFHC_5iter_universes.sh.
# Runs the unfold against runEventLoopOmniFold_MEFHC_universes.root
# with --seed 42, --estimator lgbm, NO --universe. The output xsec ROOT
# is the CV reference for the universe-covariance rollup (analyze_universes.py
# --cv ... --glob 'uq/2d_xsec_MEFHC_5iter_lgbm_uni_*.root').

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC_universes.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
XSEC_OUT="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_CV.root"

if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

python unfold_2d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator lgbm \
  --seed      42 \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
