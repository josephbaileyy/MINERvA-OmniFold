#!/bin/bash
#SBATCH --job-name=combStatFpsC
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=48G --time=00:20:00
#SBATCH --nice=0
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/combStatFpsC_%A.out --error=uq_fps/corrected/logs/combStatFpsC_%A.err
# CORRECTED FPS C_stat combine -> uq_fps/corrected/uq_cov_stat_fps.root (exact 1-100 gate).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
N=$(ls uq_fps/corrected/boot_nd_fps/res_boot_*.npz 2>/dev/null | wc -l)
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing"; exit 2; }
(( N == 100 )) || { echo "[FAIL] expected exactly 100 corrected bootstrap files, found ${N}"; exit 2; }
python3 combine_cov_nd.py --glob 'uq_fps/corrected/boot_nd_fps/res_boot_*.npz' \
  --expected-ids 1-100 --cv "${CV}" --tag statfps --out uq_fps/corrected/uq_cov_stat_fps.root
