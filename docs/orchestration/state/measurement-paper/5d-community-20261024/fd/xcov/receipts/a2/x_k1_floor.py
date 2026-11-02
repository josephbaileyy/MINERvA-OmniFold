"""X-A2 (read-only): the margin of a proposed K1 floor for the 2D NormDISCC block: |rec - own| (quadrants) against
K_TOL * PD_REL * max|B Q_R B^T| (Q_R <= C2q, so the floor is conservative), plus the same ratio for the 16-cell side's
largest band block, to show the floor binds only noise blocks. Magnitudes only."""
import json, sys
sys.path.insert(0, "nd-unfolding")
import numpy as np, fd_xcov as X, fd_xcov_steps as XS, fd_gencmp as gc
inp = X.Inputs()
defn = json.loads(XS.DEFINITION.read_text())
qz, pl, s5 = inp.npz(XS.Q_R), inp.npz(XS.CPL_R), inp.npz(XS.S5_R)
cells2d, area = np.asarray(pl["cells"], int), np.asarray(qz["area"], float)
_, (e_pt, e_pz) = gc.root_hist(inp.bytes(XS.RE2 / "partb/out/ER/xsec.root"), "hXSec2D")
A, B = X.quadrant_vectors(defn, cells2d, area, np.asarray(e_pt, float), np.asarray(e_pz, float))
Q2q = B @ np.asarray(qz["total_plus_C_PL"], float) @ B.T
mx = lambda m: float(np.abs(m).max())
v = np.array([XS.hist2d_cells(inp.bytes(XS.RE2 / f"partb/out/U_NormDISCC_{i}/xsec.root"), cells2d) for i in (0, 1)])
recq, ownq = X.cross_cov(v @ B.T, v @ B.T), B @ np.asarray(s5["band_NormDISCC"], float) @ B.T
floor = X.PD_REL * mx(Q2q)
bands = [k for k in s5 if k.startswith("band_")]
below = sorted(k for k in bands if mx(B @ np.asarray(s5[k], float) @ B.T) < floor)
print(json.dumps({"max_diff_q": mx(recq - ownq), "max_block_q": max(mx(recq), mx(ownq)), "max_Q2q": mx(Q2q),
                  "floor_PD_REL_x_maxQ2q": floor, "tol_x_floor": X.K_TOL * floor,
                  "passes_with_floor": mx(recq - ownq) <= X.K_TOL * max(mx(recq), mx(ownq), floor),
                  "margin": X.K_TOL * floor / mx(recq - ownq),
                  "block_over_maxQ2q": max(mx(recq), mx(ownq)) / mx(Q2q),
                  "2d_band_blocks_below_floor": below, "n_2d_band_blocks": len(bands)}))
