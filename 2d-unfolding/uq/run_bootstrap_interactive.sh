#!/bin/bash
# Run N Poisson-weight bootstrap replicas inside an existing interactive
# allocation, batched WIDTH-wide × (128/WIDTH)-threads-per-trial.
#
# Usage:
#   ./run_bootstrap_interactive.sh <INTERACTIVE_JOBID> <DATASET> [WIDTH] \
#       [SEED_LO] [SEED_HI] [ESTIMATOR]
#
# Args:
#   INTERACTIVE_JOBID  SLURM jobid of the running interactive allocation
#                      (single-node, full-node 128 CPUs).
#   DATASET            "1A" or "MEFHC" (selects omnifile / flux MC).
#   WIDTH              Optional. Default 4. Parallel trials per batch.
#   SEED_LO            Optional. Default 1. First bootstrap seed.
#   SEED_HI            Optional. Default 5. Last bootstrap seed (inclusive).
#   ESTIMATOR          Optional. Default lgbm. Passed to --estimator.
#
# Outputs to uq/2d_xsec_<DATASET>_5iter_<EST>_boot{N}.root.
# Per-trial logs at uq/boot${N}_${TIMESTAMP}.log.

set -eo pipefail

JOBID=${1:?"need interactive jobid as arg 1"}
DSET=${2:?"need dataset as arg 2 (1A or MEFHC)"}
WIDTH=${3:-4}
SEED_LO=${4:-1}
SEED_HI=${5:-5}
EST=${6:-lgbm}
THREADS=$((128 / WIDTH))
TS=$(date +%Y%m%d_%H%M%S)

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OUTDIR="${DOCS}/uq"
mkdir -p "${OUTDIR}"

OMNIFILE="${DOCS}/runEventLoopOmniFold_${DSET}.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_${DSET}.root"

if [[ ! -s "${OMNIFILE}" ]]; then
  echo "[FAIL] missing omnifile ${OMNIFILE}" >&2
  exit 1
fi
if [[ ! -s "${FLUX_MC}" ]]; then
  echo "[FAIL] missing flux mc ${FLUX_MC}" >&2
  exit 1
fi

cd "${DOCS}"

echo "[boot] jobid=${JOBID} dataset=${DSET} width=${WIDTH} "\
"threads/trial=${THREADS} seeds=${SEED_LO}..${SEED_HI} est=${EST}"
echo "[boot] timestamp=${TS}"
echo "[boot] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

START=$(date +%s)

run_trial() {
  local SEED=$1
  local LOG="${OUTDIR}/boot${SEED}_${DSET}_${EST}_${TS}.log"
  local OUT="${OUTDIR}/2d_xsec_${DSET}_5iter_${EST}_boot${SEED}.root"
  {
    echo "[trial boot=${SEED}] start: $(date -u '+%H:%M:%S UTC')"
    T0=$(date +%s)
    srun --jobid="${JOBID}" --overlap -n 1 --cpus-per-task="${THREADS}" bash -lc "
      set -eo pipefail
      export PYTHONUNBUFFERED=1
      export OMP_NUM_THREADS=${THREADS}
      cd ${DOCS}
      source ${REPO}/setup_salloc_env.sh
      python unfold_2d_omnifold_unbinned.py \
        --omnifile        ${OMNIFILE} \
        --mcfile          ${FLUX_MC} \
        --iters           5 \
        --use-weights \
        --estimator       ${EST} \
        --bootstrap-seed  ${SEED} \
        --seed            1 \
        --out             ${OUT}
    "
    T1=$(date +%s)
    echo "[trial boot=${SEED}] done: $((T1 - T0)) s"
  } > "${LOG}" 2>&1
}

# Run seeds [SEED_LO..SEED_HI] in batches of WIDTH.
SEEDS=()
for ((s = SEED_LO; s <= SEED_HI; s += 1)); do
  SEEDS+=("${s}")
done

for ((i = 0; i < ${#SEEDS[@]}; i += WIDTH)); do
  BATCH=("${SEEDS[@]:i:WIDTH}")
  echo
  echo "[boot] batch start ($(date -u '+%H:%M:%S UTC')): seeds=${BATCH[*]}"
  PIDS=()
  for SEED in "${BATCH[@]}"; do
    run_trial "${SEED}" &
    PIDS+=($!)
  done
  for PID in "${PIDS[@]}"; do
    wait "${PID}"
  done
  echo "[boot] batch done ($(date -u '+%H:%M:%S UTC'))"
  for SEED in "${BATCH[@]}"; do
    F="${OUTDIR}/2d_xsec_${DSET}_5iter_${EST}_boot${SEED}.root"
    if [[ -s "${F}" ]]; then
      echo "  [ok] boot=${SEED} -> ${F##*/} ($(du -h "${F}" | cut -f1))"
    else
      echo "  [MISSING] boot=${SEED}"
    fi
  done
done

END=$(date +%s)
echo
echo "[boot] all done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[boot] total wallclock: $((END - START)) s"
echo "[boot] outputs in: ${OUTDIR}"
