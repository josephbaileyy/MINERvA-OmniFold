#!/bin/bash
#SBATCH --job-name=minerva_dl
#SBATCH --account=m3246
#SBATCH --qos=xfer
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --output=download_playlist_%x_%j.out
#SBATCH --error=download_playlist_%x_%j.err

# Download one MINERvA ME FHC playlist on NERSC's data-transfer nodes.
#
# Usage:
#   sbatch --job-name=dl_1B sbatch_download_playlist.sh 1B
#   sbatch --job-name=dl_1C sbatch_download_playlist.sh 1C
#
# The xfer QOS runs on dedicated DTNs (https://docs.nersc.gov/systems/dtn/),
# 1 core per job, up to 48h walltime. xrdcp is network-bound not CPU-bound,
# so a single core is sufficient. --job-name on the sbatch CLI is optional
# but makes it easy to tell playlists apart in `sqs` output.
#
# Playlist ~735 GB => ~2-6h at FNAL-to-NERSC transfer rates.
# 24h walltime is generous headroom; do not reduce unless you've measured.

set -eo pipefail  # not -u: conda's deactivate-root.sh hook references
                  # CONDA_BACKUP_ROOTSYS which is unset in a fresh env.

PLAYLIST="${1:?usage: sbatch $0 <playlist>}"

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}"

module load python
conda activate root_6_28
# xrdcp / xrdfs come from the ROOT install in root_6_28

echo "[$(date -u '+%F %T UTC')] sbatch job ${SLURM_JOB_ID} on $(hostname) for playlist ${PLAYLIST}"
echo "[$(date -u '+%F %T UTC')] xrdcp: $(which xrdcp || echo NOT FOUND)"

bash "${REPO}/2d-unfolding/download_playlist.sh" "${PLAYLIST}"

echo "[$(date -u '+%F %T UTC')] sbatch job ${SLURM_JOB_ID} finished."
