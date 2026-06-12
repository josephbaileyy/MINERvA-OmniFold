#!/bin/bash
#SBATCH --job-name=covana_fps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=48G --time=00:30:00
#SBATCH --output=uq_fps/covana_fps_%j.out --error=uq_fps/covana_fps_%j.err

# FPS coverage verdict: per-bin coverage over the 200 closure+bootstrap toys,
# published vs extension region split (target 68.27%, flag <65%).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
N=$(ls cov_fps/res_toy_*.npz 2>/dev/null | wc -l)
(( N >= 190 )) || { echo "[FAIL] only ${N}/200 toys on disk" >&2; exit 2; }
python3 fps_extension_validation.py --toys-glob 'cov_fps/res_toy_*.npz' --npz of_inputs_fps.npz
