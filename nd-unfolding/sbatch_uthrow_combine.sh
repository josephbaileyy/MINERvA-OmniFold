#!/bin/bash
#SBATCH --job-name=uthrow_comb
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=48G --time=01:00:00
#SBATCH --output=uthrow_comb_%j.out --error=uthrow_comb_%j.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
python3 unified_throw.py --combine --bankdir bank_uthrow
