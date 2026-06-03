#!/bin/bash
#SBATCH --job-name=hadd_3d_uni_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=hadd_3d_uni_full_%j.out
#SBATCH --error=hadd_3d_uni_full_%j.err

# Gap 2 hadd: combine the 12 per-playlist 3D full-universe event-loop ROOTs into
# a single MEFHC 3D universe omnifile.
#
# NOTE: plain `hadd -f` trips ROOT's default 100 GB TTree auto-rollover mid-merge
# (the combined mc_signal_reco/mc_truth_denom trees exceed it), aborting with
# "Output file ... has been deleted (likely due to a TTree larger than 100Gb)"
# and leaving a ~94 GB partial missing the data + mc_background trees. This is the
# same wall the 2D dump-all hit; the fix (reused verbatim here) is the Python
# TFileMerger in ../2d-unfolding/uq/hadd_universes_full.py, which bumps
# TTree::SetMaxTreeSize to 300 GB. Hence mem=64G (vs 48G) too.
#
# Output (runEventLoopOmniFold_MEFHC_3D_universes_full.root, ~120 GB) is the
# --omnifile for the 3D --universe sweep (Gap 4).

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/3d-unfolding"

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
INPUTS=()
for PL in "${PLAYLISTS[@]}"; do
    INPUTS+=("runEventLoopOmniFold_3D_${PL}_universes_full.root")
done

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

OUT=runEventLoopOmniFold_MEFHC_3D_universes_full.root

# Move any corrupt partial (e.g. from a prior plain-hadd attempt) out of the way.
if [[ -s "${OUT}" ]]; then
    BAK="${OUT%.root}.partial_$(date -u +%Y%m%d_%H%M%S).root"
    echo "[sbatch] moving prior partial -> ${BAK}"
    mv "${OUT}" "${BAK}"
fi

echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] merge ${OUT} <- ${INPUTS[*]}"

# Reuse the generic 300 GB-tree-size Python merger (OUT then INPUTs).
python "${REPO}/2d-unfolding/uq/hadd_universes_full.py" "${OUT}" "${INPUTS[@]}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
ls -lh "${OUT}"
