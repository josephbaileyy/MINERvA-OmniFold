#!/bin/bash
#SBATCH --job-name=uthrow5d_run
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=80G --time=12:00:00
#SBATCH --array=0-19%10
#SBATCH --output=uq_5d/uthrow5d_run_%a_%A.out --error=uq_5d/uthrow5d_run_%a_%A.err
# GBDT 5D unified throw: 20 tasks x 8 throws = 160 throws. Each throw draws ALL
# vertical systematics together (1 Flux PPFX universe + 12 Gaussian knobs) and
# RE-UNFOLDS (5-iter LightGBM OmniFold) on the 5D bank -> the nonlinear cross-band
# covariance the block-sum drops. Incremental save per throw (slab survives a kill).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_5d/uthrow_slabs_5d
OFF=$(( SLURM_ARRAY_TASK_ID * 8 ))
python3 unified_throw_cov_5d.py --throws 8 --throw-offset ${OFF} --seed 1000 \
  --bank bank_uthrow_5d --iters 5 \
  --out "uq_5d/uthrow_slabs_5d/uthrow5d_slab_${SLURM_ARRAY_TASK_ID}.npz"
