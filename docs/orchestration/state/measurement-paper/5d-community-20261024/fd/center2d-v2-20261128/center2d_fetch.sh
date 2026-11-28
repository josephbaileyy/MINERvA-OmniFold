#!/bin/bash
# CENTER2D fetch (tier3-design, 2026-11-28): one read-only login-node read of the 16 files of CENTER2D-DECLARATION.md
# section 3 (G2R's data and tune npz, Q_R, S5_R, part B's 10 S3 lateral unfolds, the X01 scale), streamed to the laptop
# as a tar through O_RDONLY|O_NOATIME|O_NOFOLLOW reads (center2d_fetch_remote.py). Nothing is written on NERSC: no file,
# directory, cache or job. Then center2d_fetch_verify.py checks the tar against the remote manifest and against the
# digests `center2d.py expected` takes from committed records.
#
# usage: center2d_fetch.sh OUT_DIR [--check-only]
#   OUT_DIR must not exist (claimed with plain mkdir). --check-only runs every local gate and exits before any ssh.
# Exit codes: 0 FETCH OK; 2 usage; 3 a local gate refused; 4 the cert; 5 the fence; 6 the connect; 7 the verifier.
umask 077
set -C
OUT=${1:?usage: center2d_fetch.sh OUT_DIR [--check-only]}
MODE=${2:-}
case "$MODE" in ""|--check-only) ;; *) echo "REFUSED: unknown mode '$MODE'"; exit 2 ;; esac
[ "$#" -le 2 ] || { echo "REFUSED: too many arguments"; exit 2; }

D=$(cd "$(dirname "$0")" && pwd -P) || { echo "REFUSED: cannot resolve the script directory"; exit 3; }
REMOTE=$D/center2d_fetch_remote.py
VERIFY=$D/center2d_fetch_verify.py
FENCE=$D/center2d_fence.py
DRIVER=$D/center2d.py
REMOTE_SHA=dd1215a1bdef87c046bb538eaadd61811734660bf62d3961c019faad1cbe79e6
FENCE_SHA=ee696ee63877cd2ee52719d42fa63fcfa79dee8d1b6f5c3d9c8cd7fa588db9d6
VERIFY_SHA=e3385e8e8b869f672be9aeccc4a4cae27c355826fa82ee319e0681a18cd048b9
DRIVER_SHA=554ee0bcd3d5335685927b9f5b9c99351d4651d08d4a6a8f9d408b032718b27d
EXPECTED_SHA=5e50af9b841c0c115bb4b152bc5c6b9b64158c3d7ef37c33d1a67a11bb826fe6
N=16
FAMILIES="cov2d t2a rpd precharge_c geanttw_ oofvc_ covfix_ ibuchi_ ptmc_ rdx_ center2d"
HOST=saul.nersc.gov
SSH=(ssh -o ControlPath=none -o ConnectTimeout=20 -o BatchMode=yes -o LogLevel=ERROR)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

refuse() { echo "REFUSED: $2"; exit "$1"; }

# --- local gates: the four helpers by sha256, and the expected digests from committed records, each by command
s=$(shasum -a 256 "$REMOTE") && [ "${s%% *}" = "$REMOTE_SHA" ] || refuse 3 "center2d_fetch_remote.py is not $REMOTE_SHA (${s%% *})"
s=$(shasum -a 256 "$VERIFY") && [ "${s%% *}" = "$VERIFY_SHA" ] || refuse 3 "center2d_fetch_verify.py is not $VERIFY_SHA (${s%% *})"
s=$(shasum -a 256 "$FENCE") && [ "${s%% *}" = "$FENCE_SHA" ] || refuse 3 "center2d_fence.py is not $FENCE_SHA (${s%% *})"
s=$(shasum -a 256 "$DRIVER") && [ "${s%% *}" = "$DRIVER_SHA" ] || refuse 3 "center2d.py is not $DRIVER_SHA (${s%% *})"
git -C "$D" fetch -q origin || refuse 3 "git fetch origin"
EXP=$(python3 -I -B "$DRIVER" expected) || refuse 3 "center2d.py expected refused: $EXP"
e=$(printf '%s\n' "$EXP" | shasum -a 256) && [ "${e%% *}" = "$EXPECTED_SHA" ] \
    || refuse 3 "the expected digests are not $EXPECTED_SHA (${e%% *})"
