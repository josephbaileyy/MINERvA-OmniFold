#!/bin/bash
# 10-trial lgbm MEFHC 5-iter seedscan inside an existing interactive
# allocation. Mirrors seedscan/run_seedscan_interactive.sh but uses the
# production lgbm backend (matches the bootstrap + universe pipeline).
#
# Usage:
#   ./run_seedscan_lgbm_interactive.sh <INTERACTIVE_JOBID> [BATCH_WIDTH]
#
# Per-trial walltime: ~13 min at 128 threads (per bootstrap sbatch).
# Default 2-wide x 128-thread on a 256-CPU node -> 5 batches -> ~65 min.
#
# Outputs to seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed{1..10}.root.
# Per-trial logs at seedscan_lgbm/seed${N}_${TIMESTAMP}.log.

set -eo pipefail

JOBID=${1:?"need interactive jobid as arg 1"}
WIDTH=${2:-2}
TOTAL_CPUS=${TOTAL_CPUS:-256}
THREADS=$((TOTAL_CPUS / WIDTH))
TS=$(date +%Y%m%d_%H%M%S)

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OUTDIR="${DOCS}/seedscan_lgbm"
mkdir -p "${OUTDIR}"

OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

cd "${DOCS}"

echo "[seedscan-lgbm] jobid=${JOBID} width=${WIDTH} threads/trial=${THREADS}"
echo "[seedscan-lgbm] timestamp=${TS}"
echo "[seedscan-lgbm] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

START=$(date +%s)

run_trial() {
  local SEED=$1
  local LOG="${OUTDIR}/seed${SEED}_${TS}.log"
  local OUT="${OUTDIR}/2d_xsec_MEFHC_5iter_lgbm_seed${SEED}.root"
  if [[ -s "${OUT}" ]]; then
    echo "[trial seed=${SEED}] SKIP: ${OUT} already on disk" | tee "${LOG}"
    return 0
  fi
  {
    echo "[trial seed=${SEED}] start: $(date -u '+%H:%M:%S UTC')"
    T0=$(date +%s)
    srun --jobid="${JOBID}" --overlap -n 1 --cpus-per-task="${THREADS}" bash -lc "
      set -eo pipefail
      export PYTHONUNBUFFERED=1
      export OMP_NUM_THREADS=${THREADS}
      cd ${DOCS}
      source ${REPO}/setup_salloc_env.sh
      python unfold_2d_omnifold_unbinned.py \
        --omnifile  ${OMNIFILE} \
        --mcfile    ${FLUX_MC} \
        --iters     5 \
        --use-weights \
        --estimator lgbm \
        --seed      ${SEED} \
        --out       ${OUT}
    "
    T1=$(date +%s)
    echo "[trial seed=${SEED}] done: $((T1 - T0)) s"
  } > "${LOG}" 2>&1
}

SEEDS=(1 2 3 4 5 6 7 8 9 10)
for ((i = 0; i < ${#SEEDS[@]}; i += WIDTH)); do
  BATCH=("${SEEDS[@]:i:WIDTH}")
  echo "[seedscan-lgbm] batch: ${BATCH[*]}  ($(date -u '+%H:%M:%S UTC'))"
  PIDS=()
  for SEED in "${BATCH[@]}"; do
    run_trial "${SEED}" &
    PIDS+=("$!")
  done
  for PID in "${PIDS[@]}"; do
    wait "${PID}"
  done
done

END=$(date +%s)
echo "[seedscan-lgbm] all done. total wall: $((END - START)) s"
ls -lh "${OUTDIR}"/2d_xsec_MEFHC_5iter_lgbm_seed*.root 2>/dev/null || true
