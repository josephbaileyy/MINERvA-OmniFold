#!/bin/bash
#SBATCH --job-name=csplit_fps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=32G --time=00:30:00
#SBATCH --output=uq_fps/csplit_fps_%j.out --error=uq_fps/csplit_fps_%j.err

# C_ML (FPS): combine the 24 train/test-split seedscan runs (split band, the
# methodology-stance ML band). Reported mask from the sweep's matched CV.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
N=$(ls seedscan_split_fps/res_split_*.npz 2>/dev/null | wc -l)
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing" >&2; exit 2; }
(( N == 24 )) || { echo "[FAIL] expected exactly 24 split files, found ${N}" >&2; exit 2; }
python3 combine_cov_nd.py --glob 'seedscan_split_fps/res_split_*.npz' \
  --expected-ids 1-24 --cv "${CV}" --tag mlsplitfps --out uq_cov_mlsplit_fps.root
