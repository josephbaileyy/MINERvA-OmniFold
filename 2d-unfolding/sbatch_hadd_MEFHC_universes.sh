#!/bin/bash
#SBATCH --job-name=hadd_MEFHC_uni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=hadd_MEFHC_uni_%j.out
#SBATCH --error=hadd_MEFHC_uni_%j.err

# Combine 12 per-playlist universe-enabled event-loop ROOTs into a
# single MEFHC universe omnifile. Designed to run as
#   sbatch --dependency=afterok:<evloop_array_jobid> \
#       sbatch_hadd_MEFHC_universes.sh
# after sbatch_evloop_array_universes.sh completes.
#
# 1A is already on disk (runEventLoopOmniFold_1A_universes.root, from
# sbatch_rebuild_1A_universes.sh this session).
#
# Output size estimate: 1A universes = 5.3 GB; MEFHC ≈ 12x that ≈
# 60-70 GB. Walltime: hadd of 12 large ROOTs ~ 30-60 min, 2h is
# margin. Memory: hadd uses TBufferFile cycling, 24 GB is plenty.

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

INPUTS=(
    runEventLoopOmniFold_1A_universes.root
    runEventLoopOmniFold_1B_universes.root
    runEventLoopOmniFold_1C_universes.root
    runEventLoopOmniFold_1D_universes.root
    runEventLoopOmniFold_1E_universes.root
    runEventLoopOmniFold_1F_universes.root
    runEventLoopOmniFold_1G_universes.root
    runEventLoopOmniFold_1L_universes.root
    runEventLoopOmniFold_1M_universes.root
    runEventLoopOmniFold_1N_universes.root
    runEventLoopOmniFold_1O_universes.root
    runEventLoopOmniFold_1P_universes.root
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

OUT=runEventLoopOmniFold_MEFHC_universes.root
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] hadd ${OUT} <- ${INPUTS[*]}"

hadd -f "${OUT}" "${INPUTS[@]}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
ls -lh "${OUT}"
