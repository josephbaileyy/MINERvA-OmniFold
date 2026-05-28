#!/bin/bash
#SBATCH --job-name=coverage_MEFHC
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-20%10
#SBATCH --output=coverage_MEFHC_%a_%A.out
#SBATCH --error=coverage_MEFHC_%a_%A.err

# Stage-1 plan deliverable #5 — coverage toys on MEFHC.
#
# Per toy: closure-mode unfold with --bootstrap-seed N. Closure provides
# the MC truth marginal as known reference; the per-toy Poisson resampling
# on (measured, w_truth, w_reco) provides independent data-stat + MC-stat
# realizations. Across 20 toys, the spread of unfolded values around the
# CV MC truth tests whether the bootstrap covariance correctly covers
# the true truth.
#
# The --closure + --bootstrap-seed combo intentionally breaks the strict
# closure invariant (step-1 reweight = 1 per event), modelling instead a
# scenario where data and MC come from the same parent but are drawn
# independently.
#
# Per-task wall ~ 13 min at 128 CPU (lgbm). Concurrency capped at 10 to
# share scheduler with the 110-task universe sweep already in flight.
# Total wall ~2 waves * 15 min = ~30 min.
#
# Output: uq/coverage/2d_xsec_MEFHC_5iter_lgbm_coverage_toy<N>.root
# Rollup: uq/coverage_toys.py.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

# Seed offset chosen so toy seeds don't collide with the 1..50 used by
# sbatch_unfold_2d_MEFHC_5iter_bootstrap.sh (real-data bootstrap). The
# Poisson sub-RNGs inside the Python driver use seed and seed+1e7, so
# 1000 is a safe headroom.
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
