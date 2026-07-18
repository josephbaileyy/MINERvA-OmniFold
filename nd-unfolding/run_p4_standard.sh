#!/bin/bash
# CANONICAL standard-only P4 driver (repair 2026-07-18) — the ONE authoritative,
# manifest-bound, fail-closed command chain. Runs inside a compute alloc via
# `srun --overlap --jobid=<holder>` (do NOT nest srun inside stages). STANDARD only;
# FPS post-processing is Agent C's and is never invoked here.
#
# Ordered stages (each fail-closed; the chain aborts on any nonzero stage):
#   1 merge+audit    run_p4_merge_audit_std.sh            (10 hadd + per-playlist audit)
#   2 evidence       p4_evidence.py                       (recompute hashes + merged/endpoint receipts + manifest)
#   3 unfold         run_p4_unfold_std.sh                 (atomic, resumable, --seed 42, no --universe)
#   --- HARD GATE: standard-p4-verifier must PASS on the committed patch before covariance ---
#   4 components     p4_build_components.py               (manifest-bound; named bkgaware components + 5 active bands)
#   5 validate       p4_validate_active_lateral.py        (exact-5-bands / traces / component-sum / PSD / support / --merged-dir)
#   6 project        p4_project_4d.py                     (5D->4D mask/edge hashes + central non-mutation)
#
# RETIRED / FORBIDDEN for standard publication (unsafe, non-manifest-bound):
#   merge_active_endpoints.sh, run_active_lateral_unfolds_interactive.sh  (guarded to abort)
#
# STOP_AFTER controls the last stage to run (default 'evidence' = repair preflight,
# stops BEFORE covariance). Covariance stages (4-6) run ONLY with P4_VERIFIER_PASS=<token>.
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1
cd "${ND}"
STOP_AFTER="${STOP_AFTER:-evidence}"
SUPPORT_FAMILY="${SUPPORT_FAMILY:-uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root}"
EVID="active_universe_5d/standard/evidence"
CAND="active_universe_5d/standard/candidate"    # candidate outputs only (never adopted paths)
run(){ echo "[p4-std] STAGE $*"; "$@" || { echo "[p4-std] ABORT at: $*"; exit 1; }; }

echo "[p4-std] canonical driver start $(date -u +%T); STOP_AFTER=${STOP_AFTER}; code_rev=$(git rev-parse HEAD)"
run bash run_p4_merge_audit_std.sh
[[ "${STOP_AFTER}" == "merge" ]] && { echo "[p4-std] stop after merge"; exit 0; }
run env P4_CODE_REV="$(git rev-parse HEAD)" python3 p4_evidence.py
[[ "${STOP_AFTER}" == "evidence" ]] && { echo "[p4-std] stop after evidence (repair preflight; covariance gated on verifier PASS)"; exit 0; }
run bash run_p4_unfold_std.sh
[[ "${STOP_AFTER}" == "unfold" ]] && { echo "[p4-std] stop after unfold"; exit 0; }

# ---- covariance stages: authorized ONLY after standard-p4-verifier PASS ----
if [[ -z "${P4_VERIFIER_PASS}" ]]; then
  echo "[p4-std] HARD GATE: covariance construction requires P4_VERIFIER_PASS token (standard-p4-verifier PASS). Refusing."
  exit 3
fi
mkdir -p "${CAND}"
run python3 p4_build_components.py --manifest "${EVID}/p4_standard_manifest.json" \
    --support-family "${SUPPORT_FAMILY}" \
    --out "${CAND}/std_final5_candidate.root" --out-manifest "${CAND}/std_component_manifest.json"
run python3 p4_validate_active_lateral.py \
    --active "${CAND}/std_final5_candidate.root:hCov_std_final5_candidate" \
    --support "${SUPPORT_FAMILY}" --merged-dir active_universe_5d/standard/merged \
    --out "${CAND}/p4_standard_validation.json"
run python3 p4_project_4d.py --c5 "${CAND}/std_final5_candidate.root:hCov_std_final5_candidate" \
    --proj "${CAND}/M_5d_to_4d.npz" --manifest "${EVID}/p4_standard_manifest.json" \
    --out "${CAND}/std_proj4d_candidate.root"
echo "[p4-std] canonical chain complete (CANDIDATE only; adoption is a separate authorized step) $(date -u +%T)"
