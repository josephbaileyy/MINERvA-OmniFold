#!/bin/bash
# 1B A2.1, the large-sample calibration's second rerun, at the final code for c2check (the director's ruling (a),
# item 4, and ruling (A), 2026-11-05): the same job script (sbatch-calibrate.sh a12799a4) and seeds as job 60783756,
# at M = 22eda9f4. There fd_1b_mc.py (062628b6) differs from 8a9b8db9 only in check_clip_gate (the gate-sample and
# calibration-code checks), which the calibration does not call. fd_1b_c2.py (f23696ff) differs in multiplicative
# (hoisted, bitwise equal), c2_truth, c2check_main and main's parser (the c2probe and c2check-merge subcommands), with
# new functions, none of which calibrate_main's call graph reaches; and in calibrate_main itself, whose code_sha256 is
# now gate_code_digests() (the same five files by the same expression; the audit's note). compare_calibN.py then holds
# the record to d4a4739e under the pre-declared exclusions, with --expect-code-sha256 fd_1b_mc.py=062628b6...
# fd_1b_c2.py=f23696ff.... c2check at 22eda9f4 refuses any calibration whose code_sha256 is not its own, so only this
# run's record can feed it.
# As connect-calibrate.sh otherwise: the m3246 balance against the cap (stop if the cap is above half of what
# remains), a fresh clone at M in a new pscratch directory, the bound blobs, one CPU node, QOS regular, --time
# 1:30:00 (cap 1.5 node-h; 0.72 and 0.76 measured, jobs 60783756 and 60805733). The time limit is evidenced from scontrol at submission (the job script's
# time_limit_s reads a variable Slurm does not set; left as it is, so the job stays the same).
# Nothing to CFS; writes only under $W. Not under set -u. Run detached on the login node (setsid nohup).
M=22eda9f424918e96e28984fa3152e42a803a5635
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-calibN-rerun2-20261105; DD=$W/deploy
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
f23696ffd89bae28d0aee12d5b21129bcb807e14a93f2f64e0fa8ca19061c6d5  nd-unfolding/fd_1b_c2.py
062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67  nd-unfolding/fd_1b_mc.py
a12799a450092c5f1d483f09b327bcbfcde84ca468bf44b6372a97f472b17eaa  $S/sbatch-calibrate.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 -t 01:30:00 -J fd1b_c2calN -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-calibrate.sh" "$DD" "$M" "$W") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=01:30:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 01:30:00: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
