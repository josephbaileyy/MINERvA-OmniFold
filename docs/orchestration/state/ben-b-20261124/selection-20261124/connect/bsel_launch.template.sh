#!/bin/bash
# (b) part 1's read launcher: S2R's reviewed launcher (f8cd325d) with one connect. saul, then a loginNN (inner hop's
# host key checked strictly); the script goes on stdin; on NODE the /dev/shm copy's sha256 must equal the approved one,
# or NODE deletes it and exits 8 before anything runs; it runs detached (setsid nohup) and the launcher waits for it;
# the remote side exits with the script's rc. Then: fetch-bsel.tar, logs/connect-bsel.log and .done, each streamed with
# dd iflag=noatime into the session directory; the tar's sha256 must equal the log's, its RECORDS.SHA256SUMS must hold
# under --strict with one line per file, and the done file must be 0.
# Usage: bash bsel_launch.sh <new empty dir> <loginNN> <window_end_epoch> <fence prefixes, comma-sep>
F=${1:?session dir}; NODE=${2:?loginNN}; WEND=${3:?window end epoch}; FENCE=${4:?fence}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/bsel_read.sh"; SHA=@@READ_SHA@@
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || { echo "STOP: window end '$WEND'"; exit 9; }
[ "$(date +%s)" -le "$WEND" ] || { echo "STOP: the window has ended"; exit 9; }
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || { echo "STOP: fence '$FENCE'"; exit 9; }
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="f=/dev/shm/bselc.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $WEND $FENCE > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
grep -q '^script rc=' "$F/session.out" || { echo "STOP: the session did not report a script rc; no fetch"; exit 9; }
[ "$rc" -eq 0 ] && grep -qx 'script rc=0' "$F/session.out" || { echo "STOP: the read connect did not end rc 0; no fetch"; exit 9; }
grep -q '^BAIL ' "$F/session.out" && { echo "STOP: the connect bailed before writing anything; no fetch"; exit 9; }

# ---- the fetch, after the session (the connect has finished writing; nothing below writes on the cluster)
O=/pscratch/sd/j/josephrb/bsel-20261124
frc=0
for rel in fetch-bsel.tar logs/connect-bsel.log logs/connect-bsel.done; do
  ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "dd if=$O/$rel iflag=noatime status=none")" \
    > "$F/$(basename "$rel")" 2>> "$F/fetch.err"
  r=$?; echo "fetch $rel rc=$r bytes $(wc -c < "$F/$(basename "$rel")" | tr -d ' ')"
  [ "$r" -eq 0 ] || frc=1
done
[ "$frc" -eq 0 ] || { echo "STOP: a fetch failed (fetch.err)"; exit 7; }
want=$(sed -n 's/^fetch-bsel\.tar sha256 \([0-9a-f]\{64\}\) bytes .*/\1/p' "$F/connect-bsel.log")
got=$(shasum -a 256 "$F/fetch-bsel.tar" | cut -d' ' -f1)
echo "fetch-bsel.tar sha256 $got (the log's: $want)"
[ -n "$want" ] && [ "$got" = "$want" ] || { echo "STOP: the tar is not the one the connect wrote"; exit 7; }
mkdir "$F/records" && tar -C "$F/records" -xf "$F/fetch-bsel.tar" || { echo "STOP: untar"; exit 7; }
( cd "$F/records/fetch-bsel" && shasum -a 256 -c --strict --quiet RECORDS.SHA256SUMS ) > "$F/records-check.txt" 2>&1
crc=$?
ns=$(grep -c '' "$F/records/fetch-bsel/RECORDS.SHA256SUMS")
nfiles=$(cd "$F/records/fetch-bsel" && find . -type f ! -name RECORDS.SHA256SUMS | wc -l | tr -d ' ')
echo "RECORDS.SHA256SUMS check rc=$crc ($ns lines, $nfiles files in the tar besides it)"
[ "$crc" -eq 0 ] || { echo "STOP: a record differs from its sum, or a sum line is malformed"; cat "$F/records-check.txt"; exit 7; }
[ "$ns" -eq "$nfiles" ] || { echo "STOP: $ns sums for $nfiles records"; exit 7; }
dn=$(cat "$F/connect-bsel.done"); echo "connect done file: $dn"
[ "$dn" = 0 ] || { echo "STOP: the connect's done file is '$dn', not 0"; exit 7; }
exit $rc
