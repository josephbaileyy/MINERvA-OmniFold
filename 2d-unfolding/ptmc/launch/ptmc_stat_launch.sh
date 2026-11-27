#!/bin/bash
# PTMC D4 stat: the Mac-side launcher (oofvc_cleanup_launch.sh's form). One ssh session: it enters at saul.nersc.gov and
# hops to NODE; stdin carries ptmc_stat.sh, staged in a private mktemp file in /dev/shm whose sha256 must equal the
# approved one, or NODE deletes it and exits 8 before anything runs.
# Usage: bash ptmc_stat_launch.sh <new empty session dir> <login node>
F=${1:?session dir}; NODE=${2:-}
HERE=$(cd "$(dirname "$0")" && pwd)
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/ptmc_stat.sh"; SHA=6b775e313107d81b772e8bfcc6226fbafaf75a55be57c1db3bb72dd24a9e2142
case "$SHA" in *__*) echo "STOP: the approved sha256 is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
h=$(shasum -a 256 "$S" | cut -d' ' -f1) && [ "$h" = "$SHA" ] || { echo "STOP: the local stat script is not the approved one"; exit 8; }
R="umask 077; f=\$(mktemp /dev/shm/ptmc-stat.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
