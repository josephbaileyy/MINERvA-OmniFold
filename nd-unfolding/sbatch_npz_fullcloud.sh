#!/bin/bash
#SBATCH --job-name=npz_fc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=04:00:00
#SBATCH --output=npz_fc_%j.out --error=npz_fc_%j.err
# Stage 3: rebuild the padded point-cloud npz from the fullcloud MEFHC file.
# Runs on a compute node (the 49 GB read + 6 GB npz OOM-kills on the login node's
# per-user mem cgroup). Writes a NEW npz so the baseline of_inputs_pc.npz stays.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
OMNI="runEventLoopOmniFold_PC_MEFHC_fullcloud.root"
OUT="of_inputs_pc_fullcloud.npz"
[ -s "$OMNI" ] || { echo "[npz] MISSING $OMNI"; exit 1; }
echo "[npz] building ${OUT} from ${OMNI}  $(date -u '+%F %T UTC')"
python3 pet/dump_pointcloud_inputs.py --omnifile "${OMNI}" --num-part 12 --out "${OUT}"
echo "[npz] done $(stat -c '%s' ${OUT}) bytes  $(date -u '+%F %T UTC')"
