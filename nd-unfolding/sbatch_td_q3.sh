#!/bin/bash
#SBATCH --job-name=td_q3
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=uq_4d/td_q3_%A.out
#SBATCH --error=uq_4d/td_q3_%A.err

# One I/O pass over the 4D universes_full omnifile's mc_truth_denom to recover the
# truth-denominator q3 column aligned to bank_uthrow (the only column the 3D bank
# lacks). Gates task 14's 4D unified throw. Self-verifying (asserts td_w alignment).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
echo "[td_q3] start $(date -u +%H:%M:%S)"
python3 dump_td_q3.py --out bank_uthrow/td_q3.npz
echo "[td_q3] done $(date -u +%H:%M:%S)"
