#!/bin/bash
# RDX's connect launcher: RSN connect 1's (rsn_connect1_launch.sh f7cc3c80; the HPSS kit's hop: saul, then a loginNN,
# ServerAlive 15/8, StrictHostKeyChecking=accept-new on the inner hop), passing STEP, PIN and LIMIT to the script. On
# NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs; the
# script runs detached (setsid nohup), so a dropped session cannot kill it. ssh's rc is read unpiped.
# Usage: bash rdx_connect_launch.sh <new empty dir> <loginNN> <STEP> <PIN> [LIMIT]
F=${1:?session dir}; NODE=${2:?loginNN}; STEP=${3:?step}; PIN=${4:?pin}; LIMIT=${5:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
case "$STEP" in s0|s1|c1|s2|c2|m|cm|s3a|s3b) ;; *) echo "STOP: step '$STEP'"; exit 9;; esac
[[ "$PIN" =~ ^[0-9a-f]{40}$ ]] || { echo "STOP: pin '$PIN'"; exit 9; }
[[ -z "$LIMIT" || "$LIMIT" =~ ^[0-9]+:[0-9]{2}:[0-9]{2}$ ]] || { echo "STOP: limit '$LIMIT'"; exit 9; }
S="$HERE/rdx_connect.sh"; SHA=da8378ab396ac3106b950d29912ce486c878284c6db2dd232861a56c3606b9ca
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=accept-new)
R="f=/dev/shm/rdxc.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $STEP $PIN $LIMIT > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
