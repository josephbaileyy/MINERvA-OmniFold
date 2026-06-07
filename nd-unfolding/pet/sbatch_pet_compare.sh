#!/bin/bash
#SBATCH --job-name=pet_cmp
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=pet_cmp_%j.out
#SBATCH --error=pet_cmp_%j.err

# Final point-cloud validation product after sbatch_pet_train.sh writes
# products/pet/pet_weights.npz. This is intentionally separate from the GPU training job so
# the PET-vs-GBDT plot can be rerun cheaply.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

PET_WEIGHTS="${PET_WEIGHTS:-products/pet/pet_weights.npz}"
PC_INPUTS="${PC_INPUTS:-of_inputs_pc.npz}"
GBDT_XSEC="${GBDT_XSEC:-products/4d/xsec_4d_MEFHC_5iter_lgbm.root}"
OUT_PNG="${OUT_PNG:-products/pet/pet_vs_gbdt.png}"

[[ -s "${PET_WEIGHTS}" ]] || { echo "[FAIL] missing ${PET_WEIGHTS}" >&2; exit 2; }
[[ -s "${PC_INPUTS}" ]] || { echo "[FAIL] missing ${PC_INPUTS}" >&2; exit 2; }
[[ -s "${GBDT_XSEC}" ]] || { echo "[FAIL] missing ${GBDT_XSEC}" >&2; exit 2; }

if [[ -e "${OUT_PNG}" ]]; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  mv -v "${OUT_PNG}" "${OUT_PNG}.stale_${stamp}"
fi

echo "[pet-cmp] start $(date -u '+%F %T UTC')"
python3 pet/pet_vs_gbdt.py \
  --pet "${PET_WEIGHTS}" \
  --pc "${PC_INPUTS}" \
  --gbdt "${GBDT_XSEC}" \
  --out "${OUT_PNG}"
echo "[pet-cmp] wrote ${OUT_PNG}"
echo "[pet-cmp] done $(date -u '+%F %T UTC')"
