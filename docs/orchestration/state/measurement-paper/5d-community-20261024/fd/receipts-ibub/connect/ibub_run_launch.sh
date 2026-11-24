#!/bin/bash
# IBUB connect R's launcher. It is MSR connect B's launcher (msr_build_launch.sh), with this lane's script, namespace
# and tag.
#
# **The session:**
# - saul, then a loginNN, with the inner hop's host key checked strictly;
# - the script goes on stdin;
# - on the node, the /dev/shm copy's sha256 must equal the approved one, or the node deletes the copy and exits 8
#   before anything runs;
# - the script runs detached with setsid nohup;
# - ssh's rc is read unpiped.
#
# **Then the fetch:** fetch-run.tar, logs/connect-run.log and logs/connect-run.done, each streamed with dd iflag=noatime
# into the session directory. The tar's sha256 must equal the one the connect's log printed, and its
# RECORDS.SHA256SUMS must hold.
#
# Usage: bash ibub_run_launch.sh <new empty dir> <loginNN> <window_end_epoch>
F=${1:?session dir}; NODE=${2:?loginNN}; WEND=${3:?window end epoch}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || { echo "STOP: window end '$WEND'"; exit 9; }
[ "$(date +%s)" -le "$WEND" ] || { echo "STOP: the window has ended"; exit 9; }
S="$HERE/ibub_run_connect.sh"; SHA=@@CONNECT_SHA@@
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="f=/dev/shm/ibubc.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $WEND > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
src=$(sed -n 's/^script rc=\([0-9][0-9]*\)$/\1/p' "$F/session.out" | tail -1)
[ -n "$src" ] || { echo "STOP: the session did not report a script rc; no fetch"; exit 9; }
grep -q '^BAIL ' "$F/session.out" && { echo "STOP: the connect bailed before writing anything; no fetch"; exit 9; }
echo "connect script rc=$src (every stop after \$N exists writes the records tar first)"

# ---- the fetch, after the session (the connect has finished writing; nothing below writes on the cluster)
O=/pscratch/sd/j/josephrb/ibub-20261123
frc=0
for rel in logs/connect-run.log logs/connect-run.done fetch-run.tar; do
  ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "dd if=$O/$rel iflag=noatime status=none")" \
    > "$F/$(basename "$rel")" 2>> "$F/fetch.err"
  r=$?; echo "fetch $rel rc=$r bytes $(wc -c < "$F/$(basename "$rel")" | tr -d ' ')"
  [ "$r" -eq 0 ] || frc=1
done
[ "$frc" -eq 0 ] || { echo "STOP: a fetch failed (fetch.err); connect script rc was $src"; [ "$src" -ne 0 ] && exit "$src"; exit 7; }
want=$(sed -n 's/^fetch-run\.tar sha256 \([0-9a-f]\{64\}\) bytes .*/\1/p' "$F/connect-run.log")
got=$(shasum -a 256 "$F/fetch-run.tar" | cut -d' ' -f1)
echo "fetch-run.tar sha256 $got (the log's: $want)"
[ -n "$want" ] && [ "$got" = "$want" ] || { echo "STOP: the tar is not the one the connect wrote"; exit 7; }
mkdir "$F/records" && tar -C "$F/records" -xf "$F/fetch-run.tar" || { echo "STOP: untar"; exit 7; }
( cd "$F/records/fetch-run" && shasum -a 256 -c --quiet RECORDS.SHA256SUMS ) > "$F/records-check.txt" 2>&1
crc=$?
echo "RECORDS.SHA256SUMS check rc=$crc ($(grep -c . "$F/records/fetch-run/RECORDS.SHA256SUMS") files)"
[ "$crc" -eq 0 ] || { echo "STOP: a record differs from its sum"; cat "$F/records-check.txt"; exit 7; }
echo "connect done file: $(cat "$F/connect-run.done")"
[ "$src" -eq 0 ] || { echo "STOP: the connect script ended rc $src (records fetched and checked above)"; exit "$src"; }
exit $rc
