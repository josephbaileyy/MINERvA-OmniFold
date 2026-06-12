#!/bin/bash
#SBATCH --job-name=unfold5d_det
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --array=0-18%8
#SBATCH --output=uq_5d/unfold5d_det_%a_%A.out
#SBATCH --error=uq_5d/unfold5d_det_%a_%A.err

# W-resolved detector-band campaign (KNOWN_ISSUES #4 / OPEN_ITEMS #4): per-universe
# re-inference of the 9 detector bands (6 muon/beam laterals + 3 GEANT, 18 universes)
# on the full 5D axes (pt,pz,eavail,q3,W). Replaces the 4D-transferred lateral block
# in eavailW_covariance.py -- lateral universes swap the shifted pt/pz/q3/W branches
# (sim_W_<band>_<idx> etc., dumped by Workstream F); weight-only bands (GEANT,
# MinosEfficiency) fall back to CV kinematics with universe weights, exactly as in
# the 4D 187-universe sweep. Array index 0 = the MATCHED CV (same seed/config, no
# --universe) that the band differencing requires; 1-18 = detector_universes.txt.
set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
OMNIFILE="${ND}/runEventLoopOmniFold_5D_MEFHC_universes_full.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${ND}/uq_5d/detector_universes.txt"
OUTDIR="${ND}/uq_5d/universe_sweep"

[[ -s "${OMNIFILE}" ]] || { echo "[sbatch] FAIL: 5D universe omnifile missing" >&2; exit 2; }
[[ -s "${LIST}" ]] || { echo "[sbatch] FAIL: universe list missing" >&2; exit 2; }

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${ND}"

if [[ "${SLURM_ARRAY_TASK_ID}" -eq 0 ]]; then
  XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
  [[ -s "${XSEC_OUT}" ]] && { echo "[sbatch] SKIP: CV exists"; exit 0; }
  echo "[sbatch] MATCHED CV jobid=${SLURM_JOB_ID} $(date -u +%T)"
  python3 unfold_nd_omnifold_unbinned.py \
      --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
      --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42 \
      --out "${XSEC_OUT}"
  echo "[sbatch] done CV $(date -u +%T)"
  exit 0
fi

UNIVERSE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST}")
[[ -z "${UNIVERSE}" ]] && { echo "[sbatch] SKIP: index ${SLURM_ARRAY_TASK_ID} beyond list"; exit 0; }
BAND="${UNIVERSE%:*}"; UIDX="${UNIVERSE#*:}"; TAG="${BAND}_${UIDX}"
XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
[[ -s "${XSEC_OUT}" ]] && { echo "[sbatch] SKIP: ${XSEC_OUT} exists"; exit 0; }

echo "[sbatch] universe=${UNIVERSE} jobid=${SLURM_JOB_ID} task=${SLURM_ARRAY_TASK_ID} $(date -u +%T)"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
    --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42 \
    --universe "${UNIVERSE}" --out "${XSEC_OUT}"
echo "[sbatch] done ${UNIVERSE} $(date -u +%T)"
