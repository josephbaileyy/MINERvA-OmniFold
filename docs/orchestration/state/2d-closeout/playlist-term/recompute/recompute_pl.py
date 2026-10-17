#!/usr/bin/env python3
"""Independent recomputation of the 2D playlist-consistency block (DESIGN 769d33e3 sections 2-4).

Written without reading or importing playlist_term.py. Reads raw per-period xsec.root and work_cov.npz.
"""
import hashlib
import json
import sys

import numpy as np
import ROOT

OUT = "/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/out"
WCOV = "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_cov.npz"
PROD = "/pscratch/sd/j/josephrb/tmp-playlist-term-20261016/out"
EU_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
PER = ("PA", "PB", "PC")
RES = sys.argv[1]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


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
    assert hf.GetNbinsX() == X.shape[0], (hf.GetNbinsX(), X.shape)
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
    return dict(X=X, t=t, phi=phi, pot=pot, nn=nn, ept=ept, epz=epz)


def pinv(M, rc=1e-12):
    M = 0.5 * (M + M.T)
    lam, V = np.linalg.eigh(M)
    k = lam > rc * lam.max()
    return (V[:, k] / lam[k]) @ V[:, k].T


def chi2(b, M):
    return float(b @ pinv(M) @ b)


W = np.load(WCOV)
cells = W["cells"]
assert cells.size == 205 and np.unique(cells).size == 205
runs = {"CTRL": read(f"{OUT}/pu_CTRL_s42/xsec.root")}
for X in PER:
    for tag in ["s42", "s43"] + [f"b{i:02d}" for i in range(1, 11)]:
        runs[f"{X}_{tag}"] = read(f"{OUT}/pu_{X}_{tag}/xsec.root")
eu = read(EU_ROOT)
ept, epz = runs["PA_s42"]["ept"], runs["PA_s42"]["epz"]
for r in list(runs.values()) + [eu]:
    assert np.array_equal(r["ept"], ept) and np.array_equal(r["epz"], epz)
NPT, NPZ = len(ept) - 1, len(epz) - 1
assert (NPT, NPZ) == (14, 16)
ipt, ipz = cells // NPZ, cells % NPZ

flat = lambda a: a.ravel(order="C")[cells]  # noqa: E731
x = flat(W["EU"])
x_eu_root = flat(eu["X"])
rep = {"x_vs_EU_root_maxrel": float(np.max(np.abs(x / x_eu_root - 1)))}

# positivity over all runs
pos = np.ones(205, bool)
for r in runs.values():
    pos &= (flat(r["X"]) > 0) & (flat(r["t"]) > 0)
rep["cells_all_positive"] = int(pos.sum())

xs = {X: flat(runs[f"{X}_s42"]["X"]) for X in PER}
ts = {X: flat(runs[f"{X}_s42"]["t"]) for X in PER}
r = {X: xs[X] / ts[X] for X in PER}
expo = np.stack([runs[f"{X}_s42"]["pot"] * runs[f"{X}_s42"]["phi"] for X in PER])
eshare_row = expo / expo.sum(0)
e = {X: eshare_row[i][ipt] for i, X in enumerate(PER)}
rep["e_row_spread"] = {X: float(np.ptp(eshare_row[i])) for i, X in enumerate(PER)}
rep["e"] = {X: float(e[X][0]) for X in PER}
V2 = sum(e[X] ** 2 for X in PER)
kf = V2 / (1 - V2)
rep["k"] = float(kf[0])
rep["k_spread"] = float(np.ptp(kf))


def block(q):
    m = sum(e[X] * q[X] for X in PER)
    g = {X: q[X] / m - 1 for X in PER}
    C = sum(np.outer(np.sqrt(kf * e[X]) * x * g[X], np.sqrt(kf * e[X]) * x * g[X]) for X in PER)
    return C, g, m


C_PL, g, m = block(r)
S_raw, g_raw, _ = block(xs)


def sref(q):
    bs = {X: e[X] * (q[X] / q["PA"] - 1) * x for X in ("PB", "PC")}
    return sum(np.outer(b, b) for b in bs.values()), bs


S_ref, b_dr = sref(r)
S_ref_raw, b_raw = sref(xs)
rep["sum_e_g_maxabs"] = float(np.max(np.abs(sum(e[X] * g[X] for X in PER))))
lam = np.linalg.eigvalsh(C_PL)
rep["eig_top4"] = lam[::-1][:4].tolist()
rep["rank_rcond1e-12"] = int(np.sum(lam > 1e-12 * lam.max()))
rep["min_eig_over_max"] = float(lam.min() / lam.max())

# functionals
dpt, dpz = np.diff(ept), np.diff(epz)
A = dpt[ipt] * dpz[ipz]
Ppt = np.zeros((NPT, 205))
Ppz = np.zeros((NPZ, 205))
Ppt[ipt, np.arange(205)] = dpz[ipz]
Ppz[ipz, np.arange(205)] = dpt[ipt]
F = np.vstack([A[None, :], Ppt, Ppz])


