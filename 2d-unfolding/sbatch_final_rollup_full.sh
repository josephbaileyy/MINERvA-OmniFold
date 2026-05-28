#!/bin/bash
#SBATCH --job-name=final_rollup_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=final_rollup_full_%j.out
#SBATCH --error=final_rollup_full_%j.err

set -eo pipefail
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
bash uq/final_rollup_full.sh
