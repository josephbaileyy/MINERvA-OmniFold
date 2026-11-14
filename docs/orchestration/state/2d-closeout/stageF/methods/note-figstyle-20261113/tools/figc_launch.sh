#!/bin/bash
# Note figure style, group C: the Mac-side launcher, from e96d_a1_launch2.sh. Modes: presence (figc_presence.sh), family1
# (figc_family1.sh), family1b (figc_family1b.sh), and fetch-f1 / fetch-f1b (one scp of $OUT/<run>/post-<run>.tar.gz).
# One ssh session, direct to saul (ControlPath none, ServerAlive 15/8); stdin carries the script; on the login node the
# /dev/shm copy's sha256 must equal the approved one, or it is deleted and the run exits 8 before anything runs. The
# script runs detached (setsid nohup, stdin /dev/null, output to a /dev/shm file under umask 077) and is passed its own
# path; the session waits, prints the output and removes the output file. ssh's rc is read unpiped.
# Usage: bash figc_launch.sh presence|family1|family1b|fetch-f1|fetch-f1b <new empty session dir>
MODE=${1:?mode}; F=${2:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  presence) S="$HERE/figc_presence.sh"; SHA=fa6ae0f44c8acd3f8f10b2d92a11d6a5a9c51ede84d8d4ee479f540a95b62c00 ;;
  family1)  S="$HERE/figc_family1.sh";  SHA=2cc6be4f82970f3345fe130978803f80aa5a57daf8b088480674c56f460e56bc ;;
  family1b) S="$HERE/figc_family1b.sh"; SHA=4e713548e6c54f694ae272c4e439ea739e4a35bfd78bc378be3c9c54d6a4c933 ;;
  fetch-f1|fetch-f1b)
    r=${MODE#fetch-}
    scp -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 "saul.nersc.gov:/pscratch/sd/j/josephrb/note-figstyle-20261114/$r/post-$r.tar.gz" "$F/" > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post-$r.tar.gz"; exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/figc-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\"; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 \
  saul.nersc.gov "$R" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
