#!/bin/bash
# T2A status launcher: t2a_launch.sh (516565ac) with its modes replaced by one, "status", which stages t2a_status.sh.
# T2A: the Mac-side launcher (the ess_launch.sh pattern). One ssh session per call: it enters at saul.nersc.gov and hops
# to NODE; stdin carries the script through both hops; on NODE the /dev/shm copy's sha256 must equal the approved one,
# or NODE deletes it and exits 8 before anything runs. ssh's rc is read unpiped.
# Usage: bash t2a_status_launch.sh <new empty session dir> <login node>   (status only; read-only)
MODE=status; F=${1:?session dir}; NODE=${2:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  status)  S="$HERE/t2a_status.sh"; SHA=609dbea234b2ccc753353e9e24819351796f9755822c3d8148c2651762402ae0 ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/t2a-$MODE.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; echo \"script rc=\$?\""
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
