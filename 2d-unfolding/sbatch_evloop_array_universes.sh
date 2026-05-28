#!/bin/bash
#SBATCH --job-name=evloop_uni
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=16:00:00
#SBATCH --array=1-11
#SBATCH --output=evloop_uni_%a_%A.out
#SBATCH --error=evloop_uni_%a_%A.err

# Per-playlist event loop for 1B-1P (11 playlists) with the Stage-1
# universe allowlist enabled. 1A is already on disk as
# runEventLoopOmniFold_1A_universes.root (built this session by
# sbatch_rebuild_1A_universes.sh).
#
# Allowlist matches Stage-1 (110 universe weight branches/tree):
#   Flux (100 PPFX) + MaCCQE,Rvp1pi,Rvn1pi,MinosEfficiency,Muon_Energy_MINOS
#   (5 x ±1σ pairs).
#
# Outputs land in runEventLoopOmniFold_${PL}_universes.root, consumed
# by sbatch_hadd_MEFHC_universes.sh.
#
# Walltime / mem: 1A on 128 CPU took 42 min and ~40 GB RSS. On the
# shared queue with 4 CPU the same work is more like 4-6 h per
# playlist; 16h walltime gives ~3x margin.

set -eo pipefail

PLAYLISTS=(1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"

EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORKDIR="${REPO}/2d-unfolding/evloop_uni_work_${PL}_${SLURM_JOB_ID}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"

export MNV101_DUMP_UNIVERSES="Flux,MaCCQE,Rvp1pi,Rvn1pi,MinosEfficiency,Muon_Energy_MINOS"
export PYTHONUNBUFFERED=1

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} array_task=${SLURM_ARRAY_TASK_ID} playlist=${PL}"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] data manifest: ${DATA_MANIFEST}"
echo "[sbatch] mc manifest  : ${MC_MANIFEST}"
echo "[sbatch] evloop bin: ${EVLOOP_BIN} ($(stat -c '%y' ${EVLOOP_BIN}))"
echo "[sbatch] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

FINAL="${REPO}/2d-unfolding/runEventLoopOmniFold_${PL}_universes.root"
mv -v runEventLoopOmniFold.root "${FINAL}"

echo "[sbatch] done:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] final output: ${FINAL}"
ls -lh "${FINAL}"
