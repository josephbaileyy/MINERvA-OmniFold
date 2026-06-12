#!/bin/bash
#SBATCH --job-name=minos_qdiag
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=minos_qdiag_%j.out
#SBATCH --error=minos_qdiag_%j.err

# KNOWN_ISSUES #5 diagnostic: conditional efficiency of the official MINOS
# muon-quality cuts (quality==1, curvature significance) vs p_MINOS, data vs MC,
# over the 1A AnaTuples (xrootd). No unfold, no event-loop rebuild.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/2d-unfolding"
echo "[qdiag] start $(date -u '+%F %T UTC')"
python3 minos_quality_diagnostic.py \
    --max-mc-files 41 --max-data-files 120 \
    --out-png products/minos_quality_diagnostic.png
echo "[qdiag] done $(date -u '+%F %T UTC')"
