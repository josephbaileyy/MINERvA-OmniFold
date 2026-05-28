#!/bin/bash
# Stage-2 publication-grade final rollup. Run AFTER:
#   1. runEventLoopOmniFold_MEFHC_universes_full.root is on disk
#      (sbatch_hadd_MEFHC_universes_full.sh has completed).
#   2. sbatch_unfold_2d_MEFHC_5iter_universes_full.sh array has drained
#      (all uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root files present).
#   3. sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh has completed.
#      This matched CV uses the same full universe omnifile, lgbm backend,
#      seed, iteration count, and weights as the universe sweep.
#   4. All 300 bootstrap toys on disk (already true 2026-05-23).
#   5. lgbm seedscan trials on disk (already true 2026-05-23).
#
# Steps:
#   a) Compute ML-noise covariance from the 10 lgbm seedscan trials.
#   b) Refresh bootstrap covariance so grouped universe plots can include
#      the statistical component.
#   c) Compute full-universe covariance (per-band + total) from the
#      universe sweep outputs.
#   d) Re-run compare_to_paper_fullcov.py with three uncorrelated
#      OmniFold-derived covariances added to the paper TotalCov:
#        - universe cov (full vertical + lateral set)
#        - bootstrap cov (N=300)
#        - ML-noise cov (lgbm seedscan n=10)
#
# Writes a fresh combined-cov log; the chi^2/ndf is the publication-grade
# headline.

set -eo pipefail
cd "$(dirname "$0")/.."  # 2d-unfolding/

REPO="$(cd .. && pwd)"
DOCS="$(pwd)"

OMNIFILE_FULL="${DOCS}/runEventLoopOmniFold_MEFHC_universes_full.root"
SWEEP_GLOB="uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root"
FULL_CV_ROOT="uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
BOOT_GLOB="uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root"
SEEDSCAN_GLOB="seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed*.root"

UNIV_OUTDIR="uq/universe_stage2_MEFHC_full"
BOOT_OUTDIR="uq/bootstrap_MEFHC_300"
ML_OUTDIR="uq/seedscan_lgbm_ml"
LOG_OUT="${UNIV_OUTDIR}/compare_to_paper_combined_cov_full.log"

# --- preconditions
[[ -s "${OMNIFILE_FULL}" ]] || { echo "FAIL: missing ${OMNIFILE_FULL}"; exit 2; }
[[ -s "${FULL_CV_ROOT}" ]] || {
  echo "FAIL: missing matched full-universe CV ${FULL_CV_ROOT}"
  echo "Run: sbatch sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh"
  exit 2
}
N_SWEEP=$(find uq -maxdepth 1 -name '2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root' ! -name '2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root' | wc -l)
N_BOOT=$(ls ${BOOT_GLOB} 2>/dev/null | wc -l)
N_SEED=$(ls ${SEEDSCAN_GLOB} 2>/dev/null | wc -l)
echo "[preflight] universe sweep ROOTs : ${N_SWEEP}"
echo "[preflight] matched full CV ROOT : ${FULL_CV_ROOT}"
echo "[preflight] bootstrap ROOTs       : ${N_BOOT}"
echo "[preflight] seedscan lgbm ROOTs   : ${N_SEED}"
if (( N_SWEEP < 100 )); then
  echo "FAIL: too few universe sweep ROOTs (need >100, have ${N_SWEEP})"
  exit 2
fi
if (( N_BOOT < 300 )); then
  echo "WARN: bootstrap ROOT count below 300 (have ${N_BOOT}); using what's on disk"
fi
if (( N_SEED < 10 )); then
  echo "WARN: seedscan ROOT count below 10 (have ${N_SEED}); using what's on disk"
fi

source "${REPO}/setup_salloc_env.sh"

archive_old_full_rollup() {
  local archive_dir="${UNIV_OUTDIR}/archive_baseline_mismatch_$(date -u '+%Y%m%d_%H%M%S')"
  local moved=0
  local path
  for path in \
    "${UNIV_OUTDIR}/uq_universe_covariance_full.root" \
    "${UNIV_OUTDIR}/uq_universe_summary.txt" \
    "${UNIV_OUTDIR}/compare_to_paper_combined_cov_full.log" \
    "${UNIV_OUTDIR}/uq_universe_band_pt.png" \
    "${UNIV_OUTDIR}/uq_universe_band_pz.png" \
    "MEFHC_5iter_pull_full.png"; do
    if [[ -e "${path}" ]]; then
      mkdir -p "${archive_dir}"
      mv "${path}" "${archive_dir}/"
      moved=1
    fi
  done
  if (( moved )); then
    echo "[archive] moved previous baseline-mismatched full rollup artifacts to ${archive_dir}"
  fi
}

archive_old_full_rollup

# --- (a) ML-noise covariance
echo
echo "===== (a) ML-noise covariance from lgbm seedscan ====="
mkdir -p "${ML_OUTDIR}"
python uq/analyze_uq.py \
  --glob "${SEEDSCAN_GLOB}" \
  --outdir "${ML_OUTDIR}" \
  --out-root "uq_covariance_ml.root"

# --- (b) Bootstrap covariance with N=300 already on disk (refresh)
echo
echo "===== (b) Bootstrap N=300 covariance (refresh) ====="
mkdir -p "${BOOT_OUTDIR}"
python uq/analyze_uq.py \
  --glob "${BOOT_GLOB}" \
  --outdir "${BOOT_OUTDIR}" \
  --out-root "uq_covariance_boot300.root"

# --- (c) Full universe covariance (per-band + total)
echo
echo "===== (c) Full universe covariance ====="
mkdir -p "${UNIV_OUTDIR}"
# analyze_universes.py expects a CV reference for the per-band delta. It
# must be matched to the universe sweep settings; using the exact-GBT
# production CV here injects a common backend/seed baseline into every
# paired systematic band.
python uq/analyze_universes.py \
  --glob "${SWEEP_GLOB}" \
  --cv "${FULL_CV_ROOT}" \
  --bootstrap-cov "${BOOT_OUTDIR}/uq_covariance_boot300.root" \
  --outdir "${UNIV_OUTDIR}" \
  --out-root "uq_universe_covariance_full.root"

# --- (d) Combined-cov chi^2/ndf vs paper
echo
echo "===== (d) Combined-cov chi^2/ndf vs paper ====="
python compare_to_paper_fullcov.py \
  --omnifold-cov "${UNIV_OUTDIR}/uq_universe_covariance_full.root:hCov_universe_total" \
  --omnifold-cov "${BOOT_OUTDIR}/uq_covariance_boot300.root:hCov2D_reported" \
  --omnifold-cov "${ML_OUTDIR}/uq_covariance_ml.root:hCov2D_reported" \
  2>&1 | tee "${LOG_OUT}"

echo
echo "===== DONE ====="
echo "headline log: ${LOG_OUT}"
