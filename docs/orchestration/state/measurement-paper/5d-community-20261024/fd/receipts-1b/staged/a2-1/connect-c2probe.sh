#!/bin/bash
# 1B A2.1, c2check's timing probe (the director's ruling (a), item 3, and ruling (A), 2026-11-05), after the
# calibration's second rerun COMPLETES and its compare_calibN passes: sbatch-c2probe.sh (40b68ef9) at M = bf36901f on
# one exclusive CPU node with 64 BLAS/OMP threads. It times each of c2check's one-off steps (prepare(rows=True),
# c2_inputs, the terms, the (vi) row match, the draws for the 300 and the 3,000-draw gate sample) and 4 blocks of
# G18's gate sample through the real c2_truth, records |Z| per array and the peak RSS, and projects a one-truth
# c2check job as the one-off steps + 165 x the mean block (the first block set aside). A timing record only;
# nothing in it is a gate. As connect-calibrate-rerun2.sh otherwise: the m3246 balance against the cap (stop if the
# cap is above half of what remains), a fresh clone at M in a new pscratch directory, the bound blobs, one CPU node,
# QOS regular, --time 1:30:00 (cap 1.5 node-h). Nothing to CFS; writes only under $W. Not under set -u. Run detached
# on the login node (setsid nohup).
M=bf36901f957c36f37b4cb5fe6c7b6cd33f190ca7
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-c2probe-20261105; DD=$W/deploy
S=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1
CAP_NODE_H=1.5
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-c2probe.log" 2>&1
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
522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f  nd-unfolding/fd_1b_c2.py
062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67  nd-unfolding/fd_1b_mc.py
40b68ef937a43dd248f15df1b4efc8be532451fc9e022fdee3341bbbebb54158  $S/sbatch-c2probe.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive -t 01:30:00 -J fd1b_c2probe -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-c2probe.sh" "$DD" "$M" "$W") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=01:30:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 01:30:00: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
