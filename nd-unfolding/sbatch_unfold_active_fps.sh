#!/bin/bash
#SBATCH --job-name=unfActFpsC
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=96G --time=04:00:00
#SBATCH --array=0-9%5
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=active_universe_5d/fps/logs/unfActFpsC_%A_%a.out
#SBATCH --error=active_universe_5d/fps/logs/unfActFpsC_%A_%a.err
# P4-FPS active-endpoint unfolds (Agent C). GATED: run after sbatch_hadd_active_fps.sh has produced
# all 10 merged endpoint omnifiles in active_universe_5d/fps/merged/.
# 5 bands x 2 endpoints = 10 selection-complete active endpoints. Each is unfolded on the FPS 285-bin
# extended grid at the SAME fixed estimator seed 42, NO --universe (the endpoint IS the promoted
# universe baked into the merged omnifile's primary selection). Reuses the FPS sweep unfold config.
# Output name carries the _uni_full_<BAND>_<EP> token so analyze_universes_5d.py's UNI_RE groups the
# +/- endpoints by band (N=2 -> MAT mean-centered +/-1sigma outer-product lateral cov), mirroring the
# 5D-standard precedent (active_universe_5d/AGENT_A_HANDOFF.md steps 2-3).
# PUBLICATION launcher: writes negweight-refined outputs into a SEPARATE mode-explicit namespace
# active_universe_5d/fps/unfolds_negweight_refined/ (atomic .tmp->mv + a .config.json mode stamp).
# The pre-2026-07-18 purity controls in active_universe_5d/fps/unfolds/ are PRESERVED untouched (they
# ran with the unfold default --bkg-mode=purity; see fps_control_manifest.json). build_active_lateral_fps.py
# rejects any non-negweight-refined input, so a control can never enter the publication rollup.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${ND}"
PLAYBANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
PT_EXT="0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50,30.0"
PZ_EXT="0.0,0.75,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,15.0,20.0,40.0,60.0,120.0"
# PUBLICATION footing: explicit --bkg-mode (default negweight-refined). A default/purity mode is
# rejected below so a control can never be produced into the publication namespace.
BKG_MODE="${BKG_MODE:-negweight-refined}"
[[ "${BKG_MODE}" == "negweight-refined" ]] || { echo "[FAIL] publication launcher requires BKG_MODE=negweight-refined (got '${BKG_MODE}')" >&2; exit 2; }
T=${SLURM_ARRAY_TASK_ID}; ENDPOINT=$(( T % 2 )); BAND=${PLAYBANDS[$(( T / 2 ))]}
OMNIFILE="${ND}/active_universe_5d/fps/merged/runEventLoopOmniFold_5D_FPS_active_${BAND}_${ENDPOINT}_universes_full.root"
# SEPARATE mode-explicit staging namespace; the existing purity controls in unfolds/ stay untouched.
OUTDIR="${ND}/active_universe_5d/fps/unfolds_${BKG_MODE//-/_}"; mkdir -p "${OUTDIR}" "${ND}/active_universe_5d/fps/logs"
XSEC_OUT="${OUTDIR}/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_${BAND}_${ENDPOINT}.root"
CFG_OUT="${XSEC_OUT}.config.json"
CV="${ND}/uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
AUDIT="${ND}/active_universe_5d/fps/covariance/audit_merged_fps.json"
THIS_LAUNCHER="${ND}/sbatch_unfold_active_fps.sh"
# transactional skip via the ONE shared validator: skip only when ROOT recomputes COMPLETE and its
# receipt's live output hash still matches (fps_endpoint_receipt.py check).
if python3 fps_endpoint_receipt.py check --out "${XSEC_OUT}" --receipt "${CFG_OUT}"; then
  echo "[unfActFpsC] skip (validated complete + receipt) ${XSEC_OUT}"; exit 0
fi
# stale/partial/receipt-less output -> remove BOTH so a receipt is never kept for a non-fresh ROOT
rm -f "${XSEC_OUT}" "${CFG_OUT}" "${XSEC_OUT}".tmp.*
[[ -s "${OMNIFILE}" ]] || { echo "[FAIL] merged endpoint omnifile missing: ${OMNIFILE}" >&2; exit 2; }
echo "[unfActFpsC] task=$T band=${BAND} endpoint=${ENDPOINT} bkg=${BKG_MODE} $(date -u '+%F %T UTC')"
# atomic write: unfold to a UNIQUE temp then rename; a wall-kill never leaves a half-written OUT
TMP_OUT="${XSEC_OUT}.tmp.${SLURM_JOB_ID:-$$}.${SLURM_ARRAY_TASK_ID:-0}"
python3 unfold_nd_omnifold_unbinned.py \
    --omnifile "${OMNIFILE}" --mcfile "${FLUX_MC}" --axes "" \
    --full-phase-space --pt-edges "${PT_EXT}" --pz-edges "${PZ_EXT}" \
    --iters 5 --use-weights --estimator lgbm --seed 42 \
    --bkg-mode "${BKG_MODE}" \
    --out "${TMP_OUT}"
mv -f "${TMP_OUT}" "${XSEC_OUT}"                    # atomic ROOT publish
# receipt written LAST via the shared validator (validates completeness + binds live hashes +
# attributes THIS launcher). If validation fails, no receipt is minted -> the ROOT can't be consumed.
python3 fps_endpoint_receipt.py write --out "${XSEC_OUT}" --band "${BAND}" --endpoint "${ENDPOINT}" \
    --bkg-mode "${BKG_MODE}" --merged "${OMNIFILE}" --source "${ND}/unfold_nd_omnifold_unbinned.py" \
    --launcher "${THIS_LAUNCHER}" --central "${CV}" --audit "${AUDIT}" --receipt "${CFG_OUT}" \
    || { echo "[FAIL] endpoint receipt refused (bad/incomplete ROOT): ${XSEC_OUT}" >&2; rm -f "${XSEC_OUT}"; exit 3; }
echo "[unfActFpsC] done band=${BAND} endpoint=${ENDPOINT} bkg=${BKG_MODE} $(date -u '+%F %T UTC')"
