#!/usr/bin/env python3
"""Overlay generator predictions on the unfolded 3D result WITH the full
systematic (+stat+ML) uncertainty band, and quantify the data-model tension
per axis with a COVARIANCE chi^2.

The 3D systematic-UQ campaign produced the reported-bin covariance
`uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root`:
  hCov_combined3d_total  = C_syst + C_stat + C_ML   (the honest data covariance)
  hCov_universe3d_total  = C_syst only
both on the reported-bin flattening (mask cv>0, C-order ravel of (pt,pz,eavail)).

This script propagates that 3D covariance onto each 1D projection. The 1D
marginal is a *linear* functional of the 3D differential cross section
(`xsec_3d.project_axis`):
    proj_pt[i]     = sum_{j,k} xsec3d[i,j,k] * dpz[j] * dea[k]
    proj_pz[j]     = sum_{i,k} xsec3d[i,j,k] * dpt[i] * dea[k]
    proj_eavail[k] = sum_{i,j} xsec3d[i,j,k] * dpt[i] * dpz[j]
so with the projection operator J_axis (n_axis x n_reported) the projected
covariance is  C_axis = J_axis @ C @ J_axis.T  and the band is sqrt(diag).
A self-consistency check asserts J_axis @ cv_reported == hXSec_<axis> (the same
1D marginals the CV file stores).

For each generator and axis it reports a COVARIANCE chi^2 using C_axis (the full
projected covariance, off-diagonals included), plus the old stat-only chi^2 as a
lower bound for reference:
    chi2_cov = r^T C_axis^{-1} r ,  r = data - model ,  ndf = nbins

Run in the analysis env (root_6_28):
  python overlay_generators_band.py \
    --unfolded ../xsec_3d_MEFHC_5iter_lgbm.root \
    --cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total \
    --syst-cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_universe3d_total \
    --band uq_3d/stat_band_3d.root \
    --generator GENIE-CV:genie_cv_xsec3d.root \
    --generator Tune-v1:model_tunev1_xsec3d.root \
    --generator NuWro:nuwro_cv_xsec3d.root \
    --out generators_vs_unfolded_band

Paths in --cov/--syst-cov/--band are resolved relative to the 3d-unfolding
directory (parent of genie/) when not absolute, matching the campaign layout.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT

AXES = [("pt", r"$p_T$ (GeV/c)", r"$d\sigma/dp_T$"),
        ("pz", r"$p_\parallel$ (GeV/c)", r"$d\sigma/dp_\parallel$"),
        ("eavail", r"$E_{\rm avail}$ (GeV)", r"$d\sigma/dE_{\rm avail}$")]

# resolve campaign-relative paths (cov/band live under 3d-unfolding/, we run in genie/)
_D3 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(path):
    if os.path.isabs(path) or os.path.exists(path):
        return path
    cand = os.path.join(_D3, path)
    return cand if os.path.exists(cand) else path


def th1(f, name):
    h = f.Get(name)
    if not h:
        raise SystemExit(f"missing {name} in {f.GetName()}")
    n = h.GetNbinsX()
    edges = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)])
    cen = 0.5 * (edges[:-1] + edges[1:])
    val = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
    err = np.array([h.GetBinError(i) for i in range(1, n + 1)])
    return edges, cen, val, err


def load(path, names):
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {path}")
    out = {ax: th1(f, names(ax)) for ax in ("pt", "pz", "eavail")}
    f.Close()
    return out


def _axis_edges(ax):
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


def load_th3(path, name):
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if not h:
        raise SystemExit(f"missing {name} in {path}")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    a = np.zeros((nx, ny, nz))
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                a[ix, iy, iz] = h.GetBinContent(ix + 1, iy + 1, iz + 1)
    edges = (_axis_edges(h.GetXaxis()), _axis_edges(h.GetYaxis()),
             _axis_edges(h.GetZaxis()))
    f.Close()
    return a, edges


def load_cov(spec):
    """spec = 'FILE:HIST' -> (n x n) numpy covariance (reported-bin flatten)."""
    path, _, hist = spec.partition(":")
    path = _resolve(path)
    hist = hist or "hCov_combined3d_total"
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    h = f.Get(hist)
    if not h:
        raise SystemExit(f"missing {hist} in {path}")
    n = h.GetNbinsX()
    C = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    f.Close()
    return C


def build_projectors(cv3d, edges):
    """Per-axis projection operators J_axis (n_axis x n_reported) on the
    reported-bin flatten (mask cv>0, C-order), matching xsec_3d.project_axis."""
    pt_e, pz_e, ea_e = edges
    dpt, dpz, dea = np.diff(pt_e), np.diff(pz_e), np.diff(ea_e)
    NX, NY, NZ = cv3d.shape
    mask = (cv3d > 0).ravel(order="C")
    n_rep = int(mask.sum())
    # weights for each (i,j,k) into each axis bin
    J = {"pt": np.zeros((NX, n_rep)),
         "pz": np.zeros((NY, n_rep)),
         "eavail": np.zeros((NZ, n_rep))}
    r = 0
    for idx in range(NX * NY * NZ):
        if not mask[idx]:
            continue
        i, rem = divmod(idx, NY * NZ)
        j, k = divmod(rem, NZ)
        J["pt"][i, r] = dpz[j] * dea[k]
        J["pz"][j, r] = dpt[i] * dea[k]
        J["eavail"][k, r] = dpt[i] * dpz[j]
        r += 1
    return J, mask


def project_cov(C, J):
    """C_axis = J C J^T for each axis -> {axis: (cov, sigma)}."""
    out = {}
    for key, Jk in J.items():
        Ca = Jk @ C @ Jk.T
        out[key] = (Ca, np.sqrt(np.maximum(np.diag(Ca), 0)))
    return out


def cov_chi2(r, C):
    """r^T C^{-1} r with a guarded solve; returns (chi2, cond)."""
    Cs = 0.5 * (C + C.T)
    cond = np.linalg.cond(Cs)
    try:
        x = np.linalg.solve(Cs, r)
    except np.linalg.LinAlgError:
        x = np.linalg.pinv(Cs) @ r
    return float(r @ x), float(cond)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unfolded", required=True)
    ap.add_argument("--cov",
                    default="uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total",
                    help="FILE:HIST total covariance (C_syst+C_stat+C_ML); the "
                         "band + cov chi^2 use this.")
    ap.add_argument("--syst-cov",
                    default="uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_universe3d_total",
                    help="FILE:HIST systematics-only covariance, for the printed "
                         "breakdown only. '' to skip.")
    ap.add_argument("--band", default="",
                    help="optional stat_band_3d.root (hStat_*) for the inner "
                         "stat-only error bars + stat-only lower-bound chi^2.")
    ap.add_argument("--generator", action="append", default=[], metavar="LABEL:FILE")
    ap.add_argument("--out", default="generators_vs_unfolded_band")
    args = ap.parse_args()

    # data values + 1D marginals from the unfolded result
    val = load(args.unfolded, lambda a: f"hXSec_{a}")
    gens = []
    for spec in args.generator:
        lab, _, path = spec.partition(":")
        gens.append((lab, load(path, lambda a: f"hXSec_{a}")))

    # 3D cv + covariance -> projected per-axis covariance + band
    cv3d, edges = load_th3(args.unfolded, "hXSec3D")
    J, _ = build_projectors(cv3d, edges)
    C_tot = load_cov(args.cov)
    proj_tot = project_cov(C_tot, J)

    # self-consistency: J @ cv_reported must reproduce hXSec_<axis>
    cv_rep = cv3d.ravel(order="C")[(cv3d > 0).ravel(order="C")]
    print("[check] projected CV vs stored 1D marginal (max rel diff):")
    for key, _, _ in AXES:
        proj_cv = J[key] @ cv_rep
        stored = val[key][2]
        rel = np.abs(proj_cv - stored) / np.where(stored > 0, np.abs(stored), 1)
        print(f"    {key:7s} {rel.max():.2e}")
        assert rel.max() < 1e-6, f"projection mismatch on {key}: {rel.max():.2e}"

    proj_syst = None
    if args.syst_cov:
        proj_syst = project_cov(load_cov(args.syst_cov), J)

    band_stat = None
    if args.band:
        band_stat = load(_resolve(args.band), lambda a: f"hStat_{a}")

    # ---------- per-axis tension ----------
    print("\n=== data-model tension: COVARIANCE chi^2 (total C_syst+C_stat+C_ML) ===")
    print("    plus stat-only lower bound; ndf = nbins; eavail catch bin omitted")
    for key, _, _ in AXES:
        edges_a, cen, dval, _ = val[key]
        sl = slice(0, len(dval) - 1) if key == "eavail" else slice(0, len(dval))
        d = dval[sl]
        Ca_full = proj_tot[key][0]
        Ca = Ca_full[sl, sl]
        sig_tot = proj_tot[key][1][sl]
        ok = d > 0
        sig_syst = proj_syst[key][1][sl] if proj_syst else np.zeros_like(d)
        sig_stat = band_stat[key][3][sl] if band_stat else np.zeros_like(d)
        print(f"\n  axis = {key}  ({int(ok.sum())} bins)   "
              f"<rel unc> tot={100*np.median(sig_tot[ok]/d[ok]):.1f}%"
              + (f"  syst={100*np.median(sig_syst[ok]/d[ok]):.1f}%" if proj_syst else "")
              + (f"  stat={100*np.median(sig_stat[ok]/d[ok]):.1f}%" if band_stat else ""))
        for lab, g in gens:
            m = g[key][2][sl]
            r = (d - m)[ok]
            chi2c, cond = cov_chi2(r, Ca[np.ix_(ok, ok)])
            ndf = int(ok.sum())
            line = (f"    {lab:10s}  chi2_cov/ndf = {chi2c:9.1f} / {ndf:2d} "
                    f"= {chi2c/ndf:7.2f}  (cond={cond:.1e})")
            if band_stat:
                s = sig_stat[ok]
                chi2s = float(np.sum((r / s) ** 2))
                line += f"   [stat-only {chi2s/ndf:8.1f}]"
            print(line)

    # integrated (in-PS) normalisation offset on eavail (bin-width weighted, no catch)
    print("\n  integrated sigma (eavail axis, catch bin dropped):")
    e, _, dval, _ = val["eavail"]
    w = np.diff(e)[:-1]
    dint = float(np.sum(dval[:-1] * w))
    Ca_ea = proj_tot["eavail"][0][:-1, :-1]
    dint_err = float(np.sqrt(w @ Ca_ea @ w))     # full-cov propagated integral error
    print(f"    data   = {dint:.3e} +/- {dint_err:.1e} cm^2/nucleon (total)")
    for lab, g in gens:
        mint = float(np.sum(g["eavail"][2][:-1] * w))
        print(f"    {lab:10s} = {mint:.3e}   ({(mint/dint-1)*100:+5.1f}% vs data, "
              f"{abs(mint-dint)/dint_err:5.1f} sigma_tot)")

    # ---------- plot: data with total band, generators overlaid ----------
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
    colors = ["#C44E52", "#4C72B0", "#2ca02c", "#9467bd"]
    for ax, (key, xlab, ylab) in zip(axs, AXES):
        edges_a, cen, dval, _ = val[key]
        sl = slice(0, len(dval) - 1) if key == "eavail" else slice(0, len(dval))
        sig_tot = proj_tot[key][1][sl]
        # total uncertainty as a shaded band
        ax.fill_between(cen[sl], dval[sl] - sig_tot, dval[sl] + sig_tot,
                        step=None, color="0.6", alpha=0.45, lw=0, zorder=2,
                        label="total syst$\\oplus$stat (this work)")
        # inner stat-only error bars if provided, else plain markers
        yerr = band_stat[key][3][sl] if band_stat else None
        ax.errorbar(cen[sl], dval[sl], yerr=yerr, fmt="o", ms=4, color="k",
                    capsize=2, zorder=5,
                    label="unfolded $\\pm$ stat" if band_stat else "unfolded (this work)")
        for i, (lab, g) in enumerate(gens):
            col = colors[i % len(colors)]
            ax.stairs(g[key][2][sl],
                      np.append(edges_a[sl.start:sl.stop], edges_a[sl.stop]),
                      color=col, lw=2)
            ax.plot(cen[sl], g[key][2][sl],
                    marker=technote_style.gen_marker(lab), linestyle="None",
                    ms=5, color=col, label=lab, zorder=6)
        ax.set_xlabel(xlab); ax.set_ylabel(ylab + r" (cm$^2$/.../nucleon)")
        ax.grid(alpha=0.3)
        if key == "eavail":
            ax.legend(fontsize=8)
    fig.suptitle("Unfolded 3D result ($\\pm$ total syst$\\oplus$stat) vs generators "
                 "(Eavail catch bin omitted)")
    fig.tight_layout()
    out = f"{args.out}.png"
    fig.savefig(out, dpi=140)
    print(f"\n[overlay] wrote {out}")


if __name__ == "__main__":
    main()
