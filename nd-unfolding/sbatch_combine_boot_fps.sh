#!/bin/bash
#SBATCH --job-name=cboot_fps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=32G --time=00:30:00
#SBATCH --output=uq_fps/cboot_fps_%j.out --error=uq_fps/cboot_fps_%j.err

# C_stat (FPS): combine the 100 bootstrap replicas. Reported mask from the
# sweep's matched CV (same mask as the block-sum covariance).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
N=$(ls boot_nd_fps/res_boot_*.npz 2>/dev/null | wc -l)
[[ -s "${CV}" ]] || { echo "[FAIL] matched CV missing" >&2; exit 2; }
(( N >= 90 )) || { echo "[FAIL] only ${N}/100 bootstrap replicas on disk" >&2; exit 2; }
python3 combine_cov_nd.py --glob 'boot_nd_fps/res_boot_*.npz' \
  --cv "${CV}" --tag statfps --out uq_cov_stat_fps.root
