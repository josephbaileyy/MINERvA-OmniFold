#!/bin/bash
#SBATCH --job-name=sweepbank_run
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=02:00:00
#SBATCH --output=sweepbank_run_%j.out --error=sweepbank_run_%j.err
# usage: sbatch sbatch_sweep_bank_run.sh BAND:IDX  (validation / future re-runs)
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 sweep_bank.py --run --universe "$1" --bankdir bank_sweep
