#!/bin/bash
# Run the 10-trial HistGBT MEFHC 5-iter seedscan inside an existing
# interactive allocation, 4-wide × 32-thread for full-node throughput.
#
# Usage:
#   ./run_seedscan_interactive.sh <INTERACTIVE_JOBID> [BATCH_WIDTH]
#
# Args:
#   INTERACTIVE_JOBID  SLURM jobid of the running interactive allocation
#                      (single-node, full-node 128 CPUs).
#   BATCH_WIDTH        Optional. Default 4. How many trials run in
#                      parallel per batch. 4 * 32 = 128 = full node.
#
# Per-trial walltime: ~17m33s (measured on the 5-iter validation run).
# Total wall:
#   BATCH_WIDTH=4 -> 3 batches (4,4,2) -> ~52 min
#   BATCH_WIDTH=5 -> 2 batches (5,5) -> ~40-45 min, but threads drop to
#                    25 each (sublinear scaling means per-trial may slow
#                    slightly).
#
# Outputs to seedscan/2d_crossSection_omnifold_MEFHC_5iter_seed{1..10}.root.
# Per-trial logs at seedscan/seed${N}_${TIMESTAMP}.log.

set -eo pipefail

JOBID=${1:?"need interactive jobid as arg 1"}
WIDTH=${2:-4}
THREADS=$((128 / WIDTH))
TS=$(date +%Y%m%d_%H%M%S)

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OUTDIR="${DOCS}/seedscan"
mkdir -p "${OUTDIR}"

OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

cd "${DOCS}"

echo "[seedscan] jobid=${JOBID} width=${WIDTH} threads/trial=${THREADS}"
echo "[seedscan] timestamp=${TS}"
echo "[seedscan] master log will gather per-trial completions"
echo "[seedscan] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

START=$(date +%s)
BATCH_PIDS=()

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

# 10 trials in batches of WIDTH.
SEEDS=(1 2 3 4 5 6 7 8 9 10)
for ((i = 0; i < ${#SEEDS[@]}; i += WIDTH)); do
  BATCH=("${SEEDS[@]:i:WIDTH}")
  echo
  echo "[seedscan] batch start ($(date -u '+%H:%M:%S UTC')): seeds=${BATCH[*]}"
  PIDS=()
  for SEED in "${BATCH[@]}"; do
    run_trial "${SEED}" &
    PIDS+=($!)
  done
  for PID in "${PIDS[@]}"; do
    wait "${PID}"
  done
  echo "[seedscan] batch done ($(date -u '+%H:%M:%S UTC'))"
  # Quick status: which seed roots are now on disk
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
echo "[seedscan] all done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[seedscan] total wallclock: $((END - START)) s"
echo "[seedscan] outputs in: ${OUTDIR}"
