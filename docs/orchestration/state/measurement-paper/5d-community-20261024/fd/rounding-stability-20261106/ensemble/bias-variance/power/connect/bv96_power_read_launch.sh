#!/bin/bash
# BV96 O1: the Mac-side launcher for bv96_power_read_login.sh. One ssh carries both the /dev/shm digest check and the
# launch. The copy's sha256 must equal the one the director released, or the node deletes it and exits 8 before
# anything runs. ssh's rc is read unpiped. Usage: bash bv96_power_read_launch.sh <receipts dir>.
# Run only after cov2d_fence.sh (rc 0) and the login survey, both recorded in <receipts dir>, and on the director's go
# on this login script's sha256.
R=${1:?receipts dir}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/bv96_power_read_login.sh"
SHA=2f35f99f873a0ff462e3666e81ff7745ad214ae0b4cd63c73d3b7527d44dac44
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local login script is not the released one"; exit 8; }
[ ! -e "$R/o1.out" ] || { echo "STOP: $R/o1.out exists"; exit 9; }
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "f=/dev/shm/bv96o1.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; bash \"\$f\" \"\$f\"" \
  < "$S" > "$R/o1.out" 2> "$R/o1.err"
rc=$?
echo "ssh rc=$rc"
exit $rc
