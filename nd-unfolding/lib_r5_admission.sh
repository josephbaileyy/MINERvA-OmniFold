# shellcheck shell=bash
# R5 ACCOUNTING AND ADMISSION, in ONE implementation. Source it; do not retype it.
#
# Joseph, 2026-09-18: "Before every submission, account for all lanes charged usage and outstanding
# reservations, record the scientific question, inputs, expected decision value, and enforced
# resource limits, and verify admission. The overall ceiling is not a spending target."
#
# WHY A LIBRARY. The second launcher to need this block would otherwise carry a copy, and a copy is
# a second implementation that does not change when the first is corrected. This campaign has the
# shape on record: a rule retyped rebuilt the exact bug the original had been fixed for.
#
# THE UNIT IS TASK-HOURS AND IT IS NOT AllocCPUS-WEIGHTED.
# `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`, positive clause: task-hours
# are "the sum of ElapsedRaw over the arm tasks". So a reservation is `ntasks x wall`. Pricing it as
# `cpus-per-task x wall` is CORE-HOURS wearing the task-hour label, which this campaign committed
# once AFTER that ruling landed -- an 8x overstatement on the M1 request. `r5_admission_check`
# refuses a declared figure that differs from the enforced cap, in either direction: understating
# admits an item against headroom it may exceed, and overstating misreports the ledger.
#
# NO APOSTROPHES IN ANY MESSAGE HERE. An apostrophe inside ${VAR:?...} opens a quote that spans
# newlines and swallows the next assignments, voiding the guards between. Twice in this campaign.

# r5_require_declared_cap <declared> <enforced> <ntasks> <wall_hours>
# Exit 8 when the declaration is not the enforced cap.
r5_require_declared_cap() {
  local declared="$1" enforced="$2" ntasks="$3" wall="$4"
  if [ "$declared" != "$enforced" ]; then
    echo "REFUSED -- declared $declared CPU task-h, enforced cap is $enforced" >&2
    echo "          (ntasks $ntasks x wall $wall h). A reservation is the cap, not a measured" >&2
    echo "          actual from a past run, and not the cap times cpus-per-task." >&2
    return 8
  fi
  return 0
}

# r5_admission_check <code_root> <receipt_path> <cpu_task_hours> <gpu_task_hours>
# Exit 9 when the receipt is missing, or when the meter refuses admission. The meter is CALLED --
# it fails closed on a stale, missing or malformed receipt, and `check` refuses when
# spend + proposed >= the ceiling. R5 authorizes a stop, not spending.
r5_admission_check() {
  local code_root="$1" receipt="$2" cpu_h="$3" gpu_h="${4:-0}"
  if [ ! -f "$receipt" ]; then
    echo "REFUSED -- no R5 receipt at $receipt. Measure one before submitting, not after." >&2
    return 9
  fi
  if ! python3 "$code_root/docs/orchestration/r5_meter.py" check \
         --receipt "$receipt" --cpu-task-hours "$cpu_h" --gpu-task-hours "$gpu_h"; then
    echo "REFUSED -- R5 admission failed for $cpu_h CPU / $gpu_h GPU task-h against $receipt." >&2
    echo "          R5 authorizes a stop, not spending, so this returns for a decision rather" >&2
    echo "          than being retried." >&2
    return 9
  fi
  return 0
}

# r5_record_preamble <question> <decision_value> <inputs> <ntasks> <wall_hours> <task_hours> <receipt>
# The five things the authorization requires be recorded, printed into the job log where the
# receipt-gathering step can find them. A record kept only in a plan is not attached to the run.
r5_record_preamble() {
  echo "=== the five things the authorization requires be recorded ==="
  echo "  scientific question : $1"
  echo "  expected decision   : $2"
  echo "  inputs              : $3"
  echo "  enforced limits     : ntasks=$4 wall=$5 h reservation=$6 CPU task-h"
  echo "  R5 admission        : verified against $7"
  echo "  ceiling note        : the overall ceiling is not a spending target"
  date -u +"%Y-%m-%dT%H:%M:%SZ"
  showquota 2>/dev/null || echo "showquota unavailable -- record this and do not substitute df"
}

# r5_retry_notice -- the 2026-09-18 grant, printed on failure so the next actor reads the rule that
# applies rather than the one that was superseded.
r5_retry_notice() {
  echo "  NO AUTOMATIC REQUEUE. One corrective resubmission is available for this stage AFTER:" >&2
  echo "  the defect is diagnosed, the repair is verified, and a FRESH R5 receipt admits it." >&2
  echo "  A scientific failure is NOT an execution defect, does not consume that resubmission," >&2
  echo "  and is evidence to assess rather than permission to repeat until it passes." >&2
  echo "  An ambiguous submission must be reconciled before another is made." >&2
}
