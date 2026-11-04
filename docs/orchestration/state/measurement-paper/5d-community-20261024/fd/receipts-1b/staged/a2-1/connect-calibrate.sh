#!/bin/bash
# 1B A2.1, the calibration's submission (the director's R2 and Q2): on the login node, the m3246 balance against the
# job's cap (stop if the cap is above half of what remains), a fresh clone at M in a new pscratch directory, the
# bound blobs, then one CPU node, QOS regular, --time 4:00:00 (2x the 2 h estimate), the job sbatch-calibrate.sh.
# Nothing to CFS; writes only under $W. Not under set -u. Run detached on the login node (setsid nohup).
M=02e71a0bf68f6a232df70fa7b9182097ad54c22d
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-calib-20261104; DD=$W/deploy
S=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1
CAP_NODE_H=4.0
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-calibrate.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
[ "$(squeue --me -h -o %j | grep -c '^fd1b_c2')" = "0" ] || stop "an fd1b_c2 job is queued"
echo "== iris"; iris 2>&1 | head -2; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP_NODE_H"
awk -v b=$bal -v c=$CAP_NODE_H 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP_NODE_H is above half the balance $bal: to Joseph"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cat > "$W/bound.sha256" <<SUMS
c3c346454928290038585cf1f682209808258b7e06869848d750ee284c821d1d  nd-unfolding/fd_1b_c2.py
05150fb49c446ccaac70eebee22edc6214bfc9af1ebdb1a7dc72bedde0092a8b  nd-unfolding/fd_1b_mc.py
1e4bc66b7ae87d9d7f2c2d44af7b4ba31f58eb9b412f912a784d31a398cfeb89  $S/sbatch-calibrate.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
sbatch -A m3246 -q regular -C cpu -N 1 -t 04:00:00 -J fd1b_c2cal -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-calibrate.sh" "$DD" "$M" "$W" || stop sbatch
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
