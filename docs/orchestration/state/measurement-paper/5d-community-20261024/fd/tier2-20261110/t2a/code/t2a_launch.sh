#!/bin/bash
# T2A: the Mac-side launcher (the ess_launch.sh pattern). One ssh session per call: it enters at saul.nersc.gov and hops
# to NODE; stdin carries the script through both hops; on NODE the /dev/shm copy's sha256 must equal the approved one,
# or NODE deletes it and exits 8 before anything runs. ssh's rc is read unpiped.
# Usage: bash t2a_launch.sh fence|connect <new empty session dir> <login node, e.g. login27>
#        bash t2a_launch.sh fetch <new empty fetch dir>     (scp of $OUT/post.tar.gz; runs no remote script)
MODE=${1:?fence|connect|fetch}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=/pscratch/sd/j/josephrb/t2a-20261110
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  fence)   S="$HERE/cov2d_fence.sh"; SHA=16a2a5cd5e36f0a3d48577afd3c4b1d4adebe6baf72fcf228d7c85275739754a ;;
  connect) S="$HERE/t2a_connect.sh"; SHA=b2e39ada378f2fe53c01315cd7234d559c7355d6aed2d6e1cd8e0949f6935257 ;;
  fetch)
    scp -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 "saul.nersc.gov:$OUT/post.tar.gz" "$F/" \
      > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post.tar.gz"; exit $rc ;;
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
