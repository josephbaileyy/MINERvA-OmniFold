#!/bin/bash
# COV2D connect C2: the clipping probe C2 (COV2D-DECLARATION.md section 14 item 5) on a login node at nice 19, 0
# node-h, descriptive. A fresh clone at M in a new pscratch directory, the bound blobs checked, then
# clip_probe.py. Writes only under $W. Run detached: setsid nohup bash connect-c2.sh >/dev/null 2>&1 </dev/null &
set -o pipefail
M=1a07b07c25ad7f598cb4697be0994e6421d9b2e0
P=/pscratch/sd/j/josephrb; W=$P/cov2d-clip2-20261103; DD=$W/deploy
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" || exit 2
exec >> "$W/connect-c2.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ ppid=$PPID"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
echo "4b0744d7dc5ee80d68424d3b1ff16c15eab2738a54963e887ed0c03662888e6c  2d-unfolding/cov2d/cov2d.py
c085b51f46afe3675077756aac982d5a7ebc87a5801dd7cbde79dd0f867bd7de  2d-unfolding/cov2d/cov2d_receipt.py
b4bea132c0ac759e6b178e3a4ed3ac835053e548ddc5a06774a3ad6eb08b6dc8  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe.py
b95c562916091b910a5ca8d874d83296035690cb8784db3d318b2f07fed28182  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe2.py" > "$W/bound.sha256"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
(cd "$DD" && sha256sum 2d-unfolding/re2/re2_driver.py nd-unfolding/fd_1b_toys.py nd-unfolding/s5e_deform.py nd-unfolding/pv-ladder/pvl_lib.py)
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 "$PY" -B "$DD/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe2.py" --out "$W/clip2.json" > "$W/clip2.out" 2> "$W/clip2.time"
rc=$?
echo "clip2 rc=$rc"
cat "$W/clip2.out"
grep -E "Elapsed|Maximum resident|File system inputs|Percent of CPU" "$W/clip2.time"
sha256sum "$W/clip2.json" "$W/clip2.out" "$W/clip2.time"
echo "end=$(date -u +%FT%TZ)"
