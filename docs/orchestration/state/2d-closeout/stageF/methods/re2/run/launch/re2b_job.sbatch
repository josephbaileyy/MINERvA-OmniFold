#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --exclude=nid004074,nid004078
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/logs/%x-%j.out
# RE-2 part B (RE2-DECLARATION-B.md §3-§4): the runs of partb_runs.tsv whose job is $JOB, one srun step per run,
# each lane a sequence of steps. --time is set at submission (re2b_submit.sh, from partb_jobs.tsv) and checked here.
# Every run goes through the OI-136 guard with this deploy as the only admitted tree. The table is read on fd 3 and
# srun's stdin is /dev/null (part A's re2_j0.sbatch; test_lane_stdin.sh). Each lane appends a run's sha256 to
# SHA256SUMS.<job>.<lane> as soon as the run has succeeded, so a time limit cannot leave a finished run undigested.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_env.sh"
re2_preflight
info=$(scontrol show job "$SLURM_JOB_ID")
grep -q "QOS=regular" <<<"$info" || { echo "[re2b] QOS is not regular"; exit 2; }
limit=$(re2b_limit "$JOB"); [ -n "$limit" ] || { echo "[re2b] $JOB is not a partb_jobs.tsv row"; exit 2; }
grep -q "TimeLimit=$limit " <<<"$info" || { echo "[re2b] TimeLimit is not the declared $limit"; exit 2; }
re2b_check_inputs "${JOB:0:2}"
echo "[re2b] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID JOB=$JOB node=$(hostname)"
lane() {  # lane <name>: its runs in table order; a failed run is recorded and the lane goes on
    local want=$1 job ln label cpus script args est rc=0
    while IFS=$'\t' read -r -u 3 job ln label cpus script args est; do
        [ "$job" = "$JOB" ] && [ "$ln" = "$want" ] || continue
        if [ -e "$O/out/$label" ]; then echo "[re2b] $label exists; not overwritten"; rc=1; continue; fi
        [ "$script" = re2 ] || { echo "[re2b] $label: unknown script $script"; rc=1; continue; }
        mkdir -p "$O/out/$label"
        eval "set -- $args"
        srun -n1 -c "$cpus" --mem="$((cpus * 1905))M" --exact --job-name="$label" \
            python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "re2b_$label" \
            --inventory "$O/inventory/$label.jsonl" -- "$C/2d-unfolding/re2/re2_driver.py" "$@" \
            --out "$O/out/$label/xsec.root" < /dev/null > "$O/logs/$label.log" 2>&1 \
            && (cd "$O/out" && sha256sum "$label/xsec.root") >> "$O/SHA256SUMS.$JOB.${want#$JOB.}" \
            || { echo "[re2b] $label rc=$?"; rc=1; }
    done 3< <(tail -n +2 "$RUNS")
    return $rc
}
pids=""
for l in $(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $2}' "$RUNS" | sort -u); do lane "$l" & pids="$pids $!"; done
[ -n "$pids" ] || { echo "[re2b] no runs for $JOB"; exit 2; }
rc=0
for p in $pids; do wait "$p" || rc=1; done
echo "[re2b] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
