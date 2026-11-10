#!/bin/bash
# ll5d_vicheck's job: one BLAS thread, asserted; the deploy at M with porcelain 0 and the bound blobs;
# setup_salloc_env.sh (Python 3.11); ll5d.py vicheck. Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS"
cd "$W" || stop cd
/usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d.py" vicheck \
  --npz "$ND/of_inputs_5d.npz" --bkg "$P/s5c-20260924/runs/p2/bkg_dump.npz" --bank "$ND/bank_sweep_5d_bkgaware" \
  --detector-dir "$P/s5p-20260926/bank_detector" --pins "$P/fd-1b-20261030/pins.json" \
  --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  --flux-table "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" \
  --expect-flux-table-sha256 cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5 \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --prep "$P/fd-f1-20261027/f1b3/prep" \
  --manifest "$DD/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt" \
  --expect-manifest-sha256 3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031 \
  --time-limit-seconds 3600 \
  --out "$W/vicheck.json" > "$W/vicheck.out" 2> "$W/vicheck.time"
rc=$?
echo "vicheck rc=$rc"
cat "$W/vicheck.out"
grep -E "Elapsed|Maximum resident|Percent of CPU|Exit status" "$W/vicheck.time"
sha256sum "$W"/vicheck.json "$W"/vicheck.out "$W"/vicheck.time "$W"/vicheck.*.json 2>/dev/null
echo "end=$(date -u +%FT%TZ)"
exit $rc      # sacct's state is the step's
