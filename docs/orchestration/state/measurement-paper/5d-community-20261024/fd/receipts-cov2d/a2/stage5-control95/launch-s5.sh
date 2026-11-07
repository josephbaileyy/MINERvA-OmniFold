#!/bin/bash
# Launch one stage-5 bound-CLI connect (the director's ruling 2, 2026-11-07). Usage: launch-s5.sh 95|x1
#   1. the fence, read-only: no cov2d job unended (sacct) and none in squeue, recorded;
#   2. stage the connect at /dev/shm/josephrb-cov2d-<name>.sh; compare its node sha256 to the local one (separate step);
#   3. launch detached; wait for its end line;
#   4. fetch the log and outputs, compare digests, remove the staged script (and connect-95's /dev/shm dir), logged.
# Every ssh's rc is read directly (no pipe).
set -u
N=$1; H=$(cd "$(dirname "$0")" && pwd); OUT=$H/run-$N; [ -e "$OUT" ] && { echo "REFUSED $OUT exists"; exit 2; }
mkdir "$OUT"
case "$N" in
  95) LOGP=/dev/shm/josephrb-cov2d-95/connect-95.log; WD=/dev/shm/josephrb-cov2d-95
      FILES="connect-95.log control95.json control95.log blobs.before blobs.after"; END=DONE ;;
  x1) LOGP=/pscratch/sd/j/josephrb/cov2d-crossterms-20261107/connect-x1.log; WD=/pscratch/sd/j/josephrb/cov2d-crossterms-20261107
      FILES="connect-x1.log crossterms.json crossterms.out crossterms.time stat_before.txt stat_after.txt bound.sha256"; END=end= ;;
  *) echo "usage: launch-s5.sh 95|x1"; exit 2 ;;
esac
SH=/dev/shm/josephrb-cov2d-$N.sh
r() { ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s"; }

cat > "$OUT/fence.sh" <<'EOF'
echo "fence host=$(hostname) utc=$(date -u +%FT%TZ)"
echo "squeue:"; squeue -u josephrb -h -o '%i %j %T'
echo "sacct unended cov2d:"; sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/'
echo "fence end"
EOF
r < "$OUT/fence.sh" > "$OUT/fence.txt" 2>&1; frc=$?
cat "$OUT/fence.txt"
[ "$frc" = 0 ] && grep -q '^fence end$' "$OUT/fence.txt" || { echo "REFUSED fence fetch rc=$frc"; exit 2; }
[ "$(sed -n '/^squeue:$/,/^sacct unended cov2d:$/p' "$OUT/fence.txt" | grep -vc -e '^squeue:$' -e '^sacct unended cov2d:$')" = 0 ] \
  && [ "$(sed -n '/^sacct unended cov2d:$/,/^fence end$/p' "$OUT/fence.txt" | grep -vc -e '^sacct unended cov2d:$' -e '^fence end$')" = 0 ] \
  || { echo "REFUSED the fence is not clear"; exit 2; }
echo "FENCE_CLEAR"

ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 'test ! -e $SH && cat > $SH'" < "$H/connect-$N.sh"; src=$?
[ "$src" = 0 ] || { echo "REFUSED staging rc=$src ($SH exists?)"; exit 2; }
echo "sha256sum $SH" | r > "$OUT/staged_sha.txt" 2>&1; s2=$?
want=$(shasum -a 256 "$H/connect-$N.sh" | cut -c1-64); got=$(cut -c1-64 "$OUT/staged_sha.txt")
echo "staged rc=$s2 node=$got local=$want"
[ "$s2" = 0 ] && [ "$got" = "$want" ] || { echo "DIGEST_MISMATCH: not launched ($SH left for inspection)"; exit 3; }
echo "DIGEST_MATCH"

echo "setsid nohup bash $SH >/dev/null 2>&1 </dev/null & sleep 2; date -u +%FT%TZ" | r > "$OUT/launch.txt" 2>&1; lrc=$?
echo "launched rc=$lrc at $(cat "$OUT/launch.txt")"
for i in $(seq 1 720); do
  echo "tail -1 $LOGP" | r > "$OUT/tail.txt" 2>/dev/null
  t=$(cat "$OUT/tail.txt")
  case "$t" in "$END"*) break ;; esac
  sleep 20
done
echo "last line: $(cat "$OUT/tail.txt")"
for f in $FILES; do echo "cat $WD/$f" | r > "$OUT/$f" 2>&1; echo "fetched $f rc=$?"; done
[ "$N" = x1 ] && { echo "base64 $WD/crossterms.npz" | r > "$OUT/crossterms.npz.b64"; echo "fetched npz rc=$?"; base64 -D -i "$OUT/crossterms.npz.b64" -o "$OUT/crossterms.npz" && rm "$OUT/crossterms.npz.b64"; }
cat > "$OUT/remove.sh" <<EOF
echo "host=\$(hostname) utc=\$(date -u +%FT%TZ)"
cd $WD && sha256sum $FILES $( [ "$N" = x1 ] && echo crossterms.npz ) 2>&1
sha256sum $SH; rm -f $SH; echo "rm -f $SH rc=\$?"
EOF
[ "$N" = 95 ] && cat >> "$OUT/remove.sh" <<EOF
for f in $WD/*; do [ -d "\$f" ] && { echo "dir left: \$f"; continue; }; rm -f "\$f"; echo "rm -f \$f rc=\$?"; done
for f in $WD/tmp/*; do [ -e "\$f" ] || continue; rm -f "\$f"; echo "rm -f \$f rc=\$?"; done
rmdir $WD/tmp; echo "rmdir $WD/tmp rc=\$?"; rmdir $WD; echo "rmdir $WD rc=\$?"
EOF
echo 'ls -la /dev/shm | grep josephrb; echo "ls end"' >> "$OUT/remove.sh"
r < "$OUT/remove.sh" > "$OUT/removal.log.txt" 2>&1; echo "removal rc=$?"
cat "$OUT/removal.log.txt"
for f in $FILES $( [ "$N" = x1 ] && echo crossterms.npz ); do
  l=$(shasum -a 256 "$OUT/$f" | cut -c1-64); n=$(awk -v f="$f" '$2 == f {print $1}' "$OUT/removal.log.txt")
  [ "$l" = "$n" ] && echo "MATCH $f" || echo "MISMATCH $f local=$l node=$n"
done
