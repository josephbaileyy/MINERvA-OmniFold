#!/bin/bash
# RE-2 part B: submit named jobs, once each, only after the director's BINDING record and the DTN preflight.
#     bash re2b_submit.sh <deploy> <declared sha> <job> [<job> ...]        (jobs as named in partb_jobs.tsv)
# Each job passes the charge gate (re2b_gate.py) first: the charge of every ended attempt, plus every unfinished
# attempt's cap, plus its own cap, must be at most the grant's room. Attempts are read from sacct by job name
# (re2b-<job>, since 2026-10-24) and from the log, so an unlogged or duplicate submission still counts and still
# blocks a second one. The gate runs under the login node's system python3.
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2; shift 2
[ $# -gt 0 ] || { echo "name at least one job"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE2_SHA"; exit 2; }
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_env.sh"
[ -s "$STATS" ] && [ "$(grep -c . "$STATS")" = 12 ] || { echo "no complete DTN preflight record $STATS"; exit 5; }
LOG=$O/submissions.log
mkdir -p "$O/logs"
names=$(awk -F'\t' 'NR > 1 {printf "%sre2b-%s", (n++ ? "," : ""), $1}' "$JOBS")
for job in "$@"; do
    psv=$O/logs/gate-$job-$(date -u +%Y%m%dT%H%M%SZ).psv
    sacct -X -n -P -S 2026-10-24 --name="$names" -o JobID,JobName,State,ElapsedRaw,AllocTRES > "$psv"
    ids=$( { grep -o ' id=[0-9]*' "$LOG" 2>/dev/null || true; } | cut -d= -f2 | paste -sd, -)
    if [ -n "$ids" ]; then sacct -X -n -P -j "$ids" -o JobID,JobName,State,ElapsedRaw,AllocTRES >> "$psv"; fi
    /usr/bin/python3 "$C/2d-unfolding/re2/re2b_gate.py" --jobs "$JOBS" \
        --j0-ledger "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/j0_readout/j0_ledger.tsv" \
        --submissions "$LOG" --sacct "$psv" --want "$job" > "$psv.gate.json" \
        || { cat "$psv.gate.json"; echo "gate refused $job"; exit 3; }
    lim=$(re2b_limit "$job")
    id=$(sbatch --parsable --job-name="re2b-$job" --time="$lim" --export=ALL,C=$C,RE2_SHA=$RE2_SHA,JOB=$job \
        "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_job.sbatch")
    echo "$(date -u +%FT%TZ) sha=$RE2_SHA job=$job id=$id limit=$lim" | tee -a "$LOG"
done
