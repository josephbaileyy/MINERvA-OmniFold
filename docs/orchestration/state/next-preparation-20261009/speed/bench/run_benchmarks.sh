#!/bin/bash
# Run the loader/fill benchmarks one at a time (one compute thread each) and
# append one JSON line per run to $OUT. Usage: run_benchmarks.sh TREE_DIR OUT
set -euo pipefail
TREES="${1:?tree dir}"
OUT="${2:?output jsonl}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/opt/homebrew/bin/python3.13
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
: > "$OUT"
for tree in synth_rows1000000_extra0 synth_rows200000_extra0 synth_rows200000_extra192; do
  for v in pinned status columnar; do
    echo "{\"loadavg_start\": \"$(sysctl -n vm.loadavg)\", \"variant\": \"$v\", \"tree\": \"$tree\"}" >> "$OUT"
    "$PY" -I "$HERE/bench_loader.py" "$v" "$TREES/$tree.root" --repeats 5 >> "$OUT"
  done
done
echo "{\"loadavg_start\": \"$(sysctl -n vm.loadavg)\", \"variant\": \"truth\"}" >> "$OUT"
"$PY" -I "$HERE/bench_loader.py" truth "$TREES/synth_rows1000000_extra0.root" --repeats 5 >> "$OUT"
for v in fill_loop fill_n; do
  echo "{\"loadavg_start\": \"$(sysctl -n vm.loadavg)\", \"variant\": \"$v\"}" >> "$OUT"
  "$PY" -I "$HERE/bench_loader.py" "$v" "$TREES/synth_rows1000000_extra0.root" --repeats 3 >> "$OUT"
done
