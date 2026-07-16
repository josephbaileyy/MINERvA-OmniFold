#!/bin/bash
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold; source "$REPO/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
cd "$REPO/nd-unfolding"; mkdir -p uq_4d/corrected/universe_stage2_4d
CV="products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
echo "[budget] C_ML $(date -u +%T)"; python3 combine_cov_nd.py --glob 'uq_4d/corrected/seedscan_split_4d/res_split_*.npz' --expected-ids 1-24 --cv "$CV" --tag mlsplit4d --out uq_4d/corrected/uq_cov_mlsplit_4d.root
echo "[budget] C_stat $(date -u +%T)"; python3 combine_cov_nd.py --glob 'uq_4d/corrected/boot_nd_4d/res_boot_*.npz' --expected-ids 1-100 --cv "$CV" --tag stat4d --out uq_4d/corrected/uq_cov_stat_4d.root
echo "[budget] combined $(date -u +%T)"; python3 analyze_universes_nd.py --cv "$CV" --glob 'uq_4d/universe_sweep/4d_xsec_*_uni_full_*.root' --add-norm 0.014 --bootstrap-cov uq_4d/corrected/uq_cov_stat_4d.root:hCov_stat4d_reported uq_4d/corrected/uq_cov_mlsplit_4d.root:hCov_mlsplit4d_reported --outdir uq_4d/corrected/universe_stage2_4d/ --out-root uq_universe_4d_covariance_combined.root
echo "[budget] DONE $(date -u +%T)"
