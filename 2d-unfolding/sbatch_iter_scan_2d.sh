#!/bin/bash
#SBATCH --job-name=unfold_2d_iter
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=06:00:00
#SBATCH --array=1,3,5,8,10
#SBATCH --output=iter_scan_1A_%a_%A.out
#SBATCH --error=iter_scan_1A_%a_%A.err

# 2D OmniFold iteration convergence scan on playlist 1A (Phase-18.2).
# Re-validates the 5-iter production choice now that the truth-tree-
# authoritative reco gate and native miss handling changed the OmniFold
# convergence trajectory vs the pre-Phase-16 scan that originally set 5.
#
# Array task IDs ARE the iteration counts (1, 3, 5, 8, 10).
# Each task is a single-threaded Python process; runtime scales
# roughly linearly in iterations. Pre-Phase-18 timing was ~17 min/iter;
# +33% events bumps this to ~22 min/iter, so 10-iter ≈ 3h40m. Walltime
# 6h gives margin.
#
# Partition: shared QOS + cpus-per-task=2 (one physical core w/ SMT pair).
# This is the NERSC-recommended layout for single-threaded jobs (see
# https://docs.nersc.gov/jobs/examples/#single-core-job): nodes are
# shared between users, so 5 array tasks queue independently and are
# billed only for 2 cores x wallclock each, not a full 128-core node.

set -eo pipefail  # not -u: conda's deactivate-root.sh hook references
                  # CONDA_BACKUP_ROOTSYS which is unset in a fresh env.

export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

ITER=${SLURM_ARRAY_TASK_ID}
OMNIFILE="runEventLoopOmniFold_1A.root"
MCFILE="baseline_flux/runEventLoopMC_1A.root"
OUT="2d_crossSection_omnifold_1A_${ITER}iter.root"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} iter=${ITER} out=${OUT}"
echo "[sbatch] omnifile: ${OMNIFILE}"
echo "[sbatch] mcfile:   ${MCFILE}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# For --ntasks=1 jobs, srun is redundant — the sbatch step is already a
# single process on a single node. Calling srun also trips over NERSC's
# SLURM_CPUS_PER_TASK / SLURM_TRES_PER_TASK env-var conflict:
# https://docs.nersc.gov/systems/perlmutter/known-issues/#slurm-cpus-per-task-issue
# Running python directly sidesteps the issue.
python unfold_2d_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" \
    --mcfile "${MCFILE}" \
    --iters "${ITER}" \
    --use-weights \
    --out "${OUT}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
