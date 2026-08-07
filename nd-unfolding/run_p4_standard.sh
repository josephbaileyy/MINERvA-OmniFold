#!/bin/bash
# CANONICAL standard-only P4 driver (repair 2026-07-18) — the ONE authoritative,
# manifest-bound, fail-closed command chain. Runs inside a compute alloc via
# `srun --overlap --jobid=<holder>` (do NOT nest srun inside stages). STANDARD only;
# FPS post-processing is Agent C's and is never invoked here.
#
# Ordered stages (each fail-closed; the chain aborts on any nonzero stage):
#   1 audit          run_p4_merge_audit_std.sh            (10 hadd + per-playlist audit)
#   2 unfold         run_p4_unfold_std.sh                 (atomic, resumable, --seed 42, no --universe)
#   3 evidence       p4_evidence.py                       (recompute hashes + merged/endpoint receipts + manifest)
#   --- HARD GATE: standard-p4-verifier must PASS on the committed patch before covariance ---
#   4 components     p4_build_components.py               (manifest-bound; named bkgaware components + 5 active bands)
#   5 validate       p4_validate_active_lateral.py        (candidate/support/manifest/merged-audit)
#   6 project        p4_project_4d.py                     (5D->4D mask/edge hashes + central non-mutation)
#
# REPAIR-4, 2026-08-07 (verifier defect 1 of six; see
# docs/orchestration/REPAIR4-DEFECT-STATUS-20260807.md). Stages 4-6 had NEVER EXECUTED --
# STOP_AFTER defaulted to a pre-covariance stage, so nothing ever ran them and nothing
# tested them. They were not a working path with typos; all three of the following were
# independently wrong and fixing only the argument names would still have died on the key:
#   (a) ORDER: evidence ran BEFORE unfold, so the manifest described endpoints that the very
#       next stage could rewrite. Correct order is merge+audit -> unfold -> endpoint-evidence,
#       which is now what runs. NOTE the resume/attest path in run_p4_unfold_std.sh reads the
#       COMMITTED manifest from the previous round, which is what legacy attestation means --
#       it is not a forward reference to the manifest this run is about to produce.
#   (b) CLI: the validator was called with `--active`/`--merged-dir`; it requires
#       `--candidate --support --manifest --merged-audit --out`. The projector was called with
#       `--proj`, which it does not define.
#   (c) KEY: both calls named `hCov_std_final5_candidate`, which NOTHING writes. The builder
#       emits `hCov_stdcombined5d_total_candidate` (full total) and
#       `hCov_stdsyst5d_total_candidate`; the projector takes the full total.
#
# RETIRED / FORBIDDEN for standard publication (unsafe, non-manifest-bound):
#   merge_active_endpoints.sh, run_active_lateral_unfolds_interactive.sh  (guarded to abort)
#
# STOP_AFTER controls the last stage to run. DEFAULT IS 'audit' -- changed in repair-4 from
# 'evidence', because reordering put `unfold` (which WRITES receipts) before evidence, and a
# default that silently starts writing receipts is the opposite of a safe preflight. Valid:
#   audit | unfold | evidence | components | validate | project
# Covariance stages (4-6) run ONLY with a P4_VERIFIER_PASS token bound to a verifier receipt.
set -o pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1
cd "${ND}"
STOP_AFTER="${STOP_AFTER:-audit}"
case "${STOP_AFTER}" in
  audit|unfold|evidence|components|validate|project) ;;
  merge) echo "[p4-std] STOP_AFTER=merge renamed to 'audit' in repair-4 (stage 1 is merge+audit)"; STOP_AFTER=audit ;;
  *) echo "[p4-std] ABORT unknown STOP_AFTER='${STOP_AFTER}' (audit|unfold|evidence|components|validate|project)"; exit 2 ;;
esac
SUPPORT_FAMILY="${SUPPORT_FAMILY:-uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root}"
EVID="active_universe_5d/standard/evidence"
CAND="active_universe_5d/standard/candidate"    # candidate outputs only (never adopted paths)
run(){ echo "[p4-std] STAGE $*"; "$@" || { echo "[p4-std] ABORT at: $*"; exit 1; }; }

echo "[p4-std] canonical driver start $(date -u +%T); STOP_AFTER=${STOP_AFTER}; code_rev=$(git rev-parse HEAD)"
run bash run_p4_merge_audit_std.sh
[[ "${STOP_AFTER}" == "audit" ]] && { echo "[p4-std] stop after merge+audit (safe preflight; nothing written)"; exit 0; }
run bash run_p4_unfold_std.sh
[[ "${STOP_AFTER}" == "unfold" ]] && { echo "[p4-std] stop after unfold"; exit 0; }
run env P4_CODE_REV="$(git rev-parse HEAD)" python3 p4_evidence.py
[[ "${STOP_AFTER}" == "evidence" ]] && { echo "[p4-std] stop after evidence (covariance gated on verifier PASS)"; exit 0; }

# ---- covariance stages: authorized ONLY after standard-p4-verifier PASS ----
if [[ -z "${P4_VERIFIER_PASS}" ]]; then
  echo "[p4-std] HARD GATE: covariance construction requires P4_VERIFIER_PASS token (standard-p4-verifier PASS). Refusing."
  exit 3
fi
mkdir -p "${CAND}"
# D1c: read the candidate total key from p4_lib rather than hardcoding it here again.
CAND_TOTAL_KEY=$(python3 -c "import p4_lib;print(p4_lib.CANDIDATE_TOTAL_KEY)") \
  || { echo "[p4-std] ABORT cannot resolve candidate total key"; exit 2; }
[[ -n "${CAND_TOTAL_KEY}" ]] || { echo "[p4-std] ABORT empty candidate total key"; exit 2; }
echo "[p4-std] candidate total key = ${CAND_TOTAL_KEY}"
run python3 p4_build_components.py --manifest "${EVID}/p4_standard_manifest.json" \
    --support-family "${SUPPORT_FAMILY}" \
    --out "${CAND}/std_final5_candidate.root" --out-manifest "${CAND}/std_component_manifest.json"
[[ "${STOP_AFTER}" == "components" ]] && { echo "[p4-std] stop after components"; exit 0; }
# validator takes a candidate PATH (it hashes the file itself for the J32 binding), NOT ROOT:key
run python3 p4_validate_active_lateral.py \
    --candidate "${CAND}/std_final5_candidate.root" \
    --support "${SUPPORT_FAMILY}" \
    --manifest "${EVID}/p4_standard_manifest.json" \
    --merged-audit "${EVID}/p4_merged_audit.json" \
    --out "${CAND}/p4_standard_validation.json"
[[ "${STOP_AFTER}" == "validate" ]] && { echo "[p4-std] stop after validate"; exit 0; }
# projector takes ROOT:key, and the key is the FULL total the builder actually writes
run python3 p4_project_4d.py \
    --c5 "${CAND}/std_final5_candidate.root:${CAND_TOTAL_KEY}" \
    --manifest "${EVID}/p4_standard_manifest.json" \
    --out "${CAND}/std_proj4d_candidate.root"
echo "[p4-std] canonical chain complete (CANDIDATE only; adoption is a separate authorized step) $(date -u +%T)"
