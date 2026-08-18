#!/bin/bash
#SBATCH --job-name=ssplit5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=03:00:00
#SBATCH --array=1-24%24
#SBATCH --output=ssplit5d_%a_%A.out --error=ssplit5d_%a_%A.err
# C_ML (train/test-split seedscan) for 5D: dimension-general seedscan_split.py on of_inputs_5d.npz.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
source "${REPO}/lib/resume_guard.sh"   # BEN-023: resume on a completion marker, not on size
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p seedscan_split_5d
source "${REPO}/nd-unfolding/lib_member_resume.sh"; mr_require_valid_offset   # M(ii) member axis
SPLIT_OUT="$(mr_prefix "seedscan_split_5d/res_split_${SLURM_ARRAY_TASK_ID}.npz")"
mr_skip_if_complete "${SPLIT_OUT}" && exit 0
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
EST_SEED=$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))
mr_run "${SPLIT_OUT}" python3 seedscan_split.py --npz of_inputs_5d.npz --split-seed ${SLURM_ARRAY_TASK_ID} --estimator-seed ${EST_SEED} \
  --train-frac 0.8 --iters 5 --out "${SPLIT_OUT}"
