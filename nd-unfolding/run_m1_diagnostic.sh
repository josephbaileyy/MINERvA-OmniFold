#!/bin/bash
# M1 AS A DIAGNOSTIC: the 5D -> (E_avail, W) projection from the PRESERVED CANDIDATE covariance.
#
# THIS IS A DISTINCT EXECUTION PATH, NOT A BYPASS FLAG ON THE PUBLICATION PATH.
# `run_m1_projection.sh` still refuses without an adoption record and that refusal is UNTOUCHED.
# A `--force`-style switch on that script would have made the publication guard one careless
# invocation away from being waived, so this is a separate file whose product can never be a
# publication product: it is stamped `diagnostic` INSIDE the ROOT file, so a rename does not
# launder it, and it refuses to write anywhere a publication product is written.
#
# AUTHORIZATION, and its conditions. Joseph, 2026-09-18: "I explicitly authorize provisional
# projections and counterfactuals from the preserved candidate covariance when needed to resolve
# acceptance questions. Keep them labeled diagnostic and non-adopted, with separate outputs and
# receipts. Preserve the adoption requirement for publication products; add a distinct diagnostic
# execution path where needed."  Every clause of that sentence is a REFUSAL below, because a grant
# with conditions that are merely documented is a grant without conditions.
#
# WHY THE ADOPTION/PROJECTION DEPENDENCY NEEDED THIS. The acceptance question that blocks adoption
# is `tau` -- how far M1s projected correlation matrix may move before the deferred claim changes.
# `tau` is computable only FROM M1, and M1 was gated on adoption. That is a cycle, and it is the
# cycle Joseph directed be reconciled before execution. The diagnostic path cuts it in the only
# direction that does not weaken anything: the projection is produced as evidence for the adoption
# decision, and is barred by construction from being the product the decision licenses.
#
# WHAT A TERMINAL RESULT CANNOT AUTHORIZE, stated in advance: it does not adopt the trunk, does not
# calibrate a significance, does not supply support `C_Z` never had, does not become the quotable
# (E_avail,W) covariance -- `AGENTS.md:27` requires that to be projected from the ADOPTED trunk --
# and it licenses no other projection and no event-level fit. It answers one acceptance question.
#
#SBATCH --job-name=m1_diag_eavailW
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=16G --time=00:15:00
#SBATCH --output=uq_5d/m1_diag_%j.out --error=uq_5d/m1_diag_%j.err
set -eo pipefail

# ONE implementation of the R5 accounting and admission block, shared with the determinism
# launcher. A copy would not change when the original was corrected.
# shellcheck source=lib_r5_admission.sh
. "$(dirname "${BASH_SOURCE[0]:-$0}")/lib_r5_admission.sh" 2>/dev/null \
  || . "${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}/nd-unfolding/lib_r5_admission.sh"

# THE ENFORCED CAP, in the governing unit. `DECISION-20260901-joseph-delegated-ceiling-unit-is-
# task-hours.md`: task-hours are "the sum of ElapsedRaw over the arm tasks", NOT AllocCPUS-weighted.
# So the reservation is ntasks x wall = 1 x 0.25 h. Pricing this as `cpus-per-task x wall` = 2.0 is
# core-hours wearing the task-hour label, which is the exact confusion that decision record exists
# to settle, and which this campaign committed once after the ruling landed.
# These two constants are asserted EQUAL to the SBATCH directives above by
# tests/test_run_m1_diagnostic_refusals.py, which reads this file statically. They are not derived
# from BASH_SOURCE or $0 at runtime: sbatch executes a COPY, so both name the spool path.
ENFORCED_NTASKS=1
ENFORCED_WALL_HOURS=0.25
ENFORCED_TASK_HOURS=0.25

