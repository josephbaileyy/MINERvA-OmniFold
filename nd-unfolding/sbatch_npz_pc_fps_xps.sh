#!/bin/bash
#SBATCH --job-name=npz_pc_fps_xps
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=04:00:00
#SBATCH --output=npz_pc_fps_xps_%j.out --error=npz_pc_fps_xps_%j.err
# FPS Stage 1 (extended phase space): rebuild the padded point-cloud npz WITH the
# theta_mu<20deg truth gate LIFTED (--full-phase-space), so PET's own headline gen
# cloud actually spans beyond the standard published phase space (previously it did
# not -- pet/dump_pointcloud_inputs.py had no such flag until this campaign added one).
# New filenames throughout; the existing standard-PS of_inputs_pc_fps.npz is untouched.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
OMNI="runEventLoopOmniFold_PC_FPS_MEFHC.root"
OUT="of_inputs_pc_fps_xps.npz"
[ -s "$OMNI" ] || { echo "[npz] MISSING $OMNI"; exit 1; }
echo "[npz] building ${OUT} (full-phase-space) from ${OMNI}  $(date -u '+%F %T UTC')"
python3 pet/dump_pointcloud_inputs.py --omnifile "${OMNI}" --num-part 12 \
    --full-phase-space --out "${OUT}"
echo "[npz] done $(stat -c '%s' ${OUT}) bytes  $(date -u '+%F %T UTC')"
echo "[npz->npy] converting ${OUT} -> of_inputs_pc_fps_xps_npy/  $(date -u '+%F %T UTC')"
python3 pet/npz_to_npy.py --inputs "${OUT}" --out of_inputs_pc_fps_xps_npy
echo "[npz->npy] done  $(date -u '+%F %T UTC')"
