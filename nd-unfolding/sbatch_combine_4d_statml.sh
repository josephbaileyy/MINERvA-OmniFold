#!/bin/bash
#SBATCH --job-name=comb4d_statml
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=24G --time=00:30:00
#SBATCH --output=comb4d_statml_%j.out --error=comb4d_statml_%j.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
python3 combine_cov_nd.py --glob 'seedscan_split_4d/res_split_*.npz' --cv xsec_4d_MEFHC_5iter_lgbm.root --tag mlsplit4d --out uq_cov_mlsplit_4d.root
python3 combine_cov_nd.py --glob 'boot_nd_4d/res_boot_*.npz' --cv xsec_4d_MEFHC_5iter_lgbm.root --tag stat4d --out uq_cov_stat_4d.root
