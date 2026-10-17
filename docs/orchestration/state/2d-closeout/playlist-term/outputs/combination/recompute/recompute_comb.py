#!/usr/bin/env python3
"""Independent recompute of the S5 + C_PL combination (COMBINATION.md sections 2-4).

Written without reading or importing combine_s5.py. The ROOT reader is reused from the
independent playlist-term verifier (recompute/recompute_pl.py). Usage: recompute_comb.py OUT.json
"""
import hashlib
import json
import sys

import numpy as np
import ROOT

S5 = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz"
PL = "/pscratch/sd/j/josephrb/tmp-playlist-term-20261016/out/playlist_term.npz"
WCOV = "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_cov.npz"
AJ = "/pscratch/sd/j/josephrb/tmp-playlist-term-20261016/in/analysis.json"
PINS = {
    S5: "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc",
    PL: "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476",
    WCOV: "70c4daf2048875538eb74ee507b1d8741ca4ff80a8a351f0500450151a19ed1d",
    AJ: "05edff61673fed987f487f8c19ad25ec055db8118491815b9c263f3a7c3de72b",
}
PER = ("PA", "PB", "PC")
RES = sys.argv[1]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


# --- reader reused from recompute_pl.py -------------------------------------------------
def edges(ax):
    n = ax.GetNbins()
    return np.array([ax.GetBinLowEdge(i) for i in range(1, n + 1)] + [ax.GetBinUpEdge(n)])


def h2(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.empty((nx, ny))
    for i in range(nx):
        for j in range(ny):
            a[i, j] = h.GetBinContent(i + 1, j + 1)
    return a


def read(path):
    f = ROOT.TFile.Open(path)
    assert f and not f.IsZombie(), path
    hx = f.Get("hXSec2D")
    ept, epz = edges(hx.GetXaxis()), edges(hx.GetYaxis())
    X = h2(hx)
    T = h2(f.Get("hTruth2D"))
    hc = f.Get("hOFCompleteness2D")
    assert np.array_equal(edges(hc.GetXaxis()), ept) and np.array_equal(edges(hc.GetYaxis()), epz)
    Cm = h2(hc)
    hf = f.Get("hFlux_pt")
    assert hf.GetNbinsX() == X.shape[0]
    assert np.allclose(edges(hf.GetXaxis()), ept)
    phi = np.array([hf.GetBinContent(i) for i in range(1, hf.GetNbinsX() + 1)])
    pot = float(f.Get("dataPOT").GetVal())
    nn = float(f.Get("nNucleons").GetVal())
    f.Close()
    w = np.outer(np.diff(ept), np.diff(epz))
    den = Cm * phi[:, None] * nn * pot * w
    ok = (Cm > 0) & (phi[:, None] > 0)
    t = np.zeros_like(T)
    t[ok] = T[ok] / den[ok] * 1.0e4
    return dict(X=X, t=t, ept=ept, epz=epz)
# -----------------------------------------------------------------------------------------


def sym(M):
    return 0.5 * (M + M.T)


def pinv(M, rc=1e-12):
    lam, V = np.linalg.eigh(sym(M))
    k = lam > rc * lam.max()
    return (V[:, k] / lam[k]) @ V[:, k].T


def chi2(b, M):
    return float(b @ pinv(M) @ b)


def rank(M, rc):
    lam = np.linalg.eigvalsh(sym(M))
    return int(np.sum(lam > rc * lam.max())), int(np.sum(np.abs(lam) > rc * np.abs(lam).max()))


def maxrel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.max(np.abs(a - b)) / np.max(np.abs(b)))


out = {"sha256": {}}
for p, h in PINS.items():
    got = sha(p)
    out["sha256"][p] = got
    assert got == h, (p, got)

aj = json.load(open(AJ))
for X in PER:
    p = aj["_roles"][X]["s42"]
    got = sha(p)
    out["sha256"][p] = got
    assert got == aj["_runs"][p]["sha256"], (p, got)

S = np.load(S5)
Z = np.load(PL)
W = np.load(WCOV)
T, U, ST, C8 = S["total"], S["universe"], S["stat"], S["c08"]
for M in (T, U, ST, C8):
    assert M.shape == (205, 205)
F = S["functionals"]
assert F.shape == (31, 205) and S["area"].shape == (205,) and S["cells_x_EU"].shape == (205,)
CPL = Z["C_PL"]
x = Z["x"]
assert CPL.shape == (205, 205) and x.shape == (205,)
cells = Z["cells"]

