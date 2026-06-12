#!/bin/bash
#SBATCH --job-name=budgetfps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=48G --time=01:00:00
#SBATCH --output=uq_fps/budgetfps_%j.out --error=uq_fps/budgetfps_%j.err

# Final combined FPS budget: C_syst (187-universe sweep) + norm + C_stat
# (bootstrap) + C_ML (split seedscan) -- the FPS analogue of
# sbatch_combine_4d_budget.sh. (Hist names inside stay the generic
# hCov_universe4d_*/hCov_combined4d_total the analyzer writes.)
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/universe_stage2_fps
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing" >&2; exit 2; }
[[ -s uq_cov_stat_fps.root ]] || { echo "[FAIL] uq_cov_stat_fps.root missing" >&2; exit 2; }
[[ -s uq_cov_mlsplit_fps.root ]] || { echo "[FAIL] uq_cov_mlsplit_fps.root missing" >&2; exit 2; }
NUNI=$(ls uq_fps/universe_sweep/fps2d_xsec_*_uni_full_*.root 2>/dev/null | grep -v _CV.root | wc -l)
(( NUNI == 187 )) || { echo "[FAIL] sweep incomplete: ${NUNI}/187 universes" >&2; exit 2; }
python3 analyze_universes_nd.py \
  --cv "${CV}" \
  --glob 'uq_fps/universe_sweep/fps2d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 \
  --bootstrap-cov uq_cov_stat_fps.root:hCov_statfps_reported uq_cov_mlsplit_fps.root:hCov_mlsplitfps_reported \
  --outdir uq_fps/universe_stage2_fps/ --out-root uq_universe_fps_covariance_combined.root
