#!/bin/bash
# COV2D connect PILOT: binding 2 ruling 2.2, the pilot (eight runs in three lanes on one node, limit 01:41:00, 1.68
# node-h), after G18's pseudo-data PASS record is on main. The deploy made by the G18 connect is reused: it must still
# be a clean checkout at M, plain and --ignored. Records the user's cov2d-* jobs as the gate will see them, then
# submits through the bound script alone: cov2d_submit.sh <deploy> M pilot pilot (clean deploy at M; fetch; binding
# 2's M line on origin/main; the tables compared; order(), which needs origin/main's G18 pseudo_b.json naming M; the
# gate; sbatch cov2d_job.sbatch with JOB=pilot, DATA_TRUTH=G18). Nothing else is submitted. Any refusal stops here and
# goes to the director. The readout (cov2d_pilot.py) is a later connect. This log is fetched for the receipt, then it
# and this script are removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-pilot.sh >/dev/null 2>&1 </dev/null &
M=cb31611ca8b96ed2d1eeb809fda7236e56645863
C=/pscratch/sd/j/josephrb/cov2d-deploy-cb31611c
O=/pscratch/sd/j/josephrb/cov2d-run-20261104
REC=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/pseudo/G18/pseudo_b.json
LOG=/dev/shm/josephrb-cov2d-pilot.log
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un)"
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "STOP the deploy is not at M"; echo DONE; exit 2; }
echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -z "$(git -C "$C" status --porcelain --ignored)" ] || { git -C "$C" status --porcelain --ignored | head; echo "STOP the deploy is not clean (--ignored)"; echo DONE; exit 2; }
for l in P912_L_BeamAngleX_0 L_G18_BeamAngleX_0 P912_U_MaRES_0 P2b_ER X_G18 T_G18_5720000 B_G18_001 U_G18_Flux_0; do
    [ -e "$O/out/$l" ] && { echo "STOP $O/out/$l exists"; echo DONE; exit 2; }
done
git -C "$C" fetch -q origin main && echo "origin/main=$(git -C "$C" rev-parse origin/main) G18 record: $(git -C "$C" show "origin/main:$REC" | sha256sum | cut -c1-64)"
echo "sacct (as the gate reads it):"
sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes | grep '|cov2d-' || echo "(no cov2d-* jobs)"
bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" pilot pilot; echo "submit rc=$?"
echo "plain-after=$(git -C "$C" status --porcelain | wc -l) ignored-after=$(git -C "$C" status --porcelain --ignored | wc -l)"
tail -3 "$O/submissions.log" 2>&1
ls -t "$O"/logs/gate-pilot-*.json 2>/dev/null | head -2 | xargs -r cat
id=$(awk '/job=pilot / {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" 2>/dev/null | tail -1)
[ -n "$id" ] && scontrol show job "$id" | grep -E "JobId|JobName|JobState|QOS|TimeLimit|NumNodes|Partition|Account"
echo "end=$(date -u +%FT%TZ)"; echo DONE
