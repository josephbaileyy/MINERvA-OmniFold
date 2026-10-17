#!/bin/bash
# Packed-production watcher (binding AUTHORIZATION-20261016-...-packing-binding §3.2, §3.6). Exits on the first of:
#  10 ABNORMAL  any 2dc_P_ job not PENDING/RUNNING/COMPLETING/CONFIGURING/COMPLETED (TIMEOUT, FAILED, OOM, DEADLINE,
#               a CANCELLED that started); never-started CANCELLED (migration/smoke) is ignored
#  17 NOPACK    a pack that ran (ElapsedRaw>0) and is terminal, whose status file lacks the #pack line (global STOP)
#  14 STRADDLE  a RUNNING job with Start+Timelimit > 2026-10-21T13:00:00Z (maintenance start)
#  15 SLOW      a CV pack (K*_S1_/S2_/S4B_/S4CV_) with ElapsedRaw > 2000 s not listed in $SEEN_SLOW
#  16 G2ENDED   G2 packs (K*_S4U_/K*_S4CV_) terminal count >= G2_N
#  13 PROGRESS  terminal pack count >= BASE_DONE + STEP
#  2  TRANSPORT ssh/sacct failed (or printed an error) 5 times in a row
# sacct is read with TZ=UTC; Start is parsed as UTC.
BASE_DONE=${BASE_DONE:-0}; STEP=${STEP:-10}; SLEEP=${SLEEP:-300}; G2_N=${G2_N:-999}
SEEN_SLOW=${SEEN_SLOW:-/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/42670017-c41b-4c65-9b50-994312a5d203/scratchpad/seen_slow.txt}
touch "$SEEN_SLOW"
LIM=$(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%S 2026-10-21T13:00:00 +%s)
fail=0
while :; do
  out=$(ssh -o ConnectTimeout=30 -o BatchMode=yes saul.nersc.gov '
    NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
    r=$(TZ=UTC sacct -X -n -P -S 2026-10-15T00:00:00 -E now -u josephrb -o JobID,JobName,State,Start,TimelimitRaw,ElapsedRaw 2>&1) || { echo "SACCTFAIL"; exit 3; }
    case "$r" in *"sacct: error"*) echo "SACCTFAIL"; exit 3;; esac
    printf "%s\n" "$r" | grep "|2dc_P_"
    printf "%s\n" "$r" | awk -F"|" "\$2 ~ /^2dc_P_K/ && \$6+0>0 && \$3 !~ /^(RUNNING|PENDING|COMPLETING|CONFIGURING)/ {print \$1}" | while read j; do
      head -1 "$NS/packs/$j.status" 2>/dev/null | grep -q "^#pack" || echo "NOPACK|$j"; done' 2>/dev/null)
  rc=$?
  if [ $rc -ne 0 ] || [ -z "$out" ] || printf '%s' "$out" | grep -q SACCTFAIL; then
    fail=$((fail+1)); [ $fail -ge 5 ] && { echo "TRANSPORT: ssh/sacct failed 5x at $(date -u +%FT%TZ)"; exit 2; }
    sleep 120; continue
  fi
  fail=0
  r=$(printf '%s\n' "$out" | grep -v '^NOPACK|')
  np=$(printf '%s\n' "$out" | grep '^NOPACK|')
  P=$(printf '%s\n' "$r" | grep '|2dc_P_K')
  tally=$(printf '%s\n' "$P" | awk -F'|' '{split($3,a," "); print a[1]}' | sort | uniq -c | tr '\n' ' ')
  if [ -n "$np" ]; then echo "NOPACK at $(date -u +%FT%TZ) | packs: $tally"; echo "$np"; exit 17; fi
  ab=$(printf '%s\n' "$r" | awk -F'|' '{split($3,a," "); s=a[1]} s=="CANCELLED" && ($4=="None"||$4=="Unknown") && $6==0 {next} s!="PENDING"&&s!="RUNNING"&&s!="COMPLETING"&&s!="CONFIGURING"&&s!="COMPLETED"')
  if [ -n "$ab" ]; then echo "ABNORMAL at $(date -u +%FT%TZ) | packs: $tally"; echo "$ab"; exit 10; fi
  st=$(printf '%s\n' "$r" | awk -F'|' '$3 ~ /^RUNNING/ {print $1, $2, $4, $5}' | while read j n s tl; do
        e=$(( $(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%S "$s" +%s 2>/dev/null) + tl*60 ))
        [ "$e" -gt "$LIM" ] && echo "$j $n start=${s}Z tl=${tl}min"; done)
  if [ -n "$st" ]; then echo "STRADDLE at $(date -u +%FT%TZ) | packs: $tally"; echo "$st"; exit 14; fi
  slow=$(printf '%s\n' "$P" | awk -F'|' '$2 ~ /^2dc_P_K[0-9]_(S1_|S2_|S4B_|S4CV_)/ && $6+0 > 2000 {print $1"|"$2"|"$3"|"$6}' | while IFS='|' read j n s e; do
        grep -qx "$j" "$SEEN_SLOW" || echo "$j|$n|$s|$e"; done)
  if [ -n "$slow" ]; then echo "SLOW at $(date -u +%FT%TZ) | packs: $tally"; echo "$slow"; exit 15; fi
  term='COMPLETED|TIMEOUT|FAILED|OUT_OF_MEMORY|DEADLINE|CANCELLED|NODE_FAIL'
  g2=$(printf '%s\n' "$P" | awk -F'|' -v t="$term" '$2 ~ /^2dc_P_K[0-9]_S4(U|CV)_/ {split($3,a," "); if (a[1] ~ "^("t")$" && $6+0>0) n++} END{print n+0}')
  if [ "$g2" -ge "$G2_N" ]; then echo "G2ENDED n=$g2 at $(date -u +%FT%TZ) | packs: $tally"; exit 16; fi
  nd=$(printf '%s\n' "$P" | awk -F'|' -v t="$term" '{split($3,a," "); if (a[1] ~ "^("t")$" && $6+0>0) n++} END{print n+0}')
  if [ "$nd" -ge $((BASE_DONE+STEP)) ]; then echo "PROGRESS packs-ended=$nd at $(date -u +%FT%TZ) | packs: $tally"; exit 13; fi
  sleep "$SLEEP"
done