# NO APOSTROPHES IN ANY MESSAGE BELOW. An apostrophe inside ${VAR:?...} opens a quote that spans
# newlines and silently swallows the NEXT assignments, voiding the guards between. Twice already.
CODE_ROOT="${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}"
QUESTION="${MNV_ACCEPTANCE_QUESTION:?set it to the acceptance question this diagnostic resolves}"
DECISION_VALUE="${MNV_DECISION_VALUE:?set it to what a terminal result would let Joseph decide}"
SRC_COV="${MNV_SRC_COV:?set it to the PRESERVED CANDIDATE 5D covariance ROOT file}"
SRC_HIST="${MNV_SRC_HIST:?set it to the TH2D key inside that covariance}"
SRC_CV="${MNV_SRC_CV:?set it to the 5D central product supplying the reported mask}"
DST_MASK="${MNV_DST_MASK:?set it to declared-dst-cv or receiving-cells, the destination mask choice}"
OUT="${MNV_OUT:?set it to the output path, which must be under a DIAGNOSTIC directory}"
R5_RECEIPT="${MNV_R5_RECEIPT:?set it to a fresh committed R5 meter receipt}"
DECLARED_TASK_HOURS="${MNV_DECLARED_TASK_HOURS:?set it to the reservation you are declaring}"

# ---- REFUSAL 3: THE ACCEPTANCE QUESTION IS THE SCOPE OF THE GRANT ------------------------------
# The grant covers diagnostics "when needed to resolve acceptance questions". A run that cannot
# name its question is not covered by it, and neither is one that names a question in six characters.
if [ "${#QUESTION}" -lt 24 ]; then
  echo "REFUSED -- MNV_ACCEPTANCE_QUESTION is only ${#QUESTION} chars. Name the acceptance" >&2
  echo "          question this run resolves, not a label. The grant is scoped to that question." >&2
  exit 3
fi
if [ "${#DECISION_VALUE}" -lt 24 ]; then
  echo "REFUSED -- MNV_DECISION_VALUE must state what a terminal result would let Joseph decide." >&2
  echo "          A diagnostic with no decision value is compute spent to produce a number." >&2
  exit 3
fi

# ---- REFUSAL 4: THE PROJECTOR MUST BE INSTRUMENTED, INCLUDING THE CLASS LABEL ------------------
# A digest retrofitted onto an existing file records only that the file has not changed SINCE the
# retrofit, so the instrumentation has to precede the product. `runClass` is in this list because
# without it the product carries no evidence of being diagnostic other than where it happens to sit.
PROJ="$CODE_ROOT/nd-unfolding/project_cov_nd.py"
for _need in "proj_sha256" "hRowIndex" "row_index_sha256_readback" "runClass" "acceptanceQuestion"; do
  if ! grep -q "$_need" "$PROJ"; then
    echo "REFUSED -- $PROJ lacks $_need. A diagnostic product that cannot be told apart from a" >&2
    echo "          publication product is not separated, whatever directory it is written to." >&2
    exit 4
  fi
done

# ---- REFUSAL 5: THE DESTINATION MASK IS A DECLARATION, NOT A DEFAULT ---------------------------
case "$DST_MASK" in
  declared-dst-cv)
    DST_ARG=(--dst-cv "${MNV_DST_CV:?declared-dst-cv requires MNV_DST_CV, the frozen lower-D CV}") ;;
  receiving-cells)
    DST_ARG=() ;;
  *)
    echo "REFUSED -- MNV_DST_MASK must be declared-dst-cv or receiving-cells, got: $DST_MASK" >&2
    exit 5 ;;
esac

# ---- REFUSAL 6: SEPARATE OUTPUTS, ENFORCED ON THE PATH ----------------------------------------
# "separate outputs and receipts" is a condition of the grant, so it is checked rather than
# observed. The marker is required in the path itself so that a human reading a directory listing,
# or a glob in a downstream consumer, cannot pick this product up believing it is a candidate.
case "$OUT" in
  *DIAGNOSTIC*) : ;;
  *)
    echo "REFUSED -- MNV_OUT must contain DIAGNOSTIC in its path. Got: $OUT" >&2
    echo "          Separate outputs is a condition of the authorization, not a convention." >&2
    exit 6 ;;
