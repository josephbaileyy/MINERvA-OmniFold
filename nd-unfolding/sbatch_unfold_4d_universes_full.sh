#!/bin/bash
#SBATCH --job-name=unfold4d_uni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --array=1-200%32
#SBATCH --output=unfold4d_uni_%a_%A.out
#SBATCH --error=unfold4d_uni_%a_%A.err

# q3 systematic campaign: full per-(band,idx) universe sweep on the 4D dump-all
# omnifile. Mirrors sbatch_unfold_3d_MEFHC_5iter_universes_full.sh but uses the nd
# driver with --axes eavail,q3 and the new --universe path (lateral bands swap
# pt/pz AND q3; eavail stays CV). --seed 42 fixed across universes. Same 187-line
# band:idx list as the 3D campaign.
set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
OMNIFILE="${ND}/runEventLoopOmniFold_4D_MEFHC_universes_full.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${REPO}/3d-unfolding/uq_3d/universes_full_list.txt"
OUTDIR="${ND}/uq_4d/universe_sweep"

[[ -s "${OMNIFILE}" ]] || { echo "[sbatch] FAIL: 4D universe omnifile missing" >&2; exit 2; }
[[ -s "${LIST}" ]] || { echo "[sbatch] FAIL: universe list missing" >&2; exit 2; }

UNIVERSE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST}")
[[ -z "${UNIVERSE}" ]] && { echo "[sbatch] SKIP: index ${SLURM_ARRAY_TASK_ID} beyond list"; exit 0; }
BAND="${UNIVERSE%:*}"; UIDX="${UNIVERSE#*:}"; TAG="${BAND}_${UIDX}"
XSEC_OUT="${OUTDIR}/4d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
[[ -s "${XSEC_OUT}" ]] && { echo "[sbatch] SKIP: ${XSEC_OUT} exists"; exit 0; }

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${ND}"
echo "[sbatch] universe=${UNIVERSE} jobid=${SLURM_JOB_ID} task=${SLURM_ARRAY_TASK_ID} $(date -u +%T)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
    --axes eavail,q3 --iters 5 --use-weights --estimator lgbm --seed 42 \
    --universe "${UNIVERSE}" --out "${XSEC_OUT}"
echo "[sbatch] done ${UNIVERSE} $(date -u +%T)"
