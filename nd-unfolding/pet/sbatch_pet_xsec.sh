#!/bin/bash
#SBATCH --job-name=pet_xsec
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --output=pet_xsec_%j.out --error=pet_xsec_%j.err
# Absolute PET cross section + milestone gates. Reads the full-stats push weights from
# sbatch_pet_train.sh (--reweight-all) and runs pet_vs_gbdt.py --absolute:
#   * normal weights -> absolute PET dsigma vs the frozen GBDT (PET/GBDT total ~1).
#   * closure weights (CLOSURE=1) -> recovered/truth ~1 with completeness=1.
# Separate from the GPU job so the absolute extraction can be rerun cheaply.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

PC_INPUTS="${PC_INPUTS:-of_inputs_pc.npz}"
GBDT_XSEC="${GBDT_XSEC:-products/4d/xsec_4d_MEFHC_5iter_lgbm.root}"
[[ -s "${PC_INPUTS}" ]] || { echo "[FAIL] missing ${PC_INPUTS}" >&2; exit 2; }
[[ -s "${GBDT_XSEC}" ]] || { echo "[FAIL] missing ${GBDT_XSEC}" >&2; exit 2; }

if [[ "${CLOSURE:-0}" == "1" ]]; then
  PET_WEIGHTS="${PET_WEIGHTS:-products/pet/pet_weights_closure.npz}"
  [[ -s "${PET_WEIGHTS}" ]] || { echo "[FAIL] missing ${PET_WEIGHTS}" >&2; exit 2; }
  echo "[pet-xsec] CLOSURE check $(date -u '+%F %T UTC')"
  python3 pet/pet_vs_gbdt.py --pet "${PET_WEIGHTS}" --pc "${PC_INPUTS}" --gbdt "${GBDT_XSEC}" \
    --absolute --closure --pet-out products/pet/xsec_4d_PET_closure.root
else
  PET_WEIGHTS="${PET_WEIGHTS:-products/pet/pet_weights_full.npz}"
  PET_OUT="${PET_OUT:-products/pet/xsec_4d_PET_absolute.root}"
  OUT_PNG="${OUT_PNG:-products/pet/pet_vs_gbdt_absolute.png}"
  [[ -s "${PET_WEIGHTS}" ]] || { echo "[FAIL] missing ${PET_WEIGHTS}" >&2; exit 2; }
  echo "[pet-xsec] ABSOLUTE PET vs GBDT $(date -u '+%F %T UTC')"
  python3 pet/pet_vs_gbdt.py --pet "${PET_WEIGHTS}" --pc "${PC_INPUTS}" --gbdt "${GBDT_XSEC}" \
    --absolute --pet-out "${PET_OUT}" --out "${OUT_PNG}"
fi
echo "[pet-xsec] done $(date -u '+%F %T UTC')"
