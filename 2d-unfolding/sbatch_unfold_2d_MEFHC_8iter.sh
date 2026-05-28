#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_8
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --output=unfold_MEFHC_8iter_%j.out
#SBATCH --error=unfold_MEFHC_8iter_%j.err

# 2D OmniFold 8-iteration MEFHC unfold, HistGBT estimator (Phase-18.2).
# Companion to the 5-iter seedscan trials (HistGBT) so iter-count delta is
# measured with the same estimator on both sides (no estimator/iter-count
# confound).
#
# Background: an earlier exact-GBT 8-iter attempt (job 53159240) was on
# track for ~40 h and was cancelled at iter 3/8 once HistGBT was validated
# 1:1 against exact (see Task #16 / RUN_LOG 2026-05-19).
#
# Per-trial seedscan baseline: 17m33s for 5 iters at 32 CPUs (HistGBT).
# 8 iters ≈ 28 min; 1 h walltime gives ~2x margin.
#
# Seed pinned to 1 to match seedscan seed1 for a clean 5-iter vs 8-iter
# comparison at fixed ML stochasticity.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
XSEC_OUT="${DOCS}/2d_crossSection_omnifold_MEFHC_8iter.root"

source "${REPO}/setup_salloc_env.sh"
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
  --iters     8 \
  --use-weights \
  --estimator hist \
  --seed      1 \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
