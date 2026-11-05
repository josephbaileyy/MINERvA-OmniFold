#!/bin/bash
# COV2D: submit named jobs once each, only after binding 2, on origin/main, names the deploy's commit M. The director
# is told first.
#     bash cov2d_submit.sh <deploy> <M> <truth> <job> [<job> ...]     (jobs as in jobs_<truth>.tsv, or pseudo)
# Each submission passes the charge gate (cov2d_jobs.py gate): every ended cov2d-* attempt's charge, plus every
# unfinished attempt's limit, plus this job's limit, at most the cap of 165.8 node-h (COV2D-BINDING-1.md ruling 3).
set -eo pipefail
C=$(cd "$1" && pwd); M=$2; TRUTH=$3; shift 3
[ $# -gt 0 ] || { echo "name at least one job"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $M"; exit 2; }
# Binding 2 and the PASS records are commits on main after M, so both are read from origin/main, never from the
# deploy's own tree: a commit cannot hold a file that names its own hash (the director's F3). The deploy stays at M.
git -C "$C" fetch -q origin main || { echo "the fetch of origin main failed: binding 2 and the records are unread"; exit 2; }
BIND=docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md
bind=$(git -C "$C" show "origin/main:$BIND") || { echo "binding 2 is not on origin/main"; exit 2; }
grep -qF "$M" <<<"$bind" || { echo "binding 2 on origin/main does not name $M"; exit 2; }
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"
mkdir -p "$O/logs" "$O/tables"
# the tables at this deploy: written once, and every later submission regenerates and compares them (J5)
chk=$(mktemp -d)
for t in G18 AR23 pilot; do
    "$PY310" -B "$CJ" tables --truth "$t" --out "$chk" > /dev/null
    for f in runs jobs; do
        if [ -s "$O/tables/${f}_$t.tsv" ]; then cmp -s "$chk/${f}_$t.tsv" "$O/tables/${f}_$t.tsv" \
            || { echo "$O/tables/${f}_$t.tsv is not this deploy's"; exit 2; }
        else cp "$chk/${f}_$t.tsv" "$O/tables/"; fi
    done
done
rm -rf "$chk"
LOG=$O/submissions.log
for job in "$@"; do
    psv=$O/logs/gate-$job-$(date -u +%Y%m%dT%H%M%SZ).psv
    # every job of mine since the campaign began; the gate prices each cov2d-* one and refuses any it cannot (J1)
    sacct -X -n -P -S 2026-11-04 -u "$(id -un)" -o JobID,JobName,State,ElapsedRaw,NNodes > "$psv"
    want=$job; [ "$job" = pseudo ] && want=pseudo_$TRUTH
    "$PY310" -B "$CJ" order --job "$job" --truth "$TRUTH" --M "$M" --deploy "$C" --submissions "$LOG" \
        > "$psv.order.json" || { cat "$psv.order.json"; echo "the order refuses $want"; exit 3; }
    "$PY310" -B "$CJ" gate --sacct "$psv" --tables "$O/tables" --want "$want" > "$psv.gate.json" \
        || { cat "$psv.gate.json"; echo "gate refused $want"; exit 3; }
    if [ "$job" = pseudo ]; then
        id=$(sbatch --parsable --job-name="cov2d-pseudo_$TRUTH" --export=ALL,C=$C,M=$M,TRUTH=$TRUTH \
            "$C/2d-unfolding/cov2d/jobs/cov2d_pseudo.sbatch"); lim=03:00:00
    else
        lim=$(awk -F'\t' -v j="$job" 'NR > 1 && $1 == j {print $7}' "$O/tables/jobs_$TRUTH.tsv")
        [ -n "$lim" ] || { echo "$job is not a jobs_$TRUTH.tsv row"; exit 2; }
        dt=$TRUTH; [ "$TRUTH" = pilot ] && dt=G18
        id=$(sbatch --parsable --job-name="cov2d-$job" --time="$lim" --export=ALL,C=$C,M=$M,TRUTH=$TRUTH,DATA_TRUTH=$dt,JOB=$job \
            "$C/2d-unfolding/cov2d/jobs/cov2d_job.sbatch")
    fi
    echo "$(date -u +%FT%TZ) M=$M job=$want id=$id limit=$lim" | tee -a "$LOG"
done
