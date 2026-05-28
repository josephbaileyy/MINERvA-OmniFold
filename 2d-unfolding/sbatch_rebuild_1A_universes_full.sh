#!/bin/bash
#SBATCH --job-name=rebuild_1A_uni_full
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=06:00:00
#SBATCH --output=rebuild_1A_uni_full_%j.out
#SBATCH --error=rebuild_1A_uni_full_%j.err

# Stage-2 full-universe rebuild of the 1A omnifile (publication-grade).
# Uses MNV101_DUMP_UNIVERSES=1 (dump-all) so the C++ event loop writes a
# weight branch for every universe in GetStandardSystematics, plus the
# new IsVerticalOnly()-gated lateral kinematic branches
# (pT_truth_<band>_<idx>, pz_truth_<band>_<idx>) for non-vertical universes.
#
# Per-event cost is ~3x the 110-band Stage-1 rebuild because GetWeight() is
# evaluated for ~250-300 (band, idx) pairs instead of 110. Walltime budgeted
# at 6h on 128 CPU vs the 42m of the 110-band rebuild.
#
# Output: runEventLoopOmniFold_1A_universes_full.root (kept separate from
# the production 110-band file so both stay on disk during the transition).

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
WORKDIR="${DOCS}/uq/evloop_universe_full_1A_${SLURM_JOB_ID}"
DATA_MANIFEST="${DOCS}/playlist_manifests/1A_Data.txt"
MC_MANIFEST="${DOCS}/playlist_manifests/1A_MC.txt"
OMNIFILE_OUT="${DOCS}/runEventLoopOmniFold_1A_universes_full.root"
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

export MNV101_DUMP_UNIVERSES="1"
export PYTHONUNBUFFERED=1

mkdir -p "${WORKDIR}"

source "${REPO}/setup_salloc_env.sh"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES} (dump-all)"
echo "[sbatch] binary mtime: $(stat -c '%y' ${EVLOOP_BIN})"
echo "[sbatch] data manifest: ${DATA_MANIFEST} ($(wc -l < ${DATA_MANIFEST}) files)"
echo "[sbatch] mc   manifest: ${MC_MANIFEST}   ($(wc -l < ${MC_MANIFEST}) files)"

cd "${WORKDIR}"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

mv -v runEventLoopOmniFold.root "${OMNIFILE_OUT}"
ls -lh "${OMNIFILE_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE_OUT}"
