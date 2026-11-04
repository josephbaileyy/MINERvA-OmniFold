#!/bin/bash
# RPD readout (N0's reading, R1, R2 with p_era, R3; fd_rpd.py readout), the last RPD step, on a login node, detached,
# niced, after job B ended COMPLETED 0:0 with every lane done and the controls PASSed (FD-RPD-BINDING-2.md and its
# addendum A1; FD-RPD-DECLARATION-PART2.md sections 1.2 and 2). A fresh clone at M' into $R/deploy-10 (each connect
# from a fresh clone), the section 7 blobs, verify-staged (binding 2 A1), then fd_rpd.py readout. 0 node-h, no job.
# Reads under $R only; probe reads through O_NOATIME (dd iflag=noatime). Writes only under $R; nothing to CFS. No set -u
# (it aborts the root_6_28 activation). Any stop is final. The record goes to the director; the result goes to Joseph
# through the director with the declared wording per outcome. Launched from a /dev/shm copy of itself (its path is
# $1), which it deletes at exit.
SELF=$1
R=/pscratch/sd/j/josephrb/fd-rpd-20261103
M=8727c63e1d32599039ea977d833c5de25a9089d6
D=$R/deploy-10
LOG=$R/logs/readout.log
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
[ -d "$R/logs" ] && [ -d "$R/tmp" ] && [ -d "$R/receipts" ] && [ ! -e "$D" ] && [ ! -e "$LOG" ] || bail
job=$(dd if="$R/logs/jobB.jobid" iflag=noatime status=none)
[ -n "$job" ] && [ "$(sacct -j "$job" -X -n -P -o State,ExitCode | head -1)" = "COMPLETED|0:0" ] || bail   # job B ended well
done_lanes=0
for i in 0 1 2 3 4 5 6 7; do
  dd if="$R/lanes-b/line$i-$job.log" iflag=noatime status=none | grep -q "^\[f1-lane\] lane=$i done " && done_lanes=$((done_lanes + 1))
done
[ "$done_lanes" -eq 8 ] || bail                                  # every lane of job B reached done (section 2)
[ -e "$R/control/controls.json" ] && [ ! -e "$R/readout" ] || bail
exec > "$LOG" 2>&1
finish() { echo "readout rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/logs/readout.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "job B $job: $(sacct -j "$job" -X -n -P -o JobID,State,ExitCode,Elapsed,NNodes | head -1); lanes done: $done_lanes of 8"
cp "$SELF" "$R/receipts/rpd_readout_connect.sh"

# ---- the deploy: a fresh clone at M', clean, every section 7 blob at M' and in the tree
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/logs/clone-10.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M'"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
DECL=docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION-PART2.md
rows=0; bad=0
while read -r p b; do
  rows=$((rows + 1))
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done < <(sed -n '/^## 7\./,/^## 8\./p' "$D/$DECL" | sed -n 's/^| `\([^`]*\)` | `\([0-9a-f]\{40\}\)` |$/\1 \2/p')
echo "section 7: $rows blobs, $bad mismatches"
[ "$rows" -eq 23 ] && [ "$bad" -eq 0 ] || { echo "STOP: section 7 blobs"; finish 9; }

# ---- root_6_28 by prefix; verify-staged, then fd_rpd.py readout
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; finish 2; }
export TMPDIR="$R/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# one thread per library, niced (the director, 2026-11-04: a shared login node)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19"
PY=(nice -n 19 env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -B)
cd "$R" || finish 9
"${PY[@]}" "$D/nd-unfolding/fd_rpd_inputs.py" verify-staged --r "$R" --deploy "$D" > "$R/logs/verify-staged-10.out" 2>&1
rc=$?; echo "verify-staged rc=$rc"; tail -2 "$R/logs/verify-staged-10.out"
[ $rc = 0 ] || { echo "STOP at verify-staged (final)"; finish $rc; }
date -u +%FT%TZ
"${PY[@]}" "$D/nd-unfolding/fd_rpd.py" readout --r "$R" --definition "$D/nd-unfolding/pv-ladder/readouts/h2_definition.json" \
    --deploy "$D" --out-json "$R/readout/fd_rpd.json" > "$R/logs/readout.out" 2>&1
rc=$?
echo "readout rc=$rc"; tail -12 "$R/logs/readout.out"
[ -e "$R/readout/fd_rpd.json" ] && echo "readout record sha256 $(dd if="$R/readout/fd_rpd.json" iflag=noatime status=none | sha256sum | cut -d' ' -f1)"
[ $rc = 0 ] || { echo "STOP at readout (final)"; finish $rc; }
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish 0
