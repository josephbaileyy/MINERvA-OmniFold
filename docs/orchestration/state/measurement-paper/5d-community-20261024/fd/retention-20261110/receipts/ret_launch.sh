#!/bin/bash
# Retention stat: the Mac-side launcher, rpl_launch.sh (0e473dc8) with one mode. One ssh session per call: it enters
# at saul.nersc.gov and hops
# to NODE; stdin carries the script through both hops; on NODE the /dev/shm copy's sha256 must equal the approved one,
# or NODE deletes it and exits 8 before anything runs. ssh's rc is read unpiped.
# The session-drop pattern (the director's ruling after T2A's rc-255 drop, 2026-11-10): the inner hop carries
# ServerAlive 15/8 as the outer does, and the remote script runs detached (setsid nohup, stdin /dev/null, output to a
# /dev/shm file), so a dropped session cannot kill it; this session waits on it, prints its output and removes the file.
# After a drop, the stat script keeps running; its output stays in the /dev/shm .out file on NODE (named in the
# session's "detached pid" line), which only a director-approved status read may fetch.
# Usage: bash ret_launch.sh retention <new empty session dir> <login node, e.g. login27>
MODE=${1:?retention}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  retention) S="$HERE/retention_stat.sh"; SHA=08e2bd17c599e4dfb640d0dd2985a031101368aa49eb54de66040be79ec198b1 ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/ret-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
