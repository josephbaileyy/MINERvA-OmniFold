#!/bin/bash
#SBATCH --job-name=1A_2d_fix
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=06:00:00
#SBATCH --output=validate_1A_corrected_%j.out
#SBATCH --error=validate_1A_corrected_%j.err

# Do not use `set -u` here. `conda activate root_6_28` triggers
# deactivate-root.sh, which references CONDA_BACKUP_ROOTSYS and aborts under
# nounset in a fresh batch shell.
set -eo pipefail

export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
WORKDIR="${DOCS}/validate_1A_corrected_work_${SLURM_JOB_ID}"
DATA_MANIFEST="${DOCS}/playlist_manifests/1A_Data.txt"
MC_MANIFEST="${DOCS}/playlist_manifests/1A_MC.txt"
OMNIFILE_OUT="${DOCS}/runEventLoopOmniFold_1A_corrected.root"
XSEC_OUT="${DOCS}/2d_crossSection_omnifold_1A_corrected_5iter.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_1A.root"
EVLOOP_BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

mkdir -p "${WORKDIR}"

source "${REPO}/setup_salloc_env.sh"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] workdir: ${WORKDIR}"
echo "[sbatch] data manifest: ${DATA_MANIFEST}"
echo "[sbatch] mc manifest:   ${MC_MANIFEST}"
echo "[sbatch] flux mc:       ${FLUX_MC}"
echo "[sbatch] event-loop bin: ${EVLOOP_BIN}"

cd "${WORKDIR}"
"${EVLOOP_BIN}" "${DATA_MANIFEST}" "${MC_MANIFEST}"
mv -v runEventLoopOmniFold.root "${OMNIFILE_OUT}"

cd "${DOCS}"
python3 unfold_2d_omnifold_unbinned.py \
  --omnifile "${OMNIFILE_OUT}" \
  --mcfile "${FLUX_MC}" \
  --iters 5 \
  --use-weights \
  --out "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE_OUT}"
echo "[sbatch] xsec out: ${XSEC_OUT}"
