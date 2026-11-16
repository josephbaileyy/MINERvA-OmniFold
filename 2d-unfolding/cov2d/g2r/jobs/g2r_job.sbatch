#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --output=/pscratch/sd/j/josephrb/cov2d-g2r-20261112/logs/%x-%j.out
# COV2D-G2R unfolds (addendum J1): the runs of runs_g2r.tsv whose job is $JOB, one srun step per run, each lane a
# sequence of steps, as COV2D's cov2d_job.sbatch. --time is set at submission from jobs_g2r.tsv and checked here.
# Before any run: the pinned MAT environment, and every input the job's runs read (g2r_jobs.py check: $UNI's stat,
# the pins, the map against the committed prepare record's $MAPSHA, a tune's realization against COV2D's step-B
# record); any problem stops the job. Each run goes through the OI-136 guard with this deploy as the only admitted
# tree; its sha256 is appended as soon as it succeeds, and its start, end and rc are recorded. DRYRUN=1 prints each
# srun line instead (tests).
set -eo pipefail
source "$C/2d-unfolding/cov2d/g2r/jobs/g2r_env.sh"
export TMPDIR=$O/tmp/${SLURM_JOB_ID:-dry}; mkdir -p "$TMPDIR"   # nothing inherited from the submitting shell
RUNS=$O/tables/runs_g2r.tsv JOBS=$O/tables/jobs_g2r.tsv
case "$JOB" in envtest|prepare) echo "[g2r] $JOB has its own script"; exit 2 ;; esac
point=$(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $7}' "$RUNS" | sort -u)
[ -n "$point" ] && [ "$point" = "${point%%[[:space:]]*}" ] || { echo "[g2r] $JOB has no runs or mixes points: $point"; exit 2; }
export D=$(g2r_data_dir "$point")
if [ "${DRYRUN:-0}" != 1 ]; then
    g2r_preflight
    g2r_slurm_ok "$(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $7}' "$JOBS")"
    python -B "$GJ" check --runs "$RUNS" --job "$JOB" --map-sha "${MAPSHA:-}" > "$O/logs/check-$JOB-$SLURM_JOB_ID.json" \
        || { cat "$O/logs/check-$JOB-$SLURM_JOB_ID.json"; exit 4; }
fi
echo "[g2r] start $(date -u +%FT%TZ) job=${SLURM_JOB_ID:-dry} JOB=$JOB point=$point node=$(hostname)"
lane() {  # lane <name>: its runs in table order; a failed run is recorded and the lane goes on
    local want=$1 job ln label cpus args est pt role uni rc=0 t0 run_rc
    while IFS=$'\t' read -r -u 3 job ln label cpus args est pt role uni; do
        [ "$job" = "$JOB" ] && [ "$ln" = "$want" ] || continue
        if [ -e "$O/out/$label" ]; then echo "[g2r] $label exists; not overwritten"; rc=1; continue; fi
        eval "set -- $args"
        if [ "${DRYRUN:-0}" = 1 ]; then echo "srun -c $cpus $label: $*"; continue; fi
        mkdir -p "$O/out/$label"
        t0=$(date +%s); run_rc=0
        srun -n1 -c "$cpus" --mem="$((cpus * 1905))M" --exact --job-name="$label" \
            python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "g2r_$label" \
            --inventory "$O/inventory/$label.jsonl" -- "$C/2d-unfolding/re2/re2_driver.py" "$@" \
            --out "$O/out/$label/xsec.root" < /dev/null > "$O/logs/$label.log" 2>&1 \
            && (cd "$O/out" && sha256sum "$label/xsec.root") >> "$O/SHA256SUMS.$JOB.${want#$JOB.}" \
            || { echo "[g2r] $label rc=$?"; run_rc=1; rc=1; }
        printf '%s\t%s\t%s\t%s\n' "$label" "$t0" "$(date +%s)" "$run_rc" >> "$O/walls.$JOB.${want#$JOB.}.tsv"
    done 3< <(tail -n +2 "$RUNS")
    return $rc
}
pids=""
for l in $(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $2}' "$RUNS" | sort -u); do lane "$l" & pids="$pids $!"; done
[ -n "$pids" ] || { echo "[g2r] no runs for $JOB"; exit 2; }
rc=0
for p in $pids; do wait "$p" || rc=1; done
echo "[g2r] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
