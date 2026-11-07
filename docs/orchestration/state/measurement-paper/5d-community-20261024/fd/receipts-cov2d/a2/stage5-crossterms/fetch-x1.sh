#!/bin/bash
# Fetch-only tail of launch-s5.sh x1, after the Mac-side launcher died in the 2026-11-07 crash: the connect itself kept
# running on login02 (setsid). Wait for its end line, fetch the log and outputs, remove the staged script (logged),
# compare digests. No fence, staging or launch here. Every ssh rc is read directly.
set -u
H=$(cd "$(dirname "$0")" && pwd); OUT=$H/run-x1; [ -e "$OUT" ] && { echo "REFUSED $OUT exists"; exit 2; }; mkdir "$OUT"
WD=/pscratch/sd/j/josephrb/cov2d-crossterms-20261107; LOGP=$WD/connect-x1.log; SH=/dev/shm/josephrb-cov2d-x1.sh
FILES="connect-x1.log crossterms.json crossterms.out crossterms.time stat_before.txt stat_after.txt bound.sha256"
r() { ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=QUIET login02 bash -s"; }
for i in $(seq 1 720); do
  echo "tail -1 $LOGP" | r > "$OUT/tail.txt" 2>/dev/null
  case "$(cat "$OUT/tail.txt")" in end=*) break ;; esac
  sleep 20
done
echo "last line: $(cat "$OUT/tail.txt")"
for f in $FILES; do echo "cat $WD/$f" | r > "$OUT/$f" 2>&1; echo "fetched $f rc=$?"; done
echo "base64 $WD/crossterms.npz" | r > "$OUT/crossterms.npz.b64"; echo "fetched npz rc=$?"
base64 -D -i "$OUT/crossterms.npz.b64" -o "$OUT/crossterms.npz" && rm "$OUT/crossterms.npz.b64"
cat > "$OUT/remove.sh" <<EOS
echo "host=\$(hostname) utc=\$(date -u +%FT%TZ)"
cd $WD && sha256sum $FILES crossterms.npz 2>&1
sha256sum $SH; rm -f $SH; echo "rm -f $SH rc=\$?"
ls -la /dev/shm | grep josephrb; echo "ls end"
EOS
r < "$OUT/remove.sh" > "$OUT/removal.log.txt" 2>&1; echo "removal rc=$?"
cat "$OUT/removal.log.txt"
for f in $FILES crossterms.npz; do
  l=$(shasum -a 256 "$OUT/$f" | cut -c1-64); n=$(awk -v f="$f" '$2 == f {print $1}' "$OUT/removal.log.txt")
  [ "$l" = "$n" ] && echo "MATCH $f" || echo "MISMATCH $f local=$l node=$n"
done
