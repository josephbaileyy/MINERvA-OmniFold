#!/bin/bash
# 5D budget assembly (CPU work) run via interactive-GPU CPU fallback (2026-07-13):
# the CPU m3246 queue is unusable (--test-only start estimate Aug 31, exhausted
# fairshare), so run these on a GPU node's host cores via salloc+srun --gres=none.
# Mirrors sbatch_combine_5d_budget.sh exactly. School-acct HOME/ROOT fix inline;
# NO set -u (breaks conda activate).
set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "$REPO/nd-unfolding"; mkdir -p uq_5d/universe_stage2_5d
CV="products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
echo "[budget] start $(date -u +%T) on $(hostname)"
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
echo "[budget] done $(date -u +%T)"
