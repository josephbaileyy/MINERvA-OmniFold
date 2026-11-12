#!/bin/bash
# RSN connect 1: the Mac-side launcher. Its hop is RSN's audited HPSS launcher's (#1084, cd826dbd), itself #1054's:
# one ssh session enters at saul.nersc.gov and hops to NODE (a loginNN; never a data-transfer node, never a Slurm job),
# with ServerAlive 15/8 on both hops and StrictHostKeyChecking=accept-new on the inner one. stdin carries the script;
# on NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs.
# The script runs detached (setsid nohup, stdin /dev/null, output to a /dev/shm file), so a dropped session cannot
# kill it; it also tees its output to $OUT/logs/connect1.log. ssh's rc is read unpiped. Needs a current sshproxy
# certificate (Joseph renews it). Writes only into the new empty local directory F.
# Usage: bash rsn_connect1_launch.sh <new empty dir> <loginNN>
F=${1:?session dir}; NODE=${2:?loginNN}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
S="$HERE/rsn_connect1.sh"; SHA=4fbb8f29384eeccb3f5b914ce1b76a47aa84ae89ca5c68095b3b51e0d592caac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=accept-new)
R="f=/dev/shm/rsnc1.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
