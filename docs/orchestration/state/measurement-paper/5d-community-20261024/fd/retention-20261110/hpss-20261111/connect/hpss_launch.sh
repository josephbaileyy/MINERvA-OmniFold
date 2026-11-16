#!/bin/bash
# HPSS at-risk archive: the Mac-side launcher, derived from rpl_band_launch.sh (beedd94f) with three modes. One ssh session per
# call: it enters at saul.nersc.gov and hops to NODE; stdin carries the script through both hops; on NODE the /dev/shm
# copy's sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs. ssh's rc is read
# unpiped.
# The session-drop pattern (the director's ruling after T2A's rc-255 drop, 2026-11-10): the inner hop carries
# ServerAlive 15/8 as the outer does, and the remote script runs detached (setsid nohup, stdin /dev/null, output to a
# /dev/shm file), so a dropped session cannot kill it; this session waits on it, prints its output and removes the file.
# After a drop, the archive script keeps running and writes its own log under $OUT/logs, which the fetch mode reads.
# Usage: bash hpss_launch.sh fence|archive <new empty session dir> <login node, e.g. login27>
#        bash hpss_launch.sh fetch <new empty fetch dir>   (scp of $OUT/post.tar.gz and $OUT/logs/archive.log)
MODE=${1:?fence|archive|fetch}; F=${2:?session dir}; NODE=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
OUT=/pscratch/sd/j/josephrb/hpss-atrisk-20261111
case "$MODE" in
  fence)    S="$HERE/cov2d_fence.sh";  SHA=16a2a5cd5e36f0a3d48577afd3c4b1d4adebe6baf72fcf228d7c85275739754a ;;
  archive)  S="$HERE/hpss_atrisk.sh";  SHA=388cadb42b723237ffd16df9652bd0f05a3bc1baae337db66f191692f834e5a5 ;;
  fetch)
    scp -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 "saul.nersc.gov:$OUT/post.tar.gz" \
      "saul.nersc.gov:$OUT/logs/archive.log" "$F/" > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post.tar.gz" "$F/archive.log"; exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/hpssa-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
