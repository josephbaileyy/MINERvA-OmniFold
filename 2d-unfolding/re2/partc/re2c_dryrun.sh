#!/bin/bash
# RE-2 part C: the purity dry run the director allowed before binding (RE2-DECLARATION-C.md §4.1; conditions (a)-(d)):
#     bash re2c_dryrun.sh <deploy> <try name>
# (a) it writes only under DR=$B/review/partc-dryrun; (b) strace records every file the run opens, and re2c_audit.py
# requires that no refined product (part B's or J0's) is touched and no write falls outside DR; (c) the outcomes are
# committed with the declaration; (d) a failure is reported, not patched. The run is stopped at 15 min.
set -o pipefail
DR=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/review/partc-dryrun
B=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023
D=$(cd "$1" && pwd); T=$2
case "$D" in "$DR"/*) ;; *) echo "the deploy must be under $DR"; exit 2;; esac
timeout 900 strace -f -qq -e trace=open,openat,creat,rename,renameat,renameat2,unlink,unlinkat,mkdir,mkdirat \
    -o "$DR/$T.strace.log" bash "$D/2d-unfolding/re2/partc/re2c_run.sh" purity "$D" "$DR/$T" > "$DR/$T.out" 2>&1
rc=$?
echo "run rc=$rc" >> "$DR/$T.out"
/usr/bin/python3 -I "$D/2d-unfolding/re2/partc/re2c_audit.py" --strace "$DR/$T.strace.log" --dry "$DR" \
    --refined "$B/partb,$B/j0" --out "$DR/$T.audit.json" >> "$DR/$T.out" 2>&1
arc=$?
echo "audit rc=$arc" >> "$DR/$T.out"
gzip -9 "$DR/$T.strace.log"
exit $(( rc != 0 || arc != 0 ))
