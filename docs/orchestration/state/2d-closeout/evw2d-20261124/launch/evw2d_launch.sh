#!/bin/bash
# EVW2D: the Mac-side launcher (EVW5D's evw5d_launch.sh, adapted). Before every step it checks the NERSC sshproxy
# certificate by command (ssh-keygen -L on the public certificate; it reads no key): the step stops with exit 7 unless
# the certificate is valid for at least the step's margin. One ssh session per remote step: it enters at saul.nersc.gov
# and hops to NODE; stdin carries the script through both hops; on NODE the script is staged in a private mktemp file in
# /dev/shm whose sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs. The remote
# script's exit status is the remote wrapper's, so ssh's status (read unpiped) is the script's.
# Usage: bash evw2d_launch.sh connect|post|cleanup <new empty session dir> <login node, e.g. login27>
#        bash evw2d_launch.sh fetch <new empty dir>          (post.tar.gz, and cleanup.tar.gz when it exists)
MODE=${1:?connect|post|cleanup|fetch}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
LANE=__LANE_ROOT__
CERT=${EVW2D_CERT:-$HOME/.ssh/nersc-cert.pub}
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$LANE" in *__*) echo "STOP: the lane root is not filled in"; exit 9;; esac
cert_ok() {   # cert_ok <seconds>: the certificate's "Valid: ... to <local time>" is at least that far ahead
  local to end now
  to=$(ssh-keygen -L -f "$CERT" 2>/dev/null | sed -n 's/^ *Valid: from [0-9T:-]* to \([0-9T:-]*\)$/\1/p' | head -1)
  [ -n "$to" ] || { echo "STOP: no validity window read from $CERT"; return 1; }
  end=$(date -j -f %Y-%m-%dT%H:%M:%S "$to" +%s 2>/dev/null) || { echo "STOP: cannot read the time '$to'"; return 1; }
  now=$(date +%s)
  echo "certificate valid to $to local ($(( (end - now) / 60 )) min left; this step needs $(( $1 / 60 )))"
  [ $(( end - now )) -ge "$1" ] || { echo "STOP: the certificate expires too soon for this step"; return 1; }
}
case "$MODE" in
  connect) S="$HERE/evw2d_connect.sh"; SHA=__CONNECT_SHA256__; MARGIN=2700 ;;
  post)    S="$HERE/evw2d_post.sh";    SHA=__POST_SHA256__;    MARGIN=900 ;;
  cleanup) S="$HERE/evw2d_cleanup.sh"; SHA=__CLEANUP_SHA256__; MARGIN=900 ;;
  fetch)
    cert_ok 600 || exit 7
    rc=0
    for f in post.tar.gz cleanup.tar.gz; do
      [ "$f" = cleanup.tar.gz ] && { ssh "${SSH[@]}" saul.nersc.gov "test -f $LANE/$f" < /dev/null || continue; }
      scp "${SSH[@]}" "saul.nersc.gov:$LANE/$f" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
      echo "scp $f rc=$r"; [ $r = 0 ] && shasum -a 256 "$F/$f"; [ $r = 0 ] || rc=$r
    done
    exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 for $MODE is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
cert_ok "$MARGIN" || exit 7
R="umask 077; f=\$(mktemp /dev/shm/evw2d-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
