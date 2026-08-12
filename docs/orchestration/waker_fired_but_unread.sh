#!/bin/bash
# Fired-but-unread: which waker events have fired without a filed, committed verdict.
#
# WHY THIS FILE EXISTS, and it is not a convenience wrapper.
# BEN-084(B) diagnosed that "a described check must be reconstructed by every reader, and
# reconstruction is where the assumption re-enters", and prescribed the remedy of putting the
# literal command in the header. That remedy was implemented in
# PROMPTS-20260811-four-session-closeout.md STEP 1, annotated with its own failure mode -- "do not
# re-derive it (re-deriving produced events/ instead of logs/)" -- and the orchestrator re-derived it
# anyway, on 2026-08-11, in the session that had been handed the warning. BEN-097 records that
# recurrence and its conclusion: a remedy of the form "write it down and read it" must be assumed to
# fail and given a fallback that does not depend on being read. This is that fallback. The header
# now cites a PATH, and there is nothing left to reconstruct.
#
# THREE WAYS THE RECONSTRUCTED FORM WENT WRONG IN ONE NIGHT, all of which this file forecloses:
#   1. state_dir/events/ instead of state_dir/logs/. They are real siblings (wakerctl.py:149-150),
#      PROCESSED.txt keys on evt-*.log basenames, and events/ holds ~245 differently-named files
#      against ~93 processed entries -- so the check reported a ~56-item backlog that did not exist.
#      A monitor that always shows a backlog stops being read.
#   2. The bare ssh alias `perlmutter` instead of the FQDN. It does not resolve; perlmutter.nersc.gov
#      does. A failed connection is what prompted the re-derivation that caused (1).
#   3. logs/*.log instead of logs/evt-*.log. The wider glob admits cron-tick.log, which is not an
#      event log, so the "corrected" run still produced exactly one false positive. The prescribed
#      glob returns clean and needs no interpretation.
#
# CONTRACT: empty output and exit 0 means every fired watch has a filed verdict. Any line printed is
# an event id that fired and whose verdict is not yet committed. PROCESSED.txt is append-only and is
# appended to only AFTER the verdict is filed AND committed -- see its own header -- so a name here
# is a real gap, not a race.
#
# Liveness is a DIFFERENT check and this script does not do it: judge the waker by the
# last-tick.json / cron-tick.log file pair with TZ=UTC pinned, never by log growth (BEN-028).

set -euo pipefail

HOST="${MNV_CLUSTER_HOST:-perlmutter.nersc.gov}"
WAKER_DIR="${MNV_WAKER_DIR:-/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/waker}"

# comm -23 = lines in the fired set that are absent from the processed set.
ssh -o BatchMode=yes -o ConnectTimeout=25 "$HOST" \
  "cd '$WAKER_DIR' && comm -23 <(ls -1 logs/evt-*.log | xargs -n1 basename | sort) <(grep -v '^#' PROCESSED.txt | sort -u)"
