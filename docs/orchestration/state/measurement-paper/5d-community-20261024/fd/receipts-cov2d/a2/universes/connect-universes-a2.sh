#!/bin/bash
# COV2D connect UNIVERSES-A2: A2's sequence, stage 3 (COV2D-BINDING-2.md, addendum A2, revision 2): the eight universe
# jobs, the $UNI readers: G18_Ua..Ud and AR23_Ua..Ud, after stage 2's PASS record (AR23's pseudo_b.json, carrying M)
# is on main. The deploy made by stage 1 is reused: it must be a clean checkout at M, plain and --ignored. The AR23
# record on main must be byte for byte the job's file (sha256 d50ef13a...). Refuses if any universe job is already in
# submissions.log at M. Then the bound script alone, once per truth: cov2d_submit.sh <deploy> M G18 G18_Ua..Ud, and only
# if that succeeded, the same for AR23. For each job it checks the clean deploy at M, fetches, reads binding 2's A2 M
# line on origin/main, compares the tables, runs order() and the gate, then sbatch. Nothing else is submitted; any
# refusal stops the connect. This log is fetched for the receipt, then it and this script are removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-uni.sh >/dev/null 2>&1 </dev/null &
M=a60547692df5f963e428cdfe4661fc51ab785b7b
C=/pscratch/sd/j/josephrb/cov2d-deploy-a6054769
O=/pscratch/sd/j/josephrb/cov2d-run-20261104
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d
AR23_B=d50ef13af16adf26e25794ebdda41b23d6cfd7ecec2332173c237a340e682bb5
LOG=/dev/shm/josephrb-cov2d-uni.log
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un)"
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "STOP the deploy is not at M"; echo DONE; exit 2; }
echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -z "$(git -C "$C" status --porcelain --ignored)" ] || { git -C "$C" status --porcelain --ignored | head; echo "STOP the deploy is not clean (--ignored)"; echo DONE; exit 2; }
grep -E "M=$M job=(G18|AR23)_U" "$O/submissions.log" && { echo "STOP a universe job is already submitted at M"; echo DONE; exit 2; }
git -C "$C" fetch -q origin main || { echo "STOP fetch"; echo DONE; exit 2; }
echo "origin/main=$(git -C "$C" rev-parse origin/main)"
got=$(git -C "$C" show "origin/main:$R/pseudo/AR23/pseudo_b.json" | sha256sum | cut -c1-64)
[ "$got" = "$AR23_B" ] || { echo "STOP stage 2's record on main is $got, not $AR23_B"; echo DONE; exit 2; }
for r in pseudo/G18/pseudo_b.json pseudo/AR23/pseudo_b.json pilot/pilot_readout.json; do
    echo "record $r: $(git -C "$C" show "origin/main:$R/$r" | sha256sum | cut -c1-64)"
done
echo "sacct (as the gate reads it):"
sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes | grep '|cov2d-' || echo "(no cov2d-* jobs)"
bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" G18 G18_Ua G18_Ub G18_Uc G18_Ud; rc=$?; echo "submit G18 rc=$rc"
if [ "$rc" = 0 ]; then
    bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" AR23 AR23_Ua AR23_Ub AR23_Uc AR23_Ud; echo "submit AR23 rc=$?"
fi
echo "plain-after=$(git -C "$C" status --porcelain | wc -l) ignored-after=$(git -C "$C" status --porcelain --ignored | wc -l)"
tail -9 "$O/submissions.log"
for f in $(ls -tr "$O"/logs/gate-*_U?-*.json 2>/dev/null); do echo "$f: $(cat "$f")"; done
for id in $(awk -v m="M=$M" '$2 == m && /job=(G18|AR23)_U/ {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log"); do
    scontrol show job "$id" | grep -E "JobId|QOS|TimeLimit|NumNodes|JobState" | tr -s ' \n' ' '; echo
done
echo "end=$(date -u +%FT%TZ)"; echo DONE
