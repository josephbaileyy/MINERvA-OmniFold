#!/bin/bash
# 1B A2.1, c2check's timing probe (the director's ruling (a), item 3, and ruling (A)): on one exclusive CPU node,
# fd_1b_c2.py c2probe times each of c2check's one-off steps through c2check's own functions (prepare(rows=True),
# c2_inputs, the multiplicative terms once, the (vi) row match, the draws for the declared 300 and the 3,000-draw gate
# sample), then the first BLOCKS 20-draw blocks of G18's gate sample through the real c2_truth, and projects a
# one-truth c2check job. It records |Z| per array and the peak RSS. BLAS and OMP threads are set explicitly and printed
# (they can move the last bits); their count is the fourth argument (the director's ruling (a), 2026-11-05: c2check runs
# at 1, the calibration's, so its bitwise single-universe U x_T check holds). The probe runs under 1B's guarded launcher
# (fd_1b_noatime_guard.py --declared), as c2check does.
# The deploy, the commit, the output directory and the thread count are arguments (sbatch runs a copy of this file, so it cannot locate
# itself). Not under set -u, which aborts the root_6_28 activation. Writes only under $W.
DD=$1; M=$2; W=$3; THREADS=$4
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
BLOCKS=4
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ) threads=$THREADS"
case "$THREADS" in ''|*[!0-9]*|0) stop "THREADS (argument 4) is not a positive integer: '$THREADS'" ;; esac
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
/usr/bin/time -v python3 -B "$DD/nd-unfolding/fd_1b_noatime_guard.py" --declared -- "$DD/nd-unfolding/fd_1b_c2.py" c2probe \
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
  --truths g18 --blocks $BLOCKS --out "$W/probe.json" > "$W/probe.out" 2> "$W/probe.time"
rc=$?
echo "c2probe rc=$rc"
cat "$W/probe.out"
grep -E "fd_1b_noatime_guard|Elapsed|Maximum resident|Percent of CPU|Exit status" "$W/probe.time"
sha256sum "$W"/probe.json "$W"/probe.out "$W"/probe.time 2>/dev/null
echo "end=$(date -u +%FT%TZ)"
