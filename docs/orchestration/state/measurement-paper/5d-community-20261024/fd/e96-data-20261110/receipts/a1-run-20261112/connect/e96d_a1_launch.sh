#!/bin/bash
# E96D under amendment 1: the Mac-side launcher, from e96d_launch2.sh (72ab0e04) with the A1 scripts, the run
# directory e96data-a1 and a restest mode (the dummy reservation-window test). One ssh session, direct to saul (ControlPath none, ServerAlive
# 15/8); stdin carries the script; on the login node the /dev/shm copy's sha256 must equal the approved one, or it is
# deleted and the run exits 8 before anything runs. The script runs detached (setsid nohup, stdin /dev/null, output to
# a /dev/shm file under umask 077) and is passed its own path and its stage; the session waits, prints the output and
# removes the output file. ssh's rc is read unpiped. fetch-<stage> is one scp of $NEW/post-<stage>.tar.gz.
# Usage: bash e96d_a1_launch.sh restest|dry|post-dry|full|post-full|fetch-dry|fetch-full <new empty session dir>
MODE=${1:?mode}; F=${2:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
NEW=/pscratch/sd/j/josephrb/e96data-a1
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  restest)   S="$HERE/e96d_a1_restest.sh";     SHA=fca284bd3751f39a145b29b9169dcb4490f64f27a89f0b939132016680db9a31; A="" ;;
  dry)       S="$HERE/e96d_a1_dry_submit.sh";  SHA=0a59335b200397d19c77ef4d151af54e79dd5c62dc0debcf12dd07343b7f2598; A="" ;;
  full)      S="$HERE/e96d_a1_full_submit.sh"; SHA=3a5395bcad567820ba3a42352cad782ca218259bfc90114b9387bfbd341953bc; A="" ;;
  post-dry)  S="$HERE/e96d_a1_post.sh";        SHA=386d77a87681a0a0ada2adfe6948c925c21d9d137d656d9adaf1eb09b56ef2ed; A=dry ;;
  post-full) S="$HERE/e96d_a1_post.sh";        SHA=386d77a87681a0a0ada2adfe6948c925c21d9d137d656d9adaf1eb09b56ef2ed; A=full ;;
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