chk = {}
# 1. S5 product and Q
chk["total_minus_sum_over_max"] = maxrel(T, U + ST + C8)
chk["total_asym_over_max"] = float(np.max(np.abs(T - T.T)) / np.max(np.abs(T)))
lt = np.linalg.eigvalsh(sym(T))
chk["total_mineig_over_max"] = float(lt.min() / lt.max())
Q = T + CPL
chk["Q_asym_over_max"] = float(np.max(np.abs(Q - Q.T)) / np.max(np.abs(Q)))
lq = np.linalg.eigvalsh(sym(Q))
chk["Q_mineig_over_max"] = float(lq.min() / lq.max())
# 2. alignment
EUf = W["EU"].ravel(order="C")
chk["cells_npz_eq_workcov"] = bool(np.array_equal(cells, W["cells"]))
chk["cells_eq_nonzero_EU"] = bool(np.array_equal(np.sort(cells), np.flatnonzero(EUf)))
chk["x_vs_cells_x_EU_maxrel"] = float(np.max(np.abs(x / S["cells_x_EU"] - 1)))
chk["x_vs_workcov_EU_maxrel"] = float(np.max(np.abs(x / EUf[cells] - 1)))
chk["functionals_vs_npz_F_over_max"] = maxrel(F, Z["F"])
chk["area_vs_npz_F0_over_max"] = maxrel(S["area"], Z["F"][0])
chk["area_vs_F0_over_max"] = maxrel(S["area"], F[0])

# per-period raw results
runs = {X: read(aj["_roles"][X]["s42"]) for X in PER}
flat = lambda a: a.ravel(order="C")[cells]  # noqa: E731
xs = {X: flat(runs[X]["X"]) for X in PER}
r = {X: xs[X] / flat(runs[X]["t"]) for X in PER}
for X in PER:
    chk[f"r_{X}_vs_npz_maxrel"] = float(np.max(np.abs(r[X] / Z[f"r_{X}"] - 1)))
e = {X: Z[f"e_{X}"] for X in PER}
out["checks"] = chk

# 2. budget
VL = (W["cov__hCov_combined"] + W["cov__ML"])[np.ix_(cells, cells)] if W["cov__ML"].shape[0] != 205 else \
    W["cov__hCov_combined"] + W["cov__ML"]
out["VL_shape_raw"] = list(W["cov__ML"].shape)
mats = {"VL175": VL, "S5_universe": U, "S5_stat": ST, "S5_c08": C8, "S5_total": T, "C_PL": CPL, "S5_plus_C_PL": Q}
Fx = F @ x
sVL = np.sqrt(np.diag(VL))
bud = {}
for nm, M in mats.items():
    c = 100 * np.sqrt(np.diag(M)) / x
    fs = 100 * np.sqrt(np.diag(F @ M @ F.T)) / np.abs(Fx)
    bud[nm] = dict(cell_median=float(np.median(c)), cell_p84=float(np.percentile(c, 84)), cell_max=float(c.max()),
                   integral=float(fs[0]), pt=fs[1:15].tolist(), pz=fs[15:31].tolist(),
                   median_sigma_ratio_to_VL175=float(np.median(np.sqrt(np.diag(M)) / sVL)))
out["budget"] = bud

# 3. effect of C_PL on S5
inc = np.sqrt(np.diag(Q) / np.diag(T)) - 1
fT, fQ = np.diag(F @ T @ F.T), np.diag(F @ Q @ F.T)
finc = np.sqrt(fQ / fT) - 1
out["effect"] = dict(cell_sigma_increase_median=float(np.median(inc)), cell_sigma_increase_max=float(inc.max()),
                     integral_sigma_increase=float(finc[0]), max_functional_increase=float(finc.max()),
                     argmax_functional=int(finc.argmax()),
                     cpl_variance_share_cell_median=float(np.median(1 - np.diag(T) / np.diag(Q))),
                     cpl_variance_share_integral=float(1 - fT[0] / fQ[0]))

# 4. chi2 rows
vecs = {}
for X in ("PB", "PC"):
    vecs[f"b_{X}_dr"] = e[X] * (r[X] / r["PA"] - 1) * x
    vecs[f"bias_{X}"] = e[X] * (xs[X] / xs["PA"] - 1) * x
Pt, Pz = F[1:15], F[15:31]
mets = {"VL175": VL, "VL175_plus_C_PL": VL + CPL, "S5_total": T, "S5_plus_C_PL": Q}
c2 = {}
for nm, b in vecs.items():
    c2[nm] = {}
    for pk, P in (("pz", Pz), ("pt", Pt)):
        for mn, M in mets.items():
            c2[nm][f"{pk}_vs_{mn}"] = chi2(P @ b, P @ M @ P.T)
out["chi2"] = c2

# 5. ranks
out["ranks_rcond1e-10"] = {"S5_total": rank(T, 1e-10), "Q": rank(Q, 1e-10)}

json.dump(out, open(RES, "w"), indent=1)
print(json.dumps(out, indent=1))
