#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/j0/logs/%x-%j.out
# RE-2 J0 (RE2-DECLARATION.md §4): the runs of j0_runs.tsv whose job is $JOB, each lane a sequence of srun steps
# (one step per run, so sacct times every run). J0a: two 128-CPU lanes; J0b: four 64-CPU lanes. --time is set at
# submission (re2_submit_j0.sh). Every run goes through the OI-136 guard with this deploy as the only admitted tree.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_env.sh"
re2_preflight
re2_check_inputs
[ "$JOB" = J0a ] && re2_check "$LATBAX0" "$LATBAX0_SHA"
echo "[re2] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID JOB=$JOB node=$(hostname)"
lane() {  # lane <name>: its runs in table order; a failed run is recorded and the lane goes on
    local want=$1 job ln label cpus script args target rc=0
    while IFS=$'\t' read -r job ln label cpus script args; do
        [ "$job" = "$JOB" ] && [ "$ln" = "$want" ] || continue
        [ ! -e "$O/out/$label" ] || { echo "[re2] $label exists; not overwritten"; rc=1; continue; }
        mkdir -p "$O/out/$label"
        case "$script" in
            re2) target=("$C/2d-unfolding/re2/re2_driver.py") ;;
            p1ref) target=("$C/2d-unfolding/re2/re2_with_helper.py" "$C/2d-unfolding/driver_p1.py") ;;
            *) echo "[re2] $label: unknown script $script"; rc=1; continue ;;
        esac
        eval "set -- $args"
        srun -n1 -c "$cpus" --mem="$((cpus * 1905))M" --exact --cpu-bind=cores --job-name="$label" \
            python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "re2_$label" \
            --inventory "$O/inventory/$label.jsonl" -- "${target[@]}" "$@" --out "$O/out/$label/xsec.root" \
            > "$O/logs/$label.log" 2>&1 || { echo "[re2] $label rc=$?"; rc=1; }
    done < <(tail -n +2 "$RUNS")
    return $rc
}
pids=""
case "$JOB" in
    J0a) for l in a1 a2; do lane $l & pids="$pids $!"; done ;;
    J0b) for l in b1 b2 b3 b4; do lane $l & pids="$pids $!"; done ;;
    *) echo "[re2] unknown JOB $JOB"; exit 2 ;;
esac
rc=0
for p in $pids; do wait "$p" || rc=1; done
(cd "$O/out" && sha256sum */xsec.root > "$O/SHA256SUMS.$JOB") || rc=1
echo "[re2] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
