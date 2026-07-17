#!/bin/bash
#SBATCH --job-name=adoptFpsC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=8 --time=00:20:00
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/adoptFpsC_%A.out --error=uq_fps/corrected/logs/adoptFpsC_%A.err
# CORRECTED FPS unified-throw adoption (4D-style PSD-preserving inflation transfer onto
# the sweep vertical block). If FPS inflation ~1 the block-sum is validated; if >1 the
# adopted file is the publishable pre-lateral FPS covariance. adopt_unified_4d.py is
# path-parametrized (its generic *4d* hist names apply to the FPS file too).
# -> uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow.root
# NOTE: this is the VERTICAL+stat+ML adopted covariance. The selection-complete FPS
# LATERAL replacement (P4-FPS) and FINAL adoption are a SEPARATE step gated on P3F.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
COMB="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root"
UTH="uq_fps/corrected/unified_throw_cov_fps.root"
for f in "${CV}" "${COMB}" "${UTH}"; do
  [[ -s "${f}" ]] || { echo "[FAIL] missing ${f}" >&2; exit 2; }
done
python3 adopt_unified_4d.py --uthrow "${UTH}" --combined "${COMB}" --prod "${CV}" \
  --out uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow.root
