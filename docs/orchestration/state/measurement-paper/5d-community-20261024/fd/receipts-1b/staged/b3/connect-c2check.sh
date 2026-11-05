#!/bin/bash
# 1B binding 3, step 1: c2check at N for ONE truth (argument 1: g18 or ar23), the director's ruling (a): one truth per
# job, merged after (c2check-merge). sbatch-c2check.sh (2335ab4d) at M = a47cfb4b, where fd_1b_c2 (522d7edd) and
# fd_1b_mc (062628b6) are bf36901f's, the code rerun2's calibration (job 60857361) was made by, so c2check accepts it.
# c2check runs at the calibration's 1 BLAS thread (asserted in the job script) and under 1B's guarded launcher
# (fd_1b_noatime_guard.py ee20534c, --declared). Priced from the 1-thread probe (job 60870880): 17,708 s (4.92 h)
# projected per truth; --time 7:30:00 (cap 7.5 node-h, 1.5x the measurement). An out-of-band stat snapshot of every
# declared input is written to $W before submission (atime-pre.tsv); the matching one after the job is a separate step.
# Otherwise as connect-c2probe-1t.sh: the m3246 balance against the cap (stop if the cap is above half of what
# remains), a fresh clone at M in a new pscratch directory, the bound blobs, one exclusive CPU node, QOS regular.
# Refuses if this truth's c2check job is already queued; the other truth's may run alongside. Nothing to CFS; writes only
# under $W. Not under set -u. Run detached on the login node (setsid nohup).
T=$1
case "$T" in g18|ar23) ;; *) echo "STOP truth '$T' is not g18 or ar23"; exit 2 ;; esac
M=a47cfb4b9410cbf0cc8e34bee98e73c3e110f171
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-b3-c2check-$T; DD=$W/deploy
B=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/b3
CAP_NODE_H=7.5
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-c2check.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
[ "$(squeue --me -h -o %j | grep -cx "fd1b_c2chk_$T")" = "0" ] || stop "a c2check job for $T is queued"
echo "cov2d jobs at launch: [$(squeue --me -h -o "%i %j %T" | grep -i cov2d | tr '\n' ';')]"
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
2335ab4d8b9f9a8eee19abe6cd44be7834c7e126d8ddda0f161aaa40281321a9  $B/sbatch-c2check.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
ND=$P/MINERvA-OmniFold/nd-unfolding
find $ND/of_inputs_5d.npz $P/s5c-20260924/runs/p2/bkg_dump.npz $ND/bank_sweep_5d_bkgaware $P/s5p-20260926/bank_detector \
  $P/fd-1b-20261030/pins.json $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  $P/fd-1b-staged-20261102/stage1/in/flux_universes.npz $P/fd-1b-inv-20261101/i0/in $P/fd-f1-20261027/f1b3/prep \
  $P/fd-1b-a21-cvdenom2-20261103/cvdenom.npy -type f -printf "%A@\t%p\n" | sort -k2 > "$W/atime-pre.tsv" || stop "atime snapshot"
echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive -t 07:30:00 -J "fd1b_c2chk_$T" -o "$W/logs/%x_%j.out" \
  "$DD/$B/sbatch-c2check.sh" "$DD" "$M" "$W" "$T") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=07:30:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 07:30:00: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_c2chk || true
echo "end=$(date -u +%FT%TZ)"