def fsig(C):
    s = 100 * np.sqrt(np.maximum(np.diag(F @ C @ F.T), 0)) / (F @ x)
    c = 100 * np.sqrt(np.diag(C)) / x
    return dict(integral=float(s[0]), pt=s[1:15].tolist(), pz=s[15:].tolist(),
                cell=dict(median=float(np.median(c)), p84=float(np.percentile(c, 84)), max=float(c.max())))


VL = W["cov__hCov_combined"] + W["cov__ML"]
sig = {nm: fsig(Cx) for nm, Cx in (("C_PL", C_PL), ("S_ref", S_ref), ("S_raw", S_raw), ("S_ref_raw", S_ref_raw))}
for nm, Cx in (("C_PL", C_PL), ("S_ref", S_ref), ("S_raw", S_raw), ("S_ref_raw", S_ref_raw)):
    sig[nm]["median_sigma_ratio_to_VL175"] = float(np.median(np.sqrt(np.diag(Cx)) / np.sqrt(np.diag(VL))))

# chi2
lamC, VC = np.linalg.eigh(C_PL)
span = VC[:, lamC > 1e-12 * lamC.max()]
chis = {}
vecs = {"b_PB_dr": b_dr["PB"], "b_PC_dr": b_dr["PC"], "bias_PB_raw_frozen": b_raw["PB"], "bias_PC_raw_frozen": b_raw["PC"]}
for nm, b in vecs.items():
    o = {}
    for pk, P in (("pz", Ppz), ("pt", Ppt)):
        o[f"{pk}_vs_VL175"] = chi2(P @ b, P @ VL @ P.T)
        o[f"{pk}_vs_VL175_plus_C_PL"] = chi2(P @ b, P @ (VL + C_PL) @ P.T)
    o["chi2_205_vs_VL175"] = chi2(b, VL)
    res = b - span @ (span.T @ b)
    o["out_of_span_euclid"] = float(np.linalg.norm(res) / np.linalg.norm(b))
    o["out_of_span_pz_chi2_frac"] = chi2(Ppz @ res, Ppz @ VL @ Ppz.T) / o["pz_vs_VL175"]
    chis[nm] = o
eA = rep["e"]["PA"]
for X in ("PB", "PC"):
    eX = rep["e"][X]
    chis[f"b_{X}_dr"]["bound"] = eX ** 2 * (1 / eA + 1 / eX) / rep["k"]
    # exact in-span bound (u-differences) for reference
    u = {Y: x * g[Y] for Y in PER}
    bl = e[X] * (u[X] - u["PA"])
    chis[f"b_{X}_dr"]["linearized_bTCplusb"] = chi2(bl, C_PL)
    chis[f"b_{X}_dr"]["actual_bTCplusb_205"] = chi2(b_dr[X], C_PL)
    chis[f"b_{X}_dr"]["pz_bTCplusb_projected"] = chi2(Ppz @ b_dr[X], Ppz @ C_PL @ Ppz.T)

# control
fstep_dr = None
lo = (epz[:-1] >= 1.5) & (epz[1:] <= 8.0)
hi = (epz[:-1] >= 8.0) & (epz[1:] <= 15.0)
I = lambda v, s: float(np.sum((Ppz @ v)[s] * dpz[s]))  # noqa: E731
q = lambda s: (I(xs["PB"], s) / I(ts["PB"], s)) / (I(xs["PA"], s) / I(ts["PA"], s))  # noqa: E731
rep["control_dr_step"] = q(hi) / q(lo) - 1


# noise
def frac_draws(X, kind):
    base = runs[f"{X}_s42"]
    val = (lambda rr: flat(rr["X"]) / flat(rr["t"])) if kind == "r" else (lambda rr: flat(rr["X"]))
    b0 = val(base)
    bd = [val(runs[f"{X}_b{i:02d}"]) / b0 - 1 for i in range(1, 11)]
    sd = val(runs[f"{X}_s43"]) / b0 - 1
    return bd, sd


def est(dd):
    mbar = sum(e[X] * dd[X] for X in PER)
    h = {X: dd[X] - mbar for X in PER}
    return sum(np.outer(np.sqrt(kf * e[X]) * x * h[X], np.sqrt(kf * e[X]) * x * h[X]) for X in PER)


noise = {}
for kind in ("r", "x"):
    D = {X: frac_draws(X, kind) for X in PER}
    Nb = np.mean([est({X: D[X][0][k] for X in PER}) for k in range(10)], axis=0)
    Ns = est({X: D[X][1] / np.sqrt(2) for X in PER})
    base = C_PL if kind == "r" else S_raw
    o = {}
    for nm, N in (("boot", Nb), ("seed", Ns), ("total", Nb + Ns)):
        o[nm] = dict(cell=float(np.median(np.diag(N) / np.diag(base))),
                     pz=float(np.median(np.diag(Ppz @ N @ Ppz.T) / np.diag(Ppz @ base @ Ppz.T))))
    noise[kind] = o

# compare with product
Z = np.load(f"{PROD}/playlist_term.npz")
J = json.load(open(f"{PROD}/playlist_term.json"))["report"]
cmp = {}
for nm, M in (("C_PL", C_PL), ("S_ref", S_ref), ("S_raw", S_raw), ("S_ref_raw", S_ref_raw)):
    cmp[f"{nm}_entry_over_max"] = float(np.max(np.abs(M - Z[nm])) / np.max(np.abs(Z[nm])))
