#!/bin/bash
# RPD-RECO flux connect 1 (revision 2): the Mac-side launcher, in rpd_mnv_check2_launch.sh's pattern. One ssh session per call,
# entering at saul.nersc.gov and hopping to NODE. For fence, connect and fetch, stdin carries the script through both
# hops. On NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes the copy and exits 8 before
# anything runs. ssh's rc is read unpiped.
# Usage: bash rpd_flux1_launch.sh survey  <new empty session dir> <node> [<node> ...]   (read-only load survey)
#        bash rpd_flux1_launch.sh fence   <new empty session dir> <login node>   (the committed cov2d_fence.sh)
#        bash rpd_flux1_launch.sh connect <new empty session dir> <login node>   (prepares and submits job rpd_flux1)
#        bash rpd_flux1_launch.sh fetch   <new empty session dir> <login node>   (any login node; exit 10 if unfinished)
MODE=${1:?survey|fence|connect|fetch}; F=${2:?session dir}; shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel) || { echo "STOP: not inside the repository"; exit 9; }
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
SSH="ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8"
if [ "$MODE" = survey ]; then
  [ $# -ge 1 ] || { echo "STOP: no nodes named"; exit 9; }
  R=""
  for n in "$@"; do
    case "$n" in login[0-9][0-9]) ;; *) echo "STOP: '$n' is not a login node name"; exit 9 ;; esac
    R="$R echo \"== $n\"; ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $n 'cat /proc/loadavg; nproc; test -e /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 && echo ROOT-EXISTS || echo root-absent';"
  done
  $SSH saul.nersc.gov "$R" > "$F/survey.out" 2> "$F/survey.err"
  rc=$?; echo "ssh rc=$rc"; cat "$F/survey.out"; exit $rc
fi
NODE=${1:-}
case "$MODE" in
  fence)   S="$TOP/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier2-20261110/t2a/code/cov2d_fence.sh"
           SHA=16a2a5cd5e36f0a3d48577afd3c4b1d4adebe6baf72fcf228d7c85275739754a ;;
  connect) S="$HERE/rpd_flux1_connect.sh"; SHA=d7a73172aa280a5775db45f8a45223655650ef219d416a63bace846b38298b0e ;;
  fetch)   S="$HERE/rpd_flux1_fetch.sh"; SHA=dfade48a535e722cc5febdbe7749f9d4435d3a83403d8158b74beefb797f67ea ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9 ;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/rpd-flux1-$MODE.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; echo \"script rc=\$?\""
$SSH saul.nersc.gov "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
