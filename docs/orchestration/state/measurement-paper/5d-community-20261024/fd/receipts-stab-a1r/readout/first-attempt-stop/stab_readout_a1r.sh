#!/bin/bash
# FD-STAB readout (FD-STAB-BINDING-2.md ruling 5, merged at a1c8bb30 as #771): estimator_stability_analyze.py at M_A1
# with the arguments of FD-STAB-DECLARATION.md §7, on a login node, nice 19, threads 1, after the full run's DONE.
# It runs from the full run's own clean deploy ($OUT/deploy-full at M_A1, blobs re-verified), with exactly §7's
# arguments; the analysis derives its receipt from --runs (<runs>/../log-full/DONE) and grades nothing without it.
# Python with -I -B and no
# bytecode, so the deploy stays clean. Writes only $OUT/readout/ (fd_stab.json, readout.log, readout.done and a copy of
# this script). The record comes to the director before any reading is quoted. No set -u. Any stop is final.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
M=cc54d86f7ac66c1346fa69e5894b2d2f000fb09c
OUT=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104
D=$OUT/deploy-full
RO=$OUT/readout
JOB=60837713
PY=$HOME/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
[ -s "$OUT/log-full/DONE" ] && [ -x "$PY" ] && [ -d "$D" ] || bail
for x in log-full/STOP log-full/FAILED readout; do [ ! -e "$OUT/$x" ] || bail; done
case "$(sacct -j "$JOB" -X -n -P -o State | head -1)" in COMPLETED) ;; *) bail ;; esac
mkdir "$RO" || bail
exec > "$RO/readout.log" 2>&1
finish() { echo "readout rc=$1"; date -u +%FT%TZ; echo "$1" > "$RO/readout.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "readout script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$RO/stab_readout_a1r.sh"
echo "full run $JOB: $(sacct -j "$JOB" -X -n -P -o JobID,State,ExitCode,Elapsed,ElapsedRaw,NNodes | head -1)"
echo "log-full/DONE: $(dd if="$OUT/log-full/DONE" iflag=noatime status=none) sha256 $(dd if="$OUT/log-full/DONE" iflag=noatime status=none | sha256sum | cut -d' ' -f1)"
echo "log-full/SHA256SUMS sha256 $(dd if="$OUT/log-full/SHA256SUMS" iflag=noatime status=none | sha256sum | cut -d' ' -f1), $(dd if="$OUT/log-full/SHA256SUMS" iflag=noatime status=none | wc -l) products"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy-full HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "deploy-full HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: deploy-full is not clean"; finish 9; }
S=docs/orchestration/state/measurement-paper/5d-community-20261024
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
25179f9f704e61a920c9d0005283b4fcd357d825 nd-unfolding/estimator_stability_probe.py
9defbb44e99d0dcc538b7254ab998ba13feb354a nd-unfolding/sbatch_fd_stab.sh
0e4718902e1b156d340ba5a9848d522b5be0fc45 nd-unfolding/estimator_stability_analyze.py
22e211a20514f9a3c10145085f813c9f5f63f6f2 nd-unfolding/tests/test_estimator_stability_probe.py
9ab35c9839fc38322c47fedf95b774ea25d8942f nd-unfolding/tests/estimator_stability_mutation.py
27947e1add4dd5fbda17a17020976fd30bea1061 $S/fd/stab/no-ratio.json
dc2ac4e4f3098ce59a81fc043526d87b5c49ec77 $S/s1/PRESERVE-INVENTORY.sha256
BLOBS
echo "bound blobs: 7 checked, $bad mismatches"
[ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19; ionice idle"
( cd "$D" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B nd-unfolding/estimator_stability_analyze.py \
    --runs "$OUT/runs" --s5c-contract docs/orchestration/state/s5c/contract.json \
    --sigma-receipt docs/orchestration/state/s5e/cand/assess_receipt.json \
    --h2-definition nd-unfolding/pv-ladder/readouts/h2_definition.json --out "$RO/fd_stab.json" --repo . )
rc=$?
echo "analyze rc=$rc"
[ -s "$RO/fd_stab.json" ] && echo "record sha256 $(dd if="$RO/fd_stab.json" iflag=noatime status=none | sha256sum | cut -d' ' -f1)"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish $rc
