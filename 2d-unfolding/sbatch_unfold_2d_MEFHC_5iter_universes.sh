#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_uni
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-110%30
#SBATCH --output=unfold_MEFHC_uni%a_%A.out
#SBATCH --error=unfold_MEFHC_uni%a_%A.err

# 2D OmniFold MEFHC 5-iter universe sweep (Stage-2 systematic universes).
#
# 110 unfolds total on the new runEventLoopOmniFold_MEFHC_universes.root
# omnifile (built 2026-05-23 by sbatch 53319019+53319020, 63.71 GB):
#   - Flux:0 through Flux:99  (100 PPFX universes)
#   - MaCCQE:0,1              (+/- 1 sigma)
#   - Rvp1pi:0,1              (+/- 1 sigma)
#   - Rvn1pi:0,1              (+/- 1 sigma)
#   - MinosEfficiency:0,1     (+/- 1 sigma)
#   - Muon_Energy_MINOS:0,1   (+/- 1 sigma)
#
# Each task is one full MEFHC 5-iter unfold with --universe BAND:IDX, no
# bootstrap. Per-task wall ~ 13 min at 128 CPU (lgbm). Concurrency capped
# at 30 (%30 in --array) to be kind to the scheduler. With 30 concurrent
# the total wall is ~4 waves * 15 min = ~1 hour.
#
# Output: uq/2d_xsec_MEFHC_5iter_lgbm_uni_<BAND>_<IDX>.root (110 files).
# Rollup: uq/analyze_universes.py.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC_universes.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

# Universe table: 110 entries. SLURM_ARRAY_TASK_ID 1..110 maps to the
# corresponding entry below. Order matters; keep it stable so re-runs
# under the same task id reproduce the same output.
UNIVERSES=()
for i in $(seq 0 99); do
  UNIVERSES+=("Flux:${i}")
done
UNIVERSES+=("MaCCQE:0" "MaCCQE:1")
UNIVERSES+=("Rvp1pi:0" "Rvp1pi:1")
UNIVERSES+=("Rvn1pi:0" "Rvn1pi:1")
UNIVERSES+=("MinosEfficiency:0" "MinosEfficiency:1")
UNIVERSES+=("Muon_Energy_MINOS:0" "Muon_Energy_MINOS:1")

if (( ${#UNIVERSES[@]} != 110 )); then
  echo "[sbatch] ERROR: expected 110 universes, got ${#UNIVERSES[@]}" >&2
  exit 2
fi

IDX=$((SLURM_ARRAY_TASK_ID - 1))
UNIVERSE="${UNIVERSES[$IDX]}"
if [[ -z "${UNIVERSE}" ]]; then
  echo "[sbatch] ERROR: no UNIVERSE entry for array task ${SLURM_ARRAY_TASK_ID}" >&2
  exit 2
fi

BAND="${UNIVERSE%:*}"
UIDX="${UNIVERSE#*:}"
TAG="${BAND}_${UIDX}"
XSEC_OUT="${DOCS}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_${TAG}.root"

# Skip if this output already exists (safe re-submit).
if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk"
  exit 0
fi

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
