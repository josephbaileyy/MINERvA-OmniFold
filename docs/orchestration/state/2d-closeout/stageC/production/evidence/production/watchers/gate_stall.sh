#!/bin/bash
# Director watch item (2026-10-17): flag a gate reading that does not fall over 2 h while packs are completing.
# Reads the waiter's GATE lines (one per ~10-min poll). Exit 18 STALL when, for the newest reading and the newest
# reading at least 7200 s older, total_now >= total_then AND completed_now > completed_then. Exit 0 when the waiter
# output says ALL SUBMITTED or STOPPED (the waiter's own exit is handled separately).
F=${1:?waiter output file}
while :; do
  grep -q "ALL SUBMITTED\|STOPPED\|TRANSPORT" "$F" && exit 0
  # one reading per poll: the GATE line right after a "<B> gate rc=" line, for the batch named in that line (S4b)
  r=$(awk -v B="${B:-S4b}" '$2==B && $3=="gate" {ts=$1; next} /^GATE/ && ts!="" {print ts, $3, $(NF-3); ts=""} {ts=ts}' "$F")
  # columns: utc completed total
  out=$(printf '%s\n' "$r" | while read t c tot; do [ -n "$t" ] && echo "$(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%SZ "$t" +%s) $c $tot $t"; done | awk '
    {T[NR]=$1; C[NR]=$2; S[NR]=$3; L[NR]=$4; n=NR}
    END { if (n<2) exit; for (i=n-1;i>=1;i--) if (T[n]-T[i]>=7200) { if (S[n]>=S[i] && C[n]>C[i]) print "STALL then", L[i], S[i], "completed", C[i], "now", L[n], S[n], "completed", C[n]; exit } }')
  [ -n "$out" ] && { echo "$out"; exit 18; }
  sleep 600
done
