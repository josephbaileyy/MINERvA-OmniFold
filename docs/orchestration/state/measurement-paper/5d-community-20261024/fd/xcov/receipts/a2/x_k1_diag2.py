"""X-A2 diagnosis (read-only): K1's 2D band comparison for NormDISCC (and two passing bands as controls), magnitudes
only: S5_R's own block and the RE-2 universes' recomputation, projected to the quadrants and over the 205 cells, and
the spread between the universes. No entry, no cross block."""
import json, sys
sys.path.insert(0, "nd-unfolding")
import numpy as np, fd_xcov as X, fd_xcov_steps as XS, fd_gencmp as gc
inp = X.Inputs()
defn = json.loads(XS.DEFINITION.read_text())
qz, pl, s5 = inp.npz(XS.Q_R), inp.npz(XS.CPL_R), inp.npz(XS.S5_R)
cells2d, area = np.asarray(pl["cells"], int), np.asarray(qz["area"], float)
_, (e_pt, e_pz) = gc.root_hist(inp.bytes(XS.RE2 / "partb/out/ER/xsec.root"), "hXSec2D")
A, B = X.quadrant_vectors(defn, cells2d, area, np.asarray(e_pt, float), np.asarray(e_pz, float))
out = {}
for b in ("NormDISCC", "EtaNCEL", "MaRES"):
    v = np.array([XS.hist2d_cells(inp.bytes(XS.RE2 / f"partb/out/U_{b}_{i}/xsec.root"), cells2d) for i in (0, 1)])
    own = np.asarray(s5[f"band_{b}"], float)
    rec = X.cross_cov(v, v)
    recq, ownq = X.cross_cov(v @ B.T, v @ B.T), B @ own @ B.T
    mx = lambda m: float(np.abs(m).max())
    out[b] = {"univ_spread_rel": float(np.abs(v[0] - v[1]).max() / np.abs(v).max()),
              "universes_bitwise_equal": bool(np.array_equal(v[0], v[1])),
              "max_own_cells": mx(own), "max_rec_cells": mx(rec), "max_ownq": mx(ownq), "max_recq": mx(recq),
              "own_all_zero": bool(not own.any()), "rec_all_zero": bool(not rec.any()),
              "same_block_q": bool(X.same_block(recq, ownq)),
              "diffq_over_scale": (mx(recq - ownq) / max(mx(recq), mx(ownq))) if max(mx(recq), mx(ownq)) > 0 else None,
              "max_ownq_over_max_stat_q": mx(ownq) / mx(B @ np.asarray(s5["stat"], float) @ B.T)}
print(json.dumps(out))
