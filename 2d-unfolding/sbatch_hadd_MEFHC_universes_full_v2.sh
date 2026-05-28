#!/bin/bash
#SBATCH --job-name=hadd_MEFHC_uni_full_v2
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=hadd_MEFHC_uni_full_v2_%j.out
#SBATCH --error=hadd_MEFHC_uni_full_v2_%j.err

# Retry merge using Python TFileMerger with TTree::SetMaxTreeSize bumped
# to 300 GB. The previous hadd (53365633) tripped ROOT's default 100 GB
# tree-size rollover mid-merge, leaving the 94 GB partial file with
# data + mc_background trees missing. The per-playlist inputs are intact
# and reused as-is.

set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

OUT=runEventLoopOmniFold_MEFHC_universes_full.root

# Move the corrupted partial out of the way (kept for forensics).
if [[ -s "${OUT}" ]]; then
  BAK="${OUT%.root}.partial_$(date -u +%Y%m%d_%H%M%S).root"
  echo "[sbatch] moving corrupted partial -> ${BAK}"
  mv "${OUT}" "${BAK}"
fi

echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
python uq/hadd_universes_full.py
echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
ls -lh "${OUT}"
