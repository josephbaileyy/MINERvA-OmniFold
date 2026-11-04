#!/bin/bash
# 1B A2.1, the large-sample calibration's rerun at the final H1 code (the director's ruling of 2026-11-04): the same
# job script (sbatch-calibrate.sh a12799a4) and seeds as job 60783756, at M = 48ca04a1, where only fd_1b_mc.py's gate
# path differs (1046353e). compare_calibN.py then holds the record to d4a4739e under the pre-declared exclusions.
# As connect-calibrate.sh otherwise: the m3246 balance against the cap (stop if the cap is above half of what
# remains), a fresh clone at M in a new pscratch directory, the bound blobs, one CPU node, QOS regular, --time
# 1:30:00 (cap 1.5 node-h; 0.72 measured). The time limit is evidenced from scontrol at submission (the job script's
# time_limit_s reads a variable Slurm does not set; left as it is, so the job stays the same).
# Nothing to CFS; writes only under $W. Not under set -u. Run detached on the login node (setsid nohup).
M=48ca04a1355abe6e7ec294a91e59da8b809e83da
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-calibN-rerun-20261104; DD=$W/deploy
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
f19adbda6126d79d1f337755de873b530a76ebbcfd412ab60f85ab53cb33fe49  nd-unfolding/fd_1b_c2.py
1046353eb3e3c014b03c87400adc15b43d5ba9487a999b4b7f5622e4eb011ef2  nd-unfolding/fd_1b_mc.py
a12799a450092c5f1d483f09b327bcbfcde84ca468bf44b6372a97f472b17eaa  $S/sbatch-calibrate.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 -t 01:30:00 -J fd1b_c2calN -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-calibrate.sh" "$DD" "$M" "$W") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
