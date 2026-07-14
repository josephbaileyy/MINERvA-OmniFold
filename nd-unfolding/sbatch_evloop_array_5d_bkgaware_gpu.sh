#!/bin/bash
#SBATCH --job-name=ev5dbkgG
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=12:00:00
#SBATCH --array=1-12
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/ev5dbkgG_%a_%A.out --error=uq_4d/ev5dbkgG_%a_%A.err
# BACKGROUND-AWARE dump-all evloop (KNOWN_ISSUES #13), GPU-allocation variant
# (2026-07-13): CPU m3246 exhausted -> run the CPU MAT event loop on GPU-node host
# cores (m3246_g), charged to GPU-hours. Installed binary (mtime 07-11) is
# CONFIRMED bkg-aware (sim_background_<band>_<idx> branches). NON-DESTRUCTIVE:
# distinct _bkgaware WORKDIR + output name so the current per-playlist omnifiles,
# the merged 170GB omnifile (eavailW is reading it), bank_uthrow_5d, and the
# just-built budget all stay intact as the background-CV baseline. --gpus-per-task=1
# -c 32 satisfies the gpu_shared 32-cores/GPU policy; the reserved GPU is idle.
set -eo pipefail
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
PL="${PLAYLISTS[$((SLURM_ARRAY_TASK_ID - 1))]}"
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export MNV101_DUMP_UNIVERSES="1"
export PYTHONUNBUFFERED=1
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
FINAL="${REPO}/nd-unfolding/runEventLoopOmniFold_5D_${PL}_universes_full_bkgaware.root"
[[ -s "${FINAL}" ]] && { echo "[ev-bkg] skip ${PL} (exists)"; exit 0; }
WORKDIR="${REPO}/nd-unfolding/evloop_work_5d_uni_bkgaware_${PL}"
mkdir -p "${WORKDIR}"; cd "${WORKDIR}"
DATA_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_Data.txt"
MC_MANIFEST="${REPO}/2d-unfolding/playlist_manifests/${PL}_MC.txt"
echo "[ev-bkg] node=$(hostname) task=${SLURM_ARRAY_TASK_ID} playlist=${PL} bin=$(stat -c '%y' ${EVLOOP_BIN})"
echo "[ev-bkg] start $(date -u '+%F %T UTC')"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"
mv -v runEventLoopOmniFold.root "${FINAL}"
echo "[ev-bkg] done $(date -u '+%F %T UTC') -> ${FINAL}"
