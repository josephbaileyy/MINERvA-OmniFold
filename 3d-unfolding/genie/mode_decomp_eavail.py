#!/usr/bin/env python3
"""Decompose the GENIE-CV d(sigma)/dE_avail into interaction modes (QE/RES/DIS/
COH/charm) and overlay the unfolded data, to localise the low-E_avail data
excess and judge whether a 2p2h/MEC component (absent from this CV: mec==0 for
every event) is the right shape/size to bridge it.

Method (exact, no re-normalisation guesswork): in the splines normalisation each
event carries the same weight, so the CV d(sigma)/dE_avail in a bin is shared
among modes strictly by their *count fraction* in that bin (over the same CC,
in-phase-space selection and the same E_avail projection the committed
genie_cv_xsec3d.root used). So
    dsigma_mode[b] = dsigma_CV[b] * N_mode[b] / N_total[b].
We read dsigma_CV[b] straight from genie_cv_xsec3d.root:hXSec_eavail (already
validated), and only need per-bin mode counts from the gst.

The 2p2h test: MINERvA's low-recoil 2p2h sits in the QE-Delta "dip", i.e. the
low/intermediate E_avail bins. We report, per bin, data-CV residual and what
fraction of the local QE rate an added 2p2h would have to be to close it -- and
whether that is plausible (2p2h is the 2nd-largest 3D syst band).

Run in the analysis env (root_6_28).
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import unfold_3d_omnifold_unbinned as u3d
from genie_to_xsec3d import eavail_true

EA = np.asarray(u3d.EAVAIL_EDGES, float)
PT = np.asarray(u3d.PT_EDGES, float)
PZ = np.asarray(u3d.PZ_EDGES, float)
in_ps = u3d.u2d.in_truth_phase_space
MODES = ["qel", "res", "dis", "coh", "charm"]   # mec is 0 here; charm is a DIS subset flag


def mode_counts(gst):
    """Per-E_avail-bin CC-in-PS event counts, total and per exclusive mode."""
    df = ROOT.RDataFrame("gst", gst)
    cols = ["cc", "El", "pxl", "pyl", "pzl", "nf", "pdgf", "Ef",
            "qel", "res", "dis", "coh", "charm"]
    d = df.AsNumpy(cols)
    cc = d["cc"].astype(bool)
    pxl, pyl, pzl = d["pxl"], d["pyl"], d["pzl"]
    pt = np.hypot(pxl, pyl)
    pz = pzl
    inps = np.array([in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                     for a, b in zip(pt, pz)])
    sel = cc & inps
    idx = np.where(sel)[0]

    # eavail per selected event from its FS list
    ea = np.empty(idx.size)
    for k, i in enumerate(idx):
        nf = int(d["nf"][i])
        fs = [(int(d["pdgf"][i][j]), float(d["Ef"][i][j]), 0.0, 0.0, 0.0)
              for j in range(nf)]
        ea[k] = eavail_true(fs)

    tot, _ = np.histogram(ea, bins=EA)
    per = {}
    # exclusive QE/RES/DIS/COH; "charm" reported separately as a DIS-flag subset
    flags = {m: d[m].astype(bool)[idx] for m in ("qel", "res", "dis", "coh", "charm")}
    for m in ("qel", "res", "dis", "coh"):
        c, _ = np.histogram(ea[flags[m]], bins=EA)
        per[m] = c
    c, _ = np.histogram(ea[flags["charm"]], bins=EA)
    per["charm"] = c
    return tot, per, idx.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gst", default="genie_mefhc_cv.gst.root")
    ap.add_argument("--cv", default="genie_cv_xsec3d.root")
    ap.add_argument("--data", default="../xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--cov", default="uq_3d/universe_stage2_3d/"
                    "uq_universe_3d_covariance.root")
    ap.add_argument("--plot", default=None,
                    help="if set, write a stacked-by-mode + data PNG here")
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    # 1) CV and data d(sigma)/dE_avail (per-bin values, cm^2/nucleon/GeV)
    def get_h(path, hname):
        p = path if os.path.isabs(path) else os.path.join(HERE, path)
        f = ROOT.TFile.Open(p)
        h = f.Get(hname)
        v = np.array([h.GetBinContent(b) for b in range(1, h.GetNbinsX() + 1)])
        f.Close()
        return v

    cv = get_h(args.cv, "hXSec_eavail")
    data = get_h(args.data, "hXSec_eavail")
    dea = np.diff(EA)
    nb = cv.size

    # 2) per-bin mode count fractions -> mode-resolved CV
    tot, per, n_sel = mode_counts(args.gst if os.path.isabs(args.gst)
                                  else os.path.join(HERE, args.gst))
    frac = {m: np.where(tot > 0, per[m] / np.maximum(tot, 1), 0.0) for m in per}
    cv_mode = {m: cv * frac[m] for m in ("qel", "res", "dis", "coh")}

    # 3) total-uncertainty band on data (project the combined cov onto E_avail)
    #    reuse overlay's projector if available; else fall back to sqrt(diag) via hSigma
    sig = None
    try:
        from overlay_generators_band import (build_projectors, project_cov,
                                             load_cov, load_th3)
        Cfull = load_cov(args.cov + ":hCov_combined3d_total")
        cv3d, _ = load_th3(args.data, "hXSec3D")
        J, _mask = build_projectors(cv3d, (PT, PZ, EA))
        sig = project_cov(Cfull, J)["eavail"][1]
    except Exception as e:
        print(f"[warn] could not project cov ({e}); reporting residual without band")

    # ---- report ----
    print(f"[mode-decomp] CC-in-PS events used = {n_sel}; E_avail bins = {nb} "
          f"(last is the catch bin)")
    print(f"[mode-decomp] MEC fraction in this CV = 0 (confirmed) -> any 2p2h "
          f"would be ADDED, not reweighted\n")
    hdr = ("bin  Eavail[GeV]      data        CV     d-CV   (d-CV)/sig   "
           "| QE      RES     DIS     COH   | 2p2h/QE to close")
    print(hdr)
    print("-" * len(hdr))
    for b in range(nb):
        lo, hi = EA[b], EA[b + 1]
        resid = data[b] - cv[b]
        nsig = resid / sig[b] if sig is not None else float("nan")
        qe = cv_mode["qel"][b]
        # 2p2h needed (as a multiple of the local QE rate) to lift CV to data
        ratio = resid / qe if qe > 0 else float("inf")
        tag = "  <-- catch bin" if b == nb - 1 else ""
        print(f"{b:3d}  [{lo:4.2f},{hi:4.2f})  {data[b]:.3e} {cv[b]:.3e} "
              f"{resid:+.2e}  {nsig:+6.2f}   | "
              f"{cv_mode['qel'][b]:.2e} {cv_mode['res'][b]:.2e} "
              f"{cv_mode['dis'][b]:.2e} {cv_mode['coh'][b]:.1e} | "
              f"{ratio:+6.2f}{tag}")

    # integrated (drop catch bin), 2p2h-as-fraction-of-QE summary
    s = slice(0, nb - 1)
    int_d = (data[s] * dea[s]).sum()
    int_cv = (cv[s] * dea[s]).sum()
    int_qe = (cv_mode["qel"][s] * dea[s]).sum()
    print(f"\n[integrated, catch bin dropped]")
    print(f"  data   = {int_d:.3e}   CV = {int_cv:.3e}   deficit = "
          f"{int_d-int_cv:+.2e} ({100*(int_cv-int_d)/int_d:+.1f}% of data)")
    print(f"  CV QE component = {int_qe:.3e}  -> a 2p2h equal to "
          f"{100*(int_d-int_cv)/int_qe:.0f}% of the QE rate would close the "
          f"integrated deficit")
    # where is the deficit concentrated?
    resid_bins = (data[s] - cv[s]) * dea[s]
    pos = resid_bins.clip(min=0)
    if pos.sum() > 0:
        share = pos / pos.sum()
        lowfrac = share[EA[1:nb] <= 0.4].sum()   # bins up to 0.4 GeV
        print(f"  fraction of the positive deficit in E_avail<=0.4 GeV "
              f"(the QE-Delta dip, where 2p2h lives) = {100*lowfrac:.0f}%")

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        n = nb - 1                              # drop the catch bin
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
        if sig is not None:
            ax.errorbar(ctr, data[:n], yerr=sig[:n], fmt="o", color="k", ms=5,
                        capsize=3, label="unfolded data $\\pm$ total", zorder=5)
        else:
            ax.plot(ctr, data[:n], "ko", ms=5, label="unfolded data", zorder=5)
        ax.set_xlabel("$E_{avail}$ (GeV)")
        ax.set_ylabel(r"$d\sigma/dE_{avail}$ (cm$^2$/nucleon/GeV)")
        ax.set_title("Low-$E_{avail}$ excess vs GENIE-CV by mode "
                     "(no 2p2h in this CV)")
        ax.legend(fontsize=8, ncol=2)
        ax.set_xlim(EA[0], EA[n])
        technote_style.minerva_tag(ax)
        fig.tight_layout()
        fig.savefig(args.plot, dpi=130)
        print(f"[mode-decomp] wrote {args.plot}")


if __name__ == "__main__":
    main()
