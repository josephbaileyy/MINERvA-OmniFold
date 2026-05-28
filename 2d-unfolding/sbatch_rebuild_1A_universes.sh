#!/bin/bash
#SBATCH --job-name=rebuild_1A_uni
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=04:00:00
#SBATCH --output=rebuild_1A_uni_%j.out
#SBATCH --error=rebuild_1A_uni_%j.err

# Rebuild the full 1A omnifile with the Stage-1 universe allowlist.
# Mirror of uq/run_universe_omnifile_1A.sh but as sbatch so it survives
# interactive shell exit. ~2h expected wall on 128 CPU.
#
# Allowlist: Flux,MaCCQE,Rvp1pi,Rvn1pi,MinosEfficiency,Muon_Energy_MINOS
#            (110 universe weight branches).

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
WORKDIR="${DOCS}/uq/evloop_universe_1A_${SLURM_JOB_ID}"
DATA_MANIFEST="${DOCS}/playlist_manifests/1A_Data.txt"
MC_MANIFEST="${DOCS}/playlist_manifests/1A_MC.txt"
OMNIFILE_OUT="${DOCS}/runEventLoopOmniFold_1A_universes.root"
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

export MNV101_DUMP_UNIVERSES="Flux,MaCCQE,Rvp1pi,Rvn1pi,MinosEfficiency,Muon_Energy_MINOS"
export PYTHONUNBUFFERED=1

mkdir -p "${WORKDIR}"

source "${REPO}/setup_salloc_env.sh"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] MNV101_DUMP_UNIVERSES=${MNV101_DUMP_UNIVERSES}"
echo "[sbatch] data manifest: ${DATA_MANIFEST} ($(wc -l < ${DATA_MANIFEST}) files)"
echo "[sbatch] mc   manifest: ${MC_MANIFEST}   ($(wc -l < ${MC_MANIFEST}) files)"

cd "${WORKDIR}"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"

mv -v runEventLoopOmniFold.root "${OMNIFILE_OUT}"
ls -lh "${OMNIFILE_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE_OUT}"
