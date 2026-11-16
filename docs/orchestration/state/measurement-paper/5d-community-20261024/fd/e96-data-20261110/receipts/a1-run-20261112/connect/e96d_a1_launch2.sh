#!/bin/bash
# E96D under amendment 1: the Mac-side launcher for the readout, from e96d_a1_launch.sh (143f7440) with only two
# modes: analyze (e96d_a1_analyze.sh) and fetch-analyze. One ssh session, direct to saul (ControlPath none, ServerAlive
# 15/8); stdin carries the script; on the login node the /dev/shm copy's sha256 must equal the approved one, or it is
# deleted and the run exits 8 before anything runs. The script runs detached (setsid nohup, stdin /dev/null, output to
# a /dev/shm file under umask 077) and is passed its own path; the session waits, prints the output and removes the
# output file. ssh's rc is read unpiped. fetch-analyze is one scp of $NEW/post-analyze.tar.gz.
# Usage: bash e96d_a1_launch2.sh analyze|fetch-analyze <new empty session dir>
MODE=${1:?mode}; F=${2:?session dir}
HERE=$(cd "$(dirname "$0")" && pwd)
NEW=/pscratch/sd/j/josephrb/e96data-a1
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$MODE" in
  analyze)   S="$HERE/e96d_a1_analyze.sh";     SHA=76e8924db4235247e1d3491606c39426d7d3d6eb235e30acd969f06fd4599dbd; A="" ;;
  fetch-analyze)
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
