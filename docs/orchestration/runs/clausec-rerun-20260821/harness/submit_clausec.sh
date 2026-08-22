#!/bin/bash
#SBATCH --job-name=clausec
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=06:00:00
#SBATCH --output=/pscratch/sd/j/josephrb/clausec-rerun-20260821-sandbox/clausec_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/clausec-rerun-20260821-sandbox/clausec_%j.err
# EXPIRY CLAUSE (c) RERUN -- fresh non-builder, read-only against a clean detached worktree.
# Reads the real 892 MB archive. DOES NOT open, move, regenerate or delete the 41.44 GB combined
# intermediate; every write is under the sandbox below.
#
# NOTE ON `BASH_SOURCE`: this script does NOT use it. Slurm executes a COPY at
# /var/spool/slurmd/job<N>/slurm_script, so `dirname "${BASH_SOURCE[0]}"` would be the spool path.
# Every path here is absolute and stated.
export HOME=/global/homes/j/josephrb
export WT=/pscratch/sd/j/josephrb/clausec-rerun-20260821
export SB=/pscratch/sd/j/josephrb/clausec-rerun-20260821-sandbox
export HARNESS="$SB/harness"
# env BEFORE `set -u`, and the source is never piped: setup_salloc_env.sh trips an unset-var check
# and a pipeline would hide its status.
set +u
source "$WT/setup_salloc_env.sh"
set -u
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 MKL_NUM_THREADS=32
echo "[job] $(date -u '+%F %T UTC') host $(hostname) job ${SLURM_JOB_ID:-none}"
echo "[job] python3 $(command -v python3)"
bash "$HARNESS/run_arms.sh"
RC=$?
echo "[job] run_arms.sh exit $RC"
echo "[job] $(date -u '+%F %T UTC') done"
exit $RC
