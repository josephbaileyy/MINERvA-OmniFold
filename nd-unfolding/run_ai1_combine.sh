#!/bin/bash
# AI1 estimator-only scan: combine the 12 fixed-data/varied-estimator replicas into a
# covariance and print its sqrt-trace for comparison vs the ML-split band (1.493e-39).
# HOME/ROOT fix inline; NO set -u.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "$REPO/nd-unfolding"
echo "[ai1-combine] start $(date -u +%T) on $(hostname)"
python3 combine_cov_nd.py --glob 'boot_nd_5d_ai1/res_ai1_*.npz' --expected-ids 1-12 \
  --cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root --tag ai1est5d --out uq_cov_ai1est_5d.root
echo "[ai1-combine] done $(date -u +%T)"
ls -la uq_cov_ai1est_5d.root 2>/dev/null
