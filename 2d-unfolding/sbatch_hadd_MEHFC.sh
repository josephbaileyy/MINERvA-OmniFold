#!/bin/bash
#SBATCH --job-name=hadd_MEHFC
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=hadd_MEHFC_%j.out
#SBATCH --error=hadd_MEHFC_%j.err

# hadd 12 patched per-playlist event-loop outputs into a fresh MEHFC
# combined file. Pulls 1A from runEventLoopOmniFold_1A_minos_fix.root
# (already produced by the IsMinosMatchMuon fix re-run on 2026-04-25)
# and 1B-1P from the freshly produced array outputs.
#
# Designed to run as an afterok dependency of the per-playlist event-loop
# array (sbatch_evloop_array.sh).

set -eo pipefail

cd /pscratch/sd/j/josephrb/MINERvA101
module load python
conda activate root_6_28
source opt/bin/setup.sh

cd /pscratch/sd/j/josephrb/MINERvA101/Documents

INPUTS=(
    runEventLoopOmniFold_1A_minos_fix.root
    runEventLoopOmniFold_1B.root
    runEventLoopOmniFold_1C.root
    runEventLoopOmniFold_1D.root
    runEventLoopOmniFold_1E.root
    runEventLoopOmniFold_1F.root
    runEventLoopOmniFold_1G.root
    runEventLoopOmniFold_1L.root
    runEventLoopOmniFold_1M.root
    runEventLoopOmniFold_1N.root
    runEventLoopOmniFold_1O.root
    runEventLoopOmniFold_1P.root
)

# Verify all 12 inputs exist before clobbering the output
missing=0
for f in "${INPUTS[@]}"; do
    if [[ ! -s "$f" ]]; then
        echo "[sbatch] MISSING: $f" >&2
        missing=1
    fi
done
if (( missing )); then
    echo "[sbatch] aborting: not all per-playlist inputs are present" >&2
    exit 1
fi

OUT=runEventLoopOmniFold_MEHFC.root
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] hadd ${OUT} <- ${INPUTS[*]}"

hadd -f "${OUT}" "${INPUTS[@]}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
ls -la "${OUT}"
