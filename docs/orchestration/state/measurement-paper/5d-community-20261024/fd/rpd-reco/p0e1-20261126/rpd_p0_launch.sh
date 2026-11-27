#!/bin/bash
# RPD-RECO P0 for e1 (rpd_p0, generated from p0-20261123's launcher with flux4's ack guard): the Mac-side launcher, in rpd_mnv_check2_launch.sh's pattern. connect requires the three-lane ack file (cov2d, tier3-design, minerva-lib), kept byte for byte in the local session record. One ssh session per call,
# entering at saul.nersc.gov and hopping to NODE. For fence, connect and fetch, stdin carries the script through both
# hops. On NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes the copy and exits 8 before
# anything runs. ssh's rc is read unpiped.
# Usage: bash rpd_p0_launch.sh survey  <new empty session dir> <node> [<node> ...]   (read-only load survey)
#        bash rpd_p0_launch.sh fence   <new empty session dir> <login node>   (refused: not used for rpd_p0)
#        bash rpd_p0_launch.sh connect <new empty session dir> <login node> <ack.txt>   (P0, detached on the node)
#        bash rpd_p0_launch.sh fetch   <new empty session dir> <login node>   (the runner's node while it runs; exit 10 if running)
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
    R="$R echo \"== $n\"; ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $n 'cat /proc/loadavg; nproc; test -e /pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126 && echo ROOT-EXISTS || echo root-absent';"
  done
  $SSH saul.nersc.gov "$R" > "$F/survey.out" 2> "$F/survey.err"
  rc=$?; echo "ssh rc=$rc"; cat "$F/survey.out"; exit $rc
fi
NODE=${1:-}
case "$MODE" in
  fence)   echo "STOP: fence mode is not used for rpd_p0 (the connect's step-2 sacct fence replaces it)"; exit 9 ;;
  connect) S="$HERE/rpd_p0_connect.sh"; SHA=5016f37822af9c43e52b8fe9379757306c8dd47948115d9dad566d88ab242434 ;;
  fetch)   S="$HERE/rpd_p0_fetch.sh"; SHA=d52f3576192b25672f892808c0f740accfb392813ef525e4ffad5ea3da03b35b ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9 ;; esac
if [ "$MODE" = connect ]; then
  ACK=${2:-}
  [ -n "$ACK" ] && [ -f "$ACK" ] || { echo "STOP: connect needs the three-lane ack file (ack.txt) as its fourth argument"; exit 9; }
  A="$F/ack.txt"
  bad_ack() { rm -f -- "$A"; echo "STOP: $1"; exit 9; }
  # One byte-exact snapshot: the copy made here is what is validated below and what stays in the session record.
  cp "$ACK" "$A" || bad_ack "ack.txt could not be copied into the session"
  LC_ALL=C tr -d '\000' < "$A" | cmp -s - "$A" || bad_ack "ack.txt contains NUL bytes"
  now=$(date -u +%s) && [[ $now =~ ^[0-9]+$ ]] || bad_ack "the clock could not be read"
  n=0
  for lane in cov2d tier3-design minerva-lib; do  # the overlap owner, the sidecar's owner, geanttw's lane, in order
    n=$((n + 1))
    line=$(sed -n "${n}p" "$A")
    [[ $line =~ ^ACK-UTC\ ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)\ ([a-z0-9-]+)$ ]] || bad_ack "ack.txt line $n is not 'ACK-UTC <YYYY-MM-DDTHH:MM:SSZ> $lane'"
    when=${BASH_REMATCH[1]}
    who=${BASH_REMATCH[2]}
    [ "$who" = "$lane" ] || bad_ack "ack.txt line $n names '$who', not $lane"
    ack_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%SZ' "$when" +%s 2>/dev/null) || bad_ack "ack.txt line $n's time does not parse: $when"
    [ "$(TZ=UTC date -j -r "$ack_s" +%Y-%m-%dT%H:%M:%SZ)" = "$when" ] || bad_ack "ack.txt line $n's time is not a real UTC time: $when"
    [[ $ack_s =~ ^[0-9]+$ ]] || bad_ack "ack.txt line $n's time did not convert: $when"
    age=$(( now - ack_s ))
    [ "$age" -ge -300 ] || bad_ack "$lane's ack time is in the future: $when"
    [ "$age" -le 21600 ] || bad_ack "$lane's ack is older than 6 h ($when, $age s)"
    echo "$lane ack $when (age $age s)"
  done
  [ "$(sed -n '4,$p' "$A" | grep -c '[^[:space:]]')" -ge 1 ] || bad_ack "ack.txt carries no ack text after its three ACK-UTC lines"
  echo "three acks recorded byte for byte in the session as ack.txt"
fi
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/rpd-p0-$MODE.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\"; rc=\$?; echo \"script rc=\$rc\"; exit \$rc"
$SSH saul.nersc.gov "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
