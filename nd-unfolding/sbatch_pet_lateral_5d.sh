#!/bin/bash
#SBATCH --job-name=pet_lat5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=120G --time=08:00:00
#SBATCH --output=pet_lat5d_%j.out --error=pet_lat5d_%j.err
# PET 5D NATIVE LATERAL block (9 detector bands via the event-aligned 5D join,
# shifted-W joined from MC_W_<band>_<idx>). Reads the vertical combined cov and
# writes products/pet/pet_5d_covariance_combined_wlat.root. Run after (afterok)
# the vertical job. Reads the 142 GB 5D omnifile column-wise -> 120G.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"

python3 pet_lateral_band_5d.py \
  --combined products/pet/pet_5d_covariance_combined.root \
  --out-root products/pet/pet_5d_covariance_combined_wlat.root
