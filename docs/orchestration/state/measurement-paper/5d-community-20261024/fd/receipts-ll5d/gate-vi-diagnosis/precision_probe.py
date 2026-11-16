"""Read-only: fd_1b_c2.row_match (a95cc39f, verbatim 342c0ce5) on synthetic rows built the way the two writers store
them: coordinates float32 on both sides (nn_dump_inputs.py:84; sweep_bank_5d.py:114/165), the signal weight a float64
product (unfold_nd_omnifold_unbinned.py:438,466), the denominator weight that product stored float32
(sweep_bank_5d.py:183,185). Controls: both weights float64; both float32."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1])))
import numpy as np
import fd_1b_c2 as c2
rng = np.random.default_rng(20261110)
n = 200_000
x64 = np.column_stack([rng.uniform(0, 2.5, n), rng.uniform(1.5, 20, n), rng.uniform(0, 1, n), rng.uniform(0, 2, n), rng.uniform(0.9, 3, n)])
coords = x64.astype(np.float32)                 # both writers round the ROOT doubles to float32
w64 = rng.uniform(0.2, 3.0, n) * 0.212405       # w_truth x pot_scale in float64 (the npz)
cells = np.arange(n) % c2.N_CELLS
ps = np.ones(n, bool)
fm_s, fm_d = cells, cells
def run(ws, wd, label):
    r = c2.row_match(coords, ws, ps, coords.astype(np.float64), wd, fm_s, fm_d)
    print(f"{label:58s} signal_unmatched={r['signal_rows_unmatched']}/{n} truth_unmatched={r['truth_rows_unmatched']}/{n} largest_share={r['largest_cell_unmatched_share']}")
run(w64, w64.astype(np.float32), "LL5D's storage: signal w float64, denominator w float32")
run(w64, w64, "control: both weights float64")
run(w64.astype(np.float32), w64.astype(np.float32), "control: both weights float32")
print("rows whose float64 weight is exactly float32-representable:", int(np.sum(w64.astype(np.float32).astype(np.float64) == w64)))
