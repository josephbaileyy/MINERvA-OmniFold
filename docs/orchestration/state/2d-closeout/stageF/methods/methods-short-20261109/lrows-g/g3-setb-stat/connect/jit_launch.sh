#!/bin/bash
# G3's Mac-side launcher (hpss_launch.sh's pattern, 296ea772): one ssh session per call, through saul.nersc.gov to NODE;
# the script travels on stdin; on NODE its /dev/shm copy must carry the approved sha256 or NODE deletes it and exits 8;
# the script runs detached (setsid nohup) and this session prints its output; ssh's rc is read unpiped.
# Usage: bash jit_launch.sh fence|stat|statB|read <new empty session dir> <login node>
#        bash jit_launch.sh fetch <new empty fetch dir> <login node, unused>
MODE=${1:?fence|stat|statB|read|fetch}; F=${2:?session dir}; NODE=${3:?login node}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  fence) S="$HERE/../e96fence/bin/cov2d_fence.sh"; SHA=16a2a5cd5e36f0a3d48577afd3c4b1d4adebe6baf72fcf228d7c85275739754a ;;
  read)  S="$HERE/jit_read.sh"; SHA=64e21f1a0ea47650985cc77697b70f849abd986ad3de07e54df4db69a4d54f5c ;;
  fetch)
    scp -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 "saul.nersc.gov:/pscratch/sd/j/josephrb/g3-jitter-20261112/jit.tar.gz" "$F/" > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/jit.tar.gz"; exit $rc ;;
  statB) S="$HERE/jit_statB.sh"; SHA=7d97931c3fe1efa3b097694882e224ad1bc53d36ef64ed49da214b4366aeb45d ;;
  stat)  S="$HERE/jit_stat.sh"; SHA=129d5e36ad08f1e92af472247022518896ff3560ccdd7db736ebde07db4334c5 ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/g3jit-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
