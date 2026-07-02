#!/bin/bash
#SBATCH --job-name=uthrow5d_block
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=80G --time=12:00:00
#SBATCH --array=0-20%10
#SBATCH --output=uq_5d/uthrow5d_block_%a_%A.out --error=uq_5d/uthrow5d_block_%a_%A.err
# Jitter-matched block-sum units for the 5D unified/block comparison: each block
# universe (12 knob +1sigma + 100 Flux) is RE-UNFOLDED at the CV seed so its
# OmniFold jitter cancels in (x_b - x_cv). task 0 = all 12 knobs; tasks 1-20 = a
# 5-flux chunk each (5x20 = 100). Combine aggregates these into C_blocksum.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_5d/block_slabs_5d
T=${SLURM_ARRAY_TASK_ID}
if [[ "$T" -eq 0 ]]; then
  python3 unified_throw_cov_5d.py --blockunits --block-knobs all --seed 1000 \
    --bank bank_uthrow_5d --iters 5 --out "uq_5d/block_slabs_5d/block5d_knobs.npz"
else
  LO=$(( (T-1) * 5 )); HI=$(( LO + 4 ))
  python3 unified_throw_cov_5d.py --blockunits --block-knobs none --block-flux ${LO}-${HI} \
    --seed 1000 --bank bank_uthrow_5d --iters 5 \
    --out "uq_5d/block_slabs_5d/block5d_flux_${T}.npz"
fi
