#!/usr/bin/env bash
# One canonical final-writer path for the batch/interactive Gate-2 hedge.
# Both routes share this lock and publish weights first, receipt last.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
INPUT=${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
PRODUCER_RECEIPT=${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json
INDEPENDENT_RECEIPT=${REPO}/docs/orchestration/state/g2-gate1b-npz-validation-20260719.json
VALIDATOR=${REPO}/nd-unfolding/pet/gate2_target_runtime.py
LOADER=${REPO}/nd-unfolding/pet/fullevent_fps_dataloader.py
U2D=${REPO}/2d-unfolding/unfold_2d_omnifold_unbinned.py
FINAL_DIR=${REPO}/nd-unfolding/g2_fullevent/gate2/final
FINAL_WEIGHTS=${FINAL_DIR}/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy
FINAL_RECEIPT=${FINAL_DIR}/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
LOCK=${REPO}/nd-unfolding/g2_fullevent/gate2/.gate2-final-writer.lock

# These are this wrapper's pin on the code it is ABOUT TO RUN -- they say "the tree still holds what
# was reviewed", not "a past receipt is still valid".
#
# 2026-08-04 RE-ISSUE. The validator and loader hashes below were advanced because decisions D1
# (B-4: step 1 consumes w_reco) and D2 (the nominal consumes the published target) changed both
# files, and Gate-2 is being re-run against the changed code. That is the sanctioned path -- re-issue
# the owning gate -- and NOT the forbidden one, which is editing a digest so an existing receipt's
# mismatch disappears while the receipt itself is never re-earned. The previous values were
# validator=f9e20f4c3a92748e6c52deebd26c1c94c09d94bf26f259675a04e6f3695669d1
# loader=538031732c46d08540dcf64ae244b79cf001a43f518fcc7a1fb5d2b24b66abee, and the products they
# certified are archived alongside the 2026-07-19 receipt rather than deleted.
# 2026-08-05 SECOND ADVANCE, loader only. Run 56342333 PASSED against loader
# 4c3a001cb5b6a52a3e2a1f04be4aabe9ea4666b86ef550623508a56d049af0c4 (R=1.1240802949941018,
# occupied_cells=231, B-4 resolved), but the audit repairs in 2cef7e6 then moved the loader again, so
# that receipt pinned already-superseded code. Rather than argue the change was semantically inert
# for the negweight-refined path -- which is exactly the reasoning hash pins exist to reject -- the
# gate is re-run. The r1 products are archived, not deleted.
EXPECTED_INPUT_SHA=fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625
EXPECTED_VALIDATOR_SHA=13fa4853040d0afcb3c323e69b76f9b1ec20678124338c537801177a486510a0
# ADVANCED 2026-08-13 for the Gate-2 re-run under Joseph's decision. The prior value,
# 57f33f87b07e0c6b9bd27a8c56f8013acf9863c72f80f1c01de556ad09f97117, pinned the loader as it stood at
# the 2026-08-05 construction PASS. The loader now carries the Gate-5 replica-target split in
# `build_fullevent_loaders` (precomputed_target_replica_seed), which is unreachable on the nominal
# path because that branch requires bootstrap_seed to be set.
#
# THAT LAST SENTENCE IS AN ARGUMENT, NOT EVIDENCE, and this header's own precedent (2026-08-04 and
# 2026-08-05) is that the repo RE-RAN rather than re-digested, the second time explicitly refusing to
# "argue the change was semantically inert for the negweight-refined path -- which is exactly the
# reasoning hash pins exist to reject." So this bump does not stand on the argument: the re-run's
# weights must come out BIT-IDENTICAL to the archived ones, and a mismatch is a real defect that
# stops the campaign rather than a number to be explained.
EXPECTED_LOADER_SHA=e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1
EXPECTED_U2D_SHA=8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e

ROUTE=${GATE2_EXECUTION_ROUTE:-}
RUN_ID=${GATE2_RUN_ID:-}
MAX_MC_EVENTS=${GATE2_MAX_MC_EVENTS:-200000}

die() { echo "[gate2-final][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
occupied() { [[ -e "$1" || -L "$1" ]]; }

[[ "$ROUTE" == batch || "$ROUTE" == interactive ]] || die "route must be batch|interactive"
[[ "$RUN_ID" =~ ^[A-Za-z0-9._-]+$ ]] || die "invalid/missing run ID"
[[ "$MAX_MC_EVENTS" =~ ^[1-9][0-9]*$ ]] || die "invalid max-MC-events"
for path in "$INPUT" "$PRODUCER_RECEIPT" "$INDEPENDENT_RECEIPT" "$VALIDATOR" "$LOADER" "$U2D"; do
  [[ -f "$path" && ! -L "$path" ]] || die "missing/non-regular/symlink prerequisite: $path"
done
[[ "$(sha_of "$INPUT")" == "$EXPECTED_INPUT_SHA" ]] || die "frozen G2 input hash mismatch"
[[ "$(sha_of "$VALIDATOR")" == "$EXPECTED_VALIDATOR_SHA" ]] || die "validator changed after hedge submission"
[[ "$(sha_of "$LOADER")" == "$EXPECTED_LOADER_SHA" ]] || die "Gate-2 loader changed after construction PASS"
[[ "$(sha_of "$U2D")" == "$EXPECTED_U2D_SHA" ]] || die "canonical u2d changed after hedge submission"

mkdir -p "$FINAL_DIR" "$(dirname "$LOCK")"
exec 200>"$LOCK"
flock -n 200 || die "another final Gate-2 writer owns $LOCK"
occupied "$FINAL_WEIGHTS" && die "refuse occupied final weights: $FINAL_WEIGHTS"
occupied "$FINAL_RECEIPT" && die "refuse occupied final receipt: $FINAL_RECEIPT"

source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
PYTHON_BIN=$(command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "environment python3 missing"
"$PYTHON_BIN" -c 'import numpy, sklearn' || die "runtime Python lacks NumPy/sklearn"

weights_tmp=$(mktemp "${FINAL_DIR}/.gate2-weights.${RUN_ID}.XXXXXX.npy")
receipt_tmp=$(mktemp "${FINAL_DIR}/.gate2-receipt.${RUN_ID}.XXXXXX.json")
cleanup() { rm -f -- "$weights_tmp" "$receipt_tmp"; }
trap cleanup EXIT

echo "[gate2-final] route=$ROUTE run_id=$RUN_ID host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
"$PYTHON_BIN" "$VALIDATOR" validate \
  --inputs "$INPUT" \
  --producer-receipt "$PRODUCER_RECEIPT" \
  --independent-receipt "$INDEPENDENT_RECEIPT" \
  --output "$receipt_tmp" \
  --weights-output "$weights_tmp" \
  --published-weights-path "$FINAL_WEIGHTS" \
  --execution-route "$ROUTE" \
  --run-id "$RUN_ID" \
  --slurm-job-id "${SLURM_JOB_ID:-none}" \
  --max-mc-events "$MAX_MC_EVENTS"

[[ -s "$weights_tmp" && -s "$receipt_tmp" ]] || die "validator did not produce both staged products"
"$PYTHON_BIN" - "$receipt_tmp" "$weights_tmp" "$FINAL_WEIGHTS" <<'PY' || die "staged receipt/weights mismatch"
import hashlib,json,os,sys
receipt,weights,final=sys.argv[1:4]
r=json.load(open(receipt))
assert r["status"]=="PASS"
assert r["pet_training_started"] is False
assert r["step1_feed"]["weights"]["published_path"]==final
h=hashlib.sha256()
with open(weights,"rb") as f:
    for block in iter(lambda:f.read(16*1024*1024),b""): h.update(block)
assert r["step1_feed"]["weights"]["sha256"]==h.hexdigest()
assert r["step1_feed"]["weights"]["size_bytes"]==os.path.getsize(weights)
PY

# Same-filesystem hard links provide no-clobber publication. Receipt is last.
ln "$weights_tmp" "$FINAL_WEIGHTS" || die "weights publication race"
[[ "$(sha_of "$FINAL_WEIGHTS")" == "$(sha_of "$weights_tmp")" ]] || die "published weights hash mismatch"
ln "$receipt_tmp" "$FINAL_RECEIPT" || die "receipt publication race"
rm -f -- "$weights_tmp" "$receipt_tmp"
echo "[gate2-final] PASS weights=$FINAL_WEIGHTS receipt=$FINAL_RECEIPT end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
