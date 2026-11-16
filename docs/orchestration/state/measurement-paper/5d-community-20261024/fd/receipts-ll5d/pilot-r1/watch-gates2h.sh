#!/bin/bash
# watch-gates2g.sh, changed for a job that may still be queued (the LL5D pilot, 2026-11-12): polls every 5 minutes (up to
# 200 h) for the listed jobs (read only). Exits on the first:
#   JOB-EVENT             any listed job's state is not PENDING, CONFIGURING or RUNNING (an end of any kind, or a requeue)
#   SSH-RESTORED          the first successful poll after a run of maintenance refusals
#   SSH-STILL-FAILING     2 h of failures that are NOT the maintenance banner
#   CERT-LAPSED           the local sshproxy cert's "Valid ... to" time has passed (renewal is Joseph's, with MFA)
# Arguments: one or more job ids. Every rc is read unpiped.
LOG=run-gate2-watch/watch.log
CERT=$HOME/.ssh/nersc-cert.pub; E=$(mktemp -d "${TMPDIR:-/tmp}/watch2g.XXXXXX")
SSH=(ssh -o ControlPath=none -o ConnectTimeout=30 -o BatchMode=yes -o LogLevel=INFO saul.nersc.gov)
IDS=$(IFS=,; echo "$*"); N=$#
MAINT_SEEN=
for i in $(seq 1 2400); do
  cend=$(ssh-keygen -L -f "$CERT" | sed -n 's/.*Valid: from [^ ]* to \([0-9T:-]*\).*/\1/p')
  if [ -n "$cend" ] && [ "$(date +%Y-%m-%dT%H:%M:%S)" \> "$cend" ]; then echo "CERT-LAPSED $(date -u +%FT%TZ) valid-to(local)=$cend"; exit 0; fi
  s=$("${SSH[@]}" "sacct -X -n -P -j $IDS -o JobID,JobName,State,Elapsed,Start,End,ExitCode" 2>"$E/s.err"); rc=$?
  now=$(date -u +%FT%TZ)
  maint=; grep -qi 'down for maintenance' "$E/s.err" && maint=1
  if [ "$rc" != 0 ]; then
    if [ -n "$maint" ]; then MAINT_SEEN=${MAINT_SEEN:-$now}; FAIL_SINCE=; FAIL_EPOCH=
    else FAIL_SINCE=${FAIL_SINCE:-$now}; FAIL_EPOCH=${FAIL_EPOCH:-$(date -u +%s)}; fi
  else FAIL_SINCE=; FAIL_EPOCH=; fi
  tag=; [ -n "$maint" ] && tag=" MAINT"
  echo "$now rc=$rc$tag $(echo "$s" | tr '\n' ';')" >> $LOG
  if [ "$rc" = 0 ]; then
    rows=$(echo "$s" | awk -F'|' '$3 != ""' | wc -l | tr -d ' ')
    other=$(echo "$s" | awk -F'|' '$3 != "" && $3 != "RUNNING" && $3 != "PENDING" && $3 != "CONFIGURING"' | wc -l | tr -d ' ')
    if [ "$rows" != "$N" ]; then echo "JOB-EVENT $now sacct listed $rows of $N jobs: $s"; exit 0; fi
    [ "$other" -ge 1 ] && { echo "JOB-EVENT $now $s"; exit 0; }
    [ -n "$MAINT_SEEN" ] && { echo "SSH-RESTORED $now maint-first-seen=$MAINT_SEEN $s"; exit 0; }
  fi
  if [ -n "$FAIL_EPOCH" ] && [ $(( $(date -u +%s) - FAIL_EPOCH )) -ge 7200 ]; then echo "SSH-STILL-FAILING $now since=$FAIL_SINCE rc=$rc $(tail -2 "$E/s.err" | tr '\n' ' ')"; exit 0; fi
  sleep 300
done
echo "WATCH-EXPIRED last=$s"
