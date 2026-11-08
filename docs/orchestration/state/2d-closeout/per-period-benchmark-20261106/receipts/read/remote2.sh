C2=/pscratch/sd/j/josephrb/per-period-benchmark-20261106/read
TAR_SHA=bb1e00e4ed9c8ef27b9681a9daf47078b9d89d5559937104f778afd5c06c716e
D=docs/orchestration/state/2d-closeout/per-period-benchmark-20261106
PINS="9bc3921bc86b62813d8297e66012f1e941398ce641a67fc5f46fe6fa6cdd5961  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/DECLARATION.md
94fc5a3d23ffcdf6c16629aef328979f1940cfbc373cc0790761be75d331d70b  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/per_period_benchmark.py
8f3ccf8aa052d377e6a84e797a61efea4df2b0f8645c64bcc003ab1ea9ef68c0  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/test_per_period_benchmark.py
9c05e5e1aa3d12d6782a23c0b5625ea63de429071667761b026366d92b6a3be0  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/INPUTS.sha256"
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
