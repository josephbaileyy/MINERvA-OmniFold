#!/bin/bash
#SBATCH -q regular
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 00:25:00
#SBATCH -A m3246
#SBATCH -J gencmp-e2
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH -o /pscratch/sd/j/josephrb/gencmp-e2-20261102/logs/e2-unfold-%j.out
# GENCMP amendment E, step E2's unfold (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md section 2): NuWro CH, GiBUU CH and the
# NuWro carbon control R2 at estimator seed 42, and the noise-floor pair (NuWro and GiBUU carbon, committed prep ratios)
# at seed 43: five pvl_unfold runs of 32 threads at once on one node, as PV-ladder J5 (60206336) ran five, in the
# environment the PV ladder ran in (RE-1's setup_salloc_env.sh). From the deploy at the bound commit with empty
# porcelain; writes only under $R.
R=/pscratch/sd/j/josephrb/gencmp-e2-20261102
M=${BOUND:?set BOUND to the bound commit}
mkdir -p "$R/logs" "$R/tmp" || exit 2
cd "$R/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not the bound commit"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
[ -f "$R/prep_ch/R1.ok" ] || { echo "R1 has not passed: no unfold (B1)"; exit 9; }
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > "$R/logs/env-unfold.log" 2>&1
case "$(python -V 2>&1)" in *3.11*) ;; *) echo "environment did not activate"; exit 2 ;; esac
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
date -u +%FT%TZ; hostname
# as sbatch_pvl.sh:58-83: 42 CPUs and an equal share of 95 % of the job's memory per step, through mnv_guarded_run.py,
# with --threads 32 --iters 5 and each task's estimator seed
D="$R/deploy"; V="$D/nd-unfolding/pv-ladder"; O="$R/unfold"; mkdir -p "$O" "$R/inventory"
JOBMEM=${SLURM_MEM_PER_NODE:-$(scontrol show job "$SLURM_JOB_ID" | grep -o 'AllocTRES=[^ ]*' \
        | sed -n 's/.*mem=\([0-9]*\)\([MG]\).*/\1 \2/p' | awk '{print ($2 == "G") ? $1 * 1024 : $1}')}
[ -n "$JOBMEM" ] && [ "$JOBMEM" -gt 0 ] || { echo "cannot read the job's memory"; exit 2; }
NT=5; CPN=${SLURM_CPUS_ON_NODE:-$(nproc)}
[ $(( NT * 42 )) -le "$CPN" ] || { echo "$NT steps of 42 CPUs do not fit the node's $CPN"; exit 2; }
MEM=$(( JOBMEM * 95 / 100 / NT ))
echo "steps=$NT cpus_per_step=42 cpus_on_node=$CPN mem_per_step=${MEM}M"
NPZ="$R/inputs/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"; BKG="$R/inputs/s5c-20260924/runs/p2/bkg_dump.npz"
pids=()
P="$R/inputs/pv-ladder-20261024/prep/ratios/L-5D-PV"
for t in "nuwro_ch:42:$R/prep_ch/L-5D-PV/nuwro.json" "gibuu_ch:42:$R/prep_ch/L-5D-PV/gibuu.json" \
         "nuwro_carbon_R2:42:$P/nuwro.json" "nuwro_carbon_s43:43:$P/nuwro.json" "gibuu_carbon_s43:43:$P/gibuu.json"; do
  task=${t%%:*}; rest=${t#*:}; SEED=${rest%%:*}; RF=${rest#*:}; SHA=$(sha256sum "$RF" | cut -c1-64)
  srun -n1 -c 42 --mem="${MEM}M" --exact --cpu-bind=cores \
    python "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$R/inventory/$task.jsonl" \
    --label "e2:$task" -- "$V/pvl_unfold.py" --rung L-5D-PV --arm e --features all \
    --ratio "$RF" --expect-ratio-sha256 "$SHA" \
    --npz "$NPZ" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --bkg "$BKG" --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 \
    --estimator-seed "$SEED" --threads 32 --iters 5 --out "$O/L-5D-PV_e_$task.npz" > "$R/logs/$task.log" 2>&1 &
  pids+=("$!")
done
[ "${#pids[@]}" -eq "$NT" ] || { echo "launched ${#pids[@]} steps, not $NT"; }
for p in "${pids[@]}"; do wait "$p" || echo "a step failed (pid $p)"; done
python -B nd-unfolding/fd_gencmp_e2.py unfold --run-dir "$R"
rc=$?; echo "rc=$rc"; date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
exit $rc
