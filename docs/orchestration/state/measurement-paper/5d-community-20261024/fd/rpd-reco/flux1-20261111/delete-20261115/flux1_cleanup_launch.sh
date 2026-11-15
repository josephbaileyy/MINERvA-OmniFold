#!/bin/bash
# RPD-RECO flux connect 1, cleanup: the Mac-side launcher, in rpd_flux1_launch.sh's pattern. One ssh session per call,
# entering at saul.nersc.gov and hopping to NODE. stdin carries the Python script through both hops. On NODE the
# /dev/shm copy (umask 077) must have the approved sha256, or NODE deletes it and exits 8 before anything runs. The
# script runs at nice 19 under /usr/bin/python3 -B, and the copy is removed afterwards. ssh's rc is read unpiped.
# The load survey and the COV2D fence use rpd_flux1_launch.sh's approved survey and fence modes.
# Usage: bash flux1_cleanup_launch.sh inventory <new empty session dir> <login node>   (step A, read-only)
MODE=${1:?inventory}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  inventory) S="$HERE/flux1_inventory.py"; SHA=074c56a9362881ffb9168b9cba74717e578d12d5eb04ccebb46df6d4b2f6e600 ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9 ;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
SSH="ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8"
R="f=/dev/shm/limres-flux1-$MODE.\$\$.py; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; nice -n 19 /usr/bin/python3 -B \"\$f\"; rc=\$?; rm -f -- \"\$f\"; echo \"script rc=\$rc; /dev/shm copy removed: \$(test -e \"\$f\" && echo no || echo yes)\"; exit \$rc"
$SSH saul.nersc.gov "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
