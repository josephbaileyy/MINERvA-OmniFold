#!/bin/bash
#SBATCH --job-name=gevgen3d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=10:00:00
#SBATCH --array=1-20
#SBATCH --output=gevgen3d_%A_%a.out
#SBATCH --error=gevgen3d_%A_%a.err

# High-statistics base-GENIE-CV generation, parallelised over seeds.
# Each array task generates N_PER events with seed = task id; gevgen is
# single-threaded so we fan out instead of threading. After the array
# finishes, hadd the per-seed gst trees:
#
#   hadd genie_mefhc_cv_ALL.gst.root \
#        work_seed*/genie_mefhc_seed*.gst.root
#
# then feed genie_mefhc_cv_ALL.gst.root to genie_to_xsec3d.py.

set -eo pipefail
N_PER=${N_PER:-200000}
# SLURM copies the batch script to a spool dir, so BASH_SOURCE points there, not
# the genie dir. Anchor on the submit dir (where run_gevgen.sh lives).
HERE="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
[ -f "$HERE/run_gevgen.sh" ] || HERE="/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie"
SEED=${SLURM_ARRAY_TASK_ID:-1}

echo "[sbatch gevgen3d] task=$SEED N_PER=$N_PER start=$(date -u '+%F %T UTC')"
bash "$HERE/run_gevgen.sh" "$N_PER" "$SEED" "seed${SEED}"
echo "[sbatch gevgen3d] task=$SEED done=$(date -u '+%F %T UTC')"
