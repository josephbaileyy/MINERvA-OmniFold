#!/bin/bash
#SBATCH --job-name=gevgenMEC
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=06:00:00
#SBATCH --array=1-8
#SBATCH --output=gevgenMEC_%A_%a.out
#SBATCH --error=gevgenMEC_%A_%a.err

# GENIE CV *with Valencia 2p2h/MEC enabled* (--event-generator-list Default+CCMEC),
# otherwise identical to the base-CV generation (same flux/target/splines/energy).
# 8 x 250k = 2M events, mirroring the no-MEC CV statistics. Combine with:
#   hadd genie_mefhc_mec_ALL.gst.root work_mecseed*/genie_mefhc_mecseed*.gst.root
# then genie_mec_to_xsec3d.py (normalises by the NON-MEC CC count, since the
# tot_cc spline graph excludes the Nieves-Simo-Vacas MEC channel).
set -eo pipefail
N_PER=${N_PER:-250000}
# SLURM copies the batch script to a spool dir, so BASH_SOURCE is useless here;
# use the submit dir (sbatch is run from genie/) with an absolute fallback.
HERE="${SLURM_SUBMIT_DIR:-/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie}"
SEED=$((1000 + ${SLURM_ARRAY_TASK_ID:-1}))   # distinct from the no-MEC CV seeds

echo "[sbatch gevgenMEC] task=$SEED N_PER=$N_PER start=$(date -u '+%F %T UTC')"
GEVGEN_LIST="Default+CCMEC" GENIE_WORK="$HERE/work_mecseed${SEED}" \
  bash "$HERE/run_gevgen.sh" "$N_PER" "$SEED" "mecseed${SEED}"
echo "[sbatch gevgenMEC] task=$SEED done=$(date -u '+%F %T UTC')"
