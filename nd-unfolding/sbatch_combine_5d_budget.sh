#!/bin/bash
#SBATCH --job-name=budget5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=48G --time=01:00:00
#SBATCH --output=budget5d_%j.out --error=budget5d_%j.err
# Final combined 5D budget: C_stat (bootstrap) + C_ML (seedscan-split) built from the
# replica npz globs, then C_syst (universe sweep) + norm + C_stat + C_ML via
# analyze_universes_5d --bootstrap-cov. Produces uq_universe_5d_covariance_combined.root.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_5d/universe_stage2_5d
CV="products/5d/xsec_5d_MEFHC_5iter_lgbm.root"

python3 combine_cov_nd.py --glob 'boot_nd_5d/res_boot_*.npz' --expected-ids 1-100 --cv "${CV}" \
  --tag stat5d --out uq_cov_stat_5d.root
python3 combine_cov_nd.py --glob 'seedscan_split_5d/res_split_*.npz' --expected-ids 1-24 --cv "${CV}" \
  --tag mlsplit5d --out uq_cov_mlsplit_5d.root

python3 analyze_universes_5d.py \
  --cv "${CV}" \
  --glob 'uq_5d/universe_sweep/5d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 \
  --bootstrap-cov uq_cov_stat_5d.root:hCov_stat5d_reported \
                  uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported \
  --outdir uq_5d/universe_stage2_5d/ --out-root uq_universe_5d_covariance_combined.root
