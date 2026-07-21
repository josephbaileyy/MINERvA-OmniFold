#!/bin/bash
#SBATCH --job-name=uthrow5d_comb
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=80G --time=04:00:00
#SBATCH --output=uq_5d/uthrow5d_comb_%j.out --error=uq_5d/uthrow5d_comb_%j.err
# Combine corrected fixed-seed 5D throws + matched block endpoints. --null
# repeats CV at the identical seed and must be zero; no jitter subtraction.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 unified_throw_cov_5d.py \
  --combine 'uq_5d/uthrow_slabs_5d/uthrow5d_slab_*.npz' \
  --expected-throws 0-159 \
  --block-slabs 'uq_5d/block_slabs_5d/block5d_*.npz' \
  --bank bank_uthrow_5d --iters 5 --null \
  --out-root uq_5d/unified_throw_cov_5d.root
