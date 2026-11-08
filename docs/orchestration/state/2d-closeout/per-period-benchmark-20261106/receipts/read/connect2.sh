#!/bin/bash
# Per-period 2D benchmark, CONNECT 2: the read (BINDING-1.md ruling 3, PR #874). Runs only after connect 1's receipt
# reported PASS.
#
# Local part:  a fresh clone at M with empty porcelain; the four pins re-hashed and COMPARED; `git archive` deploy.
# Remote part (one `bash -s` on a login node, root_6_28, nice 19, idle I/O, BLAS 1 thread), each a separate step:
#   1. archive digest COMPARED, extracted to a new namespace, pins re-hashed and COMPARED
#   2. the cov2d fence (squeue): STOP on any cov2d-* job
#   3. per_period_benchmark.py copy    (O_NOATIME copies of the 39 operands; no hashing)
#   4. per_period_benchmark.py verify  (digests COMPARED; rc 0 required)
#   5. the fence again, then per_period_benchmark.py read  (controls first; readings only if every control passes)
# 0 node-h. Usage: bash connect2.sh <workdir>; exit = the read's rc (0 readings, 3 STOP, 4 refused) or a STOP code.
# No set -e/-u/pipefail: every rc is read explicitly, unpiped.

M=a7af2e614f2d65ca10d169e6d73582e83f9ecf1d
HOST=saul.nersc.gov
SSH=(ssh -o ControlPath=none -o BatchMode=yes "$HOST")
NS=/pscratch/sd/j/josephrb/per-period-benchmark-20261106
C2=$NS/read
SRC_REPO=/Users/josephbailey/local-research/MINERvA-OmniFold-per-period
D=docs/orchestration/state/2d-closeout/per-period-benchmark-20261106
PATHS=(technote_style.py 2d-unfolding/compare_to_paper_fullcov.py 2d-unfolding/uq/reported_cells.py
       2d-unfolding/minerva_paper_anc "$D"
       docs/orchestration/state/2d-closeout/period-unfold-20261014/scripts
       docs/orchestration/state/2d-closeout/playlist-spread-20261014/coverage/scripts
       docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/periods/analysis.json)
PINS="9bc3921bc86b62813d8297e66012f1e941398ce641a67fc5f46fe6fa6cdd5961  $D/DECLARATION.md
94fc5a3d23ffcdf6c16629aef328979f1940cfbc373cc0790761be75d331d70b  $D/per_period_benchmark.py
8f3ccf8aa052d377e6a84e797a61efea4df2b0f8645c64bcc003ab1ea9ef68c0  $D/test_per_period_benchmark.py
9c05e5e1aa3d12d6782a23c0b5625ea63de429071667761b026366d92b6a3be0  $D/INPUTS.sha256"

W=${1:?usage: connect2.sh <workdir>}
[ -e "$W" ] && { echo "STOP: $W exists; use a new workdir"; exit 2; }
mkdir -p "$W" || exit 2
LOG=$W/connect2.log
say() { echo "$*" | tee -a "$LOG"; }

say "== connect2 $(date -u +%FT%TZ) M=$M"
git clone -q --no-checkout "$SRC_REPO" "$W/clone" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: clone rc $rc"; exit 3; }
git -C "$W/clone" checkout -q "$M" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: checkout rc $rc"; exit 3; }
head=$(git -C "$W/clone" rev-parse HEAD)
[ "$head" = "$M" ] || { say "STOP: HEAD $head != M"; exit 3; }
porc=$(git -C "$W/clone" status --porcelain)
[ -z "$porc" ] || { say "STOP: porcelain not empty"; exit 3; }
(cd "$W/clone" && printf '%s\n' "$PINS" > "$W/pins.sha256" && shasum -a 256 -c "$W/pins.sha256") >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: local pins differ (rc $rc)"; exit 3; }
say "clone at M, porcelain empty, pins 4/4 equal"
git -C "$W/clone" archive -o "$W/code-M.tar" "$M" "${PATHS[@]}" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: archive rc $rc"; exit 3; }
TAR_SHA=$(shasum -a 256 "$W/code-M.tar" | awk '{print $1}')
say "archive sha256 $TAR_SHA"

