#!/bin/bash
#SBATCH --job-name=npz_pc_fps_xps2
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=05:00:00
#SBATCH --output=npz_pc_fps_xps2_%j.out --error=npz_pc_fps_xps2_%j.err
# FPS Stage 2 (extended phase space + extended reporting grid / pilot catch bins):
# rebuild the padded point-cloud npz with the theta_mu gate lifted (Stage 1) AND the
# PT_EXT/PZ_EXT reporting grid (Stage 2, from fps_acceptance.py) so the low-p|| catch
# strip and the pt>4.5 wedge enter the grid at sufficient completeness. New filenames
# throughout; the existing xps/standard-PS artifacts are untouched.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"
OMNI="runEventLoopOmniFold_PC_FPS_MEFHC.root"
OUT="of_inputs_pc_fps_xps2.npz"
PT_EXT="0,0.07,0.15,0.25,0.33,0.4,0.47,0.55,0.7,0.85,1.0,1.25,1.5,2.5,4.5,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"
[ -s "$OMNI" ] || { echo "[npz] MISSING $OMNI"; exit 1; }
echo "[npz] building ${OUT} (full-phase-space + PT_EXT/PZ_EXT) from ${OMNI}  $(date -u '+%F %T UTC')"
python3 pet/dump_pointcloud_inputs.py --omnifile "${OMNI}" --num-part 12 \
    --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" --out "${OUT}"
echo "[npz] done $(stat -c '%s' ${OUT}) bytes  $(date -u '+%F %T UTC')"
echo "[npz->npy] converting ${OUT} -> of_inputs_pc_fps_xps2_npy/  $(date -u '+%F %T UTC')"
python3 pet/npz_to_npy.py --inputs "${OUT}" --out of_inputs_pc_fps_xps2_npy
echo "[npz->npy] done  $(date -u '+%F %T UTC')"
