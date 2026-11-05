#!/bin/bash
# COV2D connect G18-PSEUDO: binding 2 ruling 2.1, the G18 pseudo-data job (one node, 03:00:00, 3.0 node-h of the
# 165.8 cap). Makes the deploy, a fresh clean clone of GitHub at M on pscratch (compute nodes cannot see /dev/shm),
# records the user's cov2d-* jobs as the gate will see them, then submits through the bound script alone:
# cov2d_submit.sh <deploy> M G18 pseudo (clean deploy at M; fetch; binding 2's M line on origin/main; the tables
# written once and compared after; order(); the gate; sbatch cov2d_pseudo.sbatch). Nothing else is submitted. Any
# refusal stops here and goes to the director. The job's own output lands in $O (cov2d_env.sh); this log and the
# deploy's porcelain are fetched for the receipt, then this script is removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-g18.sh >/dev/null 2>&1 </dev/null &
M=cb31611ca8b96ed2d1eeb809fda7236e56645863
C=/pscratch/sd/j/josephrb/cov2d-deploy-cb31611c
O=/pscratch/sd/j/josephrb/cov2d-run-20261104
LOG=/dev/shm/josephrb-cov2d-g18.log
[ -e "$LOG" ] && { echo "STOP $LOG exists"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ user=$(id -un)"
[ -e "$C" ] && { echo "STOP the deploy $C exists: a deploy is made once"; echo DONE; exit 2; }
[ -e "$O/pseudo/G18" ] && { echo "STOP $O/pseudo/G18 exists"; echo DONE; exit 2; }
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$C" \
    && git -C "$C" -c advice.detachedHead=false checkout --quiet --detach "$M" || { echo "STOP clone"; echo DONE; exit 2; }
echo "deploy=$C head=$(git -C "$C" rev-parse HEAD) porcelain=$(git -C "$C" status --porcelain | wc -l)"
git -C "$C" ls-tree HEAD 2d-unfolding/cov2d/jobs/cov2d_submit.sh 2d-unfolding/cov2d/jobs/cov2d_pseudo.sbatch \
    2d-unfolding/cov2d/jobs/cov2d_env.sh 2d-unfolding/cov2d/jobs/cov2d_jobs.py 2d-unfolding/cov2d/cov2d_pseudo.py \
    2d-unfolding/cov2d/cov2d_pseudo_write.py
echo "O: $(ls -d "$O" 2>&1) $(ls "$O" 2>&1 | tr '\n' ' ')"
echo "sacct (as the gate reads it):"
sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes | grep '|cov2d-' || echo "(no cov2d-* jobs)"
bash "$C/2d-unfolding/cov2d/jobs/cov2d_submit.sh" "$C" "$M" G18 pseudo; echo "submit rc=$?"
echo "porcelain-after=$(git -C "$C" status --porcelain | wc -l)"
tail -3 "$O/submissions.log" 2>&1
id=$(awk '/job=pseudo_G18/ {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" 2>/dev/null | tail -1)
[ -n "$id" ] && scontrol show job "$id" | grep -E "JobId|JobName|JobState|QOS|TimeLimit|NumNodes|Partition|Account"
echo "end=$(date -u +%FT%TZ)"; echo DONE
