#!/bin/bash
# E96D: the Mac-side launcher, revision 2 of e96d_launch.sh (8e94934b): the same session pattern, with the post and
# full modes added and the script's arguments passed. One ssh session, direct to saul (ControlPath none, ServerAlive
# 15/8); stdin carries the script; on the login node the /dev/shm copy's sha256 must equal the approved one, or it is
# deleted and the run exits 8 before anything runs. The script runs detached (setsid nohup, stdin /dev/null, output to
# a /dev/shm file under umask 077) and is passed its own path and its stage; the session waits, prints the output and
# removes the output file. ssh's rc is read unpiped. fetch-<stage> is one scp of $NEW/post-<stage>.tar.gz.
# Usage: bash e96d_launch2.sh dry|post-dry|full|post-full|fetch-dry|fetch-full <new empty session dir>
MODE=${1:?mode}; F=${2:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
NEW=/pscratch/sd/j/josephrb/e96data-20261111
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  dry)       S="$HERE/e96d_dry_submit.sh";  SHA=c8e017dd81f7f57f42607e01de074a528afcb164bab9935dd7eef1cc8e5c3498; A="" ;;
  full)      S="$HERE/e96d_full_submit.sh"; SHA=9ba4321ae64aa71c1e0e81dffa645cbd4d5f4a26320d50bd91db16875a254224; A="" ;;
  post-dry)  S="$HERE/e96d_post.sh";        SHA=824002aca72c07892f2e44b7bf60f6fd39878cb197444cb614f64ce1dda3e82d; A=dry ;;
  post-full) S="$HERE/e96d_post.sh";        SHA=824002aca72c07892f2e44b7bf60f6fd39878cb197444cb614f64ce1dda3e82d; A=full ;;
  fetch-dry|fetch-full)
    st=${MODE#fetch-}
    scp -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 "saul.nersc.gov:$NEW/post-$st.tar.gz" "$F/" > "$F/scp.out" 2> "$F/scp.err"
    rc=$?; echo "scp rc=$rc"; [ $rc = 0 ] && shasum -a 256 "$F/post-$st.tar.gz"; exit $rc ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local $MODE script is not the approved one"; exit 8; }
R="f=/dev/shm/e96d-$MODE.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $A > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\"; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 \
  saul.nersc.gov "$R" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
