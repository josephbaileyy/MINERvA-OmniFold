#!/bin/bash
#SBATCH --job-name=analyze_MEFHC_final
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=analyze_MEFHC_final_%j.out
#SBATCH --error=analyze_MEFHC_final_%j.err

# Final-rollup follow-up. Designed to fire on
#   sbatch --dependency=afterok:53327775 sbatch_analyze_MEFHC_final.sh
# after the bootstrap scale-up (seeds 51-300) completes.
#
# Pipeline:
#   1. analyze_uq.py over all N=300 bootstrap ROOTs -> refreshed
#      uq/uq_covariance.root (with hCov2D_reported updated).
#   2. analyze_universes.py over the universe sweep, picking up the
#      refreshed bootstrap-cov -> updated uq_universe_covariance.root
#      + summary + band plots in uq/universe_stage2_MEFHC/.
#   3. compare_to_paper_fullcov.py with both OmniFold covs -> the
#      Stage-2 final combined-cov chi^2/ndf headline.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"

CV_ROOT="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_CV.root"
UNI_GLOB="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_*.root"
BOOT_GLOB="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root"
OUTDIR="${DOCS}/uq/universe_stage2_MEFHC"
BOOT_COV="${DOCS}/uq/uq_covariance.root"

echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] universe CV: ${CV_ROOT}"
echo "[sbatch] universe glob: ${UNI_GLOB}"
echo "[sbatch] bootstrap glob: ${BOOT_GLOB}"

# Step 1: refresh bootstrap covariance from the full N=300 set.
NBOOT=$(ls ${BOOT_GLOB} 2>/dev/null | wc -l)
echo "[sbatch] bootstrap ROOTs found: ${NBOOT}"
python uq/analyze_uq.py \
    --glob "${BOOT_GLOB}" \
    --outdir "${DOCS}/uq" \
    --out-root "uq_covariance.root" \
    | tee "${DOCS}/uq/analyze_uq_N${NBOOT}.log"

# Step 2: universe-cov rollup, picks up the refreshed bootstrap-cov.
ARGS=(--cv "${CV_ROOT}"
      --glob "${UNI_GLOB}"
      --outdir "${OUTDIR}"
      --bootstrap-cov "${BOOT_COV}")
echo "[sbatch] including bootstrap-cov: ${BOOT_COV}"
python uq/analyze_universes.py "${ARGS[@]}"

# Step 3: combined-cov chi^2/ndf vs paper.
UNI_COV_ROOT="${OUTDIR}/uq_universe_covariance.root"
python compare_to_paper_fullcov.py \
    --omnifold-cov "${UNI_COV_ROOT}:hCov_universe_total" \
    --omnifold-cov "${BOOT_COV}:hCov2D_reported" \
    | tee "${OUTDIR}/compare_to_paper_combined_cov.log"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
