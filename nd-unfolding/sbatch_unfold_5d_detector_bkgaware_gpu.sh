#!/bin/bash
#SBATCH --job-name=det5dBKG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=04:00:00
#SBATCH --array=0-18%8
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/det5dBKG_%a_%A.out --error=uq_5d/det5dBKG_%a_%A.err
# KNOWN_ISSUES #13 LATERAL leg (2026-07-14), GPU variant. The bank sweep cannot
# carry the muon/beam bands' SHIFTED background kinematics (sim_background_<axis>_
# <band>_<idx>), so the 9 detector bands (6 muon/beam laterals + 3 GEANT = 18
# universes) + the matched CV re-run through the DIRECT driver, which threads
# --universe into collect_bkg_nd (per-universe background, unfold_nd:662). Reads the
# BKGAWARE omnifile. NON-DESTRUCTIVE outdir uq_5d/universe_sweep_bkgaware (same dir
# the 169 vertical bank-sweep universes land in -> analyze globs the union = 188).
# task 0 = matched CV (no --universe); 1-18 = detector_universes.txt. ~1h, <64GB.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
source "${REPO}/setup_salloc_env.sh"; cd "${ND}"
OMNIFILE="${ND}/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
LIST="${ND}/uq_5d/detector_universes.txt"
OUTDIR="${ND}/uq_5d/universe_sweep_bkgaware"
mkdir -p "${OUTDIR}"
[[ -s "${OMNIFILE}" ]] || { echo "[det-bkg] FAIL: bkgaware omnifile missing" >&2; exit 2; }

if [[ "${SLURM_ARRAY_TASK_ID}" -eq 0 ]]; then
  XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
  [[ -s "${XSEC_OUT}" ]] && { echo "[det-bkg] SKIP: CV exists"; exit 0; }
  echo "[det-bkg] MATCHED CV node=$(hostname) $(date -u '+%F %T UTC')"
  python3 unfold_nd_omnifold_unbinned.py \
      --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
      --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42 \
      --closure-slack 5000 \
      --out "${XSEC_OUT}"
  echo "[det-bkg] done CV $(date -u '+%F %T UTC')"; exit 0
fi

UNIVERSE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${LIST}")
[[ -z "${UNIVERSE}" ]] && { echo "[det-bkg] SKIP: index ${SLURM_ARRAY_TASK_ID} beyond list"; exit 0; }
BAND="${UNIVERSE%:*}"; UIDX="${UNIVERSE#*:}"; TAG="${BAND}_${UIDX}"
XSEC_OUT="${OUTDIR}/5d_xsec_MEFHC_5iter_lgbm_uni_full_${TAG}.root"
[[ -s "${XSEC_OUT}" ]] && { echo "[det-bkg] SKIP: ${XSEC_OUT} exists"; exit 0; }
echo "[det-bkg] universe=${UNIVERSE} node=$(hostname) task=${SLURM_ARRAY_TASK_ID} $(date -u '+%F %T UTC')"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" \
    --axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42 \
    --closure-slack 5000 \
    --universe "${UNIVERSE}" --out "${XSEC_OUT}"
echo "[det-bkg] done ${UNIVERSE} $(date -u '+%F %T UTC')"
