#!/bin/bash
# COV2D connect PILOT-READOUT: binding 2 ruling 2.3, the pilot readout (cov2d_pilot.py) on the ended pilot job's
# outputs, 0 node-h, on a login node. Run from the deploy at M, so its record's "M" is the deploy's HEAD
# (cov2d.deploy_head refuses a dirty checkout), in the job's environment, root_6_28 + the pinned MAT environment
# (run_check_mat_setup first). The readout copies part B's three reference products through O_NOATIME at their pins
# into $TMPDIR (/dev/shm), compares (2b) and section 9.12 by re2_k1's rule, prices REPRICE and reads the DVS record.
# Its record is written to $O/logs (never inside the deploy) and goes to the director before any bulk connect.
# A STOP or INVALID is reported unrepaired. Porcelain (plain and --ignored) before and after. login02, nice 19,
# taskset -c 8-11, threads 1. /dev/shm is removed at the end but this log, which is fetched and then removed (logged).
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-readout.sh >/dev/null 2>&1 </dev/null &
M=cb31611ca8b96ed2d1eeb809fda7236e56645863
C=/pscratch/sd/j/josephrb/cov2d-deploy-cb31611c
O=/pscratch/sd/j/josephrb/cov2d-run-20261104
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
W=/dev/shm/josephrb-cov2d-readout
OUT=$O/logs/pilot_readout.json
RUN="nice -n 19 taskset -c 8-11"
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-readout.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
finish() { rm -rf "$W/tmp"; echo "rm -rf $W/tmp rc=$?"; echo "end=$(date -u +%FT%TZ)"; echo DONE; }
[ -e "$OUT" ] && { echo "STOP $OUT exists"; finish; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "STOP the deploy is not at M"; finish; exit 2; }
echo "deploy head=$(git -C "$C" rev-parse HEAD) plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -z "$(git -C "$C" status --porcelain --ignored)" ] || { echo "STOP the deploy is not clean (--ignored)"; finish; exit 2; }
echo "sacct:"; sacct -j "$(awk '/job=pilot / {for (i = 1; i <= NF; i++) if ($i ~ /^id=/) print substr($i, 4)}' "$O/submissions.log" | tail -1)" -P \
    -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,Start,End
ls -la "$O" "$O/out" "$O/logs"; cat "$O"/walls.pilot.*.tsv; cat "$O"/SHA256SUMS.pilot.*
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$C/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  echo "python=$(command -v python)"
  cd "$W" && $RUN python -B "$C/2d-unfolding/cov2d/cov2d_pilot.py" --o "$O" --out "$OUT"
); echo "readout rc=$?"
echo "deploy after: plain=$(git -C "$C" status --porcelain | wc -l) ignored=$(git -C "$C" status --porcelain --ignored | wc -l)"
[ -f "$OUT" ] && { sha256sum "$OUT"; chmod 0440 "$OUT"; cat "$OUT"; }
finish
