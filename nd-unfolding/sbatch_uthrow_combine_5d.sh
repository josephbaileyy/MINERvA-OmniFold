#!/bin/bash
#SBATCH --job-name=uthrow5d_comb
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=80G --time=04:00:00
#SBATCH --output=uq_5d/uthrow5d_comb_%j.out --error=uq_5d/uthrow5d_comb_%j.err
# Combine the 5D unified throws + jitter-matched block units -> C_unified,
# C_blocksum, C_cross + the jitter-corrected unified/block sqrt-trace ratio
# (--null re-unfolds a 2nd CV at seed+7 to measure and subtract the OmniFold
# jitter floor). Writes uq_5d/unified_throw_cov_5d.root.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 unified_throw_cov_5d.py \
  --combine 'uq_5d/uthrow_slabs_5d/uthrow5d_slab_*.npz' \
  --block-slabs 'uq_5d/block_slabs_5d/block5d_*.npz' \
  --bank bank_uthrow_5d --iters 5 --null \
  --out-root uq_5d/unified_throw_cov_5d.root
