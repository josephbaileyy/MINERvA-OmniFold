#!/bin/bash
# Generic wakerctl notifier: mail a job's terminal state plus the tail of its own log.
#
# usage: notify_job_log.sh <job_id> <log_glob> [subject_suffix]
#
# WHY GENERIC. This is the third notifier on this campaign. The first two were job-specific
# (notify_pwclosure.sh, notify_nominal.sh) and the third nearly repeated the mistake that made
# notify_nominal.sh wrong for the throw array: a notifier hard-wired to one job's artifacts reports
# "ABSENT" for any other job, i.e. invents a failure. For a job whose product IS its printed output --
# the J28 adoption prints its before/after and both adopt variants -- the log tail is exactly the
# payload, and nothing job-specific is needed.
#
# COVERAGE, deliberately: it mails on EVERY terminal state, not just success. A notifier that only
# fires on COMPLETED is silent through a timeout or an OOM, and silence is indistinguishable from
# "still running". wakerctl dispatches by watch id rather than event type, so this runs on
# slurm-job-error too.
set -uo pipefail
JOB="${1:?usage: notify_job_log.sh <job_id> <log_glob> [subject_suffix]}"
GLOB="${2:?usage: notify_job_log.sh <job_id> <log_glob> [subject_suffix]}"
SUFFIX="${3:-}"
BODY="/pscratch/sd/j/josephrb/.job_log_notify_${JOB}.txt"

{
  echo "Job ${JOB} has left the queue."
  echo "Fired by wakerctl on $(hostname) at $(date -u +%Y-%m-%dT%H:%M:%SZ), independent of any session."
  echo
  echo "=== terminal state (per-step, so a failed step is visible) ==="
  sacct -j "${JOB}" --format=JobID%20,State,Elapsed,ExitCode,MaxRSS -P 2>/dev/null | head -12
  echo
  # shellcheck disable=SC2086
  LOGS=$(ls -1t ${GLOB} 2>/dev/null | head -2)
  if [[ -z "${LOGS}" ]]; then
    echo "=== no log matched ${GLOB} ==="
    echo "  The job produced no log at that path. If sacct shows it ran, the --output path is wrong;"
    echo "  if sacct shows PENDING/CANCELLED it never started."
  else
    for f in ${LOGS}; do
      echo "=== tail of ${f} ($(wc -l < "${f}") lines total) ==="
      tail -60 "${f}"
      echo
    done
  fi
  echo "=== reminder ==="
  echo "  Nothing here is adopted. Replacing a quarantined ledger number is a separate,"
  echo "  human-reviewed commit -- see PLAN-20260806-niter3-budget-and-J28-reroll.md step 5."
} > "${BODY}" 2>&1

/usr/bin/python3.11 /pscratch/sd/j/josephrb/send_channel_mail.py \
  "[MNV-AUTO] job ${JOB} finished${SUFFIX:+ -- ${SUFFIX}}" "${BODY}"
