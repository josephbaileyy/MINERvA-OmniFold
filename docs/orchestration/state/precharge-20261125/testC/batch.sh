#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 04:00:00
#SBATCH -J precharge_c
#SBATCH -o /pscratch/sd/j/josephrb/precharge-testC-20261126/logs/%x-%A_%a.log
# Test C array. Task i runs playlist PLS[i] in the mode given as $1 (reco or truth).
# The time limit is set per submission (see DECLARATION.md, "Cluster request").
set -eo pipefail
mode=$1
[[ $mode == reco || $mode == truth ]] || exit 2
cd /pscratch/sd/j/josephrb/precharge-testC-20261126
PLS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
bash run.sh "$mode" "${PLS[$SLURM_ARRAY_TASK_ID]}"
