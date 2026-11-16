#!/bin/bash
# Rebuild each launcher that ran (r1 4a88370d, r2 8a35418a, diag a7ffe394, r3 60b624c6) and the approved 468f1992
# from launch-g2r.sh (60b624c6) and the four committed diffs, applied in reverse. Prints each sha256; rc 1 on a mismatch.
#     bash launch-chain.sh
set -u
H=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d "${TMPDIR:-/tmp}/lchain.XXXXXX")
s() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -c1-64; }
cp "$H/launch-g2r.sh" "$T/l"; ok=0
chk() { local got; got=$(s "$T/l"); echo "$1 $got"; case $got in "$2"*) ;; *) echo "MISMATCH want $2"; ok=1 ;; esac; }
chk "r3   (as committed)" 60b624c6
rev() { if patch -s -R "$T/l" < "$H/$1"; then chk "$2" "$3"; else echo "PATCH FAILED $1"; ok=1; fi; }
rev launch-g2r-r3-vs-a7ffe394.diff.txt   "diag (r3 diff reversed)" a7ffe394
rev launch-g2r-diag-vs-8a35418a.diff.txt "r2   (diag diff reversed)" 8a35418a
rev launch-g2r-r2-vs-468f1992.diff.txt   "468f (r2 diff reversed)" 468f1992
rev launch-g2r-vs-4a88370d.diff.txt      "r1   (prepare diff reversed)" 4a88370d
rm -f "$T/l" && rmdir "$T"
[ "$ok" = 0 ] && echo "LAUNCH-CHAIN PASS" || echo "LAUNCH-CHAIN FAILED"
exit $ok
