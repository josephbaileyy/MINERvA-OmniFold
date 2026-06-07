#!/bin/bash
#SBATCH --job-name=cov4d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=48G --time=01:00:00
#SBATCH --output=cov4d_%j.out --error=cov4d_%j.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/universe_stage2_4d
python3 analyze_universes_nd.py \
  --cv products/4d/xsec_4d_MEFHC_5iter_lgbm.root \
  --glob 'uq_4d/universe_sweep/4d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 --outdir uq_4d/universe_stage2_4d/
