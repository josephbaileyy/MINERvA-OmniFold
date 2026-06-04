#!/bin/bash
#SBATCH --job-name=budget4d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=32G --time=00:45:00
#SBATCH --output=budget4d_%j.out --error=budget4d_%j.err
# Final combined 4D budget: C_syst (sweep) + norm + C_stat + C_ML(split), via
# analyze_universes_nd --bootstrap-cov. Produces the publishable 4D covariance.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/universe_stage2_4d
python3 analyze_universes_nd.py \
  --cv xsec_4d_MEFHC_5iter_lgbm.root \
  --glob 'uq_4d/universe_sweep/4d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 \
  --bootstrap-cov uq_cov_stat_4d.root:hCov_stat4d_reported uq_cov_mlsplit_4d.root:hCov_mlsplit4d_reported \
  --outdir uq_4d/universe_stage2_4d/ --out-root uq_universe_4d_covariance_combined.root
