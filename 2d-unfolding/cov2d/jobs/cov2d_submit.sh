#!/bin/bash
# COV2D: submit named jobs once each, only after binding 2 names the deploy's commit. The director is told first.
#     bash cov2d_submit.sh <deploy> <M> <truth> <job> [<job> ...]     (jobs as in jobs_<truth>.tsv, or pseudo)
# Each submission passes the charge gate (cov2d_jobs.py gate): every ended cov2d-* attempt's charge, plus every
# unfinished attempt's limit, plus this job's limit, at most the cap of 165.8 node-h (COV2D-BINDING-1.md ruling 3).
set -eo pipefail
C=$(cd "$1" && pwd); M=$2; TRUTH=$3; shift 3
[ $# -gt 0 ] || { echo "name at least one job"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $M"; exit 2; }
BIND=$C/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md
[ -f "$BIND" ] && grep -q "$M" "$BIND" || { echo "binding 2 does not name $M"; exit 2; }
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"
mkdir -p "$O/logs" "$O/tables"
[ -s "$O/tables/runs_$TRUTH.tsv" ] || "$PY310" -B "$CJ" tables --truth "$TRUTH" --out "$O/tables"
LOG=$O/submissions.log
for job in "$@"; do
    psv=$O/logs/gate-$job-$(date -u +%Y%m%dT%H%M%SZ).psv
    names=$( { awk -F'\t' 'NR > 1 {print "cov2d-" $1}' "$O"/tables/jobs_*.tsv; echo cov2d-pseudo_G18; echo cov2d-pseudo_AR23; } | paste -sd, -)
    sacct -X -n -P -S 2026-11-04 --name="$names" -o JobID,JobName,State,ElapsedRaw,NNodes > "$psv"
    want=$job; [ "$job" = pseudo ] && want=pseudo_$TRUTH
    "$PY310" -B "$CJ" gate --sacct "$psv" --tables "$O/tables" --want "$want" > "$psv.gate.json" \
        || { cat "$psv.gate.json"; echo "gate refused $want"; exit 3; }
    if [ "$job" = pseudo ]; then
        id=$(sbatch --parsable --job-name="cov2d-pseudo_$TRUTH" --export=ALL,C=$C,M=$M,TRUTH=$TRUTH \
            "$C/2d-unfolding/cov2d/jobs/cov2d_pseudo.sbatch"); lim=03:00:00
    else
        lim=$(awk -F'\t' -v j="$job" 'NR > 1 && $1 == j {print $7}' "$O/tables/jobs_$TRUTH.tsv")
        [ -n "$lim" ] || { echo "$job is not a jobs_$TRUTH.tsv row"; exit 2; }
        id=$(sbatch --parsable --job-name="cov2d-$job" --time="$lim" --export=ALL,C=$C,M=$M,TRUTH=$TRUTH,JOB=$job \
            "$C/2d-unfolding/cov2d/jobs/cov2d_job.sbatch")
    fi
    echo "$(date -u +%FT%TZ) M=$M job=$want id=$id limit=$lim" | tee -a "$LOG"
done
