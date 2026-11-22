#!/bin/bash
# RPD-RECO flux rerun rpd_flux2 (generated from flux connect 1 revision 2): the Mac-side launcher, in rpd_mnv_check2_launch.sh's pattern. One ssh session per call,
# entering at saul.nersc.gov and hopping to NODE. For fence, connect and fetch, stdin carries the script through both
# hops. On NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes the copy and exits 8 before
# anything runs. ssh's rc is read unpiped.
# Usage: bash rpd_flux2_launch.sh survey  <new empty session dir> <node> [<node> ...]   (read-only load survey)
#        bash rpd_flux2_launch.sh fence   <new empty session dir> <login node>   (refused: not used for rpd_flux2)
#        bash rpd_flux2_launch.sh connect <new empty session dir> <login node>   (prepares and submits job rpd_flux2)
#        bash rpd_flux2_launch.sh fetch   <new empty session dir> <login node>   (any login node; exit 10 if unfinished)
MODE=${1:?survey|fence|connect|fetch}; F=${2:?session dir}; shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel) || { echo "STOP: not inside the repository"; exit 9; }
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
to=$(TZ=UTC ssh-keygen -L -f "$HOME/.ssh/nersc-cert.pub" 2>/dev/null | awk '/Valid:/ {print $NF}')
to_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%S' "$to" +%s 2>/dev/null) || { echo "STOP: cannot read the cert's end time"; exit 9; }
[ $((to_s - $(date -u +%s))) -ge 1800 ] || { echo "STOP: the cert ends within 30 minutes (valid to ${to}Z)"; exit 9; }
echo "cert valid to ${to}Z (UTC)"
SSH="ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8"
if [ "$MODE" = survey ]; then
  [ $# -ge 1 ] || { echo "STOP: no nodes named"; exit 9; }
  R=""
  for n in "$@"; do
    case "$n" in login[0-9][0-9]) ;; *) echo "STOP: '$n' is not a login node name"; exit 9 ;; esac
    R="$R echo \"== $n\"; ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $n 'cat /proc/loadavg; nproc; test -e /pscratch/sd/j/josephrb/rpd-reco-flux2-20261122 && echo ROOT-EXISTS || echo root-absent';"
  done
  $SSH saul.nersc.gov "$R" > "$F/survey.out" 2> "$F/survey.err"
  rc=$?; echo "ssh rc=$rc"; cat "$F/survey.out"; exit $rc
fi
NODE=${1:-}
case "$MODE" in
  fence)   echo "STOP: fence mode is not used for rpd_flux2 (the connect's step-2 sacct fence replaces it)"; exit 9 ;;
  connect) S="$HERE/rpd_flux2_connect.sh"; SHA=7a362f34dd00b2422c91ff542366d9cc120c8dedbde730da5592b171bac73fd2 ;;
  fetch)   S="$HERE/rpd_flux2_fetch.sh"; SHA=d8f780c917b873a888ce2dd55d8f16f813018a5d4fd87211f24e5d23dea750fc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9 ;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/rpd-flux2-$MODE.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; rc=\$?; echo \"script rc=\$rc\"; exit \$rc"
$SSH saul.nersc.gov "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
