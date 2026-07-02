#!/bin/bash
#SBATCH --job-name=adopt5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=01:00:00
#SBATCH --output=uq_5d/adopt5d_%j.out --error=uq_5d/adopt5d_%j.err
# D5: adopt the 5D unified-throw inflation into the combined GBDT 5D covariance
# (PSD-safe fractional-transfer, mirrors adopt_unified_4d.py). ~5 GB peak, few min.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 adopt_unified_5d.py
