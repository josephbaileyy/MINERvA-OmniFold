#!/bin/bash
#SBATCH --job-name=asm4d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=00:30:00
#SBATCH --output=uq_4d/asm4d_%A.out
#SBATCH --error=uq_4d/asm4d_%A.err

# Orchestrator (runs afterok the td_q3 dump): assemble the 4D unified-throw bank, then
# submit the 4D throw + block arrays, with the combine chained afterok on both. One
# self-contained chain to the rigorous 4D unified covariance (task 14).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

echo "[asm4d] assembling bank_uthrow_4d $(date -u '+%F %T UTC')"
python3 assemble_bank_4d.py

echo "[asm4d] submitting 4D throw + block arrays"
JID_THROW=$(sbatch --parsable sbatch_uthrow_cov_4d.sh)
JID_BLOCK=$(sbatch --parsable sbatch_uthrow_block_4d.sh)
echo "[asm4d] throw array=${JID_THROW} block array=${JID_BLOCK}"
JID_COMB=$(sbatch --parsable --dependency=afterok:${JID_THROW}:${JID_BLOCK} sbatch_uthrow_combine_4d.sh)
echo "[asm4d] combine=${JID_COMB} (afterok throw+block)"
echo "[asm4d] done $(date -u '+%F %T UTC')"
