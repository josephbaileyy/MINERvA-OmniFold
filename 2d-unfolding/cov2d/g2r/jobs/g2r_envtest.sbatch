#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --output=/pscratch/sd/j/josephrb/cov2d-g2r-20261112/logs/%x-%j.out
# COV2D-G2R's cluster-environment test (addendum J1; binding 1 addendum C1 ruling 2), before the prepare: MaRES:0 at
# the data, part B's argv, through the pre-patch driver (the deploy $PRE at PRE_M, COV2D's) and through the patched
# driver with the flag off (the deploy $C at $M), in two lanes of 128 CPUs on this node, the same environment for
# both. Then g2r_jobs.py envtest compares the two products (every histogram and TParameter bitwise; the TNamed records
# except those that name the code and paths). Each run goes through the OI-136 guard with its own deploy as the only
# admitted tree. Exit 0 on PASS; 5 if the products differ; 4 if an input check fails; 6 if a run failed.
set -eo pipefail
source "$C/2d-unfolding/cov2d/g2r/jobs/g2r_env.sh"
RUNS=$O/tables/runs_g2r.tsv JOBS=$O/tables/jobs_g2r.tsv
E=$O/envtest
[ ! -e "$E" ] || { echo "[g2r] $E exists: an environment-test rerun is a new connect"; exit 3; }
g2r_preflight
pre_m=$("$PY310" -B -c "import sys; sys.path.insert(0, '$C/2d-unfolding/cov2d/g2r/jobs'); import g2r_jobs as g; print(g.PRE_M)")
g2r_deploy_ok "$PRE" "$pre_m" || { echo "[g2r] $PRE is not a clean checkout at $pre_m"; exit 2; }
g2r_slurm_ok "$(awk -F'\t' 'NR > 1 && $1 == "envtest" {print $7}' "$JOBS")"
python -B "$GJ" check --runs "$RUNS" --job envtest > "$O/logs/check-envtest-$SLURM_JOB_ID.json" \
    || { cat "$O/logs/check-envtest-$SLURM_JOB_ID.json"; exit 4; }
mkdir -p "$E"
echo "[g2r] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID envtest node=$(hostname) pre=$pre_m M=$M"
run() {  # run <role> <deploy>
    local role=$1 dep=$2 label args cpus t0 rc=0
    label=$(awk -F'\t' -v r="$role" 'NR > 1 && $1 == "envtest" && $8 == r {print $3}' "$RUNS")
    args=$(awk -F'\t' -v r="$role" 'NR > 1 && $1 == "envtest" && $8 == r {print $5}' "$RUNS")
    cpus=$(awk -F'\t' -v r="$role" 'NR > 1 && $1 == "envtest" && $8 == r {print $4}' "$RUNS")
    eval "set -- $args"
    t0=$(date +%s)
    srun -n1 -c "$cpus" --mem="$((cpus * 1905))M" --exact --job-name="$label" \
        python "$dep/nd-unfolding/mnv_guarded_run.py" --expect-root "$dep" --label "g2r_$label" \
        --inventory "$O/inventory/$label.jsonl" -- "$dep/2d-unfolding/re2/re2_driver.py" "$@" \
        --out "$E/$label.root" < /dev/null > "$O/logs/$label.log" 2>&1 || rc=$?
    printf '%s\t%s\t%s\t%s\n' "$label" "$t0" "$(date +%s)" "$rc" >> "$E/walls.tsv"
    return $rc
}
run pre "$PRE" & p1=$!
run post "$C" & p2=$!
rc=0; wait $p1 || rc=6; wait $p2 || rc=6
(cd "$E" && sha256sum ./*.root) || true
if [ "$rc" = 0 ]; then
    python -B "$GJ" envtest --pre "$E/E_pre_MaRES_0.root" --post "$E/E_post_MaRES_0.root" --out "$E/envtest.json" || rc=$?
fi
echo "[g2r] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
