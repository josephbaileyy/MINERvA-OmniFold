#!/bin/bash
#SBATCH --job-name=build
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=build_%j.out
#SBATCH --error=build_%j.err

# Rebuild runEventLoopOmniFold after edits to runEventLoopOmniFold.cpp.
# Build dir is opt/build_MINERvA101 (out of tree); install prefix is opt/,
# so `make install` lands the binary in opt/bin/.

set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
BUILD_DIR="${REPO}/MINERvA101/opt/build_MINERvA101"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

source "${REPO}/setup_salloc_env.sh"
cd "${BUILD_DIR}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] build dir: ${BUILD_DIR}"
echo "[sbatch] source mtime (cpp): $(stat -c '%y' ${REPO}/MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp)"
echo "[sbatch] binary mtime pre : $(stat -c '%y' ${BIN} 2>/dev/null || echo missing)"

cmake --build . --target runEventLoopOmniFold --parallel "${SLURM_CPUS_PER_TASK}"
cmake --install .

echo "[sbatch] binary mtime post: $(stat -c '%y' ${BIN})"
echo "[sbatch] done : $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
