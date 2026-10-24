#!/bin/bash
# RE-2 part B: submit named jobs, once each, only after the director's BINDING record and the DTN preflight.
#     re2b_submit.sh <deploy> <declared sha> <job> [<job> ...]        (jobs as named in partb_jobs.tsv)
# Each job passes the charge gate (re2b_gate.py) first: the charge so far, plus every unfinished job's cap, plus its
# own cap, must be at most the grant's room. Each submission is logged before the next job is gated.
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2; shift 2
[ $# -gt 0 ] || { echo "name at least one job"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE2_SHA"; exit 2; }
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_env.sh"
[ -s "$STATS" ] && [ "$(grep -c . "$STATS")" = 12 ] || { echo "no complete DTN preflight record $STATS"; exit 5; }
LOG=$B/partb/submissions.log
mkdir -p "$O/logs"
for job in "$@"; do
    ids=$( { grep -o ' id=[0-9]*' "$LOG" 2>/dev/null || true; } | cut -d= -f2 | paste -sd, -)
    psv=$O/logs/gate-$job-$(date -u +%Y%m%dT%H%M%SZ).psv
    if [ -n "$ids" ]; then sacct -X -n -P -j "$ids" -o JobID,State,ElapsedRaw,AllocTRES > "$psv"; else : > "$psv"; fi
    python3 "$C/2d-unfolding/re2/re2b_gate.py" --jobs "$JOBS" \
        --j0-ledger "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/j0_readout/j0_ledger.tsv" \
        --submissions "$LOG" --sacct "$psv" --want "$job" > "$psv.gate.json" \
        || { cat "$psv.gate.json"; echo "gate refused $job"; exit 3; }
    lim=$(re2b_limit "$job")
    id=$(sbatch --parsable --job-name="re2b-$job" --time="$lim" --export=ALL,C=$C,RE2_SHA=$RE2_SHA,JOB=$job \
        "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_job.sbatch")
    echo "$(date -u +%FT%TZ) sha=$RE2_SHA job=$job id=$id limit=$lim" | tee -a "$LOG"
done
