#!/bin/bash
#SBATCH --job-name=covfps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=48G --time=02:00:00
#SBATCH --output=uq_fps/covfps_%j.out --error=uq_fps/covfps_%j.err

# FPS block-summed systematic covariance from the 187-universe sweep (+matched CV),
# per-band rollup on the extended 2D grid. Guards on a complete sweep.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/universe_stage2_fps
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
NUNI=$(ls uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root 2>/dev/null | grep -v _CV.root | wc -l)
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing"; exit 2; }
[[ ${NUNI} -eq 187 ]] || { echo "[FAIL] ${NUNI}/187 universe files on disk (sweep incomplete?)"; exit 2; }
python3 analyze_universes_nd.py \
  --cv "${CV}" \
  --glob 'uq_fps/universe_sweep/fps2d_xsec_*_uni_full_*.root' \
  --add-norm 0.014 --outdir uq_fps/universe_stage2_fps/ \
  --out-root uq_universe_fps_covariance.root
