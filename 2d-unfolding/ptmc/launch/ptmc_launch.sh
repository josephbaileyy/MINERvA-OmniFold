#!/bin/bash
# PTMC: the Mac-side launcher (OOFVC's oofvc_launch.sh form). One ssh session per call: it enters at saul.nersc.gov
# and hops to NODE; stdin carries ptmc_remote.sh; on NODE it is staged in a private mktemp file in /dev/shm whose
# sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs. Each mode needs its own GO.
# Usage: bash ptmc_launch.sh setup|pilot|post-pilot|replicas|post <new empty session dir> <login node, e.g. login27>
#        bash ptmc_launch.sh fetch <new empty dir>     (post.tar.gz and d4.tar.gz by scp; no remote script)
MODE=${1:?setup|pilot|post-pilot|replicas|post|fetch}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=/pscratch/sd/j/josephrb/ptmc-20261128
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/ptmc_remote.sh"; SHA=__REMOTE_SHA256__
case "$MODE" in
  setup|pilot|post-pilot|replicas|post) ;;
  fetch)
    r=0
    for f in post.tar.gz d4.tar.gz; do
      scp "${SSH[@]}" "saul.nersc.gov:$OUT/$f" "$F/" >> "$F/scp.out" 2>> "$F/scp.err"; s=$?
      echo "scp $f rc=$s"; [ $s = 0 ] && shasum -a 256 "$F/$f"; [ $s = 0 ] || r=$s
    done
    exit $r ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local remote script is not the approved one"; exit 8; }
R="umask 077; f=\$(mktemp /dev/shm/ptmc-$MODE.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\" $MODE; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=40 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
