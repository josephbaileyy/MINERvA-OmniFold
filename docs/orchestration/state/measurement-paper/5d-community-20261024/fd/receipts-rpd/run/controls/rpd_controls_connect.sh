#!/bin/bash
# RPD controls (C1, K2', N0-P; fd_rpd.py controls), on a login node, detached, niced, after job A ended COMPLETED 0:0
# (FD-RPD-BINDING-2.md and its addendum A1; FD-RPD-DECLARATION-PART2.md section 2). A fresh clone at M' into $R/deploy-6
# (each connect from a fresh clone), the section 7 blobs, verify-staged (binding 2 A1), then fd_rpd.py controls. 0 node-h,
# no job. Reads under $R only; probe reads through O_NOATIME (dd iflag=noatime). Writes only under $R. No set -u (it
# aborts the root_6_28 activation). Any stop is final; job B only after its PASS and the director's go. Launched from a
# /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
R=/pscratch/sd/j/josephrb/fd-rpd-20261103
M=8727c63e1d32599039ea977d833c5de25a9089d6
D=$R/deploy-6
LOG=$R/logs/controls.log
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
[ -d "$R/logs" ] && [ -d "$R/tmp" ] && [ -d "$R/receipts" ] && [ ! -e "$D" ] && [ ! -e "$LOG" ] || bail
job=$(dd if="$R/logs/jobA.jobid" iflag=noatime status=none)
[ -n "$job" ] && [ "$(sacct -j "$job" -X -n -P -o State,ExitCode | head -1)" = "COMPLETED|0:0" ] || bail   # job A ended well
[ -e "$R/control/stageD.json" ] && [ ! -e "$R/control/controls.json" ] || bail
exec > "$LOG" 2>&1
finish() { echo "controls rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/logs/controls.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "job A $job: $(sacct -j "$job" -X -n -P -o JobID,State,ExitCode,Elapsed,NNodes | head -1)"
cp "$SELF" "$R/receipts/rpd_controls_connect.sh"

# ---- the deploy: a fresh clone at M', clean, every section 7 blob at M' and in the tree
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/logs/clone-6.log" 2>&1 || { echo "STOP: clone"; finish 3; }
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

# ---- root_6_28 by prefix; verify-staged, then fd_rpd.py controls
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; finish 2; }
export TMPDIR="$R/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# one thread per library, niced (the director, 2026-11-04: a shared login node)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19"
PY=(nice -n 19 env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -B)
cd "$R" || finish 9
"${PY[@]}" "$D/nd-unfolding/fd_rpd_inputs.py" verify-staged --r "$R" --deploy "$D" > "$R/logs/verify-staged-6.out" 2>&1
rc=$?; echo "verify-staged rc=$rc"; tail -2 "$R/logs/verify-staged-6.out"
[ $rc = 0 ] || { echo "STOP at verify-staged (final)"; finish $rc; }
date -u +%FT%TZ
"${PY[@]}" "$D/nd-unfolding/fd_rpd.py" controls --r "$R" --definition "$D/nd-unfolding/pv-ladder/readouts/h2_definition.json" \
    --deploy "$D" --out-json "$R/control/controls.json" > "$R/logs/controls.out" 2>&1
rc=$?
echo "controls rc=$rc"; tail -6 "$R/logs/controls.out"
[ $rc = 0 ] || { echo "STOP at controls (final)"; finish $rc; }
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish 0
