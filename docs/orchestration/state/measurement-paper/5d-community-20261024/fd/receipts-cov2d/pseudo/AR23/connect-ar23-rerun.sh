#!/bin/bash
# COV2D connect AR23-RERUN: A2's sequence, stage 2 (COV2D-BINDING-2.md, addendum A2): AR23's pseudo-data job rerun into
# $O/pseudo/AR23-a2 at 04:00:00, after stage 1's PASS receipt (the A2 cluster test run) is on main. The deploy made by
# stage 1 is reused: it must be a clean checkout at M, plain and --ignored. Records sacct as the gate reads it, then
# submits through the bound script alone: cov2d_submit.sh <deploy> M AR23 pseudo (clean deploy at M; fetch; binding
# 2's A2 M line on origin/main; the tables compared; order(), which admits binding 2's pilot record through
# PRIOR_RECORDS; the gate; sbatch cov2d_pseudo.sbatch --time from PSEUDO_LIMITS). Nothing else is submitted. Any
# refusal stops here. This log is fetched for the receipt, then it and this script are removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-ar23b.sh >/dev/null 2>&1 </dev/null &
M=a60547692df5f963e428cdfe4661fc51ab785b7b
C=/pscratch/sd/j/josephrb/cov2d-deploy-a6054769
O=/pscratch/sd/j/josephrb/cov2d-run-20261104
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d
LOG=/dev/shm/josephrb-cov2d-ar23b.log
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un)"
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "STOP the deploy is not at M"; echo DONE; exit 2; }
echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -z "$(git -C "$C" status --porcelain --ignored)" ] || { git -C "$C" status --porcelain --ignored | head; echo "STOP the deploy is not clean (--ignored)"; echo DONE; exit 2; }
[ -e "$O/pseudo/AR23-a2" ] && { echo "STOP $O/pseudo/AR23-a2 exists"; echo DONE; exit 2; }
git -C "$C" fetch -q origin main || { echo "STOP fetch"; echo DONE; exit 2; }
echo "origin/main=$(git -C "$C" rev-parse origin/main)"
git -C "$C" show "origin/main:$R/a2/cluster_tests/CLUSTER-TESTS.md" > /dev/null 2>&1 \
    || { echo "STOP stage 1's receipt is not on main"; echo DONE; exit 2; }
for r in pseudo/G18/pseudo_b.json pilot/pilot_readout.json a2/cluster_tests/CLUSTER-TESTS.md; do
    echo "record $r: $(git -C "$C" show "origin/main:$R/$r" | sha256sum | cut -c1-64)"
done
echo "sacct (as the gate reads it):"
sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes | grep '|cov2d-' || echo "(no cov2d-* jobs)"
bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" AR23 pseudo; echo "submit rc=$?"
echo "plain-after=$(git -C "$C" status --porcelain | wc -l) ignored-after=$(git -C "$C" status --porcelain --ignored | wc -l)"
tail -3 "$O/submissions.log" 2>&1
for f in $(ls -t "$O"/logs/gate-pseudo-*.json 2>/dev/null | head -2); do echo "$f: $(cat "$f")"; done
id=$(awk -v m="M=$M" '$2 == m && /job=pseudo_AR23/ {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" 2>/dev/null | tail -1)
[ -n "$id" ] && scontrol show job "$id" | grep -E "JobId|JobName|JobState|QOS|TimeLimit|NumNodes|Partition|Account"
echo "end=$(date -u +%FT%TZ)"; echo DONE
