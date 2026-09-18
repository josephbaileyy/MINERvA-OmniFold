#!/bin/bash
# CAUSE 1 -- the per-band endpoint census (P leg) and the one-sided magnitude (M leg).
#
# STAGE RECORD, written before submission.
#   stage    : C1, on the REQUIRED deliverable path.
#   question : both legs `CRITERIA-20260811` cause 1 asks for and this repository does not have --
#              a per-band +/- endpoint census with the flux bank's contiguity, and the sqrt-Tr and
#              per-bin median of X built BOTH WAYS on X's own bank (one-sided CV-centered vs
#              mean-centered), reported as a DISTRIBUTION and not a max.
#   decision : C1's disposition. Joseph ruled it approved as a tolerance-free DISCLOSURE, so the
#              output is a magnitude to record, not a threshold to pass.
#   NOT      : no adoption, no grading, no re-unfolding. `receipt_cause1_endpoint_census_5d.py`
#              reads per-universe flat vectors already on disk; nothing is rebuilt or replaced.
#   predeclared: docs/orchestration/PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md
#
# Priced at ~0.03 CPU task-h in SPEC 5.8b (44 as-built + 42+42 one-sided band covariances at
# ~0.5 s each, plus accumulation). The cap below is ~8x that, for the unmeasured I/O leg.
#
#SBATCH --job-name=c1_census
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=48G --time=00:15:00
#SBATCH --output=uq_5d/c1_census_%j.out --error=uq_5d/c1_census_%j.err
set -eo pipefail

ENFORCED_NTASKS=1
ENFORCED_WALL_HOURS=0.25
ENFORCED_TASK_HOURS=0.25

# shellcheck source=lib_r5_admission.sh
. "$(dirname "${BASH_SOURCE[0]:-$0}")/lib_r5_admission.sh" 2>/dev/null \
  || . "${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}/nd-unfolding/lib_r5_admission.sh"

CODE_ROOT="${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}"
DATA_REPO="${MNV_DATA_REPO:?set it to the repo holding uq_5d, passed to --repo}"
OUT="${MNV_OUT:?set it to the receipt output path}"
R5_RECEIPT="${MNV_R5_RECEIPT:?set it to a fresh committed R5 meter receipt}"
DECLARED_TASK_HOURS="${MNV_DECLARED_TASK_HOURS:?set it to the reservation you are declaring}"

QUESTION="Cause 1 both legs: the per-band +/- endpoint census with flux contiguity, and sqrt-Tr \
and per-bin median built one-sided CV-centered versus mean-centered on X own bank, as a \
distribution rather than a max."
DECISION_VALUE="C1 disposition. Ruled a tolerance-free disclosure, so this produces a magnitude \
to record rather than a threshold to pass."

if [ -e "$OUT" ]; then
  echo "REFUSED -- $OUT exists. Overwriting would destroy the record it replaces." >&2
  exit 7
fi

r5_source_environment "$CODE_ROOT" || exit $?
r5_require_interpreter "$CODE_ROOT" || exit $?
r5_require_declared_cap "$DECLARED_TASK_HOURS" "$ENFORCED_TASK_HOURS" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" || exit $?
r5_admission_check "$CODE_ROOT" "$R5_RECEIPT" "$ENFORCED_TASK_HOURS" 0 || exit $?

r5_record_preamble "$QUESTION" "$DECISION_VALUE" \
  "repo=$DATA_REPO -- per-universe flat vectors already on disk; nothing re-unfolded" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" "$ENFORCED_TASK_HOURS" "$R5_RECEIPT"
echo "  hostname : $(hostname)   SLURM_JOB ${SLURM_JOB_ID:-unset}"

cd "$CODE_ROOT/nd-unfolding"
_rc=0
python3 receipt_cause1_endpoint_census_5d.py --repo "$DATA_REPO" --out "$OUT" || _rc=$?
if [ "$_rc" -ne 0 ]; then
  echo "CAUSE 1 CENSUS rc=$_rc." >&2
  r5_retry_notice
  exit "$_rc"
fi
echo "CAUSE 1 CENSUS COMPLETE -- a DISCLOSURE, not a grade. Receipt: $OUT"
