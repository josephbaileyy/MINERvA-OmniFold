#!/bin/bash
#SBATCH --job-name=unfold2d_postfix
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=36:00:00
#SBATCH --output=unfold2d_postfix_%j.out
#SBATCH --error=unfold2d_postfix_%j.err

# Phase 16 post-fix re-run: MEHFC 5-iter with the OmniFold input-completeness
# correction (Phase 16 of 2D_OMNIFOLD_RUN_LOG.md). Output goes to a new
# filename so the pre-fix baseline (2d_crossSection_omnifold_MEHFC_5iter.root)
# is preserved for comparison.
#
# Predicted result (verify_eff_fix_predicted_xsec.py):
#   sigma_total / paper = 0.989 (was 0.745).
#   Per-strip post/paper ratios collapse from 0.572-0.984 to ~1.00-1.14.

set -eo pipefail

export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

OMNIFILE="runEventLoopOmniFold_MEHFC.root"
MCFILE="baseline_flux/runEventLoopMC_MEHFC.root"
OUT="2d_crossSection_omnifold_MEHFC_5iter_postfix.root"
ITERS=5

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] input:   ${OMNIFILE}"
echo "[sbatch] mcfile:  ${MCFILE}  (POT(data)-weighted 12-playlist flux)"
echo "[sbatch] iters:   ${ITERS}"
echo "[sbatch] out:     ${OUT}  (post Phase-16 fix)"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

python unfold_2d_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" \
    --mcfile "${MCFILE}" \
    --iters "${ITERS}" \
    --use-weights \
    --out "${OUT}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final: ${REPO}/2d-unfolding/${OUT}"
