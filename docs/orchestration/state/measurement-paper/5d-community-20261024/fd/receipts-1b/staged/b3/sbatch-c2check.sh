#!/bin/bash
# 1B binding 3, c2check at N for one truth (A2.1 §8c, the director's ruling (a): one truth per job, merged after) on
# one exclusive CPU node with BLAS and OMP threads set explicitly and printed. c2check runs under 1B's guarded
# launcher (fd_1b_noatime_guard.py --declared, the director's ruling of 2026-11-05), which refuses any plain open under
# the declared input roots. Its calibration is rerun2's (job 60857361, at the same code: c2check refuses any other)
# and its backstop's the 300-draw calibration (job 60771025, admitted by cal300_code_check).
# The deploy, the commit, the output directory and the truth are arguments (sbatch runs a copy of this file, so it
# cannot locate itself). Not under set -u, which aborts the root_6_28 activation. Writes only under $W.
DD=$1; M=$2; W=$3; T=$4
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
CAL=$P/fd-1b-a21-calibN-rerun2-20261105; CAL300=$P/fd-1b-a21-calib-20261104
THREADS=64
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID truth=$T start=$(date -u +%FT%TZ)"
case "$T" in g18|ar23) ;; *) stop "truth $T is not g18 or ar23 (the plug-in's part follows B4 and the capture)" ;; esac
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
echo "sourcing $DD/setup_salloc_env.sh sha256 $(sha256sum "$DD/setup_salloc_env.sh" | cut -d' ' -f1)"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS \
  MKL_NUM_THREADS=$THREADS NUMEXPR_NUM_THREADS=$THREADS
echo "threads OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS"
cd "$W" || stop cd
/usr/bin/time -v python3 -B "$DD/nd-unfolding/fd_1b_noatime_guard.py" --declared -- "$DD/nd-unfolding/fd_1b_c2.py" c2check \
  --npz "$ND/of_inputs_5d.npz" --bkg "$P/s5c-20260924/runs/p2/bkg_dump.npz" --bank "$ND/bank_sweep_5d_bkgaware" \
  --detector-dir "$P/s5p-20260926/bank_detector" --pins "$P/fd-1b-20261030/pins.json" \
  --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  --flux-table "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" \
  --expect-flux-table-sha256 cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5 \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --staged "$P/fd-1b-inv-20261101/i0/in" \
  --prep "$P/fd-f1-20261027/f1b3/prep" \
  --cv-tdw "$P/fd-1b-a21-cvdenom2-20261103/cvdenom.npy" \
  --expect-cv-tdw-sha256 0bc70d622ed51f7e6ce3b80e095788f315e52937b6a6c79a0bafedeb4545def8 \
  --calibration "$CAL/calibration.json" \
  --expect-calibration-sha256 66f2ae4443099baec677f07d76aae6103763816f89e3767d774ae43b8f22ef10 \
  --expect-calibration-npz-sha256 9047a6f730ca41cda8a0c6d7b60aac19ba10c04f8ab6a6b13a279a5835291a70 \
  --calibration-300 "$CAL300/calibration.json" \
  --expect-calibration-300-sha256 4b6a18b60ec70f5a0eb8a57284c85e9d5be6efc5d1574251b336c4ed64c420df \
  --truths "$T" --out "$W/gate-$T.json" > "$W/c2check.out" 2> "$W/c2check.time"
rc=$?
echo "c2check rc=$rc"
cat "$W/c2check.out"
grep -E "fd_1b_noatime_guard|Elapsed|Maximum resident|Percent of CPU|Exit status" "$W/c2check.time"
sha256sum "$W/gate-$T.json" "$W"/c2check.out "$W"/c2check.time 2>/dev/null
echo "end=$(date -u +%FT%TZ)"
