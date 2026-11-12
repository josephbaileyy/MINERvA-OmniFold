#!/bin/bash
# CFS 1A check: the Mac-side launcher, from hpss_launch.sh (296ea772) with one mode and one hop. One ssh session, direct
# to dtn01.nersc.gov (ControlPath none, ServerAlive 15/8); stdin carries the script; on dtn01 the /dev/shm copy's sha256
# must equal the approved one, or dtn01 deletes it and exits 8 before anything runs. The script runs detached (setsid
# nohup, stdin /dev/null, output to a /dev/shm file under umask 077); the session waits, prints the output and removes
# both files. ssh's rc is read unpiped.
# Usage: bash cfs_1a_launch.sh <new empty session dir>
F=${1:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/cfs_1a_check.sh"; SHA=6f10f4c33790d2ca013ec54f4ae2738fd5b398b761f4e913998fcf715c88966f
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local check script is not the approved one"; exit 8; }
R="f=/dev/shm/cfs1a-check.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\" \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 \
  dtn01.nersc.gov "$R" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
