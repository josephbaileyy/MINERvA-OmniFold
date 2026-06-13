#!/bin/bash
#SBATCH --job-name=ew_cov_wlat
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=230G
#SBATCH --time=06:00:00
#SBATCH --output=ew_cov_wlat_%j.out
#SBATCH --error=ew_cov_wlat_%j.err

# KNOWN_ISSUES #4 closure: rebuild the (E_avail,W) covariance with the W-resolved
# detector block from the 5D per-universe sweep (sbatch_unfold_5d_detector.sh)
# in place of the 4D-transferred lateral approximation. Writes a NEW output
# (_wlat) so the pre-fix product stays for comparison; the script prints the
# old-vs-new lateral comparison before adopting.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND="${REPO}/nd-unfolding"
SWEEP="${ND}/uq_5d/universe_sweep"
CVF="${SWEEP}/5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"

NUNI=$(ls "${SWEEP}"/5d_xsec_MEFHC_5iter_lgbm_uni_full_*.root 2>/dev/null | grep -cv "_CV.root" || true)
[[ -s "${CVF}" ]] || { echo "[ew_wlat] FAIL: matched sweep CV missing" >&2; exit 2; }
[[ "${NUNI}" -ge 18 ]] || { echo "[ew_wlat] FAIL: only ${NUNI}/18 sweep universes on disk" >&2; exit 2; }

source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=32
cd "${ND}"
echo "[ew_wlat] start $(date -u '+%F %T UTC') sweep universes=${NUNI}"
python3 eavailW_covariance.py \
    --omnifile runEventLoopOmniFold_5D_MEFHC_universes_full.root \
    --lateral-sweep-cv "${CVF}" \
    --lateral-sweep-glob "${SWEEP}/5d_xsec_MEFHC_5iter_lgbm_uni_full_*.root" \
    --out products/5d/eavailW_covariance_wlat.root
echo "[ew_wlat] done $(date -u '+%F %T UTC')"
