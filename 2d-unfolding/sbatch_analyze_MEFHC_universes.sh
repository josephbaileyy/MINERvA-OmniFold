#!/bin/bash
#SBATCH --job-name=analyze_MEFHC_uni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=analyze_MEFHC_uni_%j.out
#SBATCH --error=analyze_MEFHC_uni_%j.err

# Stage-2 rollup of MEFHC universe sweep + combined-cov chi^2/ndf vs
# arXiv:2106.16210 paper. Designed to run as
#   sbatch --dependency=afterok:<sweep>,<CV> sbatch_analyze_MEFHC_universes.sh
# after both 53325509 (110-task universe sweep) and the companion CV unfold
# complete.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"

CV_ROOT="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_CV.root"
GLOB="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_*.root"
OUTDIR="${DOCS}/uq/universe_stage2_MEFHC"
BOOT_COV="${DOCS}/uq/uq_covariance.root"

echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] CV ROOT:    ${CV_ROOT}"
echo "[sbatch] glob:       ${GLOB}"
echo "[sbatch] outdir:     ${OUTDIR}"

# Step 1: universe-cov rollup (per-band + total).
ARGS=(--cv "${CV_ROOT}"
      --glob "${GLOB}"
      --outdir "${OUTDIR}")
if [[ -s "${BOOT_COV}" ]]; then
  ARGS+=(--bootstrap-cov "${BOOT_COV}")
  echo "[sbatch] including bootstrap-cov: ${BOOT_COV}"
fi
python uq/analyze_universes.py "${ARGS[@]}"

# Step 2: combined-cov chi^2/ndf vs paper. The hook accepts a repeatable
# --omnifold-cov ROOT:HIST spec. Use the rollup output hCov_universe_total
# alongside the existing bootstrap-cov contribution.
UNI_COV_ROOT="${OUTDIR}/uq_universe_covariance.root"
if [[ -s "${UNI_COV_ROOT}" ]]; then
  python compare_to_paper_fullcov.py \
      --omnifold-cov "${UNI_COV_ROOT}:hCov_universe_total" \
      ${BOOT_COV:+--omnifold-cov "${BOOT_COV}:hCov2D_reported"} \
      | tee "${OUTDIR}/compare_to_paper_combined_cov.log"
fi

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
