#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:45:00
#SBATCH --array=0-10
#SBATCH -J qpsign
#SBATCH -o batch-%A_%a.log
set -eo pipefail
cd /pscratch/sd/j/josephrb/precharge-101kGc
playlists=(1A 1B 1C 1D 1E 1F 1G 1M 1N 1O 1P)
bash run.sh "${playlists[$SLURM_ARRAY_TASK_ID]}"
