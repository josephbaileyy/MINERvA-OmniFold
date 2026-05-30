#!/bin/bash
#SBATCH --job-name=unfold3d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=12:00:00
#SBATCH --output=unfold3d_%j.out
#SBATCH --error=unfold3d_%j.err

# Workstream C / C2-C3: full-statistics 3D unbinned OmniFold of the MEFHC
# omnifile (eavail branches), then the Eavail-marginal anchor check vs the
# published 2D covariance. CV weights, lgbm estimator, 5 iterations (matching
# the frozen 2D production).

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=32
export OPENBLAS_NUM_THREADS=32

cd "${REPO}/3d-unfolding"

OMNIFILE="${REPO}/3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root"
MCFILE="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
OUT="${REPO}/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} start=$(date -u '+%F %T UTC')"

python unfold_3d_omnifold_unbinned.py \
  --omnifile "${OMNIFILE}" \
  --mcfile   "${MCFILE}" \
  --iters 5 \
  --use-weights \
  --estimator lgbm \
  --seed 1 \
  --out "${OUT}" \
  --verbose

echo "[sbatch] unfold done=$(date -u '+%F %T UTC'); output: ${OUT}"

# --- Anchor check: Eavail-marginal (hXSec2D) vs published 2D covariance ---
echo "[sbatch] anchor check: Eavail-marginal vs paper full covariance"
python "${REPO}/2d-unfolding/compare_to_paper_fullcov.py" \
  --ours "${OUT}" 2>&1 | tee "${REPO}/3d-unfolding/anchor_marginal_vs_paper.txt"

echo "[sbatch] all done=$(date -u '+%F %T UTC')"
