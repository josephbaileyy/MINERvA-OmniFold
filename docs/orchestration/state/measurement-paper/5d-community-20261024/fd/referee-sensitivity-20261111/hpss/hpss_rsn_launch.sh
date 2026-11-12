#!/bin/bash
# RSN's HPSS archive: the Mac-side launcher, from hpss-20261111's hpss_launch.sh (296ea772), for a data-transfer node.
# One ssh session per call, straight to NODE.nersc.gov (a dtnNN: never a login node, never a Slurm job); stdin carries
# the script; on NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes it and exits 8 before
# anything runs. The remote script runs detached (setsid nohup, stdin /dev/null, output to a /dev/shm file), so a
# dropped session cannot kill it; after a drop the archive keeps running and writes its own log under $OUT/logs, which
# the fetch mode reads. ssh's rc is read unpiped. Needs a current sshproxy certificate (Joseph renews it).
# Usage: bash hpss_rsn_launch.sh archive <new empty session dir> <dtnNN>
#        bash hpss_rsn_launch.sh fetch <new empty fetch dir> <dtnNN>   (scp of $OUT/post.tar.gz and $OUT/logs/archive.log)
MODE=${1:?archive|fetch}; F=${2:?session dir}; NODE=${3:?dtnNN}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in dtn[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a data-transfer node name"; exit 9;; esac
OUT=/pscratch/sd/j/josephrb/hpss-rsn-20261111
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
case "$MODE" in
  archive) S="$HERE/hpss_rsn.sh"; SHA=877d9840a182a5e215d66903ca23b157dcc4872526bf67b30aa1963e35a43c9f ;;
  fetch)
    scp "${SSH[@]}" "$NODE.nersc.gov:$OUT/post.tar.gz" "$NODE.nersc.gov:$OUT/logs/archive.log" "$F/" > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post.tar.gz" "$F/archive.log"; exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/hpssr-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" "$NODE.nersc.gov" "$R" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
