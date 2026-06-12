#!/bin/bash
#SBATCH --job-name=covtoyfps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=04:00:00
#SBATCH --array=1-200%32
#SBATCH --output=uq_fps/covtoyfps_%a_%A.out --error=uq_fps/covtoyfps_%a_%A.err

# FPS coverage toys (FPS_PILOT.md "new validation"): 200 closure+bootstrap toys
# on the extended grid, npz-based (mirrors the 2D recipe at N=200). Analysis +
# published/extension region split: fps_extension_validation.py --toys-glob.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p cov_fps
OUT="cov_fps/res_toy_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists)"; exit 0; }
python3 coverage_toy_nd.py --npz of_inputs_fps.npz \
  --seed $((SLURM_ARRAY_TASK_ID + 1000)) --iters 5 --out "${OUT}"
