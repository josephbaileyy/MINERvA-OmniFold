#!/bin/bash
# 1B A2.1, the large-sample calibration's second rerun, at the ruling-(a) code (the director's ruling (a), item 4,
# 2026-11-04): the same job script (sbatch-calibrate.sh a12799a4) and seeds as job 60783756, at M = a2560cc3. There
# fd_1b_mc.py (0b4c61de) differs from 8a9b8db9 only in check_clip_gate's gate-sample check (H2), which the calibration
# does not call. fd_1b_c2.py (af69f632) differs in multiplicative (hoisted, bitwise equal), c2_truth, c2check_main and
# main's parser (the c2probe and c2check-merge subcommands), with new functions; calibrate_main reaches none of them
# but main. compare_calibN.py then holds the record to d4a4739e under the pre-declared exclusions, with
# --expect-code-sha256 fd_1b_mc.py=0b4c61de... fd_1b_c2.py=af69f632....
# As connect-calibrate.sh otherwise: the m3246 balance against the cap (stop if the cap is above half of what
# remains), a fresh clone at M in a new pscratch directory, the bound blobs, one CPU node, QOS regular, --time
# 1:30:00 (cap 1.5 node-h; 0.72 and 0.76 measured, jobs 60783756 and 60805733). The time limit is evidenced from scontrol at submission (the job script's
# time_limit_s reads a variable Slurm does not set; left as it is, so the job stays the same).
# Nothing to CFS; writes only under $W. Not under set -u. Run detached on the login node (setsid nohup).
M=a2560cc3ed78efc632307057ffbb58cdfd752875
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-calibN-rerun2-20261104; DD=$W/deploy
S=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1
CAP_NODE_H=1.5
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
af69f632610e23b6e25c7ceea7f8e95e58049acb18e53ed061ced025a9061675  nd-unfolding/fd_1b_c2.py
0b4c61de5e8ad0c809e385679c7e287b192339962ae55a069253b6e665e51d98  nd-unfolding/fd_1b_mc.py
a12799a450092c5f1d483f09b327bcbfcde84ca468bf44b6372a97f472b17eaa  $S/sbatch-calibrate.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 -t 01:30:00 -J fd1b_c2calN -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-calibrate.sh" "$DD" "$M" "$W") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
