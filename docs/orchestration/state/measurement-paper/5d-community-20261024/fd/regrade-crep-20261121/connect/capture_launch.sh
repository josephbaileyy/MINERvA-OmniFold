#!/bin/bash
# REGRADE capture launcher: T3's t3p_launch.sh pattern (saul, then a loginNN with StrictHostKeyChecking=yes and
# UpdateHostKeys=no; the script on stdin; the /dev/shm copy's sha256 checked on the node or exit 8; run detached and
# waited for). ssh's rc is read unpiped. fetch mode: scp of $OUT/post.tar.gz and the connect log through saul.
# Usage: bash capture_launch.sh run <new empty dir> <loginNN> <window_end_epoch> <fence prefixes, comma-sep>
#        bash capture_launch.sh fetch <new empty dir>
MODE=${1:?run|fetch}; F=${2:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=/pscratch/sd/j/josephrb/regrade-capture-20261121
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
if [ "$MODE" = fetch ]; then
  scp "${SSH[@]}" "saul.nersc.gov:$OUT/post.tar.gz" "saul.nersc.gov:$OUT/logs/connect-capture.log" "$F/" > "$F/scp.out" 2> "$F/scp.err"
  rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post.tar.gz" "$F/connect-capture.log"; exit $rc
fi
[ "$MODE" = run ] || { echo "STOP: mode '$MODE'"; exit 9; }
NODE=${3:?loginNN}; WEND=${4:?window end epoch}; FENCE=${5:?fence}
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || { echo "STOP: window end '$WEND'"; exit 9; }
[ "$(date +%s)" -le "$WEND" ] || { echo "STOP: the window has ended"; exit 9; }
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || { echo "STOP: fence '$FENCE'"; exit 9; }
S="$HERE/capture_connect.sh"; SHA=ba594904a56d3e81ba783ad3f030888c15be4c2acf30f61376455360a56e0509
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="f=/dev/shm/rcapc.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $WEND $FENCE > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
