#!/bin/bash
# rdx_read receipts at a committed head, in a clean clone: tests (laptop python and a py3.10 venv), the mutation check,
# and the committed-record path (definition, phi_c, sigma_c, tasks, pins) loaded through the reader with no products.
S=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a2dcbe62-b017-4025-a124-a6659ca362f5/scratchpad
C=$S/rdx-read-rcpt/clone; O=$S/rdx-read-rcpt/out; HEADSHA=${1:?head}
mkdir -p "$O"
git clone -q --no-hardlinks /Users/josephbailey/tier3-wt "$C" || exit 2
git -C "$C" -c advice.detachedHead=false checkout -q "$HEADSHA" || exit 2
cd "$C" || exit 2
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
hdr() { echo "# HEAD $(git -C "$C" rev-parse HEAD)"; echo "# clean clone, serial, $1, $(date -u +%FT%TZ)"
  (cd "$C/nd-unfolding/rdx" && shasum -a 256 rdx_read.py test_rdx_read.py rdx_read_mutation.py ../rsn/rsn_read.py ../pv-ladder/build_cmodel5d.py | sed 's/^/# /'); }
PYV="Python $(python3 -c 'import sys; print(sys.version.split()[0])'), numpy $(python3 -c 'import numpy; print(numpy.__version__)')"
{ hdr "$PYV"; echo "# command: python3 -B -m unittest -v nd-unfolding/rdx/test_rdx_read.py"
  python3 -B -m unittest -v nd-unfolding/rdx/test_rdx_read.py 2>&1; echo "# exit $?"; } > "$O/tests.txt"
P10="$S/rdx-c5/py310/bin/python"
V10="$($P10 -c 'import sys, numpy; print("Python %s, numpy %s" % (sys.version.split()[0], numpy.__version__))')"
{ hdr "a uv venv matching omnifold_py310's versions: $V10"; echo "# command: python -B -m unittest -v nd-unfolding/rdx/test_rdx_read.py"
  "$P10" -B -m unittest -v nd-unfolding/rdx/test_rdx_read.py 2>&1; echo "# exit $?"; } > "$O/tests_py310.txt"
{ hdr "$PYV"; echo "# command: python3 -B nd-unfolding/rdx/rdx_read_mutation.py --jobs 4"
  python3 -B nd-unfolding/rdx/rdx_read_mutation.py --jobs 4 2>&1; echo "# exit $?"; } > "$O/mutation.txt"
{ hdr "$PYV"; echo "# the committed-record path, no products: B5.load_definition, rsn_read.rounding_floor, the F1 readout's sigma, rdx_tasks.tsv, the pins"
  python3 -B - <<'PY' 2>&1; echo "# exit $?"; } > "$O/committed_path.txt"
import json, sys
sys.path.insert(0, "nd-unfolding/rdx")
import numpy as np
import rdx_read as R
import build_cmodel5d as B5
rmap, n = B5.load_definition(R.DEFINITION, R.STAGE1, B5.EXPECT)[:2]
L = lambda p: json.loads(open(p).read())
phi = R.RR.rounding_floor(L(R.RR.I0), L(R.RR.CMODEL_JSON))
sig = np.asarray(L(R.RR.F1_READOUT)[R.RR.SIGMA_KEY]["C_total"], float)
print("definition:", n, "reporting cells, fine map", rmap.shape[0], "entries")
print("phi_c (%):", [round(100 * v, 4) for v in phi])
print("phi_c median/min/max (%):", round(100 * float(np.median(phi)), 3), round(100 * float(phi.min()), 3), round(100 * float(phi.max()), 3))
print("sigma_c:", [round(float(v), 5) for v in sig])
print("tasks:", list(R.tasks()))
print("pins:", {k.lstrip("./"): v[:8] for k, v in R.sums(R.SUMS).items()}, "ratio", R.sums(R.PVL_SUMS)[R.RATIO_KEY][:8])
PY
echo "# clone status: $(git status --porcelain --untracked-files=all | wc -l | tr -d ' ') lines" >> "$O/committed_path.txt"
echo done
