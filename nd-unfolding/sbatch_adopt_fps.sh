#!/bin/bash
#SBATCH --job-name=adoptfps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=48G --time=00:30:00
#SBATCH --output=uq_fps/adoptfps_%j.out --error=uq_fps/adoptfps_%j.err

# FPS unified-throw adoption (the 4D-style block-sum vs unified-throw decision):
# transfer the throw's per-bin sigma inflation onto the sweep's vertical block
# (adopt_unified_4d.py is path-parametrized; the analyzer's generic *4d* hist
# names apply to the FPS file too). If the FPS inflation is ~1 the block sum is
# validated; if >1 the adopted file is the publishable FPS covariance, as in 4D.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
COMB="uq_fps/universe_stage2_fps/uq_universe_fps_covariance_combined.root"
UTH="uq_fps/unified_throw_cov_fps.root"
for f in "${CV}" "${COMB}" "${UTH}"; do
  [[ -s "${f}" ]] || { echo "[FAIL] missing ${f}" >&2; exit 2; }
done
python3 adopt_unified_4d.py --uthrow "${UTH}" --combined "${COMB}" --prod "${CV}" \
  --out uq_fps/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow.root
