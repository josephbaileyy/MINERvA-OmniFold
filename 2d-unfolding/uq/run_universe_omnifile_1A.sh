#!/bin/bash
# Rebuild the 1A omnifile with per-universe weight branches enabled via
# MNV101_DUMP_UNIVERSES. Intended to run on an existing interactive
# allocation (NERSC regular/shared QOS take too long to schedule for this
# 1-2h job). Per the REFERENCE.md "Interactive-first" rule, launch via:
#
#   srun --jobid=<INTERACTIVE_JOBID> --overlap -n 1 --cpus-per-task=128 \
#        bash -lc '/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/run_universe_omnifile_1A.sh'
#
# Output: $REPO/2d-unfolding/runEventLoopOmniFold_1A_universes.root
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
JOBTAG="$(date -u +%Y%m%d_%H%M%S)"
WORKDIR="${DOCS}/uq/evloop_universe_1A_${JOBTAG}"
DATA_MANIFEST="${DOCS}/playlist_manifests/1A_Data.txt"
MC_MANIFEST="${DOCS}/playlist_manifests/1A_MC.txt"
OMNIFILE_OUT="${DOCS}/runEventLoopOmniFold_1A_universes.root"
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
LOG="${DOCS}/uq/evloop_universe_1A_${JOBTAG}.log"

# Stage-1 universe allowlist (6 bands, 110 universe weight branches).
# - Flux:               100 PPFX universes
# - MaCCQE:               2 (+/-1 sigma)
# - Rvp1pi:               2
# - Rvn1pi:               2
# - MinosEfficiency:      2
# - Muon_Energy_MINOS:    2
export MNV101_DUMP_UNIVERSES="Flux,MaCCQE,Rvp1pi,Rvn1pi,MinosEfficiency,Muon_Energy_MINOS"

export PYTHONUNBUFFERED=1

mkdir -p "${WORKDIR}"
mkdir -p "$(dirname "${LOG}")"

source "${REPO}/setup_salloc_env.sh"

{
  echo "[universe-rebuild] host=$(hostname) start=$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "[universe-rebuild] workdir: ${WORKDIR}"
  echo "[universe-rebuild] data manifest: ${DATA_MANIFEST} ($(wc -l < ${DATA_MANIFEST}) files)"
  echo "[universe-rebuild] mc   manifest: ${MC_MANIFEST}   ($(wc -l < ${MC_MANIFEST}) files)"
  echo "[universe-rebuild] event-loop bin: ${EVLOOP_BIN}"
  echo "[universe-rebuild] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES}"
} | tee -a "${LOG}"

cd "${WORKDIR}"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}" 2>&1 | tee -a "${LOG}"

mv -v runEventLoopOmniFold.root "${OMNIFILE_OUT}" 2>&1 | tee -a "${LOG}"

{
  echo "[universe-rebuild] end=$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "[universe-rebuild] omnifile: ${OMNIFILE_OUT}"
  ls -lh "${OMNIFILE_OUT}"
} | tee -a "${LOG}"
