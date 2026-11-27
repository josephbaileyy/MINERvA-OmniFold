#!/bin/bash
# OOFVC: the Mac-side launcher (EVW5D's evw5d_launch.sh, adapted). One ssh session per call: it enters at
# saul.nersc.gov and hops to NODE; stdin carries the script; on NODE it is staged in a private mktemp file in /dev/shm
# whose sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs.
# Usage: bash oofvc_launch.sh dump-pilot <new empty session dir> <login node> <LL5D atime-post, YYYY-MM-DDTHH:MM:SSZ>
#        bash oofvc_launch.sh dump-rest|units|post <new empty session dir> <login node, e.g. login27>
#        bash oofvc_launch.sh fetch <new empty dir>      (post.tar.gz by scp; no remote script)
MODE=${1:?dump-pilot|dump-rest|units|post|fetch}; F=${2:?session dir}; NODE=${3:-}; POST=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=/pscratch/sd/j/josephrb/oofvc-20261126-r2
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
ARG=
case "$MODE" in
  dump-pilot) S="$HERE/oofvc_dump.sh";  SHA=7306001cd8a199b9d0f0efcc2562a58fd16dc5b337786e2391732a22c10ae290;  ARG=pilot
              case "$POST" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z) ARG="pilot $POST" ;;
                *) echo "STOP: dump-pilot needs cov2d's LL5D atime-post (UTC) as its fourth argument"; exit 9 ;; esac ;;
  dump-rest)  S="$HERE/oofvc_dump.sh";  SHA=7306001cd8a199b9d0f0efcc2562a58fd16dc5b337786e2391732a22c10ae290;  ARG=rest ;;
  units)      S="$HERE/oofvc_units.sh"; SHA=f5f19360af663c5afc17ecfba9164302e872344990b4d48632ce5fadff040584 ;;
  post)       S="$HERE/oofvc_post.sh";  SHA=35c699f55a60ca876e0d629f0321c18b62169b6d1ec7d5d1c8fd9dd9bb8d8565 ;;
  fetch)
    scp "${SSH[@]}" "saul.nersc.gov:$OUT/post.tar.gz" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
    echo "scp post.tar.gz rc=$r"; [ $r = 0 ] && shasum -a 256 "$F/post.tar.gz"; exit $r ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 for $MODE is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="umask 077; f=\$(mktemp /dev/shm/oofvc-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\" $ARG; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
