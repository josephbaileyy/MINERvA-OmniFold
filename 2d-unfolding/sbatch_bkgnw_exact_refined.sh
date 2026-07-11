#!/bin/bash
#SBATCH --job-name=bkgnw_exact_refined_s1
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=24:00:00
#SBATCH --output=HANDOFF_bkg_negweight/runs/bkgnw_exact_refined_s1_%j.out
#SBATCH --error=HANDOFF_bkg_negweight/runs/bkgnw_exact_refined_s1_%j.err

# Phase-D confirmation: does the Stay-Positive refinement (negweight-refined,
# arXiv:2505.03724) cure the exact-estimator (GradientBoostingClassifier)
# negative-sample-weight blow-up seen in the exact matched pair (55667224/25)?
# The raw exact negweight run exploded ~5 orders of magnitude across the iy=1
# row vs exact purity; lgbm was clean. This run is matched to that pair
# (exact, seed 1, 5-iter, same omnifile/mc) so refined/purity is a direct test:
# agreement ~1 across iy=1 => Stay-Positive fixes the exact backend.
set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
XSEC_OUT="${DOCS}/HANDOFF_bkg_negweight/runs/2d_xsec_refined_seed1_exact5.root"

# Submit-env-independent env sourcing (background/sandboxed-HOME safe).
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} mode=negweight-refined seed=1 est=exact"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator exact \
  --seed      1 \
  --bkg-mode  negweight-refined \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
