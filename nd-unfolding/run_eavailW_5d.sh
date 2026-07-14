#!/bin/bash
# (E_avail,W) covariance rebuild via interactive-GPU CPU fallback (2026-07-13).
# eavailW_covariance.py defaults are correct: --omnifile runEventLoopOmniFold_5D_MEFHC_
# universes_full.root, --cov4d uq_4d/.../uq_universe_4d_covariance_combined.root (laterals),
# --stat5d uq_cov_stat_5d.root (fresh), --prod5d + genie present. Frozen-reweighter
# block-sum (no re-unfolding), but reads the 170GB omnifile -> ~15-45min. HOME/ROOT
# fix inline; NO set -u. Writes products/5d/eavailW_covariance.root.
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "$REPO/nd-unfolding"
echo "[eavailW] start $(date -u +%T) on $(hostname)"
python3 eavailW_covariance.py
echo "[eavailW] done $(date -u +%T)"
