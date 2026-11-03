#!/bin/bash
# COV2D connect R1: the composite-weight receipt (COV2D-DECLARATION.md section 9.2) on a login node at nice 19, 0
# node-h, before the audit. A fresh clone at M in a new pscratch directory, the bound blobs checked, then
# cov2d_receipt.py. Writes only under $W. Run detached: setsid nohup bash connect-r1.sh >/dev/null 2>&1 </dev/null &
set -o pipefail
M=b4fb3c6cdd351cf68b04fbc3fea6648ba11d4fb8
P=/pscratch/sd/j/josephrb; W=$P/cov2d-receipt-20261102; DD=$W/deploy
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" || exit 2
exec >> "$W/connect-r1.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ ppid=$PPID"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
echo "4b0744d7dc5ee80d68424d3b1ff16c15eab2738a54963e887ed0c03662888e6c  2d-unfolding/cov2d/cov2d.py
c085b51f46afe3675077756aac982d5a7ebc87a5801dd7cbde79dd0f867bd7de  2d-unfolding/cov2d/cov2d_receipt.py" > "$W/bound.sha256"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
(cd "$DD" && sha256sum 2d-unfolding/re2/re2_driver.py nd-unfolding/fd_1b_toys.py nd-unfolding/s5e_deform.py nd-unfolding/pv-ladder/pvl_lib.py)
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 "$PY" -B "$DD/2d-unfolding/cov2d/cov2d_receipt.py" --out "$W/receipt.json" > "$W/receipt.out" 2> "$W/receipt.time"
rc=$?
echo "receipt rc=$rc"
cat "$W/receipt.out"
grep -E "Elapsed|Maximum resident|File system inputs|Percent of CPU" "$W/receipt.time"
sha256sum "$W/receipt.json" "$W/receipt.out" "$W/receipt.time"
echo "end=$(date -u +%FT%TZ)"
