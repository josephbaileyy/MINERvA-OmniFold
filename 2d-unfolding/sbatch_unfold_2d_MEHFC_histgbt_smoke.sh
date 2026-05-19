#!/bin/bash
#SBATCH --job-name=histgbt_smoke
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --output=histgbt_smoke_%j.out
#SBATCH --error=histgbt_smoke_%j.err

# HistGBT smoke test: 1-iter MEHFC unfold on the real Phase-18.2 input.
# Goal is wallclock + sanity, not science:
#   - Confirm HistGradientBoosting{Classifier,Regressor} train end-to-end on
#     the full 32.85M-event MC + 4.09M-event measured dataset.
#   - Time per-iter vs the ~3h50m / iter exact-GBT baseline.
#   - Verify hUnfold2D / hXSec2D integrals land in a sane neighborhood of
#     the production 5-iter result (within early-iteration drift, not exact).
#
# OMP_NUM_THREADS=32 lines up with --cpus-per-task. HistGBT scales sub-
# linearly past ~16-32 threads on 2 features, so a 128-CPU request would
# burn allocation for marginal wall benefit.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEHFC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEHFC.root"
XSEC_OUT="${DOCS}/histgbt_smoke/2d_crossSection_omnifold_MEHFC_1iter_histgbt_smoke.root"

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/histgbt_smoke"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

START_EPOCH=$(date +%s)
python unfold_2d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     1 \
  --use-weights \
  --estimator hist \
  --seed      1 \
  --out       "${XSEC_OUT}"
END_EPOCH=$(date +%s)

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] wallclock: $((END_EPOCH - START_EPOCH)) s"
