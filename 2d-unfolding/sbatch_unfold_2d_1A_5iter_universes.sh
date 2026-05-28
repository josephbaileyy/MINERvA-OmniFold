#!/bin/bash
#SBATCH --job-name=unfold_1A_uni
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-12
#SBATCH --output=unfold_1A_uni%a_%A.out
#SBATCH --error=unfold_1A_uni%a_%A.err

# 2D OmniFold 1A 5-iter universe unfolds (Stage-1 UQ #2, dev set).
#
# Each array task unfolds ONE universe (band,idx). Per-event MC weights
# in the omnifile carry per-universe replacements written by the C++
# event loop under MNV101_DUMP_UNIVERSES; the Python driver swaps
# w_truth / w_reco for the named universe at --universe BAND:IDX.
#
# Stage-1 unfold list (12 universes): Flux idx {0,50}, MaCCQE +/-1 sigma,
# Rvp1pi +/-1 sigma, Rvn1pi +/-1 sigma, MinosEfficiency +/-1 sigma,
# Muon_Energy_MINOS +/-1 sigma. CV unfold is separate (omit --universe).
#
# Prereq: runEventLoopOmniFold_1A_universes.root must already carry
# columns w_truth_<band>_<idx> and w_reco_<band>_<idx> for every band:idx
# below. Produced by uq/run_universe_omnifile_1A.sh with allowlist
# Flux,MaCCQE,Rvp1pi,Rvn1pi,MinosEfficiency,Muon_Energy_MINOS.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_1A_universes.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_1A.root"

# Universe table: index = SLURM_ARRAY_TASK_ID, value = "BAND:IDX". Keep
# in sync with --array range above.
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

IDX=$((SLURM_ARRAY_TASK_ID - 1))
UNIVERSE="${UNIVERSES[$IDX]}"
if [[ -z "${UNIVERSE}" ]]; then
  echo "[sbatch] ERROR: no UNIVERSE entry for array task ${SLURM_ARRAY_TASK_ID}"
  exit 2
fi

BAND="${UNIVERSE%:*}"
UIDX="${UNIVERSE#*:}"
TAG="${BAND}_${UIDX}"
XSEC_OUT="${DOCS}/uq/2d_xsec_1A_5iter_lgbm_uni_${TAG}.root"

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${DOCS}/uq"
cd "${DOCS}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] universe: ${UNIVERSE} (tag=${TAG})"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] flux mc:  ${FLUX_MC}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_2d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator lgbm \
  --universe  "${UNIVERSE}" \
  --seed      42 \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
