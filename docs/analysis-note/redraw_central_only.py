#!/usr/bin/env python3
"""Central-value-only redraws of four analysis-note figures (2026-10-03).

fig:3dmodels, fig:modedecomp, fig:mec and fig:ascencio drew uncertainties from SUPERSEDED
covariances: the historical 3D hCov_combined3d_total / hCov_universe3d_total (grey band, "+/- total"
bars) and the unified-throw 4D hCov_combined4d_total_uthrow (bars on our Ascencio points and the
full-cov chi^2). No adopted 3D or 4D covariance exists yet, so until one does these figures show
central values only: no band, no error bars on our points, no chi^2 / p-value. The published
Ascencio points keep the bars of their PUBLISHED covariance. The redraws are figures/<name>_central.pdf;
the versions with the superseded uncertainties stay at figures/<name>.pdf, shown in App. H, because
reproduction/s5p/scope.py pins three of them by path and sha256 (tier A) and regenerates them bitwise
from the Stage-7 producers (tier B).

The four producers are hash-recorded by the s5p deploy receipts and are NOT modified. This script
imports them unchanged and reuses their loaders, projectors, constants and technote_style; the
drawing code is theirs with every covariance-derived artist removed. No covariance file is opened:
the producers' covariance loaders are replaced by a refusal before anything runs.

Inputs are the Stage-7 (s5p, f5ed4704) flux-repaired predictions, pinned by sha256 against
docs/orchestration/state/s5p/stage7/generator-context/generator-context-receipt.json and
docs/orchestration/state/s5p/gen5d/gen5d-fluxfix-3.json; any other bytes are refused. Do NOT
point it at make_figures.sh's default 3d-unfolding/genie/ inputs: those are the pre-repair
predictions (KNOWN_ISSUES row 83).

Run in the analysis env (root_6_28), from anywhere:
  python docs/analysis-note/redraw_central_only.py \\
      --genfig  <copy of s5p-20260926/stage7/genfig>/3d-unfolding \\
      --xsec4d <...>/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root \\
      --supplemental <...>/3d-unfolding/genie/ascencio_2110.13372_supplemental.txt \\
      --outdir <dir> [--only generators modedecomp mec ascencio]
Each figure is written as <outdir>/<name>_central.png plus its technote_style .pdf twin.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
# OI-136: every import root is derived from this file, never a hardcoded cluster root.
REPO = Path(__file__).resolve().parents[2]
for _p in (REPO / "nd-unfolding", REPO / "3d-unfolding" / "genie", REPO):
    sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402

import technote_style  # noqa: E402  (no titles + consistent colours + .pdf twins)
import overlay_generators_band as ogb  # noqa: E402
import mode_decomp_eavail as md  # noqa: E402
import compare_mec_eavail as cme  # noqa: E402
import compare_ascencio_fullcov as caf  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

for _m in (technote_style, ogb, md, cme, caf):
    if REPO not in Path(_m.__file__).resolve().parents:
        raise SystemExit(f"{_m.__name__} imported from {_m.__file__}, outside {REPO}")


def _refuse(*a, **k):
    raise SystemExit("redraw_central_only: a covariance load was attempted; this redraw uses none")


# mode_decomp_eavail imports load_cov from overlay_generators_band inside its main()
ogb.load_cov = cme.load_cov = caf.load_ours = _refuse

# Stage-7 inputs, relative to --genfig (= stage7/genfig/3d-unfolding)
GENFIG_SHA256 = {
    "xsec_3d_MEFHC_5iter_lgbm.root": "0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59",
    "genie/genie_cv_xsec3d.root": "8d417234dd33de2b0944d1bb9a75d5f888fa95c5ad0a02d4f71048a5bd410e3c",
    "genie/model_tunev1_xsec3d.root": "2d3b6bedf496b1c213861affdc36fad8288216ebb7f41f72527d80abf1fb0e09",
    "genie/nuwro_cv_xsec3d.root": "e728f0893cc6d0bf4e8355279fe46b9c6a458cedbbc79877e42cb49a62d26374",
    "genie/gibuu_cv_xsec3d.root": "a54035aa96b587ad6b04e518138ea48fa0517954c77c317b56d85a4f626c7b24",
    "genie/genie_cv_xsec3d_modes.root": "16962b6d0b7c5fc05035507603f941cef6678e3a57adf3cac8aeb35766b2dfcc",
    "genie/genie_mec_cv_xsec3d.root": "38552e52ee706e1ee69dfe30de39a4572923e9738dfdd390206e1e45bf1e9f3e",
}
# the frozen 4D product and the published supplement, as read from the canonical checkout 2026-10-03
ASCENCIO_SHA256 = {
    "xsec_4d_MEFHC_5iter_lgbm.root": "1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2",
    "ascencio_2110.13372_supplemental.txt": "748afa9235f7e06b6415f213109106011ea6afa70ba8738d30e90c78a2fbde5a",
}
DATA = "xsec_3d_MEFHC_5iter_lgbm.root"
GENERATORS = [("GENIE-CV", "genie/genie_cv_xsec3d.root"),
              ("Tune-v1", "genie/model_tunev1_xsec3d.root"),
              ("NuWro", "genie/nuwro_cv_xsec3d.root"),
              ("GiBUU", "genie/gibuu_cv_xsec3d.root")]
MODES_FILE = "genie/genie_cv_xsec3d_modes.root"   # Stage 7's --cv for both E_avail figures
MEC_FILE = "genie/genie_mec_cv_xsec3d.root"


def pinned(paths, table):
    """{key: absolute path} for paths = {key: path}, refusing any file whose sha256 is not table[key]."""
    out = {}
    for rel, want in table.items():
        p = os.path.abspath(paths[rel])
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for blk in iter(lambda: f.read(1 << 20), b""):
                h.update(blk)
        if h.hexdigest() != want:
            raise SystemExit(f"{p}: sha256 {h.hexdigest()} != recorded {want}")
        print(f"[input] {want[:12]}  {p}")
        out[rel] = p
    return out


def fig_generators(g, outdir):
    """fig:3dmodels: overlay_generators_band.main() without the band, the stat bars and the chi^2."""
    val = ogb.load(g[DATA], lambda a: f"hXSec_{a}")
    gens = [(lab, ogb.load(g[rel], lambda a: f"hXSec_{a}")) for lab, rel in GENERATORS]

    cv3d, edges = ogb.load_th3(g[DATA], "hXSec3D")
    J, _ = ogb.build_projectors(cv3d, edges)
    cv_rep = cv3d.ravel(order="C")[(cv3d > 0).ravel(order="C")]
    print("[check] projected CV vs stored 1D marginal (max rel diff):")
    for key, _, _ in ogb.AXES:
        stored = val[key][2]
        rel = np.abs(J[key] @ cv_rep - stored) / np.where(stored > 0, np.abs(stored), 1)
        print(f"    {key:7s} {rel.max():.2e}")
        assert rel.max() < 1e-6, f"projection mismatch on {key}: {rel.max():.2e}"

    print("\n  integrated sigma (eavail axis, catch bin dropped):")
    e, _, dval, _ = val["eavail"]
    w = np.diff(e)[:-1]
    dint = float(np.sum(dval[:-1] * w))
    print(f"    data   = {dint:.3e} cm^2/nucleon")
    for lab, gv in gens:
        mint = float(np.sum(gv["eavail"][2][:-1] * w))
        print(f"    {lab:10s} = {mint:.3e}   ({(mint/dint-1)*100:+5.1f}% vs data)")

    fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
    colors = ["#C44E52", "#4C72B0", "#2ca02c", "#9467bd"]
    for ax, (key, xlab, ylab) in zip(axs, ogb.AXES):
        edges_a, cen, dval, _ = val[key]
        sl = slice(0, len(dval) - 1) if key == "eavail" else slice(0, len(dval))
        ax.errorbar(cen[sl], dval[sl], yerr=None, fmt="o", ms=4, color="k",
                    capsize=2, zorder=5, label="unfolded (this work)")
        for i, (lab, gv) in enumerate(gens):
            col = colors[i % len(colors)]
            ax.stairs(gv[key][2][sl],
                      np.append(edges_a[sl.start:sl.stop], edges_a[sl.stop]),
                      color=col, lw=2)
            ax.plot(cen[sl], gv[key][2][sl],
                    marker=technote_style.gen_marker(lab), linestyle="None",
                    ms=5, color=col, label=lab, zorder=6)
        ax.set_xlabel(xlab); ax.set_ylabel(ylab + r" (cm$^2$/.../nucleon)")
        ax.grid(alpha=0.3)
        if key == "eavail":
            ax.legend(fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    technote_style.minerva_tag(axs[0])
    out = os.path.join(outdir, "generators_vs_unfolded_band_central.png")
    fig.savefig(out, dpi=140)
    print(f"\n[overlay] wrote {out}")


def fig_modedecomp(g, outdir):
    """fig:modedecomp: mode_decomp_eavail.main() as Stage 7 ran it, without the "+/- total" bars.

    Stage 7 (gen5d_mode_components.py mode-decomp) replaced md.mode_counts by sigma-weighted sums
    of the flux-repaired events, so frac[m] = W_mode/W_total per bin. Those sums, / dE_avail, are
    hXSec_eavail_<mode> in genie_cv_xsec3d_modes.root, whose hXSec_eavail they reproduce to
    <= 1e-12, so frac[m] = hXSec_eavail_<mode> / hXSec_eavail is the same fraction.
    """
    EA = np.asarray(md.EA, float)
    dea = np.diff(EA)
    cv = cme.get_h(g[MODES_FILE], "hXSec_eavail")
    data = cme.get_h(g[DATA], "hXSec_eavail")
    nb = cv.size
    frac = {m: cme.get_h(g[MODES_FILE], f"hXSec_eavail_{m}") / cv for m in md.MODES}
    cv_mode = {m: cv * frac[m] for m in ("qel", "res", "dis", "coh")}

    hdr = ("bin  Eavail[GeV]      data        CV     d-CV   "
           "| QE      RES     DIS     COH   | 2p2h/QE to close")
    print(hdr)
    print("-" * len(hdr))
    for b in range(nb):
        resid = data[b] - cv[b]
        qe = cv_mode["qel"][b]
        ratio = resid / qe if qe > 0 else float("inf")
        tag = "  <-- catch bin" if b == nb - 1 else ""
        print(f"{b:3d}  [{EA[b]:4.2f},{EA[b+1]:4.2f})  {data[b]:.3e} {cv[b]:.3e} "
              f"{resid:+.2e}   | "
              f"{cv_mode['qel'][b]:.2e} {cv_mode['res'][b]:.2e} "
              f"{cv_mode['dis'][b]:.2e} {cv_mode['coh'][b]:.1e} | "
              f"{ratio:+6.2f}{tag}")

    s = slice(0, nb - 1)
    int_d = (data[s] * dea[s]).sum()
    int_cv = (cv[s] * dea[s]).sum()
    int_qe = (cv_mode["qel"][s] * dea[s]).sum()
    print("\n[integrated, catch bin dropped]")
    print(f"  data   = {int_d:.3e}   CV = {int_cv:.3e}   deficit = "
          f"{int_d-int_cv:+.2e} ({100*(int_cv-int_d)/int_d:+.1f}% of data)")
    print(f"  CV QE component = {int_qe:.3e}  -> a 2p2h equal to "
          f"{100*(int_d-int_cv)/int_qe:.0f}% of the QE rate would close the "
          f"integrated deficit")
    pos = ((data[s] - cv[s]) * dea[s]).clip(min=0)
    if pos.sum() > 0:
        lowfrac = (pos / pos.sum())[EA[1:nb] <= 0.4].sum()
        print(f"  fraction of the positive deficit in E_avail<=0.4 GeV "
              f"(the QE-Delta dip, where 2p2h lives) = {100*lowfrac:.0f}%")

    n = nb - 1
    ctr = 0.5 * (EA[:n] + EA[1:n + 1])
    w = dea[:n]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    bot = np.zeros(n)
    for m, lab, c in [("qel", "QE", "#1f77b4"), ("res", "RES", "#2ca02c"),
                      ("dis", "DIS", "#ff7f0e"), ("coh", "COH", "#9467bd")]:
        h = cv_mode[m][:n]
        ax.bar(ctr, h, width=w * 0.92, bottom=bot, color=c,
               label=f"GENIE-CV {lab}", edgecolor="white", lw=0.4)
        bot += h
    gap = (data[:n] - cv[:n]).clip(min=0)
    ax.bar(ctr, gap, width=w * 0.92, bottom=cv[:n], color="none",
           edgecolor="red", hatch="///", lw=1.2,
           label="data $-$ GENIE-CV (2p2h-shaped gap)")
    ax.errorbar(ctr, data[:n], yerr=None, fmt="o", color="k", ms=5,
                capsize=3, label="unfolded data", zorder=5)
    ax.set_xlabel("$E_{avail}$ (GeV)")
    ax.set_ylabel(r"$d\sigma/dE_{avail}$ (cm$^2$/nucleon/GeV)")
    ax.legend(fontsize=8, ncol=2)
    ax.set_xlim(EA[0], EA[n])
    technote_style.minerva_tag(ax, loc="upper right")
    fig.tight_layout()
    out = os.path.join(outdir, "mode_decomp_eavail_central.png")
    fig.savefig(out, dpi=130)
    print(f"[mode-decomp] wrote {out}")


def fig_mec(g, outdir):
    """fig:mec: compare_mec_eavail.main() on Stage 7's inputs, without the "+/- total" bars."""
    EA = np.asarray(cme.EA, float)
    data = cme.get_h(g[DATA], "hXSec_eavail")
    cv = cme.get_h(g[MODES_FILE], "hXSec_eavail")
    mec_tot = cme.get_h(g[MEC_FILE], "hXSec_eavail")          # CV+MEC
    mec_only = cme.get_h(g[MEC_FILE], "hXSec_eavail_mec")     # MEC contribution
    nb = data.size
    dea = np.diff(EA)

    hdr = "bin  Eavail[GeV]    data       CV    CV+MEC   MEC   | dip closed%"
    print(hdr); print("-" * len(hdr))
    for b in range(nb):
        closed = (100 * (mec_tot[b] - cv[b]) / (data[b] - cv[b])
                  if (data[b] - cv[b]) > 1e-42 else float("nan"))
        tag = " catch" if b == nb - 1 else ""
        print(f"{b:3d} [{EA[b]:4.2f},{EA[b+1]:5.2f}) {data[b]:.2e} {cv[b]:.2e} "
              f"{mec_tot[b]:.2e} {mec_only[b]:.1e} | {closed:6.1f}{tag}")

    s = slice(0, nb - 1)
    iD = (data[s] * dea[s]).sum(); iCV = (cv[s] * dea[s]).sum()
    iM = (mec_tot[s] * dea[s]).sum()
    print("\n[integrated, catch bin dropped]")
    print(f"  data={iD:.3e}  CV={iCV:.3e} ({100*(iCV-iD)/iD:+.1f}%)  "
          f"CV+MEC={iM:.3e} ({100*(iM-iD)/iD:+.1f}%)")
    print(f"  MEC added {iM-iCV:+.2e} = {100*(iM-iCV)/(iD-iCV):.0f}% of the "
          f"integrated deficit")
    dip = (EA[1:nb] <= 0.4)
    dD = (data[:nb-1][dip] - cv[:nb-1][dip]); dM = (mec_tot[:nb-1][dip] - cv[:nb-1][dip])
    print(f"  in the dip (Eavail<=0.4): MEC fills {100*dM.sum()/dD.sum():.0f}% "
          f"of the data-CV gap")

    n = nb - 1
    ctr = 0.5 * (EA[:n] + EA[1:n+1]); w = dea[:n]
    fig, ax = plt.subplots(figsize=(7.6, 5.3))
    ax.bar(ctr, cv[:n], width=w*0.92, color="#cfe3ff", edgecolor="#1f77b4",
           label="GENIE-CV (no 2p2h)")
    ax.bar(ctr, mec_only[:n], width=w*0.92, bottom=cv[:n], color="#d62728",
           alpha=0.75, label="+ Valencia MEC (2p2h)")
    ax.errorbar(ctr, data[:n], yerr=None, fmt="o", color="k", ms=5,
                capsize=3, label="unfolded data", zorder=5)
    ax.set_xlabel("$E_{avail}$ (GeV)")
    ax.set_ylabel(r"$d\sigma/dE_{avail}$ (cm$^2$/nucleon/GeV)")
    ax.legend(fontsize=9); ax.set_xlim(EA[0], EA[n])
    technote_style.minerva_tag(ax, loc="upper right")
    out = os.path.join(outdir, "compare_mec_eavail_central.png")
    fig.tight_layout(); fig.savefig(out, dpi=130)
    print(f"[compare-mec] wrote {out}")


