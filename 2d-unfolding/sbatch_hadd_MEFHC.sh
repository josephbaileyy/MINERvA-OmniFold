#!/bin/bash
#SBATCH --job-name=hadd_MEFHC
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=hadd_MEFHC_%j.out
#SBATCH --error=hadd_MEFHC_%j.err

# Combine 12 per-playlist event-loop ROOTs into a single MEFHC file.
# Designed to run as afterok dependency of sbatch_evloop_array.sh.
#
# Note: hadd correctly merges TTrees (concatenates) and TParameter<double>
# (sums) AND TParameter<int>/<long> (sums). hasTruthOnlyMisses is an int —
# after hadd it becomes 12 (= sum of 12 playlist values of 1), so the
# Python diagnostic now treats >=1 as "phase-17+ ROOT" rather than strictly
# ==1; this was already handled. nTruthOnlyMisses sums to the total miss
# count across playlists, as desired for the diagnostic.

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

INPUTS=(
    runEventLoopOmniFold_1A.root
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

OUT=runEventLoopOmniFold_MEFHC.root
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] hadd ${OUT} <- ${INPUTS[*]}"

hadd -f "${OUT}" "${INPUTS[@]}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
ls -la "${OUT}"
