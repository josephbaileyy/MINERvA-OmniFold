#!/bin/bash
#SBATCH --job-name=pet_wlat
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=100G
#SBATCH --time=08:00:00
#SBATCH --output=pet_wlat_%j.out
#SBATCH --error=pet_wlat_%j.err

# KNOWN_ISSUES #3: PET-native per-lateral band via the event-aligned 5D join.
# Asserts full-row alignment (npz vs 5D tree), then 18 detector universes with
# frozen PET push weights + joined shifted coords/gates/weights -> band-summed
# C_lateral -> rebuilt combined covariance (_wlat file; old file untouched).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=32
cd "${REPO}/nd-unfolding"
echo "[pet_wlat] start $(date -u '+%F %T UTC')"
python3 pet_lateral_band.py
echo "[pet_wlat] done $(date -u '+%F %T UTC')"