def load_ours_central(path):
    """compare_ascencio_fullcov.load_ours() without its covariance: (x4 flat, gmask, edges)."""
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und
    pt_e = np.asarray(u2d.PT_EDGES, float)
    pz_e = np.asarray(u2d.PZ_EDGES, float)
    ea_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
    q3_e = np.asarray(und.EXTRA_AXES["q3"]["edges"], float)
    f = ROOT.TFile.Open(path)
    hf = f.Get("hXSecND_flat")
    x4 = np.array([hf.GetBinContent(i + 1) for i in range(hf.GetNbinsX())])
    f.Close()
    return x4, np.where(x4 > 0)[0], (pt_e, pz_e, ea_e, q3_e)


def fig_ascencio(a, outdir):
    """fig:ascencio: compare_ascencio_fullcov.main() without our bars, the pulls and the chi^2.

    The super-grid and merge maps are main()'s own lines (they are not a function there); the
    published points keep their published-covariance bars, T C_a T^T.
    """
    cells, x_a, C_a = caf.parse_supplemental(a["ascencio_2110.13372_supplemental.txt"])
    x4, gmask, (pt_e, pz_e, ea_e, q3_e) = load_ours_central(a["xsec_4d_MEFHC_5iter_lgbm.root"])
    sh4 = (len(pt_e) - 1, len(pz_e) - 1, len(ea_e) - 1, len(q3_e) - 1)
    ip, iz, ie, iq = np.unravel_index(gmask, sh4)
    dpt, dpz = np.diff(pt_e), np.diff(pz_e)
    Q3_SUPER, PZ_MU_MAX = caf.Q3_SUPER, caf.PZ_MU_MAX

    # ---- build the common super-grid (compare_ascencio_fullcov.main, verbatim) ----
    super_bins = []   # (q3_lo, q3_hi, ea_lo, ea_hi)
    for qlo, qhi in zip(Q3_SUPER[:-1], Q3_SUPER[1:]):
        col = [(c, i) for i, c in enumerate(cells)
               if c[2] >= qlo - 1e-9 and c[3] <= qhi + 1e-9]
        col_edges = sorted({c[0] for c, _ in col} | {c[1] for c, _ in col})
        ea_max = max(c[1] for c, _ in col)
        com = caf.common_eavail_edges(col_edges, ea_e, ea_max)
        fine_q3 = sorted({(c[2], c[3]) for c, _ in col})
        for elo, ehi in zip(com[:-1], com[1:]):
            ok = all(
                abs(sum((c[1] - c[0]) for c, _ in col
                        if (c[2], c[3]) == fq
                        and c[0] >= elo - 1e-9 and c[1] <= ehi + 1e-9)
                    - (ehi - elo)) < 1e-6
                for fq in fine_q3)
            our_w = sum(ea_e[k+1] - ea_e[k] for k in range(len(ea_e) - 1)
                        if ea_e[k] >= elo - 1e-9 and ea_e[k+1] <= ehi + 1e-9)
            if ok and abs(our_w - (ehi - elo)) < 1e-6:
                super_bins.append((qlo, qhi, elo, ehi))
    ns = len(super_bins)
    print(f"[grid] {ns} common super-bins:")
    for qlo, qhi, elo, ehi in super_bins:
        print(f"   q3 [{qlo},{qhi})  Eavail [{elo},{ehi})")

    # ---- merge matrices (verbatim) ----
    T = np.zeros((ns, len(cells)))
    for s, (qlo, qhi, elo, ehi) in enumerate(super_bins):
        vol_s = (ehi - elo) * (qhi - qlo)
        for j, (alo, ahi, blo, bhi) in enumerate(cells):
            if alo >= elo - 1e-9 and ahi <= ehi + 1e-9 and blo >= qlo - 1e-9 and bhi <= qhi + 1e-9:
                T[s, j] = (ahi - alo) * (bhi - blo) / vol_s
    O = np.zeros((ns, gmask.size))
    for s, (qlo, qhi, elo, ehi) in enumerate(super_bins):
        vol_s = (ehi - elo) * (qhi - qlo)
        sel = ((ea_e[ie] >= elo - 1e-9) & (ea_e[ie + 1] <= ehi + 1e-9) &
               (q3_e[iq] >= qlo - 1e-9) & (q3_e[iq + 1] <= qhi + 1e-9) &
               (pz_e[iz + 1] <= PZ_MU_MAX + 1e-9))
        O[s, sel] = (dpt[ip] * dpz[iz] * np.diff(ea_e)[ie] * np.diff(q3_e)[iq])[sel] / vol_s

    y_o = O @ x4[gmask]
    y_a = T @ x_a
    Cs_a = T @ C_a @ T.T          # PUBLISHED covariance only

    print(f"\n[cmp] {'q3':14s} {'Eavail':14s} {'ours':>11s} {'Ascencio':>11s} "
          f"{'ratio':>7s} {'ours-Asc':>9s}")
    for s, (qlo, qhi, elo, ehi) in enumerate(super_bins):
        print(f"[cmp] [{qlo},{qhi}) GeV  [{elo},{ehi}) GeV {y_o[s]:11.4g} {y_a[s]:11.4g} "
              f"{y_o[s]/y_a[s]:7.3f} {100*(y_o[s]/y_a[s]-1):+8.1f}%")
    wid = np.array([(ehi - elo) * (qhi - qlo) for qlo, qhi, elo, ehi in super_bins])
    print(f"[cmp] integrated (common region): ours {np.sum(y_o*wid):.4g} "
          f"vs Ascencio {np.sum(y_a*wid):.4g}  ratio {np.sum(y_o*wid)/np.sum(y_a*wid):.4f}")

    cols = [(qlo, qhi) for qlo, qhi in zip(Q3_SUPER[:-1], Q3_SUPER[1:])
            if any(b[0] == qlo for b in super_bins)]
    ncol = len(cols)
    fig, axs = plt.subplots(1, ncol, figsize=(4.6 * ncol, 4.2), sharey=False,
                            squeeze=False)
    axs = axs[0]
    for c, (qlo, qhi) in enumerate(cols):
        idx = [s for s, b in enumerate(super_bins) if b[0] == qlo]
        ctr = [0.5 * (super_bins[s][2] + super_bins[s][3]) for s in idx]
        we = [0.5 * (super_bins[s][3] - super_bins[s][2]) for s in idx]
        A = axs[c]
        A.errorbar(ctr, [y_o[s] for s in idx], xerr=we,
                   fmt="ko", label="this work (4D marginal, $p_z<20$)")
        A.errorbar(ctr, [y_a[s] for s in idx], xerr=we,
                   yerr=[np.sqrt(Cs_a[s, s]) for s in idx],
                   fmt="rs", mfc="none", label="Ascencio et al.")
        A.set_xlabel(r"$E_{\rm avail}$ (GeV)")
        # without our bars the autoscale puts our point on the top edge and "best" moves the
        # legend onto the published bar; headroom keeps the legend where it was, upper right
        A.margins(y=0.3)
        if c == 0:
            A.set_ylabel(r"$d^2\sigma/(dE_{\rm avail}\,dq_3)$ (cm$^2$/GeV$^2$/nucleon)")
            A.legend(fontsize=8, loc="upper right")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    technote_style.minerva_tag(axs[0])
    out = os.path.join(outdir, "ascencio_fullcov_compare_central.png")
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"[cmp] wrote {out}")


