#!/bin/bash
# The launcher of rm-ibub-20261123.sh, its own login connect (not the IBUB launcher). The script goes to login38 on
# stdin. On the node, its /dev/shm copy must have the approved sha256, or the node deletes the copy and exits 8 before
# anything runs. The script runs detached (setsid nohup), its output is read back, and both /dev/shm files are
# deleted. Everything it prints, the inventory included, lands in <new empty dir>/session.out on the laptop.
# Usage: bash rm-launch.sh <new empty dir>
F=${1:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/rm-ibub-20261123.sh"; SHA=e7f875eabff78091a706d435165be2d507cd680736a61f44908e90c5165714bc
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="f=/dev/shm/rmib.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\" \"\$f\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} login38 $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
grep -v '^[dfl] ' "$F/session.out"
src=$(sed -n 's/^script rc=\([0-9][0-9]*\)$/\1/p' "$F/session.out" | tail -1)
[ -n "$src" ] || { echo "STOP: the session did not report a script rc"; exit 9; }
echo "the script's rc=$src; the full session (with the inventory) is $F/session.out"
exit "$src"
