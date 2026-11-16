#!/bin/bash
# T2A status, read-only, after the connect's ssh session ended with rc 255 (2026-11-10T17:40:43Z). Run on login21, the
# connect's node. It writes, deletes, kills and launches nothing (except removing its own /dev/shm copy, $1). It reads:
#   my processes on this node (ps -u, filtered to the capture and connect);
#   the two /dev/shm work paths, by stat of each explicit path (not listed);
#   under $OUT only: the listing of $OUT and its subdirectories, connect.done, connect.log, out.sha256 per tune.
SELF=$1
trap 'rm -f -- "$SELF"' EXIT
OUT=/pscratch/sd/j/josephrb/t2a-20261110
echo "status host=$(hostname) utc=$(date -u +%FT%TZ)"
echo "== my processes (capture/connect/readout)"
ps -u "$(id -u)" -o pid,ppid,etime,stat,args | grep -E 't2a-connect|capture_e\.py|cov2d_readout|time -v' | grep -v grep || echo "(none)"
echo "== /dev/shm work paths (stat)"
for w in /dev/shm/josephrb-cov2d-s-AR23 /dev/shm/josephrb-cov2d-s-G18; do
  stat -c '%n %F %y' "$w" 2>&1
  for s in "$w/deploy" "$w/out" "$w/capture_AR23.log" "$w/capture_G18.log"; do [ -e "$s" ] && stat -c '  %n %F %s %y' "$s"; done
done
echo "== \$OUT"
stat -c '%n %F %y' "$OUT" 2>&1
[ -d "$OUT" ] || exit 0
ls -la "$OUT" "$OUT/logs" "$OUT/AR23" "$OUT/G18" 2>&1
echo "== connect.done"; cat "$OUT/logs/connect.done" 2>&1
for t in AR23 G18; do echo "== $t/out.sha256"; cat "$OUT/$t/out.sha256" 2>&1; done
echo "== connect.log (ROOT rootmap warnings filtered)"
grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$OUT/logs/connect.log" 2>&1 | tail -150
