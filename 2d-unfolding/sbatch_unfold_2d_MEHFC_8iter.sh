#!/bin/bash
#SBATCH --job-name=unfold_MEHFC_8
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=36:00:00
#SBATCH --output=unfold_MEHFC_8iter_%j.out
#SBATCH --error=unfold_MEHFC_8iter_%j.err

# 2D OmniFold 8-iteration MEHFC unfold (Phase-18.2 pipeline).
# Parallel companion to the 5-iter production run (sbatch_unfold_2d_MEHFC.sh).
# Motivated by the 1A iter-scan: 5-iter has 1.54% per-bin RMS vs 10-iter
# asymptote; 8-iter tightens this to 0.55%, isolating residual paper
# disagreement to physics rather than unfolding under-convergence.
#
# Per-iter cost on 128 CPUs ~3h50m; 8 iters ~30h40m; 36h walltime gives
# ~5h margin.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEHFC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEHFC.root"
XSEC_OUT="${DOCS}/2d_crossSection_omnifold_MEHFC_8iter.root"

source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] flux mc:  ${FLUX_MC}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile "${OMNIFILE}" \
  --mcfile   "${FLUX_MC}" \
  --iters 8 \
  --use-weights \
  --out      "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
