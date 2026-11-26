#!/bin/bash
# EVW2D: the Mac-side launcher (EVW5D's evw5d_launch.sh, adapted). Before every step it checks the NERSC sshproxy
# certificate by command (TZ=UTC ssh-keygen -L on the public certificate; it reads no key): the step stops with exit 7
# unless ssh-keygen succeeds, the window has begun, and it lasts at least the step's margin. The first hop is told to
# present exactly that certificate (CertificateFile, with its key by IdentityFile and IdentitiesOnly), so the checked
# certificate is the one used. One ssh session per remote step: it enters at saul.nersc.gov
# and hops to NODE; stdin carries the script through both hops; on NODE the script is staged in a private mktemp file in
# /dev/shm whose sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs. The remote
# script's exit status is the remote wrapper's, so ssh's status (read unpiped) is the script's.
# Usage: bash evw2d_launch.sh connect|post|cleanup <new empty session dir> <login node, e.g. login27>
#        bash evw2d_launch.sh fetch <new empty dir>          (post.tar.gz, and cleanup.tar.gz when it exists)
MODE=${1:?connect|post|cleanup|fetch}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
LANE=/pscratch/sd/j/josephrb/evw2d-20261126
CERT=${EVW2D_CERT:-$HOME/.ssh/nersc-cert.pub}
KEY=${CERT%-cert.pub}
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o IdentitiesOnly=yes -o "IdentityFile=$KEY"
     -o "CertificateFile=$CERT")
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$LANE" in *__*) echo "STOP: the lane root is not filled in"; exit 9;; esac
cert_ok() {   # cert_ok <seconds>: ssh-keygen succeeds; the window "Valid: from A to B" (UTC) has begun and lasts that long
  local out from to b e now
  out=$(TZ=UTC ssh-keygen -L -f "$CERT" 2>&1) || { echo "STOP: ssh-keygen -L failed on $CERT"; return 1; }
  from=$(printf '%s\n' "$out" | sed -n 's/^ *Valid: from \([0-9T:-]*\) to \([0-9T:-]*\)$/\1/p' | head -1)
  to=$(printf '%s\n' "$out" | sed -n 's/^ *Valid: from \([0-9T:-]*\) to \([0-9T:-]*\)$/\2/p' | head -1)
  [ -n "$from" ] && [ -n "$to" ] || { echo "STOP: no validity window read from $CERT"; return 1; }
  b=$(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%S "$from" +%s 2>/dev/null) || { echo "STOP: cannot read the time '$from'"; return 1; }
  e=$(TZ=UTC date -j -f %Y-%m-%dT%H:%M:%S "$to" +%s 2>/dev/null) || { echo "STOP: cannot read the time '$to'"; return 1; }
  now=$(date +%s) || { echo "STOP: no clock"; return 1; }
  echo "certificate valid $from to $to UTC ($(( (e - now) / 60 )) min left; this step needs $(( $1 / 60 )))"
  [ "$b" -le "$now" ] || { echo "STOP: the certificate is not valid yet"; return 1; }
  [ $(( e - now )) -ge "$1" ] || { echo "STOP: the certificate expires too soon for this step"; return 1; }
}
cred_ok() {   # the resolved ssh configuration for saul offers only the checked key and certificate
  local g bad
  g=$(ssh -G "${SSH[@]}" saul.nersc.gov 2>&1) || { echo "STOP: ssh -G failed"; return 1; }
  bad=$(printf '%s\n' "$g" | awk -v k="$KEY" -v c="$CERT" -v h="$HOME" '
    $1 == "identityfile" || $1 == "certificatefile" { p = $2; sub(/^~/, h, p)
      if (($1 == "identityfile" && p != k) || ($1 == "certificatefile" && p != c)) print $1 " " $2 }
    $1 == "identitiesonly" && $2 != "yes" { print "identitiesonly " $2 }')
  [ -z "$bad" ] || { echo "STOP: ssh would offer another credential: $bad"; return 1; }
}
case "$MODE" in
  connect) S="$HERE/evw2d_connect.sh"; SHA=0fbc5cc452c9b12f15556f801e630a197e0b08e8654bef58bcd308d25dbd0cd6; MARGIN=2700 ;;
  post)    S="$HERE/evw2d_post.sh";    SHA=f1d81c63750fbc2eda06bc154900159a617a6f917f12b7ae22dbc20400e4f491;    MARGIN=900 ;;
  cleanup) S="$HERE/evw2d_cleanup.sh"; SHA=1fde6803a4e84ad18f5bfab88f56d5fd59b9dc8f2130447d5dee18b443c27cb7; MARGIN=900 ;;
  fetch)
    cert_ok 600 || exit 7
    cred_ok || exit 7
    rc=0
    for f in post.tar.gz cleanup.tar.gz; do
      have=$(ssh "${SSH[@]}" saul.nersc.gov "if [ -f $LANE/$f ]; then echo present; else echo absent; fi" < /dev/null); r=$?
      case "$r:$have" in
        0:present) ;;
        0:absent) echo "$f absent"; [ "$f" = post.tar.gz ] && rc=4; continue ;;
        *) echo "STOP: could not ask saul for $f (ssh rc=$r)"; rc=${r/#0/3}; continue ;;
      esac
      scp "${SSH[@]}" "saul.nersc.gov:$LANE/$f" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; r=$?
      echo "scp $f rc=$r"; [ $r = 0 ] || { rc=$r; continue; }
      shasum -a 256 "$F/$f" || rc=3
    done
    exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 for $MODE is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
cert_ok "$MARGIN" || exit 7
cred_ok || exit 7
R="umask 077; f=\$(mktemp /dev/shm/evw2d-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
