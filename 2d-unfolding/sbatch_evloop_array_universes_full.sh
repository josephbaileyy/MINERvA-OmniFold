#!/bin/bash
#SBATCH --job-name=evloop_uni_full
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --array=1-11
#SBATCH --output=evloop_uni_full_%a_%A.out
#SBATCH --error=evloop_uni_full_%a_%A.err

# Stage-2 full-universe event loop for 1B-1P (11 playlists). 1A is already
# on disk as runEventLoopOmniFold_1A_universes_full.root (built by
# sbatch_rebuild_1A_universes_full.sh).
#
# Same MNV101_DUMP_UNIVERSES=1 (dump-all) mode as 1A. The C++ event loop
# writes every band's weights AND the lateral kinematic branches per the
# IsVerticalOnly() gate.
#
# Bumped vs the Stage-1 version: 4 -> 8 CPU, 24 GB -> 48 GB mem, 16h -> 24h
# walltime to absorb the ~3x universe-eval slowdown.

set -eo pipefail

PLAYLISTS=(1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/2d-unfolding/evloop_uni_full_work_${PL}_${SLURM_JOB_ID}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

export MNV101_DUMP_UNIVERSES="1"
export PYTHONUNBUFFERED=1

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] data manifest: ${DATA_MANIFEST}"
echo "[sbatch] mc manifest  : ${MC_MANIFEST}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES} (dump-all)"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/2d-unfolding/runEventLoopOmniFold_${PL}_universes_full.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
ls -lh "${FINAL}"
