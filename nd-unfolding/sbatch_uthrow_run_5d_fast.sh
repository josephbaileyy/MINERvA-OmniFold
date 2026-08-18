#!/bin/bash
#SBATCH --job-name=uthrow5d_runF
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=90G --time=06:00:00
#SBATCH --array=0-39%40
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/uthrow5d_runF_%a_%A.out --error=uq_5d/uthrow5d_runF_%a_%A.err
# FAST variant of sbatch_uthrow_run_5d.sh (school account, 2026-07-12).
# 40 tasks x 4 throws = 160 throws, offsets t*4..t*4+3 -> union 0-159. Fine-grained
# + %40 all-concurrent on `shared` QOS (backfills even with a jammed queue) to
# beat the 6-in-flight interactive path. Writes to a SEPARATE dir so the batch
# id-layout (4 throws/file) never collides with the interactive layout (1/file);
# do_combine hard-fails on duplicate throw ids, so the two must stay in separate
# globs. Atomic-save (os.replace) means a wall-kill re-runs the whole task cleanly.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=32 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
       NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
cd "${REPO}/nd-unfolding"; mkdir -p uq_5d/uthrow_slabs_5d_sb
source "${REPO}/lib/resume_guard.sh"
source "${REPO}/nd-unfolding/lib_member_resume.sh"; mr_require_valid_offset   # M(ii) member axis
SLAB_DIR="$(mr_dir_prefix uq_5d/uthrow_slabs_5d_sb)"
OFF=$(( SLURM_ARRAY_TASK_ID * 4 ))
# M(ii) OFFSET HOOK (spec (B) option (ii), BEN-461). The launcher keeps its OWN baseline
# literal, so MNV_EST_SEED_OFFSET=0 -- the default -- reproduces the archive EXACTLY and the
# two coherence groups are preserved BY CONSTRUCTION rather than by the driver getting it
# right: one offset in, each leg adds it to its own baseline. Do not replace this with an
# absolute-seed override; that hands the group structure back to the caller.
EST_SEED=$(( 1000 + ${MNV_EST_SEED_OFFSET:-0} ))
python3 unified_throw_cov_5d.py --throws 4 --throw-offset ${OFF} --draw-seed 1000 --estimator-seed ${EST_SEED} \
  --bank bank_uthrow_5d --iters 5 --invalid-ratio neutral \
  --out "${SLAB_DIR}/uthrow5d_slab_${SLURM_ARRAY_TASK_ID}.npz"
