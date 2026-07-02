#!/bin/bash
#SBATCH --job-name=pet_uthrow5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=80G --time=04:00:00
#SBATCH --output=pet_uthrow5d_%j.out --error=pet_uthrow5d_%j.err
# PET 5D frozen-reweighter unified throw + matched block-sum from the new
# bank_uthrow_5d ratios. Cheap (no re-inference). Writes
# products/pet/pet_5d_covariance_combined_unified_wlat.root.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 pet_unified_throw_5d.py --bank bank_uthrow_5d --throws 160 \
  --out-root products/pet/pet_5d_covariance_combined_unified_wlat.root
