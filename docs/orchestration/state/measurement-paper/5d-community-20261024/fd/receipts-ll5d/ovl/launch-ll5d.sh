#!/bin/bash
# Launch one LL5D connect, after the director's go on that connect's sha256 (LL5D BINDING 1 ruling 8, BINDING 2).
# Usage: launch-ll5d.sh ovl | calib | gate-g18 | gate-ar23 <expected connect sha256>
#   ovl:   the read-only overlap check, run on login02 through bash -s; its output is the receipt.
#   other: the fence (read-only, recorded), the connect staged at /dev/shm/josephrb-ll5d-<name>.sh, its node sha256
#          compared with the local one AND with the sha256 given (the go's), launched detached, its connect log
#          tailed to its end= line and fetched, the staged copy removed (logged). The job itself is watched apart.
# Every ssh's rc is read directly (no pipe).
set -u
N=$1; WANT=${2:-}; H=$(cd "$(dirname "$0")" && pwd); OUT=$H/run-$N
[ -n "$WANT" ] || { echo "REFUSED: the go's sha256 is required"; exit 2; }
[ -e "$OUT" ] && { echo "REFUSED $OUT exists"; exit 2; }
case "$N" in
  ovl) SRC=$H/connect-ovl.sh ;;
  calib) SRC=$H/connect-calib.sh; ARG=""; LOGP=/pscratch/sd/j/josephrb/ll5d-calib-20261108/logs/connect-calib.log ;;
  gate-g18|gate-ar23) T=${N#gate-}; SRC=$H/connect-gate.sh; ARG=$T; LOGP=/pscratch/sd/j/josephrb/ll5d-gate-$T-20261108/logs/connect-gate-$T.log ;;
  *) echo "usage: launch-ll5d.sh ovl|calib|gate-g18|gate-ar23 <sha256>"; exit 2 ;;
esac
have=$(shasum -a 256 "$SRC" | cut -c1-64)
[ "$have" = "$WANT" ] || { echo "REFUSED: $SRC is $have, not the go's $WANT"; exit 2; }
mkdir "$OUT"
r() { ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s"; }
if [ "$N" = ovl ]; then
  r < "$SRC" > "$OUT/ovl.txt" 2>&1; orc=$?
  echo "ovl rc=$orc"; cat "$OUT/ovl.txt"
  [ "$orc" = 0 ] && grep -q '^DONE ' "$OUT/ovl.txt" || { echo "REFUSED: the overlap check did not end"; exit 3; }
  exit 0
fi
cat > "$OUT/fence.sh" <<'FENCE'
echo "fence host=$(hostname) utc=$(date -u +%FT%TZ)"
echo "squeue:"; squeue -u josephrb -h -o '%i %j %T'
echo "sacct unended cov2d:"; sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/'
echo "fence end"
FENCE
r < "$OUT/fence.sh" > "$OUT/fence.txt" 2>&1; frc=$?
cat "$OUT/fence.txt"
[ "$frc" = 0 ] && grep -q '^fence end$' "$OUT/fence.txt" || { echo "REFUSED fence fetch rc=$frc"; exit 2; }
[ "$(sed -n '/^sacct unended cov2d:$/,/^fence end$/p' "$OUT/fence.txt" | grep -vc -e '^sacct unended cov2d:$' -e '^fence end$')" = 0 ] \
  || { echo "REFUSED: a cov2d job is unended"; exit 2; }
echo "FENCE_CLEAR (other lanes' jobs are recorded above; the director sequences them)"
SH=/dev/shm/josephrb-ll5d-$N.sh
ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 'umask 077; test ! -e $SH && cat > $SH'" < "$SRC"; src=$?
[ "$src" = 0 ] || { echo "REFUSED staging rc=$src ($SH exists?)"; exit 2; }
echo "sha256sum $SH" | r > "$OUT/staged_sha.txt" 2>&1; s2=$?
got=$(cut -c1-64 "$OUT/staged_sha.txt")
echo "staged rc=$s2 node=$got local=$have go=$WANT"
[ "$s2" = 0 ] && [ "$got" = "$WANT" ] || { echo "DIGEST_MISMATCH: not launched ($SH left for inspection)"; exit 3; }
echo "DIGEST_MATCH"
echo "setsid nohup bash $SH $ARG >/dev/null 2>&1 </dev/null & sleep 2; date -u +%FT%TZ" | r > "$OUT/launch.txt" 2>&1; lrc=$?
echo "launched rc=$lrc at $(cat "$OUT/launch.txt")"
for i in $(seq 1 120); do
  echo "tail -1 $LOGP" | r > "$OUT/tail.txt" 2>/dev/null
  case "$(cat "$OUT/tail.txt")" in end=*) break ;; esac
  sleep 15
done
echo "last line: $(cat "$OUT/tail.txt")"
echo "cat $LOGP" | r > "$OUT/connect.log" 2>&1; echo "fetched connect log rc=$?"
cat "$OUT/connect.log"
echo "sha256sum $SH; rm -f $SH; echo \"rm -f $SH rc=\$?\"; ls $SH 2>&1" | r > "$OUT/removal.log" 2>&1; echo "removal rc=$?"
cat "$OUT/removal.log"
