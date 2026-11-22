#!/bin/bash
# T3's connect launcher (T3-CONNECT-PLAN.md section 6): RDX's rdx_connect_launch.sh pattern, with the inner hop's host
# key checked strictly (StrictHostKeyChecking=yes, UpdateHostKeys=no). saul, then a loginNN; the script goes on stdin;
# on NODE the /dev/shm copy's sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs;
# it runs detached (setsid nohup) and the launcher waits for it. ssh's rc is read unpiped.
# Usage: bash t3p_launch.sh <new empty dir> <loginNN> <dry|q3|floor> <window_end_epoch> <fence prefixes, comma-sep>
F=${1:?session dir}; NODE=${2:?loginNN}; MODE=${3:?mode}; WEND=${4:?window end epoch}; FENCE=${5:?fence}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
case "$MODE" in dry|q3|floor) ;; *) echo "STOP: mode '$MODE'"; exit 9;; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || { echo "STOP: window end '$WEND'"; exit 9; }
[ "$(date +%s)" -le "$WEND" ] || { echo "STOP: the window has ended"; exit 9; }
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || { echo "STOP: fence '$FENCE'"; exit 9; }
S="$HERE/t3p_submit.sh"; SHA=50e86da36a5b398107b1b4fd61d9cf2fa1d68dbd0852b9a7e45218c8fbe302b5
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local connect script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="f=/dev/shm/t3pc.\$\$.sh; o=\$f.out; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; setsid nohup bash \"\$f\" \"\$f\" $MODE $WEND $FENCE > \"\$o\" 2>&1 < /dev/null & p=\$!; echo \"detached pid \$p, output \$o\"; wait \$p; r=\$?; cat \"\$o\"; rm -f -- \"\$o\"; echo \"script rc=\$r\""
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.out"
exit $rc
