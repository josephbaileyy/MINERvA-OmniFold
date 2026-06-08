#!/bin/bash
# Post-generation orchestration for the (E_avail, W) generator band: hadd each
# generator's gst/flat, run the (eavail,W) converter, then overlay vs the unfolded
# data. Idempotent -- skips a generator whose events aren't present yet. Run in the
# analysis env (after sourcing setup_salloc_env.sh) on a node with ROOT.
set -uo pipefail
HERE="/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie"
cd "$HERE"
DATA="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/products/5d/excess_eavail_W.root"
GENARGS=()

# --- GENIE CV (no MEC) ---
if ls work_seed*/genie_mefhc_seed*.gst.root >/dev/null 2>&1; then
  echo "[band] hadd GENIE CV ($(ls work_seed*/genie_mefhc_seed*.gst.root | wc -l) seeds)"
  hadd -f genie_mefhc_cv_ALL.gst.root work_seed*/genie_mefhc_seed*.gst.root >/dev/null 2>&1
  python3 gen_to_xsec_eavailW.py --gst genie_mefhc_cv_ALL.gst.root --generator genie \
      --out genie_cv_xsec_eavailW.root --graphs xsec_graphs.root \
      --flux flux_mefhc_numu.root --flux-hist flux_numu && \
    GENARGS+=(--gen "GENIE-CV:genie_cv_xsec_eavailW.root")
fi

# --- GENIE + Valencia MEC ---
if ls work_mecseed*/genie_mefhc_mecseed*.gst.root >/dev/null 2>&1; then
  echo "[band] hadd GENIE+MEC ($(ls work_mecseed*/genie_mefhc_mecseed*.gst.root | wc -l) seeds)"
  hadd -f genie_mefhc_mec_ALL.gst.root work_mecseed*/genie_mefhc_mecseed*.gst.root >/dev/null 2>&1
  python3 gen_to_xsec_eavailW.py --gst genie_mefhc_mec_ALL.gst.root --generator genie \
      --out genie_mec_xsec_eavailW.root --graphs xsec_graphs.root \
      --flux flux_mefhc_numu.root --flux-hist flux_numu && \
    GENARGS+=(--gen "GENIE+MEC:genie_mec_xsec_eavailW.root")
fi

# --- NuWro ---
if ls work_nuwro_p*/nuwro_flat.root >/dev/null 2>&1; then
  echo "[band] NuWro ($(ls work_nuwro_p*/nuwro_flat.root | wc -l) files)"
  python3 nuwro_to_xsec_eavailW.py --flat 'work_nuwro_p*/nuwro_flat.root' \
      --out nuwro_cv_xsec_eavailW.root && \
    GENARGS+=(--gen "NuWro:nuwro_cv_xsec_eavailW.root")
fi

if [ ${#GENARGS[@]} -eq 0 ]; then
  echo "[band] no generator events present yet -- nothing to overlay"; exit 0
fi
echo "[band] overlay: ${GENARGS[*]}"
python3 overlay_eavailW_band.py --data "$DATA" "${GENARGS[@]}" \
    --png eavailW_band.png --out eavailW_band.root
