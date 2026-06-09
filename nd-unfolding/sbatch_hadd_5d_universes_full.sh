#!/bin/bash
#SBATCH --job-name=hadd5d_uni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=hadd5d_uni_%j.out
#SBATCH --error=hadd5d_uni_%j.err

# Merge the 12 per-playlist 5D _universes_full omnifiles (133 GB) into one MEFHC file
# for the (E_avail,W) systematic covariance (task 13). SetMaxTreeSize=300GB merger
# (NOT bare hadd) -- combined universe trees exceed ROOT's 100 GB rollover
# (see memory hadd_100gb_tree_limit).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

OUT="runEventLoopOmniFold_5D_MEFHC_universes_full.root"
INPUTS=""
for PL in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do
  F="runEventLoopOmniFold_5D_${PL}_universes_full.root"
  [[ -s "$F" ]] || { echo "[hadd] FAIL: missing $F" >&2; exit 2; }
  INPUTS="${INPUTS} ${F}"
done
echo "[hadd] start $(date -u '+%F %T UTC')"
python3 ../2d-unfolding/uq/hadd_universes_full.py "${OUT}" ${INPUTS}
echo "[hadd] done $(date -u '+%F %T UTC'); output:"
ls -lh "${OUT}"
