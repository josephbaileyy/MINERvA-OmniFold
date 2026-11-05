#!/bin/bash
# COV2D connect CELLS: the pilot's reference cell sets, before the pilot (rolling audit part 4, P5; 0 node-h).
# The pilot's (2b) and section 9.12 controls use re2_k1.compare, whose same_cell_set needs each part B reference's own
# reported cells (hXSec2D > 0, C order) to equal E_R's 205. If U_MaRES_0's or S3_BeamAngleX0's set differed, the
# control would fail (a STOP) even on a bitwise reproduction. Here, on O_NOATIME copies of the three pinned products
# (E_R by its sha, the other two by part B's committed sums, exactly as cov2d_pilot.ref reads them), the sets are
# compared. Descriptive: the record goes to the director. Read-only on the products; nothing is written beside them.
# A login node, nice 19, taskset -c 8-11, threads 1, the pinned MAT environment (RPD's standard). A fresh clone at M in
# /dev/shm; the pilot (cov2d_pilot.py), re2_k1 and re2c_rollup blobs asserted; everything removed after.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-cells.sh >/dev/null 2>&1 </dev/null &
M=045364a835bfb8702b7301e3a71bbbb701cab091
W=/dev/shm/josephrb-cov2d-cells; DD=$W/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
RUN="nice -n 19 taskset -c 8-11"
finish() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1)"; rm -rf "$DD" "$W/tmp"; echo "rc=$?"; ls -d "$DD" "$W/tmp" 2>&1; echo "end=$(date -u +%FT%TZ)"; echo DONE; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-cells.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" \
    || { echo "STOP clone"; finish; exit 2; }
echo "head=$(git -C "$DD" rev-parse HEAD) porcelain=$(git -C "$DD" status --porcelain | wc -l)"
(cd "$DD" && git ls-tree HEAD 2d-unfolding/cov2d/cov2d_pilot.py 2d-unfolding/cov2d/cov2d_pseudo_write.py \
    2d-unfolding/re2/re2_k1.py 2d-unfolding/re2/partc/re2c_rollup.py nd-unfolding/fd_rpd_inputs.py) | tee "$W/blobs"
for b in cfbe69a787ffcd2aa8ba7c787ccd956249592c26 e6124ab0819fcd0803a5e3269f610d8c592321c0 62a1dc33bb78b324485c01d9139f2264f0cc62b1 e41940cb3b4af8f273f34723fb4389d4dac86e0a 7c2e018f1169a9be0c5642daab991c664acbefcf; do
    grep -q " $b	" "$W/blobs" || { echo "STOP blob $b"; finish; exit 2; }
done
PROBE='
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/2d-unfolding/cov2d")
import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)
import cov2d_pilot  # noqa: F401  (its path setup: re2, re2/partc)
import cov2d_pseudo_write as pw
import re2_k1 as k1
import re2c_rollup as ro
sums = ro.partb_sums()
out = {}
with tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"]) as td:
    for lab in ("ER", "U_MaRES_0", "S3_BeamAngleX0"):
        src = f"{ro.NS_R}/out/{lab}/xsec.root"
        want = pw.PINS["er"][1] if lab == "ER" else sums.get(f"{lab}/xsec.root")
        d = Path(td) / lab
        d.mkdir()
        a0 = os.stat(src).st_atime_ns
        path, sha = pw.copy_noatime(src, d, want)
        cells = np.flatnonzero(k1.xsec(path).ravel(order="C") > 0)
        out[lab] = {"sha256": sha, "pinned": want, "n_cells": int(cells.size), "cells": cells.tolist(),
                    "atime_unchanged": os.stat(src).st_atime_ns == a0}
er = set(out["ER"]["cells"])
for lab in ("U_MaRES_0", "S3_BeamAngleX0"):
    s = set(out[lab]["cells"])
    out[lab].update(same_as_ER=s == er, only_here=sorted(s - er), only_in_ER=sorted(er - s))
ok = out["ER"]["n_cells"] == 205 and all(out[l]["same_as_ER"] for l in ("U_MaRES_0", "S3_BeamAngleX0"))
print("CELLS " + json.dumps(out))
print("CELL-CHECK", "PASS" if ok else "FAIL", {l: out[l]["n_cells"] for l in out})
'
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  $RUN python -B -c "import sys, json; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; m = r.mat_environment(); print('MAT ' + json.dumps({'mapped': m['mapped_mat_files'], 'dictionary': m['plotutils_mnvh1d_dictionary']}))" || exit 8
  $RUN python -B -c "$PROBE" "$DD"
) > "$W/cells.log" 2>&1; echo "cells rc=$?"; grep "^CELL-CHECK\|^MAT\|Error\|error" "$W/cells.log" | head -8
finish
