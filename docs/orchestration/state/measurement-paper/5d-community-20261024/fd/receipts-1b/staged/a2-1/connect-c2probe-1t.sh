#!/bin/bash
# 1B A2.1, c2check's timing probe at 1 BLAS thread (the director's ruling (a), 2026-11-05: c2check runs at the
# calibration's 1 thread, so its bitwise single-universe U x_T check holds; it is priced from this measurement).
# sbatch-c2probe.sh (2d6fa71a) at M = a47cfb4b, where fd_1b_c2 (522d7edd) and fd_1b_mc (062628b6) are bf36901f's, so it
# times exactly the code c2check runs; THREADS=1 is its fourth argument. It runs under 1B's guarded launcher
# (fd_1b_noatime_guard.py ee20534c, --declared), as c2check will: the guard's first live run with the real O_NOATIME.
# As connect-c2probe.sh otherwise, with an out-of-band stat snapshot of every declared input taken at launch by the
# caller: the m3246 balance against the cap (stop if the cap is above half of what remains), a fresh clone at M in a new
# pscratch directory, the bound blobs, one exclusive CPU node, QOS regular, --time 1:30:00 (cap 1.5 node-h; the director: a timeout would lose the record). Nothing to
# CFS; writes only under $W. Not under set -u. Run detached on the login node (setsid nohup).
M=a47cfb4b9410cbf0cc8e34bee98e73c3e110f171
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-c2probe-1t-20261105; DD=$W/deploy
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
ee20534c20504aa1335bad4e75be067c0465c7faaa60d2a14a47abb81e22f60c  nd-unfolding/fd_1b_noatime_guard.py
2d6fa71ad91826cd0224ed6417b313e2829e4724eb6a958aaf09c6b5a570d5e3  $S/sbatch-c2probe.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive -t 01:30:00 -J fd1b_c2probe -o "$W/logs/%x_%j.out" \
  "$DD/$S/sbatch-c2probe.sh" "$DD" "$M" "$W" 1) || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=01:30:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 01:30:00: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2 || true
echo "end=$(date -u +%FT%TZ)"
