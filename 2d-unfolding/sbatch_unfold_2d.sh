#!/bin/bash
#SBATCH --job-name=unfold_2d
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --time=03:00:00
#SBATCH --output=unfold_2d_%j.out
#SBATCH --error=unfold_2d_%j.err

# 2D OmniFold unfolding batch job.
# Playlist 1A, 5 iterations wall-clock ~1h45m; walltime set to 3h headroom.
# For full ME FHC (12 playlists), extend --time to 24:00:00 or split per playlist.

# Do not use `set -u` here. `conda activate root_6_28` triggers
# deactivate-root.sh, which references CONDA_BACKUP_ROOTSYS and aborts under
# nounset in a fresh batch shell.
set -eo pipefail

export PYTHONUNBUFFERED=1

cd /pscratch/sd/j/josephrb/MINERvA101

module load python
conda activate root_6_28
source OmniFold/unbinned_unfolding/build/setup.sh
source opt/bin/setup.sh

cd /pscratch/sd/j/josephrb/MINERvA101/Documents

# Pass through extra args: e.g. sbatch sbatch_unfold_2d.sh --iters 5 --out 2d_crossSection_omnifold.root
# srun omitted — --ntasks=1 doesn't need it, and inherited SRUN_CPUS_PER_TASK
# from an interactive allocation can break nested srun on Perlmutter.
python unfold_2d_omnifold_unbinned.py "$@"
