#!/bin/bash
# ll5d_gate_<T>'s job: one BLAS thread, asserted; the deploy at M with porcelain 0 and the bound blobs; ll5d.py gate.
# The sealed clip-prep file is hashed and sized here, never read. Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; T=$4; CAL=$5; CALSHA=$6; CALNPZSHA=$7; TLS=$8
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID truth=$T start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS"
cd "$W" || stop cd
/usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d.py" gate --truth "$T" \
  --npz "$ND/of_inputs_5d.npz" --bkg "$P/s5c-20260924/runs/p2/bkg_dump.npz" --bank "$ND/bank_sweep_5d_bkgaware" \
  --detector-dir "$P/s5p-20260926/bank_detector" --pins "$P/fd-1b-20261030/pins.json" \
  --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  --flux-table "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" \
  --expect-flux-table-sha256 cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5 \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --prep "$P/fd-f1-20261027/f1b3/prep" \
  --manifest "$DD/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt" \
  --expect-manifest-sha256 3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031 \
  --staged "$P/fd-1b-inv-20261101/i0/in" --calibration "$CAL" --expect-calibration-sha256 "$CALSHA" \
  --expect-calibration-npz-sha256 "$CALNPZSHA" --time-limit-seconds "$TLS" \
  --out "$W/gate-$T.json" > "$W/gate.out" 2> "$W/gate.time"
rc=$?
echo "gate rc=$rc"
cat "$W/gate.out"
grep -E "Elapsed|Maximum resident|Percent of CPU|Exit status" "$W/gate.time"
sha256sum "$W/gate-$T.json" "$W/gate-$T.receipt.npz" "$W"/gate.out "$W"/gate.time "$W"/gate-$T.*.json 2>/dev/null
[ -e "$W/gate-$T.clipprep.npz" ] && echo "SEALED gate-$T.clipprep.npz bytes=$(stat -c %s "$W/gate-$T.clipprep.npz") sha256=$(sha256sum "$W/gate-$T.clipprep.npz" | cut -d' ' -f1)"
echo "end=$(date -u +%FT%TZ)"
exit $rc      # A1a.1 round: sacct's state is the step's (run 1 read COMPLETED 0:0 on rc 1)