esac
case "$OUT" in
  *projections_candidate*|*products/*)
    echo "REFUSED -- MNV_OUT points into a publication or candidate product tree: $OUT" >&2
    echo "          A diagnostic must not be written where a quotable product is looked for." >&2
    exit 6 ;;
esac

# ---- REFUSAL 7: NO SILENT OVERWRITE OF A PRIOR DIAGNOSTIC -------------------------------------
# Two diagnostics answering two questions must not collapse into one file, and a re-run under the
# one-corrective-resubmission grant must not erase the failed attempt it is correcting.
if [ -e "$OUT" ]; then
  echo "REFUSED -- $OUT already exists. Name a new output or move the old one aside." >&2
  echo "          Overwriting would destroy the receipt chain of the run it replaces." >&2
  exit 7
fi

# ---- THE ENVIRONMENT COMES FIRST. Same defect as job 58506753 found in the sibling launcher ---
# This script did not source the campaign environment AT ALL, so both its admission check and its
# payload would have run under the node default python3 -- 3.6.15, no ROOT -- and the admission
# check would have reported an interpreter SyntaxError as an accounting refusal, in the words of
# an accounting refusal. The environment is a PRECONDITION of evaluating the boundary.
r5_source_environment "$CODE_ROOT" || exit $?
r5_require_interpreter "$CODE_ROOT" || exit $?

# ---- REFUSAL 8: THE DECLARED RESERVATION MUST BE THE ENFORCED CAP -----------------------------
# A reservation bounds what the scheduler MAY charge, which is the wall cap -- never a measured
# actual from a past run, and never the cap multiplied by cpus-per-task. Both mistakes are on
# record in this campaign. Declaring a number smaller than the cap is the one that matters: it
# admits an item against headroom it may exceed.
r5_require_declared_cap "$DECLARED_TASK_HOURS" "$ENFORCED_TASK_HOURS" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" || exit $?

# ---- REFUSAL 9: R5 ADMISSION, MEASURED AND FRESH ----------------------------------------------
# Joseph, 2026-09-18: "Before every submission, account for all lanes charged usage and outstanding
# reservations ... and verify admission." The meter is the instrument for that and it is CALLED
# here rather than restated -- a rule retyped is a second implementation. It fails closed on a
# stale, missing or malformed receipt, and `check` refuses when spend + proposed >= the ceiling.
r5_admission_check "$CODE_ROOT" "$R5_RECEIPT" "$ENFORCED_TASK_HOURS" 0 || exit $?

# ---- THE PRE-SUBMISSION RECORD, which is the other half of the accounting clause ---------------
r5_record_preamble "$QUESTION" "$DECISION_VALUE" \
  "cov=$SRC_COV hist=$SRC_HIST cv=$SRC_CV mask=$DST_MASK" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" "$ENFORCED_TASK_HOURS" "$R5_RECEIPT"

# ---- THE RUN. One invocation. NO AUTOMATIC REQUEUE. -------------------------------------------
# Joseph, 2026-09-18, replacing the per-attempt approval requirement: "one corrective resubmission
# per stage after a diagnosed execution defect, a verified repair, and fresh admission. Keep
# automatic requeue disabled." So this script still never resubmits itself. What changed is that a
# DIAGNOSED defect with a VERIFIED repair no longer needs a separate approval -- it needs a fresh
# receipt and a fresh admission, which means coming back through the refusals above.
cd "$CODE_ROOT/nd-unfolding"
python3 project_cov_nd.py \
  --src-cov "$SRC_COV" --src-hist "$SRC_HIST" --src-cv "$SRC_CV" \
  --src-axes pt,pz,eavail,q3,W --keep-axes eavail,W \
  --run-class diagnostic --acceptance-question "$QUESTION" \
  "${DST_ARG[@]}" --out "$OUT" || _rc=$?
_rc="${_rc:-0}"

if [ $_rc -ne 0 ]; then
  echo "M1 DIAGNOSTIC FAILED rc=$_rc." >&2
  r5_retry_notice
  exit $_rc
fi

if [ ! -f "${OUT}.receipt.json" ]; then
  echo "REFUSED -- ${OUT}.receipt.json absent. The product exists but nothing binds it." >&2
  exit 10
fi
echo "M1 DIAGNOSTIC COMPLETE -- NON-ADOPTED, PROVISIONAL."
echo "  It answers: $QUESTION"
echo "  It does NOT adopt the trunk and is NOT the quotable (E_avail,W) covariance."
echo "  Receipt: ${OUT}.receipt.json"
