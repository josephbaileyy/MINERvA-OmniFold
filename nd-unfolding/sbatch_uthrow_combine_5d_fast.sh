#!/bin/bash
#SBATCH --job-name=uthrow5d_combF
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G --time=03:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/uthrow5d_combF_%j.out --error=uq_5d/uthrow5d_combF_%j.err
# FAST-path combine (school account, 2026-07-12): aggregate the batch-dir throws
# (union 0-159, fixed seed 1000) + matched block endpoints into the headline ROOT.
# --null repeats CV at the identical seed and must be zero (no jitter subtraction).
# Submit with --dependency=afterok:<throwjob>:<blockjob>. Writes the SAME target
# the interactive supervisor watches, so producing it here auto-stops that loop.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
EST_SEED=$(( 1000 + ${MNV_EST_SEED_OFFSET:-0} ))
python3 unified_throw_cov_5d.py --draw-seed 1000 --estimator-seed ${EST_SEED} \
  --combine 'uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz' \
  --expected-throws 0-159 \
  --block-slabs 'uq_5d/block_slabs_5d_sb/block5d_*.npz' \
  --bank bank_uthrow_5d --iters 5 --null \
  --out-root uq_5d/unified_throw_cov_5d.root
