#!/bin/bash
# CAUSE 4 -- supply the re-added jitter print's value, seed and both operand digests.
#
# STAGE RECORD, written before submission.
#   stage    : C4, on the REQUIRED deliverable path.
#   question : `causes.4` asks for "the scalar jitter add-back print value, seed and both operand
#              digests". SPEC 2.4's four conditions; the print was re-added at ce15cc2f and has
#              never been run, so the value does not exist.
#   decision : C4's disposition. Ruled approved, so this supplies the recorded quantity; the
#              tolerance-free part is that no threshold is applied to it.
#   NOT      : no adoption, no grading. The output ROOT is written to a DIAGNOSTIC path and is NOT
#              a candidate -- the preserved precursor at z_precursor_20260914 is untouched.
#
# COST. The jitter quantity needs a SECOND CV unfold at estimator_seed + 7, inside a combine.
# Measured anchors: `uthrow5d_combF` actuals 0.3875 / 0.4239 / 0.5764 CPU task-h, plus ~0.30 h for
# one CV unfold (from job 58524334's 2184 s for TWO). So ~0.9 h expected against the 2.00 h cap
# below -- about 2.3x margin. The production combine's own cap is 3.00 h; this is tightened because
# the measured distribution supports it.
#
#SBATCH --job-name=c4_jitter
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G --time=02:00:00
#SBATCH --output=uq_5d/c4_jitter_%j.out --error=uq_5d/c4_jitter_%j.err
set -eo pipefail

ENFORCED_NTASKS=1
ENFORCED_WALL_HOURS=2.0
ENFORCED_TASK_HOURS=2.0

# shellcheck source=lib_r5_admission.sh
. "$(dirname "${BASH_SOURCE[0]:-$0}")/lib_r5_admission.sh" 2>/dev/null \
  || . "${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}/nd-unfolding/lib_r5_admission.sh"

CODE_ROOT="${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}"
BANK="${MNV_BANK:?set it to the digest-verified bank directory}"
THROW_GLOB="${MNV_THROW_GLOB:?set it to the preserved uthrow slab glob}"
BLOCK_GLOB="${MNV_BLOCK_GLOB:?set it to the preserved block slab glob}"
SEED="${MNV_ESTIMATOR_SEED:?set it to the estimator seed}"
DRAW="${MNV_DRAW_SEED:?set it to the draw seed}"
OUT_ROOT="${MNV_OUT_ROOT:?set it to a DIAGNOSTIC output root path}"
R5_RECEIPT="${MNV_R5_RECEIPT:?set it to a fresh committed R5 meter receipt}"
DECLARED_TASK_HOURS="${MNV_DECLARED_TASK_HOURS:?set it to the reservation you are declaring}"

QUESTION="Cause 4: the scalar jitter add-back print value at estimator_seed + 7, its seed, and \
both operand content digests. SPEC 2.4 conditions 1 and 2; condition 3 is enforced by the in-code \
guard and condition 4 by the deliberate absence of the retired subtraction."
DECISION_VALUE="C4 disposition. The quantity is a recorded magnitude with no threshold applied to \
it, which is what a tolerance-free disclosure means."

case "$OUT_ROOT" in
  *DIAGNOSTIC*) : ;;
  *) echo "REFUSED -- MNV_OUT_ROOT must contain DIAGNOSTIC. Got: $OUT_ROOT" >&2; exit 6 ;;
esac
case "$OUT_ROOT" in
  *z_precursor_20260914*|*universe_stage2*)
    echo "REFUSED -- MNV_OUT_ROOT points into preserved production data: $OUT_ROOT" >&2
    echo "          The preserved precursor must not be overwritten by a diagnostic." >&2
    exit 6 ;;
esac
if [ -e "$OUT_ROOT" ]; then
  echo "REFUSED -- $OUT_ROOT exists; name a new path." >&2; exit 7
fi

r5_source_environment "$CODE_ROOT" || exit $?
r5_require_interpreter "$CODE_ROOT" || exit $?
r5_require_declared_cap "$DECLARED_TASK_HOURS" "$ENFORCED_TASK_HOURS" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" || exit $?
r5_admission_check "$CODE_ROOT" "$R5_RECEIPT" "$ENFORCED_TASK_HOURS" 0 || exit $?

r5_record_preamble "$QUESTION" "$DECISION_VALUE" \
  "bank=$BANK throws=$THROW_GLOB blocks=$BLOCK_GLOB seed=$SEED draw=$DRAW -- preserved slabs, \
40 throw and 21 block, matching the precursor's declared populations" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" "$ENFORCED_TASK_HOURS" "$R5_RECEIPT"
echo "  hostname : $(hostname)   SLURM_JOB ${SLURM_JOB_ID:-unset}   CPUS ${SLURM_CPUS_PER_TASK:-unset}"

cd "$CODE_ROOT/nd-unfolding"
_rc=0
python3 unified_throw_cov_5d.py --combine "$THROW_GLOB" --block-slabs "$BLOCK_GLOB" \
  --bank "$BANK" --iters 5 --draw-seed "$DRAW" --estimator-seed "$SEED" \
  --jitter-print --out-root "$OUT_ROOT" || _rc=$?

if [ "$_rc" -ne 0 ]; then
  echo "CAUSE 4 JITTER PRINT rc=$_rc." >&2
  r5_retry_notice
  exit "$_rc"
fi
echo "CAUSE 4 JITTER PRINT COMPLETE -- the value is a DISCLOSURE, not a grade."
echo "  grep '[cause4]' in the log for the value and the condition-3 guard result."
