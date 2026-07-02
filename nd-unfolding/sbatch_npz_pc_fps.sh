#!/bin/bash
#SBATCH --job-name=npz_pc_fps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=04:00:00
#SBATCH --output=npz_pc_fps_%j.out --error=npz_pc_fps_%j.err
# FPS headline, step 2b: rebuild the padded point-cloud npz from the cloud-fixed
# FPS MEFHC file. Compute node (the ~70 GB read + npz OOM-kills on the login-node
# per-user mem cgroup). Writes a NEW npz so baselines stay.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
OMNI="runEventLoopOmniFold_PC_FPS_MEFHC.root"
OUT="of_inputs_pc_fps.npz"
[ -s "$OMNI" ] || { echo "[npz] MISSING $OMNI"; exit 1; }
echo "[npz] building ${OUT} from ${OMNI}  $(date -u '+%F %T UTC')"
python3 pet/dump_pointcloud_inputs.py --omnifile "${OMNI}" --num-part 12 --out "${OUT}"
echo "[npz] done $(stat -c '%s' ${OUT}) bytes  $(date -u '+%F %T UTC')"
# Step 2b-tail: convert to memmappable .npy so the 4-GPU horovod train can stride-load
# (npz can't mmap). Produces of_inputs_pc_fps_npy/ for sbatch_pet_train_fps_hvd.sh.
echo "[npz->npy] converting ${OUT} -> of_inputs_pc_fps_npy/  $(date -u '+%F %T UTC')"
python3 pet/npz_to_npy.py --inputs "${OUT}" --out of_inputs_pc_fps_npy
echo "[npz->npy] done  $(date -u '+%F %T UTC')"
