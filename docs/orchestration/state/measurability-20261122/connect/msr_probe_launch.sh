#!/bin/bash
# MSR connect P's launcher (DECLARATION.md rev 2 section 8): T3's read launcher t3p_read_launch.sh (9d6bf0f1), its pattern (saul, then a loginNN with the inner
# hop's host key checked strictly; the script on stdin; on NODE the /dev/shm copy's sha256 must equal the approved one,
# or NODE deletes it and exits 8 before anything runs; detached with setsid nohup; ssh's rc read unpiped), then the
# fetch: fetch-probe.tar, logs/connect-probe.log and logs/connect-probe.done, each streamed with dd iflag=noatime into the
# session directory; the tar's sha256 must equal the one the connect's log printed, and its RECORDS.SHA256SUMS must hold.
# Usage: bash msr_probe_launch.sh <new empty dir> <loginNN> <window_end_epoch> <fence prefixes, comma-sep>
F=${1:?session dir}; NODE=${2:?loginNN}; WEND=${3:?window end epoch}; FENCE=${4:?fence}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || { echo "STOP: window end '$WEND'"; exit 9; }
[ "$(date +%s)" -le "$WEND" ] || { echo "STOP: the window has ended"; exit 9; }
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || { echo "STOP: fence '$FENCE'"; exit 9; }
S="$HERE/msr_probe_connect.sh"; SHA=b622141fde5894917be2dd198af8a9ec688612149e7c09360a7c9a89ea09480d
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="f=/dev/shm/msrp.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $WEND $FENCE > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
grep -q '^script rc=' "$F/session.out" || { echo "STOP: the session did not report a script rc; no fetch"; exit 9; }
grep -q '^BAIL ' "$F/session.out" && { echo "STOP: the connect bailed before writing anything; no fetch"; exit 9; }

# ---- the fetch, after the session (the connect has finished writing; nothing below writes on the cluster)
O=/pscratch/sd/j/josephrb/msr-p-20261122
frc=0
for rel in fetch-probe.tar logs/connect-probe.log logs/connect-probe.done; do
  ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "dd if=$O/$rel iflag=noatime status=none")" \
    > "$F/$(basename "$rel")" 2>> "$F/fetch.err"
  r=$?; echo "fetch $rel rc=$r bytes $(wc -c < "$F/$(basename "$rel")" | tr -d ' ')"
  [ "$r" -eq 0 ] || frc=1
done
[ "$frc" -eq 0 ] || { echo "STOP: a fetch failed (fetch.err)"; exit 7; }
want=$(sed -n 's/^fetch-probe\.tar sha256 \([0-9a-f]\{64\}\) bytes .*/\1/p' "$F/connect-probe.log")
got=$(shasum -a 256 "$F/fetch-probe.tar" | cut -d' ' -f1)
echo "fetch-probe.tar sha256 $got (the log's: $want)"
[ -n "$want" ] && [ "$got" = "$want" ] || { echo "STOP: the tar is not the one the connect wrote"; exit 7; }
mkdir "$F/records" && tar -C "$F/records" -xf "$F/fetch-probe.tar" || { echo "STOP: untar"; exit 7; }
( cd "$F/records/fetch-probe" && shasum -a 256 -c --quiet RECORDS.SHA256SUMS ) > "$F/records-check.txt" 2>&1
crc=$?
echo "RECORDS.SHA256SUMS check rc=$crc ($(grep -c . "$F/records/fetch-probe/RECORDS.SHA256SUMS") files)"
[ "$crc" -eq 0 ] || { echo "STOP: a record differs from its sum"; cat "$F/records-check.txt"; exit 7; }
echo "connect done file: $(cat "$F/connect-probe.done")"
exit $rc
