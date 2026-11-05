#!/bin/bash
# 1B A2.1, c2check's timing probe (the director's ruling (a), item 3, 2026-11-04), after the calibration's second
# rerun: sbatch-c2probe.sh (3424680a) at M = a2560cc3 on one exclusive CPU node with 64 BLAS/OMP threads. It times
# prepare, the multiplicative terms and 4 blocks of G18's gate sample through the real c2_truth, and projects a
# one-truth c2check job as prepare + terms + 165 x the mean block (the first block set aside). A timing record only;
# nothing in it is a gate. As connect-calibrate-rerun2.sh otherwise: the m3246 balance against the cap (stop if the
# cap is above half of what remains), a fresh clone at M in a new pscratch directory, the bound blobs, one CPU node,
# QOS regular, --time 1:30:00 (cap 1.5 node-h). Nothing to CFS; writes only under $W. Not under set -u. Run detached
# on the login node (setsid nohup).
M=a2560cc3ed78efc632307057ffbb58cdfd752875
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-c2probe-20261104; DD=$W/deploy
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
af69f632610e23b6e25c7ceea7f8e95e58049acb18e53ed061ced025a9061675  nd-unfolding/fd_1b_c2.py
0b4c61de5e8ad0c809e385679c7e287b192339962ae55a069253b6e665e51d98  nd-unfolding/fd_1b_mc.py
3424680aea866b93625647895930ce58e51dca48abd913f5f9218c5b6d7229f1  $S/sbatch-c2probe.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive -t 01:30:00 -J fd1b_c2probe -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-c2probe.sh" "$DD" "$M" "$W") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
