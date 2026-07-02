#!/bin/bash
#SBATCH --job-name=hadd_pc_fps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=16G --time=03:00:00
#SBATCH --output=hadd_pc_fps_%j.out --error=hadd_pc_fps_%j.err
# FPS headline, step 2a: merge the 12 cloud-fixed FULL-PHASE-SPACE point-cloud
# CV-only files (re-dumped by sbatch_evloop_array_pointcloud_fps.sh with the
# 2026-06-28 cloud-coverage binary) into one MEFHC file. CV-only PC files total
# ~70 GB -> under ROOT's 100 GB TTree limit, plain hadd is safe. Writes a NEW
# -fps name; leaves the restricted-PS fullcloud file untouched.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
INPUTS=()
for pl in "${PLAYLISTS[@]}"; do
  f="runEventLoopOmniFold_PC_FPS_${pl}.root"
  [ -s "$f" ] || { echo "[hadd] MISSING per-playlist input: $f"; exit 1; }
  INPUTS+=("$f")
done
OUT="runEventLoopOmniFold_PC_FPS_MEFHC.root"
echo "[hadd] merging ${#INPUTS[@]} files -> ${OUT}  $(date -u '+%F %T UTC')"
hadd -f "${OUT}" "${INPUTS[@]}"
echo "[hadd] done $(stat -c '%s' ${OUT}) bytes  $(date -u '+%F %T UTC')"
