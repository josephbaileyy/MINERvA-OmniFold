#!/bin/bash
#SBATCH --job-name=ew_cov
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=06:00:00
#SBATCH --output=ew_cov_%j.out
#SBATCH --error=ew_cov_%j.err

# Task 13: (E_avail,W) frozen-reweighter block-sum covariance + per-generator significance,
# on the merged 5D _universes_full omnifile. One CV unfold (frozen push weights) then 13 knob
# + 100 flux re-binned universes -> C_syst, + diagonal stat + transferred 4D laterals -> C_total,
# then chi^2 / N-sigma of unfolded data vs GENIE-CV/+MEC/NuWro/GiBUU in the high-W DIS corner.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=32
cd "${REPO}/nd-unfolding"
echo "[ew_cov] start $(date -u '+%F %T UTC')"
python3 eavailW_covariance.py \
    --omnifile runEventLoopOmniFold_5D_MEFHC_universes_full.root \
    --out products/5d/eavailW_covariance.root
echo "[ew_cov] done $(date -u '+%F %T UTC')"
