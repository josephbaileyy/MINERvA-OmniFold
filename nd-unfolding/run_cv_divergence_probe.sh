#!/bin/bash
# Locate the FIRST divergence between two repeated PRODUCTION CV executions.
#
# STAGE RECORD, written before submission per the 2026-09-18 grant.
#   stage     : D-CVDIV-1, a new diagnostic stage under the standing compute grant.
#   question  : unified_throw_cov.py:840 and :1011 call `_xsec_for_weights` with the SAME seed and
#               the same operands, and the two results differ by r_null = 4.4520002137582904e-14.
#               WHERE does the divergence first appear?
#   decision  : which remedy class is even applicable. If the first classifier evaluation already
#               differs, the estimator is non-reproducible on production inputs and pinning is the
#               candidate remedy. If evaluation N differs after N-1 identical ones, the estimator is
#               reproducible and something downstream accumulates -- pinning would NOT fix it. If
#               none differ, r_null arises outside this path entirely.
#   NOT       : no adoption, no grading, no significance, no cross-node claim.
#
# PRODUCTION-FAITHFUL, NOT MERELY LARGER. The allocation shape below MATCHES
# `sbatch_uthrow_combine_5d_fast.sh:4` -- `--cpus-per-task=16 --mem=90G` -- because the estimator
# runs with `n_jobs=None`, i.e. every available thread, so the CPU count is part of the
# configuration under study. A different shape would be a different experiment.
#
#SBATCH --job-name=z_cvdiv
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G --time=02:00:00
#SBATCH --output=uq_5d/z_cvdiv_%j.out --error=uq_5d/z_cvdiv_%j.err
set -eo pipefail

# Asserted equal to the #SBATCH directives by tests/test_compute_launcher_pricing.py, which reads
# this file statically -- sbatch runs a COPY, so $0 and BASH_SOURCE both name the spool path.
ENFORCED_NTASKS=1
ENFORCED_WALL_HOURS=2.0
ENFORCED_TASK_HOURS=2.0

# shellcheck source=lib_r5_admission.sh
. "$(dirname "${BASH_SOURCE[0]:-$0}")/lib_r5_admission.sh" 2>/dev/null \
  || . "${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}/nd-unfolding/lib_r5_admission.sh"

CODE_ROOT="${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}"
BANK="${MNV_BANK:?set it to the bank DIRECTORY holding cv.npz}"
SEED="${MNV_ESTIMATOR_SEED:?set it to the estimator seed, the SAME one for both executions}"
ITERS="${MNV_ITERS:-5}"
OUT="${MNV_OUT:?set it to the output record path, under a DIAGNOSTIC directory}"
R5_RECEIPT="${MNV_R5_RECEIPT:?set it to a fresh committed R5 meter receipt}"
DECLARED_TASK_HOURS="${MNV_DECLARED_TASK_HOURS:?set it to the reservation you are declaring}"

QUESTION="Where does the first divergence appear between two repeated production CV executions \
that are given identical operands and the same estimator seed? The endpoint norm r_null = \
4.4520002137582904e-14 says they differ and cannot say where."
DECISION_VALUE="Which remedy class applies at all: an estimator-level fix such as pinning, a \
downstream accumulation fix, or neither because the divergence is outside this path. The three \
outcomes point at different repairs and only one of them is pinning."

case "$OUT" in
  *DIAGNOSTIC*) : ;;
  *)
    echo "REFUSED -- MNV_OUT must contain DIAGNOSTIC in its path. Got: $OUT" >&2
    exit 6 ;;
esac
if [ -e "$OUT" ]; then
  echo "REFUSED -- $OUT exists. Overwriting would destroy the record it replaces." >&2
  exit 7
fi
if [ ! -f "$BANK/cv.npz" ]; then
  echo "REFUSED -- no $BANK/cv.npz. MNV_BANK is a DIRECTORY, not a file." >&2
  exit 15
fi

r5_source_environment "$CODE_ROOT" || exit $?
r5_require_interpreter "$CODE_ROOT" || exit $?
if ! python3 -c "import lightgbm, numpy" 2>/dev/null; then
  echo "REFUSED -- the interpreter cannot import lightgbm and numpy." >&2
  python3 -V >&2
  exit 11
fi

r5_require_declared_cap "$DECLARED_TASK_HOURS" "$ENFORCED_TASK_HOURS" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" || exit $?
r5_admission_check "$CODE_ROOT" "$R5_RECEIPT" "$ENFORCED_TASK_HOURS" 0 || exit $?

r5_record_preamble "$QUESTION" "$DECISION_VALUE" \
  "bank=$BANK (cv.npz digest-verified in-probe) seed=$SEED iters=$ITERS -- REAL inputs, REAL \
weights, production estimator settings UNPINNED, and _xsec_for_weights itself" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" "$ENFORCED_TASK_HOURS" "$R5_RECEIPT"

echo "=== environment, recorded because the answer is a property of it ==="
echo "  hostname   : $(hostname)"
echo "  SLURM_JOB  : ${SLURM_JOB_ID:-unset}"
echo "  SLURM_CPUS : ${SLURM_CPUS_PER_TASK:-unset}   (production combine used 16)"

cd "$CODE_ROOT/nd-unfolding"
_rc=0
python3 z_cv_divergence_probe.py --bank "$BANK" --iters "$ITERS" \
  --estimator-seed "$SEED" --out "$OUT" || _rc=$?

if [ "$_rc" -ne 0 ]; then
  echo "CV DIVERGENCE PROBE rc=$_rc." >&2
  echo "  rc 15 means the bank had no cv.npz; a nonzero from the probe itself may mean the bank" >&2
  echo "  digest did not match the precursor receipt, which is a refusal and not a result." >&2
  r5_retry_notice
  exit "$_rc"
fi
echo "CV DIVERGENCE PROBE COMPLETE -- DIAGNOSTIC, NON-ADOPTED. Record: $OUT"
echo "  It grades nothing and adopts nothing."