FIGURES = {"generators": "genfig", "modedecomp": "genfig", "mec": "genfig", "ascencio": "ascencio"}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--genfig", help="s5p-20260926/stage7/genfig/3d-unfolding, or a copy of it "
                                     "(the Stage-7 inputs; needed by generators, modedecomp, mec)")
    ap.add_argument("--xsec4d", help="the frozen 4D product (needed by ascencio)")
    ap.add_argument("--supplemental", help="the Ascencio supplemental data (needed by ascencio)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--only", nargs="*", choices=sorted(FIGURES), default=None)
    args = ap.parse_args()
    if not os.path.isdir(args.outdir):
        raise SystemExit(f"--outdir {args.outdir} does not exist")
    want = args.only or list(FIGURES)
    g = a = {}
    if any(FIGURES[f] == "genfig" for f in want):
        if not args.genfig:
            ap.error("--genfig is required for generators, modedecomp and mec")
        g = pinned({rel: os.path.join(args.genfig, rel) for rel in GENFIG_SHA256}, GENFIG_SHA256)
    if "ascencio" in want:
        if not (args.xsec4d and args.supplemental):
            ap.error("--xsec4d and --supplemental are required for ascencio")
        a = pinned({"xsec_4d_MEFHC_5iter_lgbm.root": args.xsec4d,
                    "ascencio_2110.13372_supplemental.txt": args.supplemental}, ASCENCIO_SHA256)
    run = {"generators": lambda: fig_generators(g, args.outdir),
           "modedecomp": lambda: fig_modedecomp(g, args.outdir),
           "mec": lambda: fig_mec(g, args.outdir),
           "ascencio": lambda: fig_ascencio(a, args.outdir)}
    for name in want:
        print(f"\n===== {name} =====")
        run[name]()


if __name__ == "__main__":
    main()
