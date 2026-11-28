#!/bin/bash
# PTMC: the Mac-side launcher (OOFVC's oofvc_launch.sh form). One ssh session per call. Login-node modes enter at
# saul.nersc.gov and hop to NODE (loginNN). The stage mode goes by direct ssh to dtn01.nersc.gov (the declaration's
# O_NOATIME DTN copy; its fence is the prestage mode, from a login node, immediately before). stdin carries
# ptmc_remote.sh. On the remote host it is staged in a private mktemp file in /dev/shm whose sha256 must equal the
# approved one, or the host deletes it and exits 8 before anything runs. Each mode needs its own GO. Every local gate
# fails closed (exit 9, or 8 for the sha).
# Usage: bash ptmc_launch.sh setup|prestage|pilot|post-pilot|replicas|post <new empty session dir> <loginNN>
#        bash ptmc_launch.sh stage <new empty session dir> dtn01
#        bash ptmc_launch.sh fetch <new empty dir>     (post.tar.gz, d4.tar.gz and post's tars.sha256 by scp; each tar's
#                                                       local sha256 must equal the remote one; no remote script)
set -u -o pipefail
MODE=${1:-}; F=${2:-}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd) || { echo "STOP: the launcher's directory"; exit 9; }
OUT=/pscratch/sd/j/josephrb/ptmc-20261128
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -n "$F" ] && [ -d "$F" ] || { echo "STOP: '$F' is not a directory"; exit 9; }
ls_f=$(ls -A "$F") || { echo "STOP: ls of $F failed"; exit 9; }
[ -z "$ls_f" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/ptmc_remote.sh"; SHA=__REMOTE_SHA256__
case "$MODE" in
  setup|prestage|pilot|post-pilot|replicas|post)
    case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac ;;
  stage)
    [ "$NODE" = dtn01 ] || { echo "STOP: stage runs on dtn01, not '$NODE'"; exit 9; } ;;
  fetch)
    r=0
    for f in tars.sha256 post.tar.gz d4.tar.gz; do
      scp "${SSH[@]}" "saul.nersc.gov:$OUT/$f" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; s=$?
      echo "scp $f rc=$s"
      [ $s = 0 ] || r=$s
    done
    [ "$r" = 0 ] || exit $r
    for f in post.tar.gz d4.tar.gz; do
      h=$(shasum -a 256 "$F/$f" | cut -d' ' -f1) || { echo "STOP: hashing $f failed"; exit 9; }
      want=$(awk -v f="$f" '$2 == f {print $1}' "$F/tars.sha256") || { echo "STOP: reading tars.sha256 failed"; exit 9; }
      [ ${#want} = 64 ] || { echo "STOP: tars.sha256 has no single digest for $f"; exit 9; }
      [ "$h" = "$want" ] || { echo "STOP: the fetched $f is $h, the remote one $want"; exit 9; }
      echo "$h  $f (equal to the remote digest)"
    done
    exit 0 ;;
  *) echo "STOP: mode '$MODE'"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 is not filled in"; exit 9;; esac
h=$(shasum -a 256 "$S" | cut -d' ' -f1) || { echo "STOP: hashing the remote script failed"; exit 9; }
[ "$h" = "$SHA" ] || { echo "STOP: the local remote script is not the approved one"; exit 8; }
R="umask 077; f=\$(mktemp /dev/shm/ptmc-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\" || exit 8; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\" $MODE; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
if [ "$MODE" = stage ]; then
  ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=40 dtn01.nersc.gov "$R" \
    < "$S" > "$F/session.out" 2> "$F/session.err"
else
  ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=40 saul.nersc.gov \
    "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
    < "$S" > "$F/session.out" 2> "$F/session.err"
fi
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
