#!/bin/bash
# A1a.2 receipts from a clean detached checkout: both suites (numpy 1.26 at seeds 0,1,2; numpy 2 at seed 0), both
# mutation checks, and the REQUIRED test against a95cc39f's ll5d.py. Writes to $OUT; never into the checkout.
set -u
C=/Users/josephbailey/cov2d-work/wt-a1a2-rcpt; OUT=$1; mkdir -p "$OUT"
P126=/Users/josephbailey/miniconda3/bin/python3; P2=/opt/homebrew/bin/python3.13
cd "$C/nd-unfolding"
H=$(git -C "$C" rev-parse HEAD)
hdr() {  # $1 title, $2 interpreter
  echo "# $1"
  echo "# date $(date -u +%FT%TZ)  made at HEAD $H, a clean checkout (porcelain $(git -C "$C" status --porcelain | wc -l | tr -d ' '))"
  echo "# python $($2 -c 'import sys,numpy;print(sys.version.split()[0], "numpy", numpy.__version__)')"
  (cd "$C/nd-unfolding" && shasum -a 256 ll5d.py ll5d_b.py fd_1b_c2.py tests/test_ll5d.py tests/test_ll5d_b.py tests/ll5d_a1a_mutation.py tests/ll5d_a1b_mutation.py | sed 's/^/# /')
}
for mod in test_ll5d test_ll5d_b; do
  for s in 0 1 2; do
    f="$OUT/$mod-numpy126-seed$s.txt"; { hdr "$mod.py at PYTHONHASHSEED=$s, numpy 1.26" $P126; PYTHONHASHSEED=$s OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 $P126 -B -m unittest tests.$mod 2>&1; echo "# rc=$?"; } > "$f"
  done
  f="$OUT/$mod-numpy2-seed0.txt"; { hdr "$mod.py at PYTHONHASHSEED=0, numpy 2" $P2; PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 $P2 -B -m unittest tests.$mod 2>&1; echo "# rc=$?"; } > "$f"
done
for m in ll5d_a1a_mutation ll5d_a1b_mutation; do
  f="$OUT/$m.txt"; { hdr "$m.py" $P126; $P126 -B tests/$m.py 2>&1; echo "# rc=$?"; } > "$f"
done
OLD=$(mktemp -d); git -C "$C" show a95cc39f7437170af0b65ba042934fad079e0ee2:nd-unfolding/ll5d.py > "$OLD/ll5d.py"
f="$OUT/required-test-at-a95cc39f.txt"
{ hdr "MatchedRows.test_vi_finds_every_matched_row_and_the_read_is_not_forced with a95cc39f's ll5d.py first on sys.path (expected: FAIL)" $P2
  echo "# a95cc39f ll5d.py sha256 $(shasum -a 256 "$OLD/ll5d.py" | cut -c1-64)"
  cd "$C/nd-unfolding/tests" && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 $P2 -B -c "import runpy, sys; sys.path.insert(0, '$OLD'); sys.argv = ['test_ll5d.py', 'MatchedRows.test_vi_finds_every_matched_row_and_the_read_is_not_forced']; runpy.run_path('test_ll5d.py', run_name='__main__')" 2>&1
  echo "# rc=$?"; } > "$f"
rm -rf "$OLD"
echo "porcelain_after= $(git -C "$C" status --porcelain | wc -l | tr -d ' ')"
for f in "$OUT"/*.txt; do echo "$(basename "$f"): $(grep -E '^Ran |^OK|^FAILED|UNMUTATED|ALL-KILLED|MUTATION-CHECK FAILED|^# rc=' "$f" | tr '\n' ' ')"; done
