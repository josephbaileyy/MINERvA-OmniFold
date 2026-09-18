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

# r5_source_environment <code_root>
# Exit 13 when the campaign environment script is absent. Under `set -e` a bare
# `source missing_file` dies with rc 1, which is indistinguishable from a payload failure -- so the
# absence of the environment would report as "the job failed", with no indication that nothing ran.
# A precondition that cannot announce its own absence is the shape that made job 58506753 print an
# accounting failure for an interpreter fault.
r5_source_environment() {
  local code_root="$1" script="$1/setup_salloc_env.sh"
  if [ ! -f "$script" ]; then
    echo "REFUSED -- no campaign environment script at $script." >&2
    echo "          MNV_CODE_ROOT must be a full checkout, not a directory containing one file." >&2
    return 13
  fi
  # shellcheck source=/dev/null
  . "$script"
  return 0
}

# r5_require_interpreter <code_root>
# Exit 12 when `python3` cannot even RUN the meter. This must be called -- and the campaign
# environment sourced -- BEFORE `r5_admission_check`.
#
# ⚠ WHY THIS EXISTS, MEASURED THE HARD WAY. Job 58506753 failed in 4 s printing
# "R5 admission failed for 0.25 CPU task-h". It had not failed admission at all: the login/compute
# default `python3` is 3.6.15, `r5_meter.py` opens with `from __future__ import annotations`, and
# the SyntaxError came back as a nonzero exit that the old one-line `if !` test read as a refusal.
# An ENVIRONMENT failure was reported as an ACCOUNTING failure, in the words of an accounting
# failure, and the two route to completely different actions.
r5_require_interpreter() {
  local code_root="$1"
  if ! python3 "$code_root/docs/orchestration/r5_meter.py" --self-test >/dev/null 2>&1; then
    echo "REFUSED -- python3 cannot run the R5 meter, so admission cannot be EVALUATED." >&2
    echo "          This is an environment fault, NOT an accounting stop. Source the campaign" >&2
    echo "          environment first: the default python3 here is too old to parse the meter." >&2
    python3 -V >&2 || true
    return 12
  fi
  return 0
}

# r5_admission_check <code_root> <receipt_path> <cpu_task_hours> <gpu_task_hours>
# The meter is CALLED, never reimplemented, and its EXIT CODE is read rather than its truthiness.
#
#   0        admitted
#   3        the R5 stop has fired
#   4        the receipt is missing, malformed, future-dated or STALE -- fails closed
#   5        the proposal would reach or exceed a ceiling
#   anything else   THE METER DID NOT EVALUATE ANYTHING
#
# The last row is the one the previous version could not express. "I could not look" and "I looked
# and refused" are different findings with different next actions, and a gate that prints the
# second when the first happened sends the reader to the wrong problem. Both still STOP -- the
# fail-closed direction is unchanged -- but they stop with distinct codes and distinct words.
r5_admission_check() {
  local code_root="$1" receipt="$2" cpu_h="$3" gpu_h="${4:-0}"
  if [ ! -f "$receipt" ]; then
    echo "REFUSED -- no R5 receipt at $receipt. Measure one before submitting, not after." >&2
    return 9
  fi
  local rc=0
  python3 "$code_root/docs/orchestration/r5_meter.py" check \
    --receipt "$receipt" --cpu-task-hours "$cpu_h" --gpu-task-hours "$gpu_h" || rc=$?
  case "$rc" in
    0) return 0 ;;
    3|4|5)
      echo "REFUSED -- R5 admission REFUSED for $cpu_h CPU / $gpu_h GPU task-h (meter rc $rc:" >&2
      echo "          3 stop fired, 4 receipt stale or unreadable, 5 would reach a ceiling)." >&2
      echo "          The meter evaluated the boundary and said no. R5 authorizes a stop, not" >&2
      echo "          spending, so this returns for a decision rather than being retried." >&2
      return 9 ;;
    *)
      echo "REFUSED -- the R5 meter exited $rc, which is none of its verdict codes (0/3/4/5), so" >&2
      echo "          the boundary was NOT EVALUATED. This is a blind gate, not a refusal, and it" >&2
      echo "          is an environment or invocation fault to fix rather than a decision to seek." >&2
      return 12 ;;
  esac
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
