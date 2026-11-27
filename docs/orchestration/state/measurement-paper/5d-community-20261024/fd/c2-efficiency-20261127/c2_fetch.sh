#!/bin/bash
# C2-EFF fetch (tier3-design, 2026-11-27): one read-only login-node connect that streams REF-C2C1's c2 units
# (c2_replica_b1..b300 and c2_central, .npz + .done) and read-2's staged E_R copies 001..301_xsec.root to the laptop as a
# tar, through O_NOATIME|O_NOFOLLOW reads (c2_fetch_remote.py). Nothing is written on NERSC: no file, directory, cache or
# job. Then c2_fetch_verify.py checks the tar on the laptop against the remote manifest, the done-markers, the committed
# c2_central sha256 and read-2's committed inputs listing.
#
# usage: c2_fetch.sh OUT_DIR [--check-only]
#   OUT_DIR must not exist (claimed with plain mkdir). --check-only runs every local gate and exits before any ssh.
# Exit codes: 0 FETCH OK; 2 usage; 3 a local gate refused; 4 the cert; 5 the fence; 6 the connect; 7 the verifier.
umask 077
set -C
OUT=${1:?usage: c2_fetch.sh OUT_DIR [--check-only]}
MODE=${2:-}
case "$MODE" in ""|--check-only) ;; *) echo "REFUSED: unknown mode '$MODE'"; exit 2 ;; esac
[ "$#" -le 2 ] || { echo "REFUSED: too many arguments"; exit 2; }

D=$(cd "$(dirname "$0")" && pwd -P) || { echo "REFUSED: cannot resolve the script directory"; exit 3; }
REMOTE=$D/c2_fetch_remote.py
VERIFY=$D/c2_fetch_verify.py
REMOTE_SHA=c43de0fcbe66cad4a6fdd7ef43a0c0c0a714cd32b4eba8519abf45b736e16274
VERIFY_SHA=22583d1d58d48dd313ed66dfda0725c7240df2ebcb88cf3736fcb6ed14883284
P=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2
LISTING_PATH=$P/read-2/inputs-listing.txt
LISTING_BLOB=cfcc15403019240b3f41e94bd93cf1ed726f7850
CENTRAL_DONE_PATH=$P/units-centrals/c2_central.done
CENTRAL_SHA=929d0e78011ead72e9677a05bad06eec80e914e181c8d02f94bbdea1c43b76f4
UNITS=/pscratch/sd/j/josephrb/ref-c2c1-20261106/units
INPUTS=/pscratch/sd/j/josephrb/ref-c2c1-20261106/read-2/inputs
HOST=saul.nersc.gov
SSH=(ssh -o ControlPath=none -o ConnectTimeout=20 -o BatchMode=yes -o LogLevel=ERROR)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

refuse() { echo "REFUSED: $2"; exit "$1"; }

# --- local gates: the two helpers and the two committed operands, each by command, never typed
s=$(shasum -a 256 "$REMOTE") && [ "${s%% *}" = "$REMOTE_SHA" ] || refuse 3 "c2_fetch_remote.py is not $REMOTE_SHA (${s%% *})"
s=$(shasum -a 256 "$VERIFY") && [ "${s%% *}" = "$VERIFY_SHA" ] || refuse 3 "c2_fetch_verify.py is not $VERIFY_SHA (${s%% *})"
git -C "$D" fetch -q origin || refuse 3 "git fetch origin"
b=$(git -C "$D" rev-parse "origin/main:$LISTING_PATH") && [ "$b" = "$LISTING_BLOB" ] \
    || refuse 3 "origin/main's read-2 inputs listing is not blob $LISTING_BLOB ($b)"
