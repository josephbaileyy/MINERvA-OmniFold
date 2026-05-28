#!/bin/bash
# Backward seed runner for the HistGBT MEFHC 5-iter ML-stochasticity scan.
#
# Runs seeds 10,9,8,7 inside an existing interactive allocation while the
# sbatch array 53192001 is left to dispatch 5,6 (lower IDs are first in
# squeue, so they have the best shot of running before maintenance). Both
# paths converge on identical seed{N}.root files because random_state is
# pinned, so any sbatch/interactive overlap is harmless.
#
# 2-wide x 64 threads: fewer concurrent processes than the 4-wide x 32
# attempt that saturated memory bandwidth.
#
# Usage:
#   ./run_seedscan_backward.sh <INTERACTIVE_JOBID>

set -eo pipefail

JOBID=${1:?"need interactive jobid as arg 1"}
WIDTH=2
THREADS=$((128 / WIDTH))
TS=$(date +%Y%m%d_%H%M%S)

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OUTDIR="${DOCS}/seedscan"
mkdir -p "${OUTDIR}"

OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

cd "${DOCS}"

echo "[backward] jobid=${JOBID} width=${WIDTH} threads/trial=${THREADS}"
echo "[backward] timestamp=${TS}"
echo "[backward] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

START=$(date +%s)

run_trial() {
  local SEED=$1
  local LOG="${OUTDIR}/seed${SEED}_${TS}.log"
  local OUT="${OUTDIR}/2d_crossSection_omnifold_MEFHC_5iter_seed${SEED}.root"
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
        --estimator hist \
        --seed      ${SEED} \
        --out       ${OUT}
    "
    T1=$(date +%s)
    echo "[trial seed=${SEED}] done: $((T1 - T0)) s"
  } > "${LOG}" 2>&1
}

SEEDS=(10 9 8 7)
for ((i = 0; i < ${#SEEDS[@]}; i += WIDTH)); do
  BATCH=("${SEEDS[@]:i:WIDTH}")
  echo
  echo "[backward] batch start ($(date -u '+%H:%M:%S UTC')): seeds=${BATCH[*]}"
  PIDS=()
  for SEED in "${BATCH[@]}"; do
    run_trial "${SEED}" &
    PIDS+=($!)
  done
  for PID in "${PIDS[@]}"; do
    wait "${PID}"
  done
  echo "[backward] batch done ($(date -u '+%H:%M:%S UTC'))"
  for SEED in "${BATCH[@]}"; do
    F="${OUTDIR}/2d_crossSection_omnifold_MEFHC_5iter_seed${SEED}.root"
    if [[ -s "${F}" ]]; then
      echo "  [ok] seed=${SEED} -> ${F##*/} ($(du -h "${F}" | cut -f1))"
    else
      echo "  [MISSING] seed=${SEED}"
    fi
  done
done

END=$(date +%s)
echo
echo "[backward] all done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[backward] total wallclock: $((END - START)) s"
