#!/bin/bash
# Stage-1.5 Flux PPFX ramp.
#
# Stage-1 left us with only Flux idx 0 and 50 (N=2 per-band cov is noisy).
# This script runs 28 additional PPFX indices, linspace-spaced across
# 0..99, so analyze_universes.py has ~30 Flux universes to compute a
# sample covariance over.
#
# Usage:
#   ./uq/run_flux_ramp_interactive.sh <JOBID> [SEED=42]
set -eo pipefail

JOBID="${1:?usage: $0 <INTERACTIVE_JOBID> [SEED=42]}"
SEED="${2:-42}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_1A_universes.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_1A.root"

# linspace(0, 99, 30) rounded, with 0 excluded (already done in Stage-1).
# Resulting list of 29 new indices; combined with existing {0, 50}
# (50 is not in the linspace) gives 31 unique Flux indices.
FLUX_IDX=(3 7 10 14 17 20 24 27 31 34 38 41 44 48 51 55 58 61 65 68 72 75 79 82 85 89 92 96 99)

mkdir -p "${DOCS}/uq"
TS="$(date -u +%Y%m%d_%H%M%S)"
MASTER_LOG="${DOCS}/uq/flux_ramp_${TS}.log"
echo "[flux-ramp] start=$(date -u '+%Y-%m-%d %H:%M:%S UTC') JOBID=${JOBID} SEED=${SEED} N=${#FLUX_IDX[@]}" | tee "${MASTER_LOG}"

for i in "${!FLUX_IDX[@]}"; do
  IDX="${FLUX_IDX[$i]}"
  TAG="Flux_${IDX}"
  XSEC_OUT="${DOCS}/uq/2d_xsec_1A_5iter_lgbm_uni_${TAG}.root"
  PER_LOG="${DOCS}/uq/uni_${TAG}_${TS}.log"

  if [[ -f "${XSEC_OUT}" ]]; then
    echo "[flux-ramp] [$((i+1))/${#FLUX_IDX[@]}] SKIP existing ${XSEC_OUT}" | tee -a "${MASTER_LOG}"
    continue
  fi

  echo "[flux-ramp] [$((i+1))/${#FLUX_IDX[@]}] universe=Flux:${IDX} -> ${XSEC_OUT}" | tee -a "${MASTER_LOG}"
  srun --jobid="${JOBID}" --overlap -n 1 --cpus-per-task=128 bash -lc "
    set -eo pipefail
    export PYTHONUNBUFFERED=1
    export OMP_NUM_THREADS=128
    source ${REPO}/setup_salloc_env.sh
    cd ${DOCS}
    python unfold_2d_omnifold_unbinned.py \
      --omnifile  ${OMNIFILE} \
      --mcfile    ${FLUX_MC} \
      --iters     5 \
      --use-weights \
      --estimator lgbm \
      --universe  Flux:${IDX} \
      --seed      ${SEED} \
      --out       ${XSEC_OUT}
  " 2>&1 | tee "${PER_LOG}" >> "${MASTER_LOG}"
done

echo "[flux-ramp] end=$(date -u '+%Y-%m-%d %H:%M:%S UTC')" | tee -a "${MASTER_LOG}"
ls -lh "${DOCS}"/uq/2d_xsec_1A_5iter_lgbm_uni_Flux_*.root 2>/dev/null | tee -a "${MASTER_LOG}"