cat > "$W/remote2.sh" <<REMOTE
C2=$C2
TAR_SHA=$TAR_SHA
D=$D
PINS="$PINS"
REMOTE
cat >> "$W/remote2.sh" <<'REMOTE'
fence() {
  squeue -u josephrb -h -o '%i|%j|%T' > "R/squeue_$1.txt" 2>"R/squeue_$1.err"; local rc=$?
  echo "fence $1: squeue rc $rc, rows $(wc -l < "R/squeue_$1.txt")"
  [ $rc -eq 0 ] || { echo "STOP: squeue failed; the fence cannot be checked"; exit 14; }
  if grep -q '|cov2d-' "R/squeue_$1.txt"; then echo "STOP: a cov2d-* job is queued or running"; exit 15; fi
}
echo "== remote $(date -u +%FT%TZ) $(hostname)"
cd "$C2" || { echo "STOP: no $C2"; exit 10; }
got=$(sha256sum code-M.tar | awk '{print $1}')
[ "$got" = "$TAR_SHA" ] || { echo "STOP: archive digest $got != $TAR_SHA"; exit 11; }
mkdir code R || exit 12
tar -xf code-M.tar -C code || { echo "STOP: untar"; exit 12; }
printf '%s\n' "$PINS" > R/pins.sha256
(cd code && sha256sum -c ../R/pins.sha256) > R/pins.check 2>&1; rc=$?
cat R/pins.check
[ $rc -eq 0 ] || { echo "STOP: remote pins differ"; exit 13; }
fence before_copy
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 16; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=$(command -v python3)
"$PY" -c 'import sys; print(sys.version)' > R/env.txt 2>&1
S="$C2/code/$D/per_period_benchmark.py"
echo "== step copy"
nice -n 19 ionice -c 3 "$PY" -B "$S" copy --dest "$C2/copies" > R/copy.log 2>&1; rc=$?
echo "copy rc $rc"; [ $rc -eq 0 ] || { tail -n 5 R/copy.log; echo "STOP at copy"; exit 21; }
echo "== step verify"
nice -n 19 ionice -c 3 "$PY" -B "$S" verify --dest "$C2/copies" > R/verify.log 2>&1; rc=$?
cp "$C2/copies/verify.json" R/verify.json 2>/dev/null; cp "$C2/copies/copies.json" R/copies.json 2>/dev/null
echo "verify rc $rc"; [ $rc -eq 0 ] || { tail -n 5 R/verify.log; echo "STOP at verify"; exit 22; }
fence before_read
echo "== step read"
nice -n 19 ionice -c 3 "$PY" -B "$S" read --dest "$C2/copies" --out "$C2/out" > R/read.log 2>&1; read_rc=$?
echo "read rc $read_rc"
cp "$C2"/out/* R/ 2>/dev/null
ls R
cd R && sha256sum * > ../SHA256SUMS.R && mv ../SHA256SUMS.R SHA256SUMS
exit $read_rc
REMOTE

say "== upload (new namespace; refuses if $C2 exists)"
"${SSH[@]}" "test ! -e $C2 && mkdir -p $C2 && cat > $C2/code-M.tar" < "$W/code-M.tar" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: upload rc $rc"; exit 4; }
say "== remote run"
"${SSH[@]}" bash -s < "$W/remote2.sh" > "$W/remote2.out" 2>&1; rrc=$?
cat "$W/remote2.out" >> "$LOG"
say "remote rc $rrc"
say "== fetch receipt"
"${SSH[@]}" "tar -C $C2 -cf - R" > "$W/R.tar" 2>>"$LOG"; rc=$?
[ $rc -eq 0 ] || { say "STOP: fetch rc $rc"; exit 5; }
mkdir -p "$W/receipt" && tar -xf "$W/R.tar" -C "$W/receipt" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: untar receipt rc $rc"; exit 5; }
cp "$W/remote2.out" "$W/receipt/R/remote2.out"
say "receipt in $W/receipt/R; remote rc $rrc"
exit $rrc
