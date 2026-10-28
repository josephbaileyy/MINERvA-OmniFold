"""Probe (local, numpy as recorded): (i) does the shape-only chi2 move under 1-ulp changes of C or V_g, or under the
other summation order of C's parts; (ii) which triangle np.linalg.cholesky reads. Run from the repo root."""
import json, sys
import numpy as np
sys.path.insert(0, "nd-unfolding")
import fd_g_compare as G
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
dp = json.load(open(f"{FD}/data-product/fd_data_product.json")); gr = json.load(open(f"{FD}/readout/fd_g_readout.json"))
f = np.array(dp["f"]); C = np.array(dp["matrices"]["C_total_plus_C_resp"])
Ce, Cm, Cr = (np.array(dp["matrices"][k]) for k in ("C_e", "C_model_abs", "C_resp"))
print("numpy", np.__version__)
print("C == (C_e + C_model_abs) + C_resp bit for bit:", np.array_equal((Ce + Cm) + Cr, C))
rng = np.random.default_rng(20261028); cells = [f"R{i:02d}" for i in range(16)]
for p in gr["predictions"]:
    idx = [cells.index(c) for c in p["cells"]]; g = np.zeros(16); Vg = np.zeros(16)
    g[idx] = p["g"]; Vg[idx] = (np.array(p["sigma_Vg_over_f"]) * f[idx]) ** 2
    base = {k: G.compare(f, g, Vg, C, idx, "x")[k]["chi2"] for k in ("total", "shape_only")}
    o = {k: G.compare(f, g, Vg, Ce + (Cm + Cr), idx, "x")[k]["chi2"] for k in ("total", "shape_only")}
    sh, tt = [], []
    for _ in range(20):
        E = rng.choice([-1.0, 0.0, 1.0], size=C.shape); E = np.triu(E) + np.triu(E, 1).T
        Cp = C + E * np.spacing(np.abs(C)); Vp = Vg + rng.choice([-1.0, 0.0, 1.0], 16) * np.spacing(Vg)
        r = G.compare(f, g, Vp, Cp, idx, "x")
        sh.append(abs(r["shape_only"]["chi2"] / base["shape_only"] - 1)); tt.append(abs(r["total"]["chi2"] / base["total"] - 1))
    print(f"{p['name']}: other order total {abs(o['total']/base['total']-1):.2e} shape {abs(o['shape_only']/base['shape_only']-1):.2e}; "
          f"20 one-ulp draws: total max {max(tt):.2e}, shape max {max(sh):.2e}; this host vs Stage G: total "
          f"{abs(base['total']/p['total']['chi2']-1):.2e} shape {abs(base['shape_only']/p['shape_only']['chi2']-1):.2e}")
A = np.array([[4.0, 1.0], [2.0, 3.0]])
L1 = np.linalg.cholesky(A); L2 = np.linalg.cholesky(np.tril(A) + np.tril(A, -1).T); L3 = np.linalg.cholesky(np.triu(A) + np.triu(A, 1).T)
print("cholesky reads the lower triangle:", np.array_equal(L1, L2) and not np.array_equal(L1, L3))

# (iii) after the independent review of 9ea78b92: what a one-ulp change of C does to the shape-only matrix, what one
# ulp of f does, the shape-only matrix's condition, and an independent solver (np.linalg.solve, 100 f f^T built as
# 100 * f_i * f_j) against Stage G's chi2
print("--- (iii)")
for p in gr["predictions"]:
    idx = [cells.index(c) for c in p["cells"]]; g = np.zeros(16); Vg = np.zeros(16)
    g[idx] = p["g"]; Vg[idx] = (np.array(p["sigma_Vg_over_f"]) * f[idx]) ** 2
    ii = np.ix_(idx, idx); fs = f[idx]
    Ms = C[ii] + np.diag(Vg[idx]) + G.SHAPE_LAMBDA * np.outer(fs, fs)
    Cp = C + np.spacing(np.abs(C))
    Msp = Cp[ii] + np.diag(Vg[idx]) + G.SHAPE_LAMBDA * np.outer(fs, fs)
    fp = f.copy(); k = idx[3]; fp[k] = np.nextafter(fp[k], np.inf)
    s0 = G.compare(f, g, Vg, C, idx, "x")["shape_only"]["chi2"]
    s1 = G.compare(fp, g, Vg, C, idx, "x")["shape_only"]["chi2"]
    d = (f - g)[idx]
    Mi = C[ii] + np.diag(Vg[idx]) + np.array([[100.0 * a * b for b in fs] for a in fs])
    lu = float(d @ np.linalg.solve(Mi, d))
    Mt = C[ii] + np.diag(Vg[idx])
    lut = float(d @ np.linalg.solve(Mt, d))
    print(f"{p['name']}: entries of the shape-only matrix changed by +1 ulp on every C entry: "
          f"{int(np.sum(Msp != Ms))} of {Ms.size}; 100 f f^T max / M max {np.abs(G.SHAPE_LAMBDA * np.outer(fs, fs)).max() / np.abs(C[ii] + np.diag(Vg[idx])).max():.2e}; "
          f"cond {np.linalg.cond(Ms):.2e}; one ulp of f[{cells[k]}] moves the shape-only chi2 by {abs(s1 / s0 - 1):.2e}; "
          f"np.linalg.solve vs Stage G shape-only {abs(lu / p['shape_only']['chi2'] - 1):.2e}, "
          f"total {abs(lut / p['total']['chi2'] - 1):.2e}")
