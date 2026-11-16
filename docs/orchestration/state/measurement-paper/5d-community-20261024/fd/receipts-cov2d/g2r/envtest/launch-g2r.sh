#!/bin/bash
# Launch one COV2D-G2R connect, after the director's go on that connect's sha256 (addendum J1; COV2D-G2R-BINDING-1).
# Adapted from launch-ll5d.sh (4cd22193): the fence (read-only, recorded), the connect staged at
# /dev/shm/josephrb-g2r-<name>.sh, its node sha256 compared with the local one AND with the sha256 given (the go's),
# launched detached (the launch ssh's rc must be 0), its /dev/shm log tailed until its last line is DONE (polls every
# 15 s, up to 90 min), then fetched. The staged copy and the log are removed (logged) ONLY if the fetched log ends with
# DONE; otherwise both stay, and the launcher prints TIMEOUT with the log's last lines and exits 5 (the audit's B1). The
# job itself is watched apart. Every ssh's rc is read directly (no pipe).
# Usage: launch-g2r.sh envtest|envtest-r2|envtest-r3|diag-tune|prepare <sha256>
# Exit: 0 launched, fetched and removed; 2 refused before staging; 3 digest mismatch; 4 the launch ssh failed (STOP);
# 5 TIMEOUT or the fetched log does not end with DONE (both files left in place).
# Test mode (test_launch_g2r.sh only): G2R_LAUNCH_TEST=1 lets G2R_SHM, G2R_TEST_SRC, G2R_WAIT_N and G2R_POLL_S stand
# in for /dev/shm, the connect, the poll count and the poll interval. The launcher announces it, and nothing else
# changes; the hooks are ignored without it.
set -u
N=$1; WANT=${2:-}; H=$(cd "$(dirname "$0")" && pwd); OUT=$H/run-$N
SHM=/dev/shm; WAIT_N=360; POLL_S=15                           # 360 x 15 s = 90 min
[ -n "$WANT" ] || { echo "REFUSED: the go's sha256 is required"; exit 2; }
[ -e "$OUT" ] && { echo "REFUSED $OUT exists"; exit 2; }
case "$N" in
  envtest) SRC=$H/connect-g2r-envtest.sh; ARG="" ;;
  envtest-r2) SRC=$H/connect-g2r-envtest-r2.sh; ARG="" ;;   # r1 STOPped at the suite gate (TMPDIR under $O)
  envtest-r3) SRC=$H/connect-g2r-envtest-r3.sh; ARG="" ;;   # r2 STOPped: tmpfs atime under the glue test's O_NOATIME=0 patch
  diag-tune) SRC=$H/connect-g2r-diag-tune.sh; ARG="" ;;     # envtest-r2 STOP diagnostic (PhaseTune STOP)
  prepare) SRC=$H/connect-g2r-prepare.sh; ARG="" ;;
  *) echo "usage: launch-g2r.sh envtest|envtest-r2|envtest-r3|diag-tune|prepare <sha256>"; exit 2 ;;
esac
if [ "${G2R_LAUNCH_TEST:-}" = 1 ]; then
  SHM=${G2R_SHM:-$SHM}; SRC=${G2R_TEST_SRC:-$SRC}; WAIT_N=${G2R_WAIT_N:-$WAIT_N}; POLL_S=${G2R_POLL_S:-$POLL_S}
  echo "TEST MODE: SHM=$SHM SRC=$SRC WAIT_N=$WAIT_N POLL_S=$POLL_S"
fi
LOGP=$SHM/josephrb-g2r-$N.log
have=$(shasum -a 256 "$SRC" | cut -c1-64)
[ "$have" = "$WANT" ] || { echo "REFUSED: $SRC is $have, not the go's $WANT"; exit 2; }
mkdir "$OUT"
r() { ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s"; }
cat > "$OUT/fence.sh" <<'FENCE'
echo "fence host=$(hostname) utc=$(date -u +%FT%TZ)"
echo "squeue:"; squeue -u josephrb -h -o '%i %j %T'
echo "sacct unended cov2d:"; sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/'
echo "fence end"
FENCE
r < "$OUT/fence.sh" > "$OUT/fence.txt" 2>&1; frc=$?
cat "$OUT/fence.txt"
[ "$frc" = 0 ] && grep -q '^fence end$' "$OUT/fence.txt" || { echo "REFUSED fence fetch rc=$frc"; exit 2; }
[ "$(sed -n '/^sacct unended cov2d:$/,/^fence end$/p' "$OUT/fence.txt" | grep -vc -e '^sacct unended cov2d:$' -e '^fence end$')" = 0 ] \
  || { echo "REFUSED: a cov2d job is unended"; exit 2; }
echo "FENCE_CLEAR (other lanes' jobs are recorded above; the director sequences them)"
SH=$SHM/josephrb-g2r-$N.sh
ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 'umask 077; test ! -e $SH && cat > $SH'" < "$SRC"; src=$?
[ "$src" = 0 ] || { echo "REFUSED staging rc=$src ($SH exists?)"; exit 2; }
echo "sha256sum $SH" | r > "$OUT/staged_sha.txt" 2>&1; s2=$?
got=$(cut -c1-64 "$OUT/staged_sha.txt")
echo "staged rc=$s2 node=$got local=$have go=$WANT"
[ "$s2" = 0 ] && [ "$got" = "$WANT" ] || { echo "DIGEST_MISMATCH: not launched ($SH left for inspection)"; exit 3; }
echo "DIGEST_MATCH"
echo "setsid nohup bash $SH $ARG >/dev/null 2>&1 </dev/null & sleep 2; date -u +%FT%TZ" | r > "$OUT/launch.txt" 2>&1; lrc=$?
echo "launched rc=$lrc at $(cat "$OUT/launch.txt")"
[ "$lrc" = 0 ] || { echo "STOP: the launch ssh returned rc=$lrc; $SH and any $LOGP left in place"; exit 4; }
done_seen=0
for i in $(seq 1 "$WAIT_N"); do
  echo "tail -1 $LOGP" | r > "$OUT/tail.txt" 2>/dev/null
  case "$(cat "$OUT/tail.txt")" in DONE) done_seen=1; break ;; esac
  sleep "$POLL_S"
done
echo "last line: $(cat "$OUT/tail.txt") (polls=$i of $WAIT_N, done_seen=$done_seen)"
echo "cat $LOGP" | r > "$OUT/connect.log" 2>&1; echo "fetched connect log rc=$?"
cat "$OUT/connect.log"
if [ "$done_seen" != 1 ] || [ "$(tail -1 "$OUT/connect.log")" != DONE ]; then
  echo "TIMEOUT: the connect's log does not end with DONE after $WAIT_N polls of ${POLL_S} s; $SH and $LOGP left in place"
  echo "its last lines:"; tail -5 "$OUT/connect.log"
  exit 5
fi
echo "sha256sum $SH $LOGP; rm -f $SH $LOGP; echo \"rm -f $SH $LOGP rc=\$?\"; ls $SH $LOGP 2>&1" | r > "$OUT/removal.log" 2>&1; echo "removal rc=$?"
cat "$OUT/removal.log"
