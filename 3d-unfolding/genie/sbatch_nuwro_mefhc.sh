#!/bin/bash
#SBATCH --job-name=nuwro3d
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=10:00:00
#SBATCH --array=1-8
#SBATCH --output=nuwro3d_%A_%a.out
#SBATCH --error=nuwro3d_%A_%a.err

# NuWro numu-on-CH generation parallelised over seeds (8 x 250k = 2M), each task
# -> work_nuwro_p<seed>/nuwro_flat.root (now carrying the W branch). After the
# array, feed the glob to nuwro_to_xsec_eavailW.py.
set -eo pipefail
N_PER=${N_PER:-250000}
HERE="${SLURM_SUBMIT_DIR:-/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie}"
[ -f "$HERE/run_nuwro.sh" ] || HERE="/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie"
SEED=$(( 20 + SLURM_ARRAY_TASK_ID ))

echo "[sbatch nuwro3d] task=${SLURM_ARRAY_TASK_ID} N=$N_PER seed=$SEED start=$(date -u '+%F %T UTC')"
bash "$HERE/run_nuwro.sh" "$N_PER" "$SEED" "p${SLURM_ARRAY_TASK_ID}"
echo "[sbatch nuwro3d] task=${SLURM_ARRAY_TASK_ID} done=$(date -u '+%F %T UTC')"
