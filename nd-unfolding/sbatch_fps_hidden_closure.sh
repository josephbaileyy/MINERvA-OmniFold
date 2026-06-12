#!/bin/bash
#SBATCH --job-name=fps_hidcls
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=06:00:00
#SBATCH --output=uq_fps/fps_hidcls_%j.out --error=uq_fps/fps_hidcls_%j.err

# FPS extension-region hidden-variable closure (FPS_PILOT.md "new validation"):
# inject a Gaussian truth bump in true E_avail (NOT an unfolding axis -- the 2D
# FPS unfold never sees it) on the closure pseudo-data, unfold on the extended
# (pT,pz) grid, and check per-cell recovery. Region split (published vs
# extension) via fps_extension_validation.py --closure-root.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps

OMNIFILE="runEventLoopOmniFold_5D_FPS_MEFHC.root"
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"
OUT="products/5d/closure_2d_FPS_hidden_eavail_MEFHC.root"
[[ -s "${OUT}" ]] && { echo "skip (exists)"; exit 0; }

python3 unfold_nd_omnifold_unbinned.py \
  --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" --axes "" \
  --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" \
  --iters 5 --use-weights --estimator lgbm --seed 42 \
  --closure --closure-reweight-axis eavail \
  --out "${OUT}"

python3 fps_extension_validation.py --closure-root "${OUT}"
