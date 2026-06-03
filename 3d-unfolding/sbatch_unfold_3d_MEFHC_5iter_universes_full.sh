#!/bin/bash
#SBATCH --job-name=unfold3d_uni_full
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=02:00:00
#SBATCH --array=1-200%20
#SBATCH --output=unfold3d_uni_full_%a_%A.out
#SBATCH --error=unfold3d_uni_full_%a_%A.err

# Gap 4 of the 3D systematic-UQ campaign: full per-(band,idx) universe sweep on
# the 3D dump-all omnifile. Each array task unfolds ONE universe read from
# uq_3d/universes_full_list.txt (187 lines; identical band:idx set to the 2D
# campaign). Array upper bound (200) is generous; indices beyond the list length
# exit cleanly via the skip-if-empty guard, concurrency capped at 20 on regular QOS.
#
# Mirrors sbatch_unfold_2d_MEFHC_5iter_universes_full.sh but calls the 3D driver
# with --universe (lateral bands swap pT/pz only; E_avail stays CV per Gap 1).
# --seed 42 is fixed across all universes so GBDT randomness does not add spurious
# universe-to-universe variance (the delta is purely the systematic shift).
#
# Output: uq_3d/universe_sweep/3d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<IDX>.root
# Rollup: uq_3d/analyze_universes_3d.py (full 3D cov) + the 2D
#         ../2d-unfolding/uq/analyze_universes.py on hXSec2D (Eavail-marginal cov).

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
D3="${REPO}/3d-unfolding"
OMNIFILE="${D3}/runEventLoopOmniFold_MEFHC_3D_universes_full.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${D3}/uq_3d/universes_full_list.txt"
OUTDIR="${D3}/uq_3d/universe_sweep"

if [[ ! -s "${OMNIFILE}" ]]; then
  echo "[sbatch] FAIL: 3D universe omnifile ${OMNIFILE} missing/empty." >&2
  echo "[sbatch] Run Gap 2 first (sbatch_evloop_array_3d_universes_full.sh + hadd)." >&2
  exit 2
fi
if [[ ! -s "${LIST}" ]]; then
  echo "[sbatch] FAIL: universe list ${LIST} missing or empty." >&2
  echo "[sbatch] Run: python ../2d-unfolding/uq/gen_universe_list.py ${OMNIFILE} ${LIST}" >&2
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
XSEC_OUT="${OUTDIR}/3d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
if [[ -s "${XSEC_OUT}" ]]; then
  echo "[sbatch] SKIP: ${XSEC_OUT} already on disk"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${D3}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] universe: ${UNIVERSE} (tag=${TAG})"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] xsec out: ${XSEC_OUT}"

python unfold_3d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator lgbm \
  --universe  "${UNIVERSE}" \
  --seed      42 \
  --out       "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
