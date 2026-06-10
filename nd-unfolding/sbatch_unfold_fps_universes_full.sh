#!/bin/bash
#SBATCH --job-name=unfoldfps_uni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --array=0-187%32
#SBATCH --output=uq_fps/unfoldfps_uni_%a_%A.out
#SBATCH --error=uq_fps/unfoldfps_uni_%a_%A.err

# FPS systematic campaign: per-(band,idx) universe sweep on the FPS 2D extended
# grid. Mirrors sbatch_unfold_4d_universes_full.sh; the FPS flags add the
# extended edges + theta-gate lift; lateral universes swap the shifted pt/pz
# branches exactly as in 4D. Array index 0 = the MATCHED CV (no --universe,
# same omnifile/seed/config) required by analyze_universes_nd.py;
# indices 1-187 = the universe list.
set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
OMNIFILE="${ND}/runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${REPO}/3d-unfolding/uq_3d/universes_full_list.txt"
OUTDIR="${ND}/uq_fps/universe_sweep"

PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"

[[ -s "${OMNIFILE}" ]] || { echo "[sbatch] FAIL: FPS universe omnifile missing" >&2; exit 2; }
[[ -s "${LIST}" ]] || { echo "[sbatch] FAIL: universe list missing" >&2; exit 2; }

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${ND}"

if [[ "${SLURM_ARRAY_TASK_ID}" -eq 0 ]]; then
  XSEC_OUT="${OUTDIR}/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
  [[ -s "${XSEC_OUT}" ]] && { echo "[sbatch] SKIP: CV exists"; exit 0; }
  echo "[sbatch] MATCHED CV jobid=${SLURM_JOB_ID} $(date -u +%T)"
  python3 unfold_nd_omnifold_unbinned.py \
      --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" --axes "" \
      --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" \
      --iters 5 --use-weights --estimator lgbm --seed 42 \
      --out "${XSEC_OUT}"
  echo "[sbatch] done CV $(date -u +%T)"
  exit 0
fi

UNIVERSE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST}")
[[ -z "${UNIVERSE}" ]] && { echo "[sbatch] SKIP: index ${SLURM_ARRAY_TASK_ID} beyond list"; exit 0; }
BAND="${UNIVERSE%:*}"; UIDX="${UNIVERSE#*:}"; TAG="${BAND}_${UIDX}"
XSEC_OUT="${OUTDIR}/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
[[ -s "${XSEC_OUT}" ]] && { echo "[sbatch] SKIP: ${XSEC_OUT} exists"; exit 0; }

echo "[sbatch] universe=${UNIVERSE} jobid=${SLURM_JOB_ID} task=${SLURM_ARRAY_TASK_ID} $(date -u +%T)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" --axes "" \
    --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" \
    --iters 5 --use-weights --estimator lgbm --seed 42 \
    --universe "${UNIVERSE}" --out "${XSEC_OUT}"
echo "[sbatch] done ${UNIVERSE} $(date -u +%T)"
