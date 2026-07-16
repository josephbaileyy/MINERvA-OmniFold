#!/bin/bash
#SBATCH --job-name=cv4dpilot
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/cv4dpilot_%j.out --error=uq_4d/corrected/logs/cv4dpilot_%j.err
# P6-4D: validate the from-5D-assembled 4D throw bank reproduces the frozen 4D
# central unfold (one OmniFold re-unfold at CV weights). GPU host cores, m3246_g.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 pilot_cv_check_4d.py
