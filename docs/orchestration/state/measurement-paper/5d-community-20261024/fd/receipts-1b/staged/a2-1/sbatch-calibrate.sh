#!/bin/bash
# 1B A2.1, the large-sample calibration job (Joseph's decision of 2026-11-04; the director's P1-P7): G18 and AR23 on
# one CPU node, 10,000 replicate sets of GATE_N = 3,000 draws per truth across 64 single-threaded worker processes,
# fd_1b_c2.py calibrate (schema /2: the s rule, power, and the controls at N). The deploy, the commit and the output
# directory are arguments (sbatch runs a copy of this file, so it cannot locate itself). Not under set -u, which
# aborts the root_6_28 activation. Writes only under $W.
DD=$1; M=$2; W=$3
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ) time_limit_s=$SLURM_JOB_TIME_LIMIT"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
echo "sourcing $DD/setup_salloc_env.sh sha256 $(sha256sum "$DD/setup_salloc_env.sh" | cut -d' ' -f1)"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$W" || stop cd
# the budget guard: the projection from one measured set on the real fine-cell count must fit inside --time
/usr/bin/time -v python3 -B "$DD/nd-unfolding/fd_1b_c2.py" calibrate \
  --npz "$ND/of_inputs_5d.npz" --bkg "$P/s5c-20260924/runs/p2/bkg_dump.npz" --bank "$ND/bank_sweep_5d_bkgaware" \
  --detector-dir "$P/s5p-20260926/bank_detector" --pins "$P/fd-1b-20261030/pins.json" \
  --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  --flux-table "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" \
  --expect-flux-table-sha256 cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5 \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --prep "$P/fd-f1-20261027/f1b3/prep" \
  --cv-tdw "$P/fd-1b-a21-cvdenom2-20261103/cvdenom.npy" \
  --expect-cv-tdw-sha256 0bc70d622ed51f7e6ce3b80e095788f315e52937b6a6c79a0bafedeb4545def8 \
  --truths g18 ar23 --workers 64 --budget-seconds 5000 --out "$W/calibration.json" \
  > "$W/calibration.out" 2> "$W/calibration.time"
rc=$?
echo "calibrate rc=$rc"
cat "$W/calibration.out"
grep -E "Elapsed|Maximum resident|Percent of CPU|Exit status" "$W/calibration.time"
sha256sum "$W"/calibration.json "$W"/calibration.npz "$W"/calibration.out "$W"/calibration.time 2>/dev/null
echo "end=$(date -u +%FT%TZ)"
