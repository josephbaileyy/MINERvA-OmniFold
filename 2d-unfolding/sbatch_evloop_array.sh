#!/bin/bash
#SBATCH --job-name=evloop
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --array=1-11
#SBATCH --output=evloop_%a_%A.out
#SBATCH --error=evloop_%a_%A.err

# Per-playlist event loop for 1B–1P (11 playlists). 1A is produced
# separately (run from sbatch directly or via interactive shell).
#
# Uses the production binary at MINERvA-OmniFold/MINERvA101/opt/bin/
# runEventLoopOmniFold with the Phase-18 truth-tree-authoritative reco
# gate plus Phase-18.2 reco-side dedupe.
#
# Outputs land in runEventLoopOmniFold_${PL}.root, consumed by
# sbatch_hadd_MEFHC.sh.

set -eo pipefail

PLAYLISTS=(1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/2d-unfolding/evloop_work_${PL}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] data manifest: ${DATA_MANIFEST}"
echo "[sbatch] mc manifest  : ${MC_MANIFEST}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/2d-unfolding/runEventLoopOmniFold_${PL}.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
