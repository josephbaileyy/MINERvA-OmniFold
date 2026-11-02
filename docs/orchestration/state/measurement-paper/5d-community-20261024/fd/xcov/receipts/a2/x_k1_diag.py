"""X-A2 diagnosis (read-only): K1's 16-cell band comparison for the multi-match bands, as magnitudes only (no entry,
no cross block): max|block| of S1's own block and of the products' recomputation (A-projected and at 16 cells), the
spread between the band's universes, and same_block's verdict. From the X-A2 head's code."""
import json, sys
from pathlib import Path
sys.path.insert(0, "nd-unfolding")
import numpy as np, fd_xcov as X, fd_xcov_steps as XS, fd_gencmp as gc, s1_assemble as sa
inp = X.Inputs()
defn = json.loads(XS.DEFINITION.read_text()); U = gc.cell_matrix()
qz, pl, s1 = inp.npz(XS.Q_R), inp.npz(XS.CPL_R), inp.npz(XS.S1_NPZ)
cells2d, area = np.asarray(pl["cells"], int), np.asarray(qz["area"], float)
_, (e_pt, e_pz) = gc.root_hist(inp.bytes(XS.RE2 / "partb/out/ER/xsec.root"), "hXSec2D")
A, B = X.quadrant_vectors(defn, cells2d, area, np.asarray(e_pt, float), np.asarray(e_pz, float))
by = {}
for b, i in XS.universe_list():
    by.setdefault(b, []).append(i)
out = {}
for b in ("EtaNCEL", "MaNCEL", "NormDISCC", "NormNCRES", "GEANT_Neutron", "MinosEfficiency", "Rvn1pi", "MaRES"):
    xs = np.array([U @ sa.xs(XS.S1DIR / f"S1_{b}_{i}.npz") for i in sorted(by[b])])
    X16 = xs @ A.T
    own = np.asarray(s1[f"C_band_{b}"], float)
    rec16, recq, ownq = X.cross_cov(xs, xs), X.cross_cov(X16, X16), A @ own @ A.T
    out[b] = {"n_univ": len(by[b]), "univ_spread_rel": float(np.abs(xs - xs.mean(0)).max() / np.abs(xs).max()),
              "max_own16": float(np.abs(own).max()), "max_rec16": float(np.abs(rec16).max()),
              "max_ownq": float(np.abs(ownq).max()), "max_recq": float(np.abs(recq).max()),
              "own16_all_zero": bool(not own.any()), "rec16_all_zero": bool(not rec16.any()),
              "same_block_q": X.same_block(recq, ownq), "same_block_16": X.same_block(rec16, own),
              "diff16_over_scale": (float(np.abs(rec16 - own).max() / max(np.abs(own).max(), np.abs(rec16).max()))
                                    if max(np.abs(own).max(), np.abs(rec16).max()) > 0 else None)}
print(json.dumps(out, default=lambda o: bool(o) if isinstance(o, np.bool_) else str(o)))
