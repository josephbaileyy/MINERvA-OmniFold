#!/bin/bash
#SBATCH --job-name=ev5dfpsuni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=24:00:00
#SBATCH --array=1-12
#SBATCH --output=uq_fps/ev5dfpsuni_%a_%A.out
#SBATCH --error=uq_fps/ev5dfpsuni_%a_%A.err

# FPS UQ campaign step 1: per-playlist FULL-PHASE-SPACE event loop with the
# complete universe dump (MNV101_DUMP_UNIVERSES) -- the FPS analogue of
# sbatch_evloop_array_5d_universes_full.sh. Submit ONLY after the MEFHC-scale
# anchor gate passes (FPS_PILOT.md / fps_mefhc job).
#
# Expect ~40-50% larger files than the standard 5D universes_full run (the
# truth denominator grows from 32.8M to ~49M events): plan ~190 GB merged.
# NEVER bare-hadd the outputs (100 GB TTree limit) -- use
# 2d-unfolding/uq/hadd_universes_full.py via the matching sbatch.

set -eo pipefail

PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export MNV101_DUMP_UNIVERSES="1"
export MNV101_FULL_PHASE_SPACE="1"
export PYTHONUNBUFFERED=1

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/nd-unfolding/evloop_work_5d_fpsuni_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL} FPS=1 UNIVERSES=1"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_5D_FPS_${PL}_universes_full.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