c=$(git -C "$D" show "origin/main:$CENTRAL_DONE_PATH") || refuse 3 "c2_central.done is not on origin/main"
cs=$(printf '%s' "$c" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(d["sha256"] if d.get("verdict") == "PASS" else "")') \
    && [ "$cs" = "$CENTRAL_SHA" ] || refuse 3 "origin/main's c2_central.done does not carry $CENTRAL_SHA ($cs)"
py=$(python3 -I -c 'import sys, numpy; print(sys.version.split()[0], numpy.__version__)') || refuse 3 "local python3 with numpy"
echo "local gates passed: remote $REMOTE_SHA, verify $VERIFY_SHA, listing blob $LISTING_BLOB, central $CENTRAL_SHA; python $py"

left=$(TZ=UTC ssh-keygen -L -f "$HOME/.ssh/nersc-cert.pub" | python3 -I -c '
import re, sys, calendar, time
m = re.search(r"Valid: from \S+ to (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", sys.stdin.read())
print(int(calendar.timegm(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")) - time.time()))') \
    && [ "$left" -gt 1800 ] 2>/dev/null || refuse 4 "the NERSC cert has under 30 minutes left, or could not be read ($left)"
echo "cert: ${left} s left"

if [ "$MODE" = --check-only ]; then echo "check-only: every local gate passed; no connect made"; exit 0; fi

mkdir "$OUT" || refuse 3 "OUT_DIR $OUT exists or cannot be created"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/start_utc.txt"
{ echo "remote $REMOTE_SHA"; echo "verify $VERIFY_SHA"; echo "wrapper $(shasum -a 256 "$0" | cut -d' ' -f1)"; } > "$OUT/code.txt"

# --- the fence: sacct only (never squeue). Refuse while any of my REF-C2C1 or C2-EFF jobs is pending or running.
"${SSH[@]}" "$HOST" 'sacct -X -n -P -u josephrb -S now-14days -s PD,R,RQ,S -o JobID,JobName,State' \
    < /dev/null > "$OUT/fence.txt" 2> "$OUT/fence.err"
frc=$?
[ "$frc" -eq 0 ] || refuse 5 "the sacct fence failed (rc $frc); see $OUT/fence.err"
hit=$(python3 -I -c '
import sys
bad = [l for l in open(sys.argv[1]) if l.strip() and l.split("|")[1].startswith(("fd_c2c1", "refc2c1", "c2c1", "c2eff"))]
print(len(bad))' "$OUT/fence.txt") && [ "$hit" = 0 ] || refuse 5 "the fence found a REF-C2C1 or C2-EFF job ($hit); see $OUT/fence.txt"
echo "fence clear at $(date -u +%T)Z ($(wc -l < "$OUT/fence.txt" | tr -d ' ') other pending/running rows recorded)"

# --- the fetch: one ssh; the remote reader writes only to its stdout and stderr
"${SSH[@]}" "$HOST" "env -i PATH=/usr/bin:/bin HOME=\$HOME OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 ionice -c 3 /usr/bin/python3 -I -B - $UNITS $INPUTS" \
    < "$REMOTE" > "$OUT/fetch.tar" 2> "$OUT/remote.err"
rc=$?
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/end_utc.txt"
echo "$rc" > "$OUT/rc.txt"
[ "$rc" -eq 0 ] || refuse 6 "the connect returned rc $rc; see $OUT/remote.err"
last=$(tail -n 1 "$OUT/remote.err") && [ "$last" = "FETCH-DONE 903 files" ] || refuse 6 "the remote reader did not finish ($last)"

# --- verify on the laptop
git -C "$D" show "origin/main:$LISTING_PATH" > "$OUT/inputs-listing.committed.txt" || refuse 7 "cannot write the committed listing"
python3 -I -B "$VERIFY" "$OUT" "$OUT/inputs-listing.committed.txt" "$CENTRAL_SHA" > "$OUT/verify.out" 2>&1
vrc=$?
v=$(tail -n 1 "$OUT/verify.out") && [ "$vrc" -eq 0 ] && [ "$v" = "VERIFY OK 903" ] || refuse 7 "the verifier refused (rc $vrc): $v"
t=$(shasum -a 256 "$OUT/fetch.tar") || refuse 7 "cannot hash fetch.tar"
echo "C2-EFF FETCH OK: 903 files, fetch.tar ${t%% *}, $(cat "$OUT/start_utc.txt") to $(cat "$OUT/end_utc.txt")"
exit 0
