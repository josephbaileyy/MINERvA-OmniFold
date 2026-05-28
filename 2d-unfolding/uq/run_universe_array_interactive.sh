#!/bin/bash
# Run the Stage-1 universe-unfold sweep inside an existing interactive
# allocation. Mirrors the sbatch array in
# sbatch_unfold_2d_1A_5iter_universes.sh but runs the 12 universes
# sequentially via one shared srun, avoiding the regular_m queue wait.
#
# Usage:
#   ./uq/run_universe_array_interactive.sh <JOBID> [SEED=42] [LO=1] [HI=12]
#
# JOBID = the interactive allocation ID. LO/HI index into the same
# UNIVERSES table as the sbatch script so you can resume partial sweeps.
set -eo pipefail

JOBID="${1:?usage: $0 <INTERACTIVE_JOBID> [SEED=42] [LO=1] [HI=12]}"
SEED="${2:-42}"
LO="${3:-1}"
HI="${4:-12}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_1A_universes.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_1A.root"

UNIVERSES=(
  "Flux:0"
  "Flux:50"
  "MaCCQE:0"
  "MaCCQE:1"
  "Rvp1pi:0"
  "Rvp1pi:1"
  "Rvn1pi:0"
  "Rvn1pi:1"
  "MinosEfficiency:0"
  "MinosEfficiency:1"
  "Muon_Energy_MINOS:0"
  "Muon_Energy_MINOS:1"
)

mkdir -p "${DOCS}/uq"
TS="$(date -u +%Y%m%d_%H%M%S)"
MASTER_LOG="${DOCS}/uq/universe_array_interactive_${TS}.log"
echo "[universe-array] start=$(date -u '+%Y-%m-%d %H:%M:%S UTC') JOBID=${JOBID} SEED=${SEED} LO=${LO} HI=${HI}" | tee "${MASTER_LOG}"

for i in $(seq "${LO}" "${HI}"); do
  IDX=$((i - 1))
  UNIVERSE="${UNIVERSES[$IDX]}"
  if [[ -z "${UNIVERSE}" ]]; then
    echo "[universe-array] no entry at index ${i}" | tee -a "${MASTER_LOG}"
    continue
  fi
  BAND="${UNIVERSE%:*}"
  UIDX="${UNIVERSE#*:}"
  TAG="${BAND}_${UIDX}"
  XSEC_OUT="${DOCS}/uq/2d_xsec_1A_5iter_lgbm_uni_${TAG}.root"
  PER_LOG="${DOCS}/uq/uni_${TAG}_${TS}.log"

  echo "[universe-array] [$i/${HI}] universe=${UNIVERSE} -> ${XSEC_OUT}" | tee -a "${MASTER_LOG}"
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
      --universe  ${UNIVERSE} \
      --seed      ${SEED} \
      --out       ${XSEC_OUT}
  " 2>&1 | tee "${PER_LOG}" >> "${MASTER_LOG}"
done

echo "[universe-array] end=$(date -u '+%Y-%m-%d %H:%M:%S UTC')" | tee -a "${MASTER_LOG}"
ls -lh "${DOCS}"/uq/2d_xsec_1A_5iter_lgbm_uni_*.root 2>/dev/null | tee -a "${MASTER_LOG}"
