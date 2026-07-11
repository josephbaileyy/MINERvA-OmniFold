#!/bin/bash
#SBATCH --job-name=unfold_MEFHC_uni_nw
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-400%30
#SBATCH --output=unfold_MEFHC_uni_full_%a_%A.out
#SBATCH --error=unfold_MEFHC_uni_full_%a_%A.err

# Stage-2 publication-grade full universe sweep on MEFHC (dump-all
# omnifile). Each array task unfolds ONE (band, idx) read from the list
# file uq/universes_full_list.txt produced by uq/gen_universe_list.py.
#
# Array upper bound (400) is generous; tasks with index > list length
# exit cleanly via the skip-if-empty check. Concurrency capped at 30 to
# share the regular QOS scheduler with other production work.
#
# Output: uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<IDX>.root
# Rollup: uq/analyze_universes.py with --glob matching the _full pattern.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC_universes_full.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${DOCS}/uq/universes_full_list.txt"

if [[ ! -s "${LIST}" ]]; then
  echo "[sbatch] FAIL: universe list ${LIST} missing or empty." >&2
  echo "[sbatch] Run: python uq/gen_universe_list.py" >&2
  exit 2
fi

UNIVERSE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST}")
if [[ -z "${UNIVERSE}" ]]; then
  echo "[sbatch] SKIP: array index ${SLURM_ARRAY_TASK_ID} beyond list length ($(wc -l < ${LIST}))"
  exit 0
fi

BAND="${UNIVERSE%:*}"
UIDX="${UNIVERSE#*:}"
TAG="${BAND}_${UIDX}"
XSEC_OUT="${DOCS}/uq/negweight_uni/2d_xsec_MEFHC_5iter_lgbm_nw_uni_${TAG}.root"

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
  --bkg-mode  negweight \
  --seed      42 \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
