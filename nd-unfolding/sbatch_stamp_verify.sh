#!/bin/bash
#SBATCH --job-name=stamp_verify
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=180G --time=01:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/stamp_verify_%j.out --error=uq_5d/stamp_verify_%j.err
# Verify BEN-106's provenance stamps LAND -- the first attempt printed success while all nine
# writes failed into a read-only file (TFile.Open re-points ROOT's global current directory).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=32
cd "${REPO}/nd-unfolding"
python3 adopt_unified_5d.py \
  --uthrow uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root \
  --combined uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root \
  --out uq_5d/readopt_20260811_footing/STAMPTEST2_bkgaware_meancentered.root