cmp["x"] = float(np.max(np.abs(x / Z["x"] - 1)))
cmp["cells_equal"] = bool(np.array_equal(cells, Z["cells"]))
for X in PER:
    cmp[f"g_{X}_abs"] = float(np.max(np.abs(g[X] - Z[f"g_{X}"])))
    cmp[f"e_{X}_rel"] = float(np.max(np.abs(e[X] / Z[f"e_{X}"] - 1)))
    cmp[f"r_{X}_rel"] = float(np.max(np.abs(r[X] / Z[f"r_{X}"] - 1)))
# F rows up to a positive scale
Fz = Z["F"]
sc = (Fz * F).sum(1) / (F * F).sum(1)
cmp["F_rows_scale_rel_resid"] = float(np.max(np.abs(Fz - sc[:, None] * F)) / np.max(np.abs(Fz)))
cmp["F_scales"] = [float(sc.min()), float(sc.max())]


def rel(a, b):
    a, b = np.atleast_1d(np.asarray(a, float)), np.atleast_1d(np.asarray(b, float))
    return float(np.max(np.abs(a / b - 1)))


for nm in sig:
    jj = J[nm]
    cmp[f"sig_{nm}_cell_stats"] = rel([sig[nm]["cell"][k] for k in ("median", "p84", "max")],
                                      [jj["cell_rel_sigma_pct"][k] for k in ("median", "p84", "max")])
    cmp[f"sig_{nm}_integral"] = rel(sig[nm]["integral"], jj["integral_rel_sigma_pct"])
    cmp[f"sig_{nm}_pt14_rounded4"] = rel(np.round(sig[nm]["pt"], 4), jj["pt_rel_sigma_pct"])
    cmp[f"sig_{nm}_pz16_rounded4"] = rel(np.round(sig[nm]["pz"], 4), jj["pz_rel_sigma_pct"])
    cmp[f"sig_{nm}_pt14_abs_unrounded"] = float(np.max(np.abs(np.array(sig[nm]["pt"]) - jj["pt_rel_sigma_pct"])))
    cmp[f"sig_{nm}_pz16_abs_unrounded"] = float(np.max(np.abs(np.array(sig[nm]["pz"]) - jj["pz_rel_sigma_pct"])))
    cmp[f"sig_{nm}_ratioVL"] = rel(sig[nm]["median_sigma_ratio_to_VL175"], jj["median_sigma_ratio_to_VL175"])
# functionals from the product's own C and F, full precision (31 sigma)
for nm, M in (("C_PL", C_PL), ("S_ref", S_ref)):
    s_me = np.sqrt(np.diag(F @ M @ F.T)) / (F @ x)
    s_pr = np.sqrt(np.diag(Fz @ Z[nm] @ Fz.T)) / (Fz @ Z["x"])
    cmp[f"sig31_{nm}_fullprec_vs_npz"] = rel(s_me, s_pr)
JR = J["reference_scenario_algebraic"]
for nm, o in chis.items():
    for kk in ("pz_vs_VL175", "pz_vs_VL175_plus_C_PL", "pt_vs_VL175", "pt_vs_VL175_plus_C_PL"):
        cmp[f"chi2_{nm}_{kk}"] = rel(o[kk], JR[nm][kk])
    cmp[f"oos_{nm}_euclid"] = rel(o["out_of_span_euclid"], JR[nm]["out_of_span"]["euclid"])
    cmp[f"oos_{nm}_pzfrac"] = rel(o["out_of_span_pz_chi2_frac"], JR[nm]["out_of_span"]["pz_vl175_chi2_fraction"])
    if "bound" in o:
        cmp[f"bound_{nm}"] = rel(o["bound"], JR[nm]["first_order_in_span_bound"])
JN = J["noise_share"]
for nm in ("boot", "seed", "total"):
    cmp[f"noise_{nm}_cell_r"] = rel(noise["r"][nm]["cell"], JN[nm]["median_cell_variance_share"])
    cmp[f"noise_{nm}_pz_r"] = rel(noise["r"][nm]["pz"], JN[nm]["median_pz_marginal_variance_share"])
    cmp[f"noise_{nm}_cell_x_vs_reported"] = rel(noise["x"][nm]["cell"], JN[nm]["median_cell_variance_share"])
cmp["k"] = rel(rep["k"], J["k_factor"])
cmp["e_json"] = rel([rep["e"][X] for X in PER], [J["exposure_share"][X] for X in PER])
# eigenmodes
lz = np.sort(np.linalg.eigvalsh(Z["C_PL"]))[::-1][:2]
cmp["eig_top2_vs_json"] = rel(lam[::-1][:2], [J["eigenmodes"][0]["eigenvalue"], J["eigenmodes"][1]["eigenvalue"]])
cmp["eig_top2_vs_npz"] = rel(lam[::-1][:2], lz)

out = dict(rep=rep, sig=sig, chis=chis, noise=noise, cmp=cmp)
json.dump(out, open(RES, "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
