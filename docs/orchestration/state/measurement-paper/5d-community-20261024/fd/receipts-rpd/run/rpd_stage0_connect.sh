#!/bin/bash
# RPD stage 0 (the dr_PB/PA step on 5B's period unfolds; part 1 section 3), on a login node, detached
# (FD-RPD-BINDING-2.md rulings 4 and 5; FD-RPD-DECLARATION-PART2.md section 2). A fresh clone at M' into
# $R/deploy-3 (each connect from a fresh clone), the section 7 blobs, verify-staged (binding 2 A1), then fd_rpd.py stage0. 0 node-h, no job.
# Reads the staged copies under $R only; probe reads through O_NOATIME (dd iflag=noatime). Writes only under $R. No
# set -u (it aborts the root_6_28 activation). Any stop is final; the record goes to the director before job A.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
R=/pscratch/sd/j/josephrb/fd-rpd-20261103
M=8727c63e1d32599039ea977d833c5de25a9089d6
D=$R/deploy-3
LOG=$R/logs/stage0.log
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
[ -d "$R/logs" ] && [ -d "$R/tmp" ] && [ -d "$R/receipts" ] && [ ! -e "$D" ] && [ ! -e "$LOG" ] || bail
[ "$(dd if="$R/logs/stageS-2.done" iflag=noatime status=none)" = 0 ] || bail   # stage S's second connect passed
[ ! -e "$R/control" ] || bail                                                 # stage 0 writes the first record there
mkdir "$R/control" || bail
exec > "$LOG" 2>&1
finish() { echo "stage0 rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/logs/stage0.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/receipts/rpd_stage0_connect.sh"

# ---- the deploy: a fresh clone at M', clean, every section 7 blob at M' and in the tree
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/logs/clone-stage0.log" 2>&1 || { echo "STOP: clone"; finish 3; }
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

# ---- root_6_28 by prefix; verify-staged, then fd_rpd.py stage0
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; finish 2; }
export TMPDIR="$R/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# one thread per library, niced (the director, 2026-11-04: a shared login node)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19"
PY=(nice -n 19 env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -B)
cd "$R" || finish 9
"${PY[@]}" "$D/nd-unfolding/fd_rpd_inputs.py" verify-staged --r "$R" --deploy "$D" > "$R/logs/verify-staged-3.out" 2>&1
rc=$?; echo "verify-staged rc=$rc"; tail -2 "$R/logs/verify-staged-3.out"
[ $rc = 0 ] || { echo "STOP at verify-staged (final)"; finish $rc; }
date -u +%FT%TZ
"${PY[@]}" "$D/nd-unfolding/fd_rpd.py" stage0 --r "$R" --definition "$D/nd-unfolding/pv-ladder/readouts/h2_definition.json" \
    --deploy "$D" --out-json "$R/control/stage0.json" > "$R/logs/stage0.out" 2>&1
rc=$?
echo "stage0 rc=$rc"; tail -3 "$R/logs/stage0.out"
[ $rc = 0 ] || { echo "STOP at stage0 (final)"; finish $rc; }
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish 0
