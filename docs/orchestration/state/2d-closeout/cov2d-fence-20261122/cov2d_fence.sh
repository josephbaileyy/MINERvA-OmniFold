#!/bin/bash
# cov2d_fence.sh rev 3 (2026-11-23): the COV2D fence, run on a Perlmutter login node before another lane's connect.
# Reads sacct only (no squeue: standing rule). Replaces rev 2 (sha256 3fbc9cbd...), whose 60-day -S Perlmutter refused
# ("Too wide of a date range in query", login38 2026-11-23), and rev 1 (16a2a5cd...), which called squeue.
# CLEAR (exit 0) only if sacct exits 0, every line it writes (stdout and stderr together) is a well-formed
# JobID|JobName|State row with a numeric JobID, and every row named cov2d* or t2a* (ours, last 14 days) is in a
# terminal state. Anything else is exit 3: an unended or unclassifiable matching row, a malformed or stray line
# (so an error sacct prints on stderr while exiting 0 refuses), sacct failing, or the start time failing.
# Known gap, sacct-only by rule: sacct's default listing omits a pending job with no EligibleTime (sbatch --hold,
# scontrol hold, array tasks held by a %limit) and can lag slurmdbd briefly.
# A connect that relies on this fence also takes a fresh ack from the cov2d session, which covers that gap.
# State is classified here against a closed terminal set (first word of State, so "CANCELLED by N" counts);
# any other state, including ones this file does not name, refuses. sacct -s is not used (Perlmutter rejects CF).
# Writes nothing. May be launched from a /dev/shm copy of itself whose path is $1. At exit it deletes $1 only if $1
# is under /dev/shm/, has no .. component, and is the running script itself ([ "$1" -ef "$0" ]); any other $1 is
# kept and named. (Without the .. rule, /dev/shm/../<repo>/cov2d_fence.sh run from the repo would delete the repo file.)
SELF=$1
fin() {
  if [ -n "$SELF" ]; then
    case $SELF in
      */../*|*/..) echo "self-copy not removed: $SELF" ;;
      /dev/shm/*) if [ "$SELF" -ef "$0" ]; then rm -f -- "$SELF"; else echo "self-copy not removed: $SELF"; fi ;;
      *) echo "self-copy not removed: $SELF" ;;
    esac
  fi
  exit "$1"
}
echo "fence host=$(hostname) utc=$(date -u +%FT%TZ)"
# sacct reads -S in the cluster's local time. 14 days covers the 48 h MaxWall with margin and is a range Perlmutter's
# sacct accepts (rev 1 and the T3 and flux2 fences used it); 60 days was refused.
start=$(date -d '14 days ago' +%FT%T) || { echo "FENCE REFUSED: start time failed"; fin 3; }
[[ $start =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$ ]] || { echo "FENCE REFUSED: start time malformed: '$start'"; fin 3; }
user=$(id -un) || { echo "FENCE REFUSED: id -un failed"; fin 3; }
[ -n "$user" ] || { echo "FENCE REFUSED: empty user"; fin 3; }
echo "sacct -X -n -P -u $user -S $start -E now -o JobID,JobName,State 2>&1"
s=$(sacct -X -n -P -u "$user" -S "$start" -E now -o JobID,JobName,State 2>&1) || { echo "FENCE REFUSED: sacct failed"; printf '%s\n' "$s" | sed 's/^/sacct: /'; fin 3; }
v=$(printf '%s\n' "$s" | awk -F'|' '
  BEGIN { split("BOOT_FAIL CANCELLED COMPLETED DEADLINE FAILED NODE_FAIL OUT_OF_MEMORY PREEMPTED TIMEOUT", t, " ")
          for (i in t) term[t[i]] = 1 }
  /^$/ { next }
  NF != 3 || $1 !~ /^[0-9]+([_+].*)?$/ { print "malformed: " $0; bad = 1; next }
  $2 ~ /^(cov2d|t2a)/ { n++; split($3, w, " "); if (!(w[1] in term)) { print "unended: " $0; bad = 1 } }
  END { print "matching rows: " n + 0; exit bad }')
rc=$?
printf '%s\n' "$v" | sed 's/^/sacct /'
[ "$rc" -eq 0 ] || { echo "FENCE REFUSED: an unended, unclassifiable or malformed sacct row"; fin 3; }
echo "FENCE CLEAR"
fin 0