n=$(printf '%s\n' "$EXP" | wc -l | tr -d ' ') && [ "$n" = "$N" ] || refuse 3 "center2d.py expected listed $n files, not $N"
py=$(python3 -I -c 'import sys, numpy; print(sys.version.split()[0], numpy.__version__)') || refuse 3 "local python3 with numpy"
echo "local gates passed: remote $REMOTE_SHA, verify $VERIFY_SHA, fence $FENCE_SHA, driver $DRIVER_SHA, expected $EXPECTED_SHA; python $py"

left=$(TZ=UTC ssh-keygen -L -f "$HOME/.ssh/nersc-cert.pub" | python3 -I -c '
import re, sys, calendar, time
m = re.search(r"Valid: from \S+ to (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", sys.stdin.read())
print(int(calendar.timegm(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")) - time.time()))') \
    && [ "$left" -gt 1800 ] 2>/dev/null || refuse 4 "the NERSC cert has under 30 minutes left, or could not be read ($left)"
echo "cert: ${left} s left"

if [ "$MODE" = --check-only ]; then echo "check-only: every local gate passed; no connect made"; exit 0; fi

mkdir "$OUT" || refuse 3 "OUT_DIR $OUT exists or cannot be created"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/start_utc.txt"
{ echo "remote $REMOTE_SHA"; echo "verify $VERIFY_SHA"; echo "fence $FENCE_SHA"; echo "driver $DRIVER_SHA"; echo "expected $EXPECTED_SHA";
  echo "wrapper $(shasum -a 256 "$0" | cut -d' ' -f1)"; } > "$OUT/code.txt"
printf '%s\n' "$EXP" > "$OUT/expected.tsv"

# --- the fence (director's ruling 5): sacct and squeue. sacct without -s (which would select jobs by any state held
# during the window); center2d_fence.py refuses on a fenced-family row whose State is not terminal, and on any
# fenced-family row squeue lists.
"${SSH[@]}" "$HOST" 'sacct -X -n -P -u josephrb -S now-14days -o JobID,JobName,State' \
    < /dev/null > "$OUT/fence_sacct.txt" 2> "$OUT/fence_sacct.err"
frc=$?
[ "$frc" -eq 0 ] || refuse 5 "the sacct fence failed (rc $frc); see $OUT/fence_sacct.err"
"${SSH[@]}" "$HOST" 'squeue -h -u josephrb -o "%i|%j|%T"' < /dev/null > "$OUT/fence_squeue.txt" 2> "$OUT/fence_squeue.err"
qrc=$?
[ "$qrc" -eq 0 ] || refuse 5 "the squeue fence failed (rc $qrc); see $OUT/fence_squeue.err"
hit=$(python3 -I -B "$FENCE" "$FAMILIES" "$OUT/fence_sacct.txt" "$OUT/fence_squeue.txt" 2> "$OUT/fence_hits.txt") \
    && [ "$hit" = 0 ] || refuse 5 "the fence found ${hit:-an undecidable} refusing row(s); see $OUT/fence_hits.txt"
echo "fence clear at $(date -u +%T)Z (families: $FAMILIES; $(wc -l < "$OUT/fence_sacct.txt" | tr -d ' ') sacct and $(wc -l < "$OUT/fence_squeue.txt" | tr -d ' ') squeue rows recorded, none refusing)"

# --- the fetch: one ssh; the remote reader writes only to its stdout and stderr
"${SSH[@]}" "$HOST" "env -i PATH=/usr/bin:/bin HOME=\$HOME OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 ionice -c 3 /usr/bin/python3 -I -B -" \
    < "$REMOTE" > "$OUT/fetch.tar" 2> "$OUT/remote.err"
rc=$?
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/end_utc.txt"
echo "$rc" > "$OUT/rc.txt"
[ "$rc" -eq 0 ] || refuse 6 "the connect returned rc $rc; see $OUT/remote.err"
last=$(tail -n 1 "$OUT/remote.err") && [ "$last" = "FETCH-DONE $N files" ] || refuse 6 "the remote reader did not finish ($last)"

# --- verify on the laptop
python3 -I -B "$VERIFY" "$OUT" "$OUT/expected.tsv" > "$OUT/verify.out" 2>&1
vrc=$?
v=$(tail -n 1 "$OUT/verify.out") && [ "$vrc" -eq 0 ] && [ "$v" = "VERIFY OK $N" ] || refuse 7 "the verifier refused (rc $vrc): $v"
t=$(shasum -a 256 "$OUT/fetch.tar") || refuse 7 "cannot hash fetch.tar"
echo "CENTER2D FETCH OK: $N files, fetch.tar ${t%% *}, $(cat "$OUT/start_utc.txt") to $(cat "$OUT/end_utc.txt")"
exit 0
