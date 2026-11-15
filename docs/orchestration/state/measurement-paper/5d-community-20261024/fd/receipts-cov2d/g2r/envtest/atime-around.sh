#!/bin/bash
# The before-and-after of atime-stat-list.sh around the G2R envtest (the director's empirical overlap check).
#   bash atime-around.sh pre    before the envtest's launch: run-envtest-stat/pre.raw
#   bash atime-around.sh post   after the envtest job has ended: run-envtest-stat/post.raw, then the comparison
# Each reading must end with "stat_rc=0 n_list=1146" and hold 1146 "seconds<TAB>path" lines. post compares the two
# readings' lines exactly. Exit: 0 every reading complete and, for post, 0 of 1146 moved (NONE-MOVED); 3 a reading is
# incomplete (INCOMPLETE, nothing concluded); 4 an atime moved (MOVED: a STOP to the director, the overlap change void).
set -u
H=$(cd "$(dirname "$0")" && pwd); D=$H/run-envtest-stat; S=$H/atime-stat-list.sh
mode=${1:-}
case "$mode" in pre|post) ;; *) echo "usage: atime-around.sh pre|post"; exit 2 ;; esac
mkdir -p "$D"
[ -e "$D/$mode.raw" ] && { echo "REFUSED $D/$mode.raw exists"; exit 2; }
[ "$mode" = post ] && [ ! -s "$D/pre.raw" ] && { echo "REFUSED no pre reading"; exit 2; }
echo "script $(shasum -a 256 "$S" | cut -c1-64)"
ssh -o ControlPath=none -o ConnectTimeout=30 -o BatchMode=yes saul.nersc.gov 'bash -s' < "$S" > "$D/$mode.raw" 2> "$D/$mode.err"
src=$?
echo "ssh_rc=$src"; head -1 "$D/$mode.raw"; tail -1 "$D/$mode.raw"
complete() {  # complete <file>: the closing line and 1146 body lines
    tail -1 "$1" | grep -q '^stat_rc=0 n_list=1146 ' && [ "$(grep -cE $'^[0-9]+\t/' "$1")" = 1146 ]
}
[ "$src" = 0 ] && complete "$D/$mode.raw" || { echo "INCOMPLETE: the $mode reading did not complete"; exit 3; }
[ "$mode" = pre ] && { echo "PRE-COMPLETE 1146 paths"; exit 0; }
grep -E $'^[0-9]+\t/' "$D/pre.raw" > "$D/pre.tsv"
grep -E $'^[0-9]+\t/' "$D/post.raw" > "$D/post.tsv"
diff "$D/pre.tsv" "$D/post.tsv" > "$D/moved.diff"; drc=$?
moved=$(grep -c '^>' "$D/moved.diff")
echo "diff_rc=$drc moved=$moved of 1146"
case "$drc" in
    0) echo "NONE-MOVED"; exit 0 ;;
    1) echo "MOVED: a STOP to the director (the overlap change is void)"; cat "$D/moved.diff"; exit 4 ;;
    *) echo "INCOMPLETE: diff rc=$drc"; exit 3 ;;
esac
