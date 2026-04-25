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

ROOTDIR="/pscratch/sd/j/josephrb/MINERvA101"
DOCS="${ROOTDIR}/Documents"
WORKDIR="${DOCS}/validate_1A_corrected_work_${SLURM_JOB_ID}"
DATA_MANIFEST="${ROOTDIR}/Doc_tmp/1A_Data.txt"
MC_MANIFEST="${ROOTDIR}/Doc_tmp/1A_MC.txt"
OMNIFILE_OUT="${DOCS}/runEventLoopOmniFold_1A_corrected.root"
XSEC_OUT="${DOCS}/2d_crossSection_omnifold_1A_corrected_5iter.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_1A.root"
EVLOOP_BIN="${ROOTDIR}/opt/bin/runEventLoopOmniFold"

mkdir -p "${WORKDIR}"

cd "${ROOTDIR}"
module load python
conda activate root_6_28
source OmniFold/unbinned_unfolding/build/setup.sh
source opt/bin/setup.sh

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

cd "${ROOTDIR}"
python3 Documents/unfold_2d_omnifold_unbinned.py \
  --omnifile "${OMNIFILE_OUT}" \
  --mcfile "${FLUX_MC}" \
  --iters 5 \
  --use-weights \
  --out "${XSEC_OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] omnifile: ${OMNIFILE_OUT}"
echo "[sbatch] xsec out: ${XSEC_OUT}"
