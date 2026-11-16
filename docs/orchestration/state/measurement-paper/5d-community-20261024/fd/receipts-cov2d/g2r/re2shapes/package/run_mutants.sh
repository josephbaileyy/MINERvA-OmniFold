#!/bin/bash
# The driver's mutants (mutants.out.txt): each replaces one line of re2c_rollup_g2r.py in a copy and runs test_driver.sh
# on it; each must show a FAIL.
#   bash run_mutants.sh <wt> <M> <B>
WT=$1; M=$2; B=$3; H=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d "${TMPDIR:-/tmp}/mut.XXXXXX")
for m in "ro.partb_sums, ro.Path = partb_sums, path|ro.partb_sums = partb_sums" "ro.partb_sums, ro.Path = partb_sums, path|ro.Path = path" \
         "if mode == \"g2r\" and len(a) == 3|if len(a) == 3" "    if sha(tsv) != PRODUCTS_SHA:|    if False:"; do
  d=$(mktemp -d "$T/m.XXXX"); cp "$H/test_driver.sh" "$d/"
  python3 - "$m" "$H/re2c_rollup_g2r.py" "$d/re2c_rollup_g2r.py" <<'PY'
import sys
a, b = sys.argv[1].split("|"); s = open(sys.argv[2]).read(); assert s.count(a) == 1; open(sys.argv[3], "w").write(s.replace(a, b))
PY
  out=$(bash "$d/test_driver.sh" "$WT" "$M" "$B" 2>&1 | grep -E "^FAIL " | cut -c1-40 | tr "\n" ";")
  echo "MUTANT [$m] -> ${out:-SURVIVED}"
done
find "$T" -type f -exec rm -f {} +; find "$T" -depth -type d -exec rmdir {} \;
