#!/bin/bash
# COV2D connect X1: readout (i), the cross terms (COV2D-AMENDMENT-1.md section 4; COV2D-DECLARATION.md section 6), on a
# login node at nice 19, 0 node-h; the director's ruling 2 of 2026-11-07 (stage 5: the bound CLI may run at M now).
# A fresh clone at M in a new pscratch directory, the bound files checked, then cov2d_readouts.py cross-terms. It reads
# $UNI, the constraint file and the two tunes' ratio files through O_NOATIME (the CLI records their atimes); their
# stat is recorded before and after here (the director's ruling). Reads no bulk output and no toy error.
# Writes only under $W. Run detached: setsid nohup bash connect-x1.sh >/dev/null 2>&1 </dev/null &
set -o pipefail
M=a60547692df5f963e428cdfe4661fc51ab785b7b
P=/pscratch/sd/j/josephrb; W=$P/cov2d-crossterms-20261107; DD=$W/deploy
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" || exit 2
exec >> "$W/connect-x1.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ ppid=$PPID"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
echo "76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed  2d-unfolding/cov2d/cov2d.py
1bc3c8b13029b448a2fb05f379c0d5f2d28ff37445ba5899936958442415c56b  2d-unfolding/cov2d/cov2d_readouts.py
c085b51f46afe3675077756aac982d5a7ebc87a5801dd7cbde79dd0f867bd7de  2d-unfolding/cov2d/cov2d_receipt.py
05aff0d090404a9c2e9c5924f130e911f3e6548da481cfe5af7d46d3a03d297d  2d-unfolding/cov2d/cov2d_pseudo.py
b4bea132c0ac759e6b178e3a4ed3ac835053e548ddc5a06774a3ad6eb08b6dc8  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe.py
869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08  nd-unfolding/fd_1b_toys.py" > "$W/bound.sha256"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
READS="/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
/pscratch/sd/j/josephrb/fd-f1-20261027/f1b3/prep/bridged/genie_v3_g18.json
/pscratch/sd/j/josephrb/fd-f1-20261027/f1b3/prep/bridged/genie_v3_ar23.json"
stat -c '%n size=%s mtime=%y atime=%x inode=%i' $READS > "$W/stat_before.txt" || stop "stat before"
cat "$W/stat_before.txt"
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 "$PY" -B "$DD/2d-unfolding/cov2d/cov2d_readouts.py" cross-terms --out "$W/crossterms.json" > "$W/crossterms.out" 2> "$W/crossterms.time"
rc=$?
echo "cross-terms rc=$rc"
cat "$W/crossterms.out"
grep -E "Elapsed|Maximum resident|File system inputs|Percent of CPU" "$W/crossterms.time"
stat -c '%n size=%s mtime=%y atime=%x inode=%i' $READS > "$W/stat_after.txt" || stop "stat after"
cat "$W/stat_after.txt"
cmp "$W/stat_before.txt" "$W/stat_after.txt" && echo "STAT_UNCHANGED" || echo "STAT_CHANGED"
n=$(git -C "$DD" status --porcelain --ignored | wc -l); echo "deploy porcelain_ignored_after_lines=$n"
sha256sum "$W/crossterms.json" "$W/crossterms.npz" "$W/crossterms.out" "$W/crossterms.time"
echo "end=$(date -u +%FT%TZ)"
