#!/bin/bash
#SBATCH --job-name=budgetFpsC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=8 --time=00:40:00
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/budgetFpsC_%A.out --error=uq_fps/corrected/logs/budgetFpsC_%A.err
# CORRECTED FPS combined budget: C_syst (REUSED 187-universe sweep, seed-42, mean-centered
# analyze_universes_nd) + flat norm 0.014 + CORRECTED C_stat + CORRECTED C_ML ->
# uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root.
# The sweep is reused (all 187 universe unfolds + matched CV ran at --seed 42; the block
# rollup was always MAT mean-centered). Only C_stat/C_ML are the corrected regenerations.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/corrected/universe_stage2_fps
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing" >&2; exit 2; }
[[ -s uq_fps/corrected/uq_cov_stat_fps.root ]] || { echo "[FAIL] corrected uq_cov_stat_fps.root missing" >&2; exit 2; }
[[ -s uq_fps/corrected/uq_cov_mlsplit_fps.root ]] || { echo "[FAIL] corrected uq_cov_mlsplit_fps.root missing" >&2; exit 2; }
NUNI=$(ls uq_fps/universe_sweep/fps2d_xsec_*_uni_full_*.root 2>/dev/null | grep -v _CV.root | wc -l)
(( NUNI == 187 )) || { echo "[FAIL] reused sweep incomplete: ${NUNI}/187 universes" >&2; exit 2; }
python3 analyze_universes_nd.py \
  --cv "${CV}" \
  --glob 'uq_fps/universe_sweep/fps2d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 \
  --bootstrap-cov uq_fps/corrected/uq_cov_stat_fps.root:hCov_statfps_reported \
                  uq_fps/corrected/uq_cov_mlsplit_fps.root:hCov_mlsplitfps_reported \
  --outdir uq_fps/corrected/universe_stage2_fps/ --out-root uq_universe_fps_covariance_combined.root
