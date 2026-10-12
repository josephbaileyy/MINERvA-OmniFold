#!/usr/bin/env python3
"""Build the C04+X01-repaired 2D covariance from the adopted products (no re-unfold).

Grant: docs/orchestration/AUTHORIZATION-20261012-2d-closeout-fluxrepair.md (sha256 1b079177...).

The adopted universe rollup (VL172, analyze_universes.py --add-norm 0.014 --bootstrap-cov VL170) is
kept block for block, with two blocks replaced:

  C04  Flux: MAT MnvVertErrorBand::CalcCovMx with the per-universe nu-e+IMD constraint weights,
       C = sum_u w_u (X_u - xbar_w)(X_u - xbar_w)^T / sum_u w_u,  xbar_w = sum_u w_u X_u / sum_u w_u,
       over the 100 existing flux-fixed Flux universe outputs. The weights are read from the Flux band
       of every per-playlist flux MnvH1D (GetUnivWgts) and checked against the constraint file.
  X01  Muon_Energy_MINOS: each of the 2 existing outputs is multiplied per pT bin by
       Phi_CV(pT) / Phi_MINOS,u(pT), the POT-combined flux integral of the MINOS correlated-flux
       universe (exact: Phi enters only as a per-pT divisor). Block: unweighted MAT form, 1/N.

Every other block (42 bands + the 1.4 % normalization) is copied from the adopted file and checked
byte-identical. The total is accumulated in analyze_universes.py's order (sorted bands, then the
normalization), and hCov_combined = total + C_boot, so the control path (no swap) must reproduce the
adopted hCov_universe_total and hCov_combined bitwise.

MAT checks: the weighted Flux block, the rescaled MINOS block, and the whole repaired universe block
(44 vertical bands on one 205-bin MnvH1D, GetTotalErrorMatrix) against numpy, max|diff|/max|C| <= 1e-12.

Writes, under --out:
  uq_universe_covariance_c04x01.root   analyze_universes.py schema (hCov_universe_total, per band,
                                       hCov_combined, hSigma_*, hReportedCells)
  uq_universe_covariance_control.root  the same schema rebuilt without the swap (control)
  cov2d_blocks_205.npz / .json         the Fig. 1 export, repaired (same keys as the 2026-10-11 one)
  cov2d_blocks_205_control.npz         the same export from the adopted file (control)
  minos_rescaled.npz                   the two rescaled MINOS outputs and their per-pT factors
  budget.json                          per band / block / total: per-cell median, p84, max, integral
  build.json                           inputs with sha256, every check, every headline number

Read-only on every input. Login node. Run in the root_6_28 environment with MAT on the library path.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
D = f"{R}/2d-unfolding"
UQ = f"{D}/uq"
BF = f"{D}/baseline_flux"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
FLUX_HIST = "pTmu_reweightedflux_integrated"
INPUTS = {
    "cv_E_U": f"{UQ}/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    "rollup_vl172": f"{UQ}/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/"
                    "uq_universe_covariance_full_matcorr_fluxfix.root",
    "boot_vl170": f"{UQ}/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root",
    "ml": f"{UQ}/seedscan_lgbm_ml/uq_covariance_ml.root",
    "flux_band": f"{BF}/flux_integral_universes_MEFHC.root",
    "flux_mefhc": f"{BF}/runEventLoopMC_MEFHC.root",
    "constraint": f"{R}/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
                  "sorted_NuEConstraint_FHC_RHC_IMD.txt",
}
PINNED = {  # sha256 pinned by the grant's inputs (VL172/VL173 receipts) and the C04 verification
    "cv_E_U": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c",
    "rollup_vl172": "077912e3e7a53376c6df89ee1af4a2a504fe1f49423bab88780204beccd952f5",
    "boot_vl170": "71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115",
    "ml": "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9",
    "flux_band": "5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb",
    "constraint": "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2",
}
SWEEP_GLOB = f"{UQ}/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root"
UNI_RE = re.compile(r".*_uni_(?P<band>[A-Za-z0-9_]+?)_(?P<idx>\d+)\.root$")  # analyze_universes.py
FLUX_BAND, MINOS_BAND, NORM_BAND = "full_Flux", "full_Muon_Energy_MINOS", "__Normalization_flat"
MAT_TOL = 1e-12

out = {"grant": "AUTHORIZATION-20261012-2d-closeout-fluxrepair.md", "inputs": {}, "checks": {},
       "numbers": {}}


def fail(msg):
    out["FAILED"] = msg
    print(f"[FAIL] {msg}")
    raise SystemExit(2)


def check(name, ok, value=None):
    out["checks"][name] = {"pass": bool(ok), "value": value}
    print(f"[check] {name}: {'PASS' if ok else 'FAIL'}  {value if value is not None else ''}")
    if not ok:
        fail(name)


def sha(path):
    h = hashlib.sha256()
    with open(os.path.realpath(path), "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def th2(path, name="hXSec2D"):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if not h:
        fail(f"{name} missing in {path}")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.array([[h.GetBinContent(ix, iy) for iy in range(1, ny + 1)] for ix in range(1, nx + 1)])
    area = np.array([[h.GetXaxis().GetBinWidth(ix) * h.GetYaxis().GetBinWidth(iy)
                      for iy in range(1, ny + 1)] for ix in range(1, nx + 1)])
    f.Close()
    return a, area


def sq(f, name):
    h = f.Get(name)
    if not h:
        return None
    n = h.GetNbinsX()
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])


def wcov(X, w):
    """MAT MnvVertErrorBand::CalcCovMx with universe weights (w = 1 gives analyze_universes' form)."""
    w = np.asarray(w, float)
    mu = (w[:, None] * X).sum(axis=0) / w.sum()
    Z = X - mu
    return (Z.T * w) @ Z / w.sum()


def mat_cov(c, bands, weights=None):
    """GetTotalErrorMatrix(no stat, absolute, no area norm) of a 205-bin MnvH1D with these vert bands."""
    n = c.size
    tag = "_".join(sorted(bands))[:40] + str(len(bands))
    h = ROOT.PlotUtils.MnvH1D(f"h_{abs(hash(tag))}", "", n, 0.0, float(n))
    for i in range(n):
        h.SetBinContent(i + 1, float(c[i]))
        h.SetBinError(i + 1, 0.0)
    for b, X in bands.items():
        h.AddVertErrorBand(b, int(X.shape[0]))
        vb = h.GetVertErrorBand(b)
        for u in range(X.shape[0]):
            hu = vb.GetHist(u)
            for i in range(n):
                hu.SetBinContent(i + 1, float(X[u, i]))
                hu.SetBinError(i + 1, 0.0)
        if weights and b in weights:
            vec = ROOT.std.vector("double")()
            for x in weights[b]:
                vec.push_back(float(x))
            vb.SetUnivWgts(vec)
    tm = h.GetTotalErrorMatrix(False, False, False)
    return np.array([[tm(i + 1, j + 1) for j in range(n)] for i in range(n)])


def rel_max(a, b):
    return float(np.abs(a - b).max() / np.abs(b).max())


def write_rollup(path, bands_cov, total, combined, cells_hist_src, NX, NY, rep_flat, pt_edges, pz_edges):
    """Same object set and names as analyze_universes.py."""
    rf = ROOT.TFile.Open(path, "RECREATE")

    def cov_h(name, title, m):
        n = m.shape[0]
        h = ROOT.TH2D(name, title, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, float(m[i, j]))
        h.Write()

    def sig_h(name, title, s):
        full = np.zeros(NX * NY)
        full[rep_flat] = s
        full2d = full.reshape(NX, NY, order="C")
        h = ROOT.TH2D(name, title, len(pt_edges) - 1, pt_edges, len(pz_edges) - 1, pz_edges)
        for ix in range(NX):
            for iy in range(NY):
                h.SetBinContent(ix + 1, iy + 1, float(full2d[ix, iy]))
        h.Write()

    cov_h("hCov_universe_total", "Universe-only covariance, reported bins", total)
    sig_h("hSigma_universe_total", "Universe-only sqrt(diag) over reported bins",
          np.sqrt(np.maximum(np.diag(total), 0)))
    for b, m in bands_cov.items():
        cov_h(f"hCov_universe_{b}", f"Universe covariance ({b})", m)
    cov_h("hCov_combined", "Universe + bootstrap covariance, reported bins", combined)
    sig_h("hSigma_combined", "Combined sqrt(diag) over reported bins",
          np.sqrt(np.maximum(np.diag(combined), 0)))
    cells_hist_src.Write("hReportedCells")
    rf.Close()


def summary(C, x, area):
    r = np.sqrt(np.maximum(np.diag(C), 0)) / x
    a = x * area
    return {"median_pct": float(100 * np.median(r)), "p84_pct": float(100 * np.percentile(r, 84)),
            "min_pct": float(100 * r.min()), "max_pct": float(100 * r.max()),
            "integral_sigma_pct": float(100 * np.sqrt(area @ C @ area) / a.sum()),
            "sqrt_trace": float(np.sqrt(np.trace(C)))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo", required=True, help="git archive of the repo at the grant's main (09c8bae0)")
    ap.add_argument("--committed-export", required=True,
                    help="receipts/2d-lgbm42-20261011/cov2d_blocks_205.npz (f04f496a...), for the export control")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    ROOT.gSystem.Load("libMAT.so")
    out["mat_library"] = os.path.realpath(ROOT.gSystem.DynamicPathName("libMAT.so", True) or "")

    # ---------------------------------------------------------------- inputs, re-hashed
    for k, p in INPUTS.items():
        out["inputs"][k] = {"path": p, "realpath": os.path.realpath(p), "sha256": sha(p)}
    for k, v in PINNED.items():
        check(f"input_pin_{k}", out["inputs"][k]["sha256"] == v, out["inputs"][k]["sha256"])
    out["inputs"]["committed_export"] = {"path": args.committed_export, "sha256": sha(args.committed_export)}
    check("input_pin_committed_export", out["inputs"]["committed_export"]["sha256"] ==
          "f04f496aa7ad04b76a5879e495bb18dbf44816f5f45412d8e444a983677317dc")
    for pl in PLAYLISTS:
        for kind in ("MC", "Data"):
            p = f"{BF}/runEventLoop{kind}_{pl}.root"
            out["inputs"][f"flux_{kind}_{pl}"] = {"path": p, "sha256": sha(p)}

    cv2, area2 = th2(INPUTS["cv_E_U"])
    NX, NY = cv2.shape
    rep2 = cv2 > 0
    rep = rep2.ravel(order="C")
    x = cv2.ravel(order="C")[rep]
    area = area2.ravel(order="C")[rep]
    check("n_reported_205", int(rep.sum()) == 205, int(rep.sum()))

    paths = sorted(glob.glob(SWEEP_GLOB))
    sweep = {}
    for p in paths:
        m = UNI_RE.match(os.path.basename(p))
        if not m:
            continue
        a, _ = th2(p)
        sweep.setdefault(m.group("band"), {})[int(m.group("idx"))] = {
            "x": a.ravel(order="C")[rep], "full": a, "path": p, "sha256": sha(p)}
    out["inputs"]["sweep"] = {b: {str(i): e["sha256"] for i, e in sorted(v.items())} for b, v in sorted(sweep.items())}
    out["inputs"]["sweep_digest"] = hashlib.sha256(
        "".join(e["sha256"] for b in sorted(sweep) for _, e in sorted(sweep[b].items())).encode()).hexdigest()
    check("sweep_44_bands_187_files", len(sweep) == 44 and sum(len(v) for v in sweep.values()) == 187,
          [len(sweep), sum(len(v) for v in sweep.values())])
    check("flux_100_minos_2", sorted(sweep[FLUX_BAND]) == list(range(100)) and
          sorted(sweep[MINOS_BAND]) == [0, 1])

    # ---------------------------------------------------------------- adopted blocks
    f = ROOT.TFile.Open(INPUTS["rollup_vl172"])
    stored = OrderedDict()
    for b in sorted(sweep):
        stored[b] = sq(f, f"hCov_universe_{b}")
        if stored[b] is None:
            fail(f"adopted rollup lacks hCov_universe_{b}")
    stored[NORM_BAND] = sq(f, f"hCov_universe_{NORM_BAND}")
    stored_total, stored_comb = sq(f, "hCov_universe_total"), sq(f, "hCov_combined")
    keys = [k.GetName() for k in f.GetListOfKeys()]
    # The adopted file predates hReportedCells; write it with the committed reported_cells.py.
    sys.path.insert(0, os.path.join(args.repo, "2d-unfolding", "uq"))
    from reported_cells import identity_hist, read_cells, reported_indices, require_same_cells
    cells = reported_indices(rep2)
    cells_h = identity_hist(cells)
    cells_h.SetDirectory(0)
    sig_ref = f.Get("hSigma_universe_total")
    pt_edges = np.array([sig_ref.GetXaxis().GetBinLowEdge(i) for i in range(1, sig_ref.GetNbinsX() + 2)])
    pz_edges = np.array([sig_ref.GetYaxis().GetBinLowEdge(i) for i in range(1, sig_ref.GetNbinsY() + 2)])
    f.Close()
    check("adopted_object_set", set(keys) == {"hCov_universe_total", "hSigma_universe_total", "hCov_combined",
                                              "hSigma_combined"} |
          {f"hCov_universe_{b}" for b in stored}, sorted(keys))
    fb = ROOT.TFile.Open(INPUTS["boot_vl170"]); C_boot = sq(fb, "hCov2D_reported")
    boot_cells, boot_src = read_cells(fb, mean_fallback="hMean2D"); fb.Close()
    require_same_cells(cells, boot_cells, "CV E_U", f"bootstrap ({boot_src})")
    check("boot_cells_equal_cv_cells", True, boot_src)
    fm = ROOT.TFile.Open(INPUTS["ml"]); C_ml = sq(fm, "hCov2D_reported"); fm.Close()

    def accumulate(blocks):
        tot = np.zeros((205, 205))
        for b in blocks:  # analyze_universes.py order: sorted bands, then the normalization
            tot += blocks[b]
        return tot, tot + C_boot

    # Control 1: the adopted total/combined are exactly this accumulation of the stored blocks.
    t0, c0 = accumulate(stored)
    check("control_total_bitwise", np.array_equal(t0, stored_total), rel_max(t0, stored_total))
    check("control_combined_bitwise", np.array_equal(c0, stored_comb), rel_max(c0, stored_comb))
    # Control 2: the Flux and MINOS blocks recompute bitwise from the sweep with analyze_universes' formula.
    def recompute(band):
        Dl = np.stack([sweep[band][i]["x"] - x for i in sorted(sweep[band])])
        Z = Dl - Dl.mean(axis=0, keepdims=True)
        return (Z.T @ Z) / Dl.shape[0]
    for b in (FLUX_BAND, MINOS_BAND):
        r = recompute(b)
        check(f"control_{b}_block_recompute", np.array_equal(r, stored[b]) or rel_max(r, stored[b]) < 1e-14,
              {"bitwise": bool(np.array_equal(r, stored[b])), "max_rel": rel_max(r, stored[b])})
    # Control 3: the export rebuilt from the adopted file equals the committed one bitwise.
    ce = np.load(args.committed_export)
    check("control_export_bitwise", np.array_equal(ce["universe_plus_boot"], stored_comb) and
          np.array_equal(ce["ml"], C_ml))
    np.savez(os.path.join(args.out, "cov2d_blocks_205_control.npz"), universe_plus_boot=stored_comb, ml=C_ml)

    # ---------------------------------------------------------------- C04: weights and weighted Flux block
    wl = []
    phi_cv_l, phi_minos_l, pot = [], [], []
    for pl in PLAYLISTS:
        fmc = ROOT.TFile.Open(f"{BF}/runEventLoopMC_{pl}.root")
        h = fmc.Get(FLUX_HIST)
        n_pt = h.GetNbinsX()
        vb = h.GetVertErrorBand("Flux")
        wl.append(np.array(list(vb.GetUnivWgts())))
        phi_cv_l.append(np.array([h.GetBinContent(i) for i in range(1, n_pt + 1)]))
        mb = h.GetVertErrorBand("Muon_Energy_MINOS")
        if not mb or mb.GetNHists() != 2:
            fail(f"{pl}: Muon_Energy_MINOS band missing or != 2 universes")
        phi_minos_l.append(np.array([[mb.GetHist(u).GetBinContent(i) for i in range(1, n_pt + 1)]
                                     for u in range(2)]))
        fmc.Close()
        fd = ROOT.TFile.Open(f"{BF}/runEventLoopData_{pl}.root")
        pot.append(float(fd.Get("POTUsed").GetVal()))
        fd.Close()
    w = wl[0]
    check("weights_100", w.size == 100, int(w.size))
    check("weights_identical_across_playlists", all(np.array_equal(w, wi) for wi in wl))
    cons = []
    with open(INPUTS["constraint"]) as fc:
        for line in fc:
            t = line.split()
            if len(t) == 3 and t[0] == "Flux":
                cons.append((int(t[1]), float(t[2])))
    cons = np.array([v for i, v in sorted(cons) if i < 100])
    check("weights_equal_constraint_file_first_100", cons.size == 100 and float(np.abs(cons - w).max()) == 0.0,
          float(np.abs(cons - w).max()) if cons.size == 100 else cons.size)
    out["numbers"]["weights"] = {"sum": float(w.sum()), "min": float(w.min()), "max": float(w.max()),
                                 "n_eff": float(w.sum() ** 2 / (w ** 2).sum())}

    XF = np.stack([sweep[FLUX_BAND][u]["x"] for u in range(100)])
    C_flux_w = wcov(XF, w)
    C_flux_u = wcov(XF, np.ones(100))
    check("flux_unweighted_wcov_equals_stored", rel_max(C_flux_u, stored[FLUX_BAND]) < 1e-14,
          rel_max(C_flux_u, stored[FLUX_BAND]))
    Mw = mat_cov(x, {"Flux": XF}, {"Flux": w})
    Mu = mat_cov(x, {"Flux": XF})
    check("mat_flux_weighted_le_1e-12", rel_max(Mw, C_flux_w) <= MAT_TOL, rel_max(Mw, C_flux_w))
    check("mat_flux_unweighted_vs_stored_le_1e-12", rel_max(Mu, stored[FLUX_BAND]) <= MAT_TOL,
          rel_max(Mu, stored[FLUX_BAND]))

    # ---------------------------------------------------------------- X01: MINOS denominator
    pot = np.array(pot)
    W = pot.sum()
    phi_cv = (np.stack(phi_cv_l).T @ pot) / W
    phi_minos = np.tensordot(pot, np.stack(phi_minos_l), axes=([0], [0])) / W  # (2, n_pt)
    fM = ROOT.TFile.Open(INPUTS["flux_mefhc"])
    hM = fM.Get(FLUX_HIST)
    phi_exist = np.array([hM.GetBinContent(i) for i in range(1, hM.GetNbinsX() + 1)])
    fM.Close()
    fB = ROOT.TFile.Open(INPUTS["flux_band"])
    hB = fB.Get("hFluxCV")
    phi_band = np.array([hB.GetBinContent(i) for i in range(1, hB.GetNbinsX() + 1)])
    fB.Close()
    check("phi_cv_vs_runEventLoopMC_MEFHC_le_1e-9", rel_max(phi_cv, phi_exist) <= 1e-9, rel_max(phi_cv, phi_exist))
    check("phi_cv_vs_hFluxCV_le_1e-12", rel_max(phi_cv, phi_band) <= 1e-12, rel_max(phi_cv, phi_band))
    check("n_pt_equals_NX", phi_cv.size == NX, [phi_cv.size, NX])
    # The divisor each MINOS output actually used is its own hFlux_pt (Phi_CV); undo it, apply Phi_MINOS,u.
    used = []
    for u in range(2):
        fu = ROOT.TFile.Open(sweep[MINOS_BAND][u]["path"])
        hu = fu.Get("hFlux_pt")
        used.append(np.array([hu.GetBinContent(i) for i in range(1, hu.GetNbinsX() + 1)]))
        fu.Close()
    used = np.stack(used)
    check("minos_outputs_divided_by_phi_cv", rel_max(used, np.stack([phi_exist, phi_exist])) <= 1e-15,
          rel_max(used, np.stack([phi_exist, phi_exist])))
    scale = used / phi_minos  # (2, n_pt); per pT = axis 0 of hXSec2D
    out["numbers"]["minos_flux_ratio_phi_u_over_phi_cv"] = {
        f"u{u}": {"min": float((phi_minos[u] / phi_exist).min()), "max": float((phi_minos[u] / phi_exist).max())}
        for u in range(2)}
    XM_new = []
    for u in range(2):
        a = sweep[MINOS_BAND][u]["full"] * scale[u][:, None]
        XM_new.append(a.ravel(order="C")[rep])
    XM_new = np.stack(XM_new)
    np.savez(os.path.join(args.out, "minos_rescaled.npz"), scale=scale, phi_cv=phi_exist, phi_minos=phi_minos,
             x_rescaled=XM_new, x_adopted=np.stack([sweep[MINOS_BAND][u]["x"] for u in range(2)]))
    Dm = XM_new - x
    Zm = Dm - Dm.mean(axis=0, keepdims=True)
    C_minos = (Zm.T @ Zm) / 2
    Mm = mat_cov(x, {"Muon_Energy_MINOS": XM_new})
    check("mat_minos_rescaled_le_1e-12", rel_max(Mm, C_minos) <= MAT_TOL, rel_max(Mm, C_minos))

    # ---------------------------------------------------------------- repaired rollup
    repaired = OrderedDict((b, (C_flux_w if b == FLUX_BAND else C_minos if b == MINOS_BAND else stored[b]))
                           for b in stored)
    for b in repaired:
        if b not in (FLUX_BAND, MINOS_BAND):
            check(f"block_identical_{b}", repaired[b] is stored[b] and np.array_equal(repaired[b], stored[b]))
    t1, c1 = accumulate(repaired)
    # MAT on the whole universe block: all 44 vertical bands on one MnvH1D, Flux weighted, MINOS rescaled.
    bands = {}
    for b in sorted(sweep):
        if b == MINOS_BAND:
            bands[b] = XM_new
        else:
            bands[b] = np.stack([sweep[b][i]["x"] for i in sorted(sweep[b])])
    Mall = mat_cov(x, bands, {FLUX_BAND: w})
    check("mat_universe_total_minus_norm_le_1e-12", rel_max(Mall, t1 - stored[NORM_BAND]) <= MAT_TOL,
          rel_max(Mall, t1 - stored[NORM_BAND]))
    Mall0 = mat_cov(x, {b: (np.stack([sweep[b][i]["x"] for i in sorted(sweep[b])])) for b in sorted(sweep)})
    check("mat_adopted_universe_total_minus_norm_le_1e-12", rel_max(Mall0, stored_total - stored[NORM_BAND]) <= MAT_TOL,
          rel_max(Mall0, stored_total - stored[NORM_BAND]))

    write_rollup(os.path.join(args.out, "uq_universe_covariance_c04x01.root"), repaired, t1, c1, cells_h,
                 NX, NY, rep, pt_edges, pz_edges)
    write_rollup(os.path.join(args.out, "uq_universe_covariance_control.root"), stored, t0, c0, cells_h,
                 NX, NY, rep, pt_edges, pz_edges)
    # read-back: the written files hold exactly the matrices
    for fn, tt, cc, blocks in (("uq_universe_covariance_c04x01.root", t1, c1, repaired),
                               ("uq_universe_covariance_control.root", t0, c0, stored)):
        fr = ROOT.TFile.Open(os.path.join(args.out, fn))
        ok = np.array_equal(sq(fr, "hCov_universe_total"), tt) and np.array_equal(sq(fr, "hCov_combined"), cc) \
            and all(np.array_equal(sq(fr, f"hCov_universe_{b}"), m) for b, m in blocks.items())
        fr.Close()
        check(f"readback_{fn}", ok)

    np.savez(os.path.join(args.out, "cov2d_blocks_205.npz"), universe_plus_boot=c1, ml=C_ml)
    json.dump({"universe_plus_boot": {"path": os.path.join(args.out, "uq_universe_covariance_c04x01.root"),
                                      "object": "hCov_combined", "shape": [205, 205],
                                      "sqrt_trace": float(np.sqrt(np.trace(c1))),
                                      "construction": "VL172 rollup with the C04 (MAT-weighted Flux) and X01 "
                                                      "(MINOS / Phi_MINOS,u) blocks; universe + VL170 bootstrap"},
               "ml": {"path": INPUTS["ml"], "object": "hCov2D_reported", "sha256": PINNED["ml"],
                      "shape": [205, 205], "sqrt_trace": float(np.sqrt(np.trace(C_ml)))}},
              open(os.path.join(args.out, "cov2d_blocks_205.json"), "w"), indent=1)

    # ---------------------------------------------------------------- budget
    def budget(blocks, tot, comb):
        bs = comb + C_ml
        return {"per_band": {b: summary(m, x, area) for b, m in blocks.items()},
                "universe_plus_norm": summary(tot, x, area), "boot": summary(C_boot, x, area),
                "ml": summary(C_ml, x, area), "universe_plus_boot": summary(comb, x, area),
                "block_sum": summary(bs, x, area)}
    bud = {"x": "E_U hXSec2D (4f5a1b6d...), 205 reported cells; integral = sum x*area over them",
           "adopted": budget(stored, t0, c0), "repaired": budget(repaired, t1, c1)}
    json.dump(bud, open(os.path.join(args.out, "budget.json"), "w"), indent=1)
    out["numbers"]["block_sum_median_pct"] = {"adopted": bud["adopted"]["block_sum"]["median_pct"],
                                              "repaired": bud["repaired"]["block_sum"]["median_pct"]}
    out["numbers"]["block_sum_integral_pct"] = {"adopted": bud["adopted"]["block_sum"]["integral_sigma_pct"],
                                                "repaired": bud["repaired"]["block_sum"]["integral_sigma_pct"]}
    for b in (FLUX_BAND, MINOS_BAND):
        out["numbers"][f"{b}_median_pct"] = {"adopted": bud["adopted"]["per_band"][b]["median_pct"],
                                             "repaired": bud["repaired"]["per_band"][b]["median_pct"]}
    for b in (FLUX_BAND, MINOS_BAND):
        out["numbers"][f"{b}_integral_pct"] = {"adopted": bud["adopted"]["per_band"][b]["integral_sigma_pct"],
                                               "repaired": bud["repaired"]["per_band"][b]["integral_sigma_pct"]}
    check("control_block_sum_median_6.8707", round(bud["adopted"]["block_sum"]["median_pct"], 4) == 6.8707,
          bud["adopted"]["block_sum"]["median_pct"])
    for fn in sorted(os.listdir(args.out)):
        if fn != "build.json":
            out.setdefault("products", {})[fn] = sha(os.path.join(args.out, fn))
    out["ALL_CHECKS_PASS"] = all(v["pass"] for v in out["checks"].values())
    print(json.dumps(out["numbers"], indent=1))


if __name__ == "__main__":
    try:
        main()
    finally:
        a = sys.argv
        o = a[a.index("--out") + 1] if "--out" in a else "."
        os.makedirs(o, exist_ok=True)
        json.dump(out, open(os.path.join(o, "build.json"), "w"), indent=1)
