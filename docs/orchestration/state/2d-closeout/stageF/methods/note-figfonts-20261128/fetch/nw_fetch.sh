#!/bin/bash
# nw_fetch.sh: fetch the two inputs of negweight_ratio_2d.pdf to the laptop (limitation-resolver, 2026-11-28; 0 node-h,
# one login-node ssh, nothing written on the cluster or to CFS).
# usage: bash nw_fetch.sh <mode pscratch|hpss> <expected sha256 of nw_remote.sh> <expected sha256 of nw_verify.py> <new out dir>
# The mode is chosen by the person who runs it, never at run time: pscratch first; hpss only as a separate, explicit
# run if pscratch reports MISSING. It refuses unless both scripts have the shas the director approved, the cert is valid
# for at least 30 more minutes (read in UTC), and <out dir> is new. It runs nw_remote.sh once over ssh with a fresh
# connection (ControlPath=none), stdout to payload.tar and stderr to session.log, and reads ssh's rc unpiped. Then
# nw_verify.py extracts only the two inputs into <out dir>/inputs and checks them against the inventory shas.
set -u
MODE=${1:-}; EXPR=${2:-}; EXPV=${3:-}; OUT=${4:-}
case "$MODE" in pscratch|hpss) ;; *) echo "usage: nw_fetch.sh <pscratch|hpss> <sha nw_remote.sh> <sha nw_verify.py> <new out dir>"; exit 2;; esac
[ -n "$OUT" ] && [ ! -e "$OUT" ] || { echo "REFUSED: <out dir> must be new"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
gr=$(shasum -a 256 "$HERE/nw_remote.sh" | awk '{print $1}'); gv=$(shasum -a 256 "$HERE/nw_verify.py" | awk '{print $1}')
[ "$gr" = "$EXPR" ] || { echo "REFUSED: nw_remote.sh sha256 $gr, expected $EXPR"; exit 2; }
[ "$gv" = "$EXPV" ] || { echo "REFUSED: nw_verify.py sha256 $gv, expected $EXPV"; exit 2; }
to=$(TZ=UTC ssh-keygen -L -f "$HOME/.ssh/nersc-cert.pub" | awk '/Valid:/ {print $NF}')
to_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%S' "$to" +%s) || { echo "REFUSED: cannot read the cert's end time"; exit 3; }
now=$(date -u +%s)
mkdir -p "$OUT"
echo "cert valid to ${to}Z (UTC); now $(date -u +%FT%TZ)" | tee "$OUT/cert.txt"
[ $((to_s - now)) -ge 1800 ] || { echo "REFUSED: cert expires within 30 minutes"; exit 3; }
cp "$HERE/nw_remote.sh" "$HERE/nw_verify.py" "$OUT/"
printf '%s  nw_remote.sh\n%s  nw_verify.py\n' "$gr" "$gv" > "$OUT/scripts.sha256"
echo "mode $MODE; start $(date -u +%FT%TZ)" | tee "$OUT/mode.txt"
ssh -o ControlPath=none -o BatchMode=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=4 \
  josephrb@saul.nersc.gov "bash -s -- $MODE" < "$HERE/nw_remote.sh" > "$OUT/payload.tar" 2> "$OUT/session.log"
rc=$?
echo "$rc" > "$OUT/ssh_rc.txt"
echo "ssh rc=$rc; payload $(wc -c < "$OUT/payload.tar" | tr -d ' ') bytes; end $(date -u +%FT%TZ)"
grep -E '^(nw_remote|fence|FENCE|REFUSED|MISSING|node-read)' "$OUT/session.log"
[ "$rc" = 0 ] || { echo "FETCH FAIL: ssh rc $rc (see session.log); nothing extracted"; exit 4; }
python3 -I "$HERE/nw_verify.py" "$MODE" "$OUT/payload.tar" "$OUT/inputs" > "$OUT/verify.txt" 2>&1
vrc=$?
cat "$OUT/verify.txt"
[ "$vrc" = 0 ] && echo "FETCH PASS ($MODE)" || { echo "FETCH FAIL: verify rc $vrc"; exit 5; }
