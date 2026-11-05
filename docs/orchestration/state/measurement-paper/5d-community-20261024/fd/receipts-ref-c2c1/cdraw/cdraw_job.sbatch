#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 C-DRAW job: regenerate Q_R replica S1_001 through RE-2's bound driver at its deploy pin (dbdad2f9), with
# its recorded argv (partb_runs.tsv), the way part B's lanes ran it (re2b_job.sbatch: the OI-136 guard, one srun step,
# 64 CPUs, the re2_preflight environment); then cdraw_compare.py: PASS iff the regenerated p1Streams record equals the
# recorded one exactly. Then the staged CV copy is deleted with a ledger row (the director's ruling 3(b)).
# Arguments: <deploy> <O>. Writes only under <O>.
set -o pipefail   # NOT set -u
C="${1:?deploy}"; O="${2:?out}"
MC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
CVS=/pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw/inputs/runEventLoopOmniFold_MEFHC.root
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw ] || { echo "[cdraw] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = dbdad2f93a255f1bd4bf357951aaa5689aaac512 ] || { echo "[cdraw] refusing: deploy HEAD is not dbdad2f9"; exit 2; }
[ -z "$(git -C "$C" status --porcelain)" ] || { echo "[cdraw] refusing: the deploy is not clean"; exit 2; }
echo "[cdraw] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) deploy HEAD $(git -C "$C" rev-parse HEAD)"
source "$C/setup_salloc_env.sh"   # root_6_28, as re2_preflight sources it (set -u would abort its activation)
export TMPDIR=$O/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1   # as part B (re2_env.sh)
unset LOKY_MAX_CPU_COUNT
mkdir -p "$TMPDIR" "$O/out/S1_001" "$O/logs" "$O/inventory"
srun -n1 -c 64 --mem="$((64 * 1905))M" --exact --job-name=S1_001 \
    python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label cdraw_S1_001 \
    --inventory "$O/inventory/S1_001.jsonl" -- "$C/2d-unfolding/re2/re2_driver.py" \
    --omnifile "$CVS" --mcfile "$MC" --iters 5 --use-weights --estimator lgbm --seed 42 --bootstrap-seed 1 \
    --bootstrap-streams three --bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31 \
    --out "$O/out/S1_001/xsec.root" < /dev/null > "$O/logs/S1_001.log" 2>&1
drc=$?
echo "[cdraw] driver rc=$drc end=$(date -u +%FT%TZ)"
crc=9
if [ "$drc" -eq 0 ]; then
    python3 "$O/cdraw_compare.py" "$O/out/S1_001/xsec.root" "$O/recorded/S1_001_xsec.root" "$O/cdraw.json" > "$O/logs/compare.log" 2>&1
    crc=$?
    cat "$O/logs/compare.log"
fi
echo "[cdraw] compare rc=$crc"
# the staged copy, deleted after the run with a ledger row (the B9 form: utc, path, sha256, size, mtime, inode, condition)
if [ -f "$CVS" ]; then
    st=$(stat -c '%s %Y %i' "$CVS")
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$CVS" 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df \
        $st "C-DRAW run over (driver rc $drc, compare rc $crc); staged from CFS by cdraw_stage_dtn.sh, checked in stage.json" >> "$O/deletions.tsv"
    rm -f -- /pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw/inputs/runEventLoopOmniFold_MEFHC.root
    echo "[cdraw] staged copy deleted (rc $?), ledger row in deletions.tsv"
fi
[ "$drc" -eq 0 ] && [ "$crc" -le 1 ] || exit 1
exit 0
