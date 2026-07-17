#!/bin/bash
#SBATCH --job-name=combMlFpsC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=8 --time=00:20:00
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/combMlFpsC_%A.out --error=uq_fps/corrected/logs/combMlFpsC_%A.err
# CORRECTED FPS C_ML combine -> uq_fps/corrected/uq_cov_mlsplit_fps.root (exact 1-24 gate).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
N=$(ls uq_fps/corrected/seedscan_split_fps/res_split_*.npz 2>/dev/null | wc -l)
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing"; exit 2; }
(( N == 24 )) || { echo "[FAIL] expected exactly 24 corrected split files, found ${N}"; exit 2; }
python3 combine_cov_nd.py --glob 'uq_fps/corrected/seedscan_split_fps/res_split_*.npz' \
  --expected-ids 1-24 --cv "${CV}" --tag mlsplitfps --out uq_fps/corrected/uq_cov_mlsplit_fps.root
