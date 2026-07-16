#!/bin/bash
#SBATCH --job-name=proj54dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=00:40:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/proj54dC_%j.out --error=uq_4d/corrected/logs/proj54dC_%j.err
# P7 DRY-RUN (validation only, NOT a quotable result): project the CURRENT committed
# adopted 5D covariance to a 4D marginal (drop W) as M C_5D M^T with width-weighted M,
# reporting onto the frozen 4D CV mask. Validates project_cov_nd end-to-end on real
# data (CV reproduction, PSD, mask handling). The FINAL 5D->4D marginal number waits
# for Agent A's committed selection-complete adopted 5D covariance. -> candidate path.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/projections_candidate
python3 project_cov_nd.py \
  --src-cov uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root \
  --src-hist hCov_combined5d_total_uthrow \
  --src-cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root \
  --src-axes pt,pz,eavail,q3,W --keep-axes pt,pz,eavail,q3 \
  --dst-cv products/4d/xsec_4d_MEFHC_5iter_lgbm.root \
  --out uq_4d/corrected/projections_candidate/cov_5d_to_4d_marginal_DRYRUN.root
