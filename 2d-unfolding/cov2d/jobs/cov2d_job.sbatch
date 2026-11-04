#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --output=/pscratch/sd/j/josephrb/cov2d-run-20261104/logs/%x-%j.out
# COV2D unfolds (COV2D-DECLARATION.md sections 4.4 and 8): the runs of runs_<TRUTH>.tsv whose job is $JOB, one srun
# step per run, each lane a sequence of steps, as part B's re2b_job.sbatch. --time is set at submission from
# jobs_<TRUTH>.tsv and checked here. Before any run: the pinned MAT environment, and every input the job's runs read
# (cov2d_jobs.py check: staged copies re-hashed against inputs.stat, data files against step B's record, $UNI's stat,
# the flux pins); any problem stops the job. Each run goes through the OI-136 guard with this deploy as the only
# admitted tree; its sha256 is appended as soon as it succeeds, and its start, end and rc are recorded (the wall per
# run, for section 8's REPRICE trigger). DRYRUN=1 prints each srun line instead (tests).
set -eo pipefail
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"
RUNS=$O/tables/runs_$TRUTH.tsv JOBS=$O/tables/jobs_$TRUTH.tsv
export D=$O/pseudo/${DATA_TRUTH:-$TRUTH}/b   # the pilot reads G18's data files (DATA_TRUTH=G18)
if [ "${DRYRUN:-0}" != 1 ]; then
    cov2d_preflight
    info=$(scontrol show job "$SLURM_JOB_ID")
    grep -q "QOS=regular" <<<"$info" || { echo "[cov2d] QOS is not regular"; exit 2; }
    limit=$(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $7}' "$JOBS")
    [ -n "$limit" ] && grep -q "TimeLimit=$limit " <<<"$info" || { echo "[cov2d] TimeLimit is not $JOB's $limit"; exit 2; }
    python -B "$CJ" check --runs "$RUNS" --job "$JOB" --stats "$STATS" --pseudo-b "$D/pseudo_b.json" \
        > "$O/logs/check-$JOB-$SLURM_JOB_ID.json" || { cat "$O/logs/check-$JOB-$SLURM_JOB_ID.json"; exit 4; }
    if [ "$JOB" = pilot ]; then   # the director's ruling (b): a timed read in place of a full CFS-read lateral
        lat0=runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root
        python -B "$CJ" dvs-rate --staged "$ACT/$lat0" --cfs "$CFSACT/$lat0" > "$O/logs/dvs-rate-$SLURM_JOB_ID.json" \
            || echo "[cov2d] dvs-rate failed (descriptive; recorded, not a stop)"
    fi
fi
echo "[cov2d] start $(date -u +%FT%TZ) job=${SLURM_JOB_ID:-dry} JOB=$JOB node=$(hostname)"
lane() {  # lane <name>: its runs in table order; a failed run is recorded and the lane goes on
    local want=$1 job ln label cpus script args est rc=0 t0
    while IFS=$'\t' read -r -u 3 job ln label cpus script args est; do
        [ "$job" = "$JOB" ] && [ "$ln" = "$want" ] || continue
        if [ -e "$O/out/$label" ]; then echo "[cov2d] $label exists; not overwritten"; rc=1; continue; fi
        [ "$script" = re2 ] || { echo "[cov2d] $label: unknown script $script"; rc=1; continue; }
        eval "set -- $args"
        if [ "${DRYRUN:-0}" = 1 ]; then echo "srun -c $cpus $label: $*"; continue; fi
        mkdir -p "$O/out/$label"
        t0=$(date +%s)
        srun -n1 -c "$cpus" --mem="$((cpus * 1905))M" --exact --job-name="$label" \
            python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "cov2d_$label" \
            --inventory "$O/inventory/$label.jsonl" -- "$C/2d-unfolding/re2/re2_driver.py" "$@" \
            --out "$O/out/$label/xsec.root" < /dev/null > "$O/logs/$label.log" 2>&1 \
            && (cd "$O/out" && sha256sum "$label/xsec.root") >> "$O/SHA256SUMS.$JOB.${want#$JOB.}" \
            || { echo "[cov2d] $label rc=$?"; rc=1; }
        printf '%s\t%s\t%s\t%s\n' "$label" "$t0" "$(date +%s)" "$rc" >> "$O/walls.$JOB.${want#$JOB.}.tsv"
    done 3< <(tail -n +2 "$RUNS")
    return $rc
}
pids=""
for l in $(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $2}' "$RUNS" | sort -u); do lane "$l" & pids="$pids $!"; done
[ -n "$pids" ] || { echo "[cov2d] no runs for $JOB"; exit 2; }
rc=0
for p in $pids; do wait "$p" || rc=1; done
echo "[cov2d] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
