#!/bin/bash
# P4-FPS interactive unfolds (Agent C). Drives the 10 FPS active-endpoint unfolds as
# concurrent `srun --overlap` steps into a held interactive-QOS alloc (fast QOS; the shared
# depressed QOS left the batch array unscheduled ~6.5h). Mirrors sbatch_unfold_active_fps.sh
# EXACTLY: FPS 285-bin extended grid, --axes "" + --full-phase-space + PT_EXT/PZ_EXT, seed 42,
# NO --universe (the merged ROOT already IS the promoted selection-complete universe), output
# name carries the _uni_full_<BAND>_<EP> token for analyze_universes_nd.py's UNI_RE. skip-if-exists
# + atomic per-endpoint log so a wall-kill only loses in-flight endpoints (re-grab + rerun resumes).
# Concurrency is moderate for the 75GB/endpoint Lustre files (io-bound-bank lesson) -- but --axes ""
# reads only the scalar pt/pz/weight branches, a small subset of the point cloud.
#   JOBID=<interactive alloc id> [CONC=5] [CPT=24] bash run_active_fps_unfolds_interactive.sh
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
JOBID="${JOBID:?set JOBID to the interactive alloc job id}"
CONC="${CONC:-5}"; CPT="${CPT:-24}"
BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"
# PUBLICATION footing: explicit --bkg-mode (default negweight-refined) into a SEPARATE namespace.
# The pre-2026-07-18 purity controls in active_universe_5d/fps/unfolds/ are PRESERVED untouched.
BKG_MODE="${BKG_MODE:-negweight-refined}"
[[ "${BKG_MODE}" == "negweight-refined" ]] || { echo "[FAIL] publication driver requires BKG_MODE=negweight-refined (got '${BKG_MODE}')"; exit 2; }
MERGEDIR="${ND}/active_universe_5d/fps/merged"
OUTDIR="${ND}/active_universe_5d/fps/unfolds_${BKG_MODE//-/_}"; mkdir -p "${OUTDIR}"
echo "[p4fps-unfold] JOBID=${JOBID} CONC=${CONC} CPT=${CPT} bkg=${BKG_MODE} ns=${OUTDIR} start $(date -u '+%F %T UTC')"
for BAND in "${BANDS[@]}"; do
  for EP in 0 1; do
    MERGED="${MERGEDIR}/runEventLoopOmniFold_5D_FPS_active_${BAND}_${EP}_universes_full.root"
    OUT="${OUTDIR}/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_${BAND}_${EP}.root"
    # skip-if-COMPLETE: validate the existing output on the compute node (login node has no ROOT).
    # A wall-truncated .root passes `-s` but fails completeness -> remove & redo (never skip a bad file).
    if [[ -s "${OUT}" ]]; then
      if srun --jobid="${JOBID}" --overlap --exact -n1 -c2 bash -lc \
           "export HOME=/global/homes/j/josephrb ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28; source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1; cd '${ND}' && python3 fps_unfold_complete.py '${OUT}'" >/dev/null 2>&1; then
        echo "[SKIP] ${BAND}:${EP} (validated complete)"; continue
      fi
      echo "[REDO] ${BAND}:${EP} (present but incomplete/truncated -> removing)"; rm -f "${OUT}"
    fi
    if [[ ! -s "${MERGED}" ]]; then echo "[WAIT] ${BAND}:${EP} merged ROOT absent"; continue; fi
    while [ "$(jobs -rp | wc -l)" -ge "${CONC}" ]; do sleep 8; done
    srun --jobid="${JOBID}" --overlap --exact -n1 -c"${CPT}" bash -lc "
      export HOME=/global/homes/j/josephrb OMP_NUM_THREADS=${CPT} \
        ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
      source '${REPO}/setup_salloc_env.sh' >/dev/null 2>&1
      cd '${ND}'
      TMP='${OUT}.tmp'
      python3 unfold_nd_omnifold_unbinned.py --omnifile '${MERGED}' --mcfile '${FLUX_MC}' --axes '' \
        --full-phase-space --pt-edges '${PT_EXT}' --pz-edges '${PZ_EXT}' \
        --iters 5 --use-weights --estimator lgbm --seed 42 --bkg-mode '${BKG_MODE}' --out \"\$TMP\" --verbose \
        > '${OUTDIR}/unfold_${BAND}_${EP}.log' 2>&1 \
        && mv -f \"\$TMP\" '${OUT}' \
        && echo '[done] ${BAND}:${EP} '\$(date -u +%T) \
        || echo '[FAIL] ${BAND}:${EP} rc='\$? ' (see ${OUTDIR}/unfold_${BAND}_${EP}.log)'" &
    sleep 3
  done
done
wait
# mode-stamped completion/config manifest sidecars (login node; clean JSON, no ROOT). Written only
# for outputs that landed, so a truncated/absent endpoint has no config and cannot enter the rollup.
for BAND in "${BANDS[@]}"; do for EP in 0 1; do
  OUT="${OUTDIR}/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_${BAND}_${EP}.root"
  [[ -s "${OUT}" ]] || continue
  cat > "${OUT}.config.json" <<EOF
{"band":"${BAND}","endpoint":${EP},"bkg_mode":"${BKG_MODE}","estimator":"lgbm","seed":42,
 "iters":5,"use_weights":true,"full_phase_space":true,"launcher":"run_active_fps_unfolds_interactive.sh"}
EOF
done; done
N=$(find "${OUTDIR}" -name 'fps2d_xsec_MEFHC_5iter_lgbm_uni_full_*_?.root' -size +0c 2>/dev/null | wc -l)
echo "[p4fps-unfold] all steps returned $(date -u '+%F %T UTC'); unfolds present=${N}/10 (bkg=${BKG_MODE})"
