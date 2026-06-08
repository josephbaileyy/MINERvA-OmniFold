#!/bin/bash
#SBATCH --job-name=pet_syst
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=uq_4d/pet_syst_%j.out
#SBATCH --error=uq_4d/pet_syst_%j.err

# PET 4D combined covariance (syst block-sum over 12 knobs + 100 flux universes,
# Poisson bootstrap stat, CV-vs-hi-iter ML band). Frozen-reweighter path: re-bins
# the fixed full-stats PET push weights per universe (no re-inference), completeness
# anchored to the validated GBDT product. All Python re-binning, ~30-40 min.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
mkdir -p uq_4d
echo "[pet_syst] start $(date -u '+%F %T UTC')"
python3 pet_systematics.py \
    --pc of_inputs_pc.npz \
    --weights products/pet/pet_weights_full.npz \
    --weights-alt products/pet/pet_weights_full_hi.npz \
    --bank bank_uthrow \
    --comp-ref products/4d/xsec_4d_MEFHC_5iter_lgbm.root \
    --nboot 100 \
    --out-root products/pet/pet_4d_covariance_combined.root
echo "[pet_syst] done $(date -u '+%F %T UTC')"
