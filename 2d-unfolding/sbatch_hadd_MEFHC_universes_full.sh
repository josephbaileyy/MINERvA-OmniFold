#!/bin/bash
#SBATCH --job-name=hadd_MEFHC_uni_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=hadd_MEFHC_uni_full_%j.out
#SBATCH --error=hadd_MEFHC_uni_full_%j.err

# Combine 12 per-playlist full-universe event-loop ROOTs into a single
# MEFHC universe omnifile. Designed to run as
#   sbatch --dependency=afterok:<evloop_full_array_jobid> \
#       sbatch_hadd_MEFHC_universes_full.sh
# after sbatch_evloop_array_universes_full.sh completes.
#
# 1A is already on disk (runEventLoopOmniFold_1A_universes_full.root).
#
# Output size estimate: ~150 GB (vs the 110-band 63.7 GB) — roughly 2.5x
# the per-event branch count after dump-all + lateral kinematic branches.

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/2d-unfolding"

INPUTS=(
    runEventLoopOmniFold_1A_universes_full.root
    runEventLoopOmniFold_1B_universes_full.root
    runEventLoopOmniFold_1C_universes_full.root
    runEventLoopOmniFold_1D_universes_full.root
    runEventLoopOmniFold_1E_universes_full.root
    runEventLoopOmniFold_1F_universes_full.root
    runEventLoopOmniFold_1G_universes_full.root
    runEventLoopOmniFold_1L_universes_full.root
    runEventLoopOmniFold_1M_universes_full.root
    runEventLoopOmniFold_1N_universes_full.root
    runEventLoopOmniFold_1O_universes_full.root
    runEventLoopOmniFold_1P_universes_full.root
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

OUT=runEventLoopOmniFold_MEFHC_universes_full.root
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] hadd ${OUT} <- ${INPUTS[*]}"

hadd -f "${OUT}" "${INPUTS[@]}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
ls -lh "${OUT}"
