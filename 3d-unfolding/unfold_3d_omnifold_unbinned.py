#!/usr/bin/env python3
"""3D unbinned OmniFold driver: d^3 sigma / (dp_T dp_|| dEavail).

Workstream C (C2). Generalizes the 2D driver
(../2d-unfolding/unfold_2d_omnifold_unbinned.py) to add available energy as a
third axis. The OmniFold call is already dimension-agnostic; what changes is:
  - the feature column_stack gains the eavail column;
  - histogram binning / completeness / cross-section extraction go to 3D, via
    xsec_3d.py (extract_cross_section_3d / project_eavail_marginal / project_axis).

Reuse: data/MC/flux/POT/nucleon loading helpers, the truth phase-space gate, and
the analysis (pT, p_||) edges are imported from the 2D module rather than
duplicated. Only the 3D-specific readers and the bin/extract/project path are
new here.

Scope (staged): CV-only first closure + the real-data unfold whose
**Eavail-marginal must reproduce the frozen 2D cross section** (the validation
anchor — written out as a TH2D named ``hXSec2D`` so
../2d-unfolding/compare_to_paper_fullcov.py reads it unchanged). The systematic
universe / lateral-kinematics / alt-model / bootstrap machinery of the 2D driver
is intentionally NOT ported here; that is the deferred 3D-UQ campaign.

Usage (full MEFHC):
  python unfold_3d_omnifold_unbinned.py \
    --omnifile runEventLoopOmniFold_MEFHC_3D.root \
    --mcfile   ../2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root \
    --iters 5 --use-weights --estimator lgbm \
    --out xsec_3d_MEFHC.root
"""
import argparse
import math
import sys
from array import array

import numpy as np
import ROOT

# --- Reuse the mature 2D driver helpers (data loading, flux, POT, gate) ------
_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_2D = f"{_REPO}/2d-unfolding"
if _2D not in sys.path:
    sys.path.insert(0, _2D)
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402

sys.path.insert(0, f"{_REPO}/3d-unfolding")
from xsec_3d import (  # noqa: E402
    extract_cross_section_3d,
    project_eavail_marginal,
    project_axis,
)

PT_EDGES = u2d.PT_EDGES        # 14 bins (GeV/c)
PZ_EDGES = u2d.PZ_EDGES        # 16 bins (GeV/c)
# Default Eavail binning: physics-motivated low-recoil bins + a catch-all top
# bin so the marginal captures the full CC-inclusive recoil tail (truth Eavail
# runs 0 -> ~90 GeV). The catch bin is essential for the Eavail-marginal anchor:
# Sum_k xsec3d[i,j,k]*dEa_k == 2D xsec ONLY if every truth event lands in a bin.
EAVAIL_EDGES = [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]  # GeV, 7 bins


# ---------------------------------------------------------------------------
# 3D histogram helper
# ---------------------------------------------------------------------------
def make_th3d(name, title, xedges, yedges, zedges):
    h = ROOT.TH3D(name, title,
                  len(xedges) - 1, array("d", xedges),
                  len(yedges) - 1, array("d", yedges),
                  len(zedges) - 1, array("d", zedges))
    h.Sumw2()
    h.SetDirectory(0)
    return h


def numpy_to_th3d(arr, err, name, title, xedges, yedges, zedges):
    """Fill a TH3D from (n_pt, n_pz, n_ea) content + error arrays."""
    h = make_th3d(name, title, xedges, yedges, zedges)
    nx, ny, nz = arr.shape
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                h.SetBinContent(ix + 1, iy + 1, iz + 1, float(arr[ix, iy, iz]))
                if err is not None:
                    h.SetBinError(ix + 1, iy + 1, iz + 1, float(err[ix, iy, iz]))
    return h


def numpy_to_th2d(arr, err, name, title, xedges, yedges):
    h = u2d.make_th2d(name, title, xedges, yedges)
    nx, ny = arr.shape
    for ix in range(nx):
        for iy in range(ny):
            h.SetBinContent(ix + 1, iy + 1, float(arr[ix, iy]))
            if err is not None:
                h.SetBinError(ix + 1, iy + 1, float(err[ix, iy]))
    return h


def numpy_to_th1d(edges, vals, name, title):
    h = u2d.make_th1d(name, title, edges)
    for i, v in enumerate(vals, start=1):
        h.SetBinContent(i, float(v))
    return h


def hist3d(pt, pz, ea, w, pt_edges, pz_edges, ea_edges):
    """Weighted (n_pt, n_pz, n_ea) count + sqrt(sum w^2) error arrays.

    Events falling outside any axis range are dropped (np.histogramdd
    excludes them), matching the in-range convention of the 2D TH2D Fill.
    """
    sample = np.column_stack([pt, pz, ea])
    bins = [np.asarray(pt_edges, float), np.asarray(pz_edges, float),
            np.asarray(ea_edges, float)]
    counts, _ = np.histogramdd(sample, bins=bins, weights=w)
    sumw2, _ = np.histogramdd(sample, bins=bins, weights=np.asarray(w) ** 2)
    return counts, np.sqrt(sumw2)


# ---------------------------------------------------------------------------
# 3D TTree readers (eavail-aware; CV weights)
# ---------------------------------------------------------------------------
def collect_truth_denom_3d(t, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                           use_weights=False, verbose=False):
    """mc_truth_denom -> truth-only (pt, pz, ea, w) for the completeness denom."""
    pt_a = array("d", [0.0]); pz_a = array("d", [0.0]); ea_a = array("d", [0.0])
    wt_a = array("d", [1.0])
    t.SetBranchAddress("MC", pt_a)
    t.SetBranchAddress("MC_pz", pz_a)
    t.SetBranchAddress("MC_eavail", ea_a)
    if use_weights:
        t.SetBranchAddress("w_truth", wt_a)
    pt_l, pz_l, ea_l, w_l = [], [], [], []
    bad, drop = 0, 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        pt, pz, ea = float(pt_a[0]), float(pz_a[0]), float(ea_a[0])
        w = float(wt_a[0]) if use_weights else 1.0
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(ea)
                and math.isfinite(w) and 0 <= w < 1e4):
            bad += 1
            continue
        if not u2d.in_truth_phase_space(pt, pz, pt_lo, pt_hi, pz_lo, pz_hi):
            drop += 1
            continue
        pt_l.append(pt); pz_l.append(pz); ea_l.append(ea); w_l.append(w * pot_scale)
    if verbose:
        print(f"[INFO] truth_denom: kept={len(pt_l)}, dropped={drop}, bad={bad}")
    return {"truth_pt": np.asarray(pt_l), "truth_pz": np.asarray(pz_l),
            "truth_ea": np.asarray(ea_l), "w_truth": np.asarray(w_l)}


def collect_signal_3d(t, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                      use_weights=False, verbose=False):
    """mc_signal_reco -> dict of 3D arrays for OmniFold.

    Gating mirrors the 2D driver's collect_signal_arrays_2d: truth-pass via the
    (pT, p_||) phase-space gate, reco-pass via sim_pass AND the (pT, p_||)
    rectangle. Eavail is NOT gated (it is the extra observable, not a fiducial
    cut); reco eavail is -9999 wherever the event does not reco-pass.
    """
    mc_pt = array("d", [0.0]); mc_pz = array("d", [0.0]); mc_ea = array("d", [0.0])
    sim_pt = array("d", [0.0]); sim_pz = array("d", [0.0]); sim_ea = array("d", [0.0])
    sim_pass = array("B", [0])
    wt_a = array("d", [1.0]); wr_a = array("d", [1.0])
    t.SetBranchAddress("MC", mc_pt)
    t.SetBranchAddress("MC_pz", mc_pz)
    t.SetBranchAddress("MC_eavail", mc_ea)
    t.SetBranchAddress("sim", sim_pt)
    t.SetBranchAddress("sim_pz", sim_pz)
    t.SetBranchAddress("sim_eavail", sim_ea)
    t.SetBranchAddress("sim_pass", sim_pass)
    if use_weights:
        t.SetBranchAddress("w_truth", wt_a)
        t.SetBranchAddress("w_reco", wr_a)

    tpt, tpz, tea = [], [], []
    rpt, rpz, rea = [], [], []
    pr, ptr, wtl, wrl = [], [], [], []
    drop, bad = 0, 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        a_pt, a_pz, a_ea = float(mc_pt[0]), float(mc_pz[0]), float(mc_ea[0])
        b_pt, b_pz, b_ea = float(sim_pt[0]), float(sim_pz[0]), float(sim_ea[0])
        passed = sim_pass[0] != 0
        wt = float(wt_a[0]) if use_weights else 1.0
        wr = float(wr_a[0]) if use_weights else wt
        if not (math.isfinite(wt) and math.isfinite(wr)
                and 0 <= wt < 1e4 and 0 <= wr < 1e4):
            bad += 1
            continue
        wt *= pot_scale; wr *= pot_scale
        tru_ok = u2d.in_truth_phase_space(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(b_pt) and math.isfinite(b_pz)
                  and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru_ok or (passed and rec_ok)):
            drop += 1
            continue
        tpt.append(a_pt if math.isfinite(a_pt) else -9999.0)
        tpz.append(a_pz if math.isfinite(a_pz) else -9999.0)
        tea.append(a_ea if math.isfinite(a_ea) else -9999.0)
        rpt.append(b_pt if (passed and rec_ok) else -9999.0)
        rpz.append(b_pz if (passed and rec_ok) else -9999.0)
        rea.append(b_ea if (passed and rec_ok and math.isfinite(b_ea)) else -9999.0)
        pr.append(passed and rec_ok)
        ptr.append(tru_ok)
        wtl.append(wt); wrl.append(wr)
    if verbose:
        print(f"[INFO] signal: kept={len(tpt)}, dropped={drop}, bad={bad}")
    return {
        "truth_pt": np.asarray(tpt), "truth_pz": np.asarray(tpz),
        "truth_ea": np.asarray(tea),
        "reco_pt": np.asarray(rpt), "reco_pz": np.asarray(rpz),
        "reco_ea": np.asarray(rea),
        "pass_reco": np.asarray(pr, bool), "pass_truth": np.asarray(ptr, bool),
        "w_truth": np.asarray(wtl), "w_reco": np.asarray(wrl),
    }


def collect_data_3d(t, pt_lo, pt_hi, pz_lo, pz_hi, guard_max=1e3, verbose=False):
    meas = array("d", [0.0]); meas_pz = array("d", [0.0]); meas_ea = array("d", [0.0])
    meas_pass = array("B", [0])
    t.SetBranchAddress("measured", meas)
    t.SetBranchAddress("measured_pz", meas_pz)
    t.SetBranchAddress("measured_eavail", meas_ea)
    t.SetBranchAddress("measured_pass", meas_pass)
    pts, pzs, eas = [], [], []
    skip = 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        if meas_pass[0] == 0:
            skip += 1
            continue
        pt, pz, ea = float(meas[0]), float(meas_pz[0]), float(meas_ea[0])
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(ea)):
            skip += 1
            continue
        if abs(pt) > guard_max or abs(pz) > guard_max:
            skip += 1
            continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            skip += 1
            continue
        pts.append(pt); pzs.append(pz); eas.append(ea)
    if verbose:
        print(f"[INFO] data: kept={len(pts)}, skipped={skip}")
    return (np.asarray(pts), np.asarray(pzs), np.asarray(eas))


def collect_bkg_3d(t, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi,
                   guard_max=1e3, verbose=False):
    sb = array("d", [0.0]); sb_pz = array("d", [0.0]); sb_ea = array("d", [0.0])
    sb_pass = array("B", [0]); w_b = array("d", [1.0])
    t.SetBranchAddress("sim_background", sb)
    t.SetBranchAddress("sim_background_pz", sb_pz)
    t.SetBranchAddress("sim_background_eavail", sb_ea)
    t.SetBranchAddress("sim_background_pass", sb_pass)
    t.SetBranchAddress("w_bkg", w_b)
    pts, pzs, eas, ws = [], [], [], []
    skip = 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        if sb_pass[0] == 0:
            skip += 1
            continue
        pt, pz, ea, w = float(sb[0]), float(sb_pz[0]), float(sb_ea[0]), float(w_b[0])
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(ea)
                and math.isfinite(w) and 0 <= w < 1e6):
            skip += 1
            continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            skip += 1
            continue
        pts.append(pt); pzs.append(pz); eas.append(ea); ws.append(w * pot_scale)
    if verbose:
        print(f"[INFO] bkg: kept={len(pts)}, skipped={skip}")
    return (np.asarray(pts), np.asarray(pzs), np.asarray(eas), np.asarray(ws))


def build_measured_training_3d(meas_pt, meas_pz, meas_ea, data3d, bkg3d,
                               pt_edges, pz_edges, ea_edges, verbose=False):
    """Per-event measured training weights = max(0, data-bkg)/data in the
    reco-space (pT, p_||, Eavail) bin the event falls in. Mirrors the 2D
    build_measured_training_2d floor-at-zero convention."""
    target = np.maximum(0.0, data3d - bkg3d)
    ix = np.digitize(meas_pt, pt_edges) - 1
    iy = np.digitize(meas_pz, pz_edges) - 1
    iz = np.digitize(meas_ea, ea_edges) - 1
    nx, ny, nz = data3d.shape
    weights = np.zeros(meas_pt.shape[0], dtype=float)
    n_zero = 0
    for i in range(meas_pt.shape[0]):
        a, b, c = ix[i], iy[i], iz[i]
        if not (0 <= a < nx and 0 <= b < ny and 0 <= c < nz):
            n_zero += 1
            continue
        d = data3d[a, b, c]
        if d <= 0.0:
            n_zero += 1
            continue
        weights[i] = target[a, b, c] / d
    if verbose:
        print(f"[INFO] measured training: eff sum={weights.sum():.6g}, "
              f"zero-weight={n_zero}/{weights.size}")
    return weights


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_MEFHC_3D.root",
                    help="3D omnifile from runEventLoopOmniFold (eavail branches)")
    ap.add_argument("--mcfile",
                    default=f"{_2D}/baseline_flux/runEventLoopMC_MEFHC.root",
                    help="Binned MC file holding the flux histogram")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--use-weights", action="store_true",
                    help="Use w_truth/w_reco CV weights from the event loop")
    ap.add_argument("--estimator", default="lgbm",
                    help="OmniFold GBDT estimator (lgbm/histgb/gb)")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--bootstrap-seed", type=int, default=None,
                    help="Poisson(1) bootstrap on data+MC weights for the "
                         "statistical-uncertainty band (mirrors the 2D driver). "
                         "CV result is the unweighted unfold (flag omitted).")
    ap.add_argument("--eavail-edges", default=None,
                    help="Comma-separated Eavail bin edges (GeV); "
                         "default = physics bins + catch-all top bin")
    ap.add_argument("--out", default="xsec_3d_MEFHC.root")
    ap.add_argument("--verbose", action="store_true")
    # --- Closure (C3) ---
    ap.add_argument("--closure", action="store_true",
                    help="Closure test: use MC reco (pass_reco & pass_truth) as "
                         "pseudo-data instead of real data; completeness=1; the "
                         "3D unfold + Eavail-marginal must recover the (optionally "
                         "reweighted) MC truth reference within MC-stat noise.")
    ap.add_argument("--closure-reweight-eavail", action="store_true",
                    help="Truth-reweight closure on the NEW axis: apply a Gaussian "
                         "bump in truth Eavail to BOTH the pseudo-data weights and "
                         "the truth reference. Tests whether 3D OmniFold recovers "
                         "an injected Eavail shape (requires --closure).")
    ap.add_argument("--closure-eavail-amplitude", type=float, default=0.3)
    ap.add_argument("--closure-eavail-center", type=float, default=0.3,
                    help="GeV; center of the truth-Eavail Gaussian bump")
    ap.add_argument("--closure-eavail-sigma", type=float, default=0.15,
                    help="GeV; width of the truth-Eavail Gaussian bump")
    args = ap.parse_args()
    if args.closure_reweight_eavail and not args.closure:
        ap.error("--closure-reweight-eavail requires --closure")

    pt_edges = PT_EDGES
    pz_edges = PZ_EDGES
    ea_edges = ([float(x) for x in args.eavail_edges.split(",")]
                if args.eavail_edges else EAVAIL_EDGES)
    pt_lo, pt_hi = pt_edges[0], pt_edges[-1]
    pz_lo, pz_hi = pz_edges[0], pz_edges[-1]
    print(f"[INFO] pT  edges ({len(pt_edges)-1} bins): {pt_edges}")
    print(f"[INFO] p|| edges ({len(pz_edges)-1} bins): {pz_edges}")
    print(f"[INFO] Eavail edges ({len(ea_edges)-1} bins): {ea_edges}")

    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")
    t_sig = f_in.Get("mc_signal_reco")
    t_bkg = f_in.Get("mc_background")
    t_data = f_in.Get("data")
    t_truth_denom = f_in.Get("mc_truth_denom")
    if not (t_sig and t_bkg and t_data and t_truth_denom):
        raise RuntimeError("Missing required TTrees (need eavail-branch omnifile)")
    for tree, bname in [(t_sig, "sim_eavail"), (t_sig, "MC_eavail"),
                        (t_bkg, "sim_background_eavail"),
                        (t_data, "measured_eavail")]:
        if not tree.GetListOfBranches().FindObject(bname):
            raise RuntimeError(f"Branch '{bname}' missing from '{tree.GetName()}'. "
                               "Re-run the C1 event loop.")

    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f_in)
    print(f"[INFO] POT: data={data_pot:.4g}, mc={mc_pot:.4g}, scale={pot_scale:.6g}")

    p_has = f_in.Get("hasTruthOnlyMisses")
    has_misses = bool(int(p_has.GetVal())) if p_has else False
    print(f"[INFO] Phase-17 truth-only-miss mode: {has_misses} "
          f"(completeness expected ~1)")

    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    print(f"[INFO] Fiducial nucleons (geometry): {n_nucleons:.6e}")

    flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_edges)
    print(f"[INFO] Flux bins (m^-2/POT): {flux_bins}")
    print(f"[INFO] Flux sum = {flux_bins.sum():.4g} m^-2/POT")

    # --- Read arrays ---
    meas_pt, meas_pz, meas_ea = collect_data_3d(
        t_data, pt_lo, pt_hi, pz_lo, pz_hi, verbose=args.verbose)
    bkg_pt, bkg_pz, bkg_ea, bkg_w = collect_bkg_3d(
        t_bkg, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi, verbose=args.verbose)
    sig = collect_signal_3d(t_sig, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                            use_weights=args.use_weights, verbose=args.verbose)
    truth_denom = collect_truth_denom_3d(t_truth_denom, pt_lo, pt_hi, pz_lo, pz_hi,
                                         pot_scale, use_weights=args.use_weights,
                                         verbose=args.verbose)
    if sig["truth_pt"].size == 0 or meas_pt.size == 0:
        raise RuntimeError("Empty signal or data after selection")

    # --- Closure: substitute MC reco (pass_reco & pass_truth) as pseudo-data ---
    # Mirrors the 2D driver: pseudo-data weights are w_reco (not a data-bkg
    # floor), so step-1 learns ~identity and step-2 should recover the CV (or
    # reweighted) MC truth. closure_rw is f(truth) applied to BOTH the
    # pseudo-data and the truth reference (built after the unfold).
    closure_rw_truthpass = None  # f(truth) on the pass_truth subset (for reference)
    if args.closure:
        print("[INFO] *** CLOSURE MODE: MC reco as pseudo-data ***")
        cmask = sig["pass_reco"] & sig["pass_truth"]
        meas_pt = sig["reco_pt"][cmask].copy()
        meas_pz = sig["reco_pz"][cmask].copy()
        meas_ea = sig["reco_ea"][cmask].copy()
        measured_weights = (sig["w_reco"][cmask].copy() if args.use_weights
                            else np.ones(meas_pt.size))
        if args.closure_reweight_eavail:
            tea_c = sig["truth_ea"][cmask]
            A, c0, s = (args.closure_eavail_amplitude,
                        args.closure_eavail_center, args.closure_eavail_sigma)
            rw_data = 1.0 + A * np.exp(-((tea_c - c0) / s) ** 2)
            measured_weights = measured_weights * rw_data
            print(f"[INFO] Eavail reweight closure: A={A}, center={c0} GeV, "
                  f"sigma={s} GeV; data factor mean={rw_data.mean():.4f}, "
                  f"max={rw_data.max():.4f}")
            # The matching factor on the pass_truth subset (for the reference).
            tea_t = sig["truth_ea"][sig["pass_truth"]]
            closure_rw_truthpass = 1.0 + A * np.exp(-((tea_t - c0) / s) ** 2)
        print(f"[INFO] closure pseudo-data: {meas_pt.size} events, "
              f"sum(w)={measured_weights.sum():.6g}")
    else:
        # --- Real data: measured training target (data - bkg, floored) ---
        data3d, _ = hist3d(meas_pt, meas_pz, meas_ea,
                           np.ones(meas_pt.size), pt_edges, pz_edges, ea_edges)
        bkg3d, _ = hist3d(bkg_pt, bkg_pz, bkg_ea, bkg_w,
                          pt_edges, pz_edges, ea_edges)
        measured_weights = build_measured_training_3d(
            meas_pt, meas_pz, meas_ea, data3d, bkg3d,
            pt_edges, pz_edges, ea_edges, verbose=args.verbose)

    # --- Poisson(1) bootstrap (statistical uncertainty) ---
    # Independent Poisson(1) multipliers on data and MC weights, so data-stat
    # and MC-stat contribute jointly per replica (mirrors the 2D driver). The
    # reco weight rides the truth draw so a single MC event is consistently
    # up/down-weighted at truth and reco level.
    if args.bootstrap_seed is not None:
        rng_d = np.random.default_rng(args.bootstrap_seed)
        rng_m = np.random.default_rng(args.bootstrap_seed + 10_000_000)
        b_data = rng_d.poisson(1.0, size=measured_weights.shape[0]).astype(float)
        b_mc = rng_m.poisson(1.0, size=sig["w_truth"].shape[0]).astype(float)
        measured_weights = measured_weights * b_data
        sig["w_truth"] = sig["w_truth"] * b_mc
        sig["w_reco"] = sig["w_reco"] * b_mc
        print(f"[INFO] Poisson bootstrap seed={args.bootstrap_seed}: "
              f"data factor sum={b_data.sum():.6g}, mc factor sum={b_mc.sum():.6g}")

    # --- OmniFold ---
    _OF_PY = f"{_REPO}/unbinned_unfolding/python"
    if _OF_PY not in sys.path:
        sys.path.insert(0, _OF_PY)
    from omnifold import OmniFold_helper_functions as ohf

    print(f"[INFO] Running 3D OmniFold ({args.iters} iters, "
          f"estimator={args.estimator})...")
    print(f"[INFO] MC events: {sig['truth_pt'].size}, "
          f"pass_truth={sig['pass_truth'].sum()}, pass_reco={sig['pass_reco'].sum()}")
    print(f"[INFO] Measured events: {meas_pt.size}, "
          f"eff training sum={measured_weights.sum():.6g}")

    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"], sig["truth_ea"]])
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"], sig["reco_ea"]])
    measured = np.column_stack([meas_pt, meas_pz, meas_ea])

    if args.seed is not None:
        c1 = {"random_state": int(args.seed)}
        c2 = {"random_state": int(args.seed) + 1}
        rg = {"random_state": int(args.seed) + 2}
    else:
        c1 = c2 = rg = None

    step1_weights, step2_weights = ohf.omnifold(
        MCgen, MCreco, measured,
        sig["pass_reco"], sig["pass_truth"],
        np.ones(meas_pt.size, dtype=bool),
        int(args.iters),
        MCgen_weights=sig["w_truth"] if args.use_weights else None,
        MCreco_weights=sig["w_reco"] if args.use_weights else None,
        measured_weights=measured_weights,
        classifier1_params=c1, classifier2_params=c2, regressor_params=rg,
        parameter_format="dict",
        estimator=args.estimator, device=args.device,
    )
    print(f"[INFO] OmniFold done. step2 sum={step2_weights.sum():.4g}, "
          f"mean={step2_weights.mean():.4f}, "
          f"min={step2_weights.min():.4f}, max={step2_weights.max():.4f}")

    # --- Bin truth-pass events into 3D (prior, unfolded, completeness) ---
    m = sig["pass_truth"]
    tpt, tpz, tea = sig["truth_pt"][m], sig["truth_pz"][m], sig["truth_ea"][m]
    tw = sig["w_truth"][m]
    if tpt.size != step2_weights.size:
        raise RuntimeError(f"weight size mismatch: truth={tpt.size}, "
                           f"step2={step2_weights.size}")

    prior3d, prior_err = hist3d(tpt, tpz, tea, tw, pt_edges, pz_edges, ea_edges)
    unfold3d, unfold_err = hist3d(tpt, tpz, tea, step2_weights * tw,
                                  pt_edges, pz_edges, ea_edges)

    # Completeness c = (OmniFold-input truth-pass) / (full mc_truth_denom), 3D.
    # In closure the pseudo-data lives in the same subset as the training, so no
    # scale-up is appropriate: c == 1 (mirrors the 2D driver's closure path).
    if args.closure:
        completeness3d = np.ones((len(pt_edges) - 1, len(pz_edges) - 1,
                                  len(ea_edges) - 1), dtype=float)
        c_global = 1.0
        print("[INFO] closure: completeness set to 1.0 in all bins.")
    else:
        of_input3d, _ = hist3d(tpt, tpz, tea, tw, pt_edges, pz_edges, ea_edges)
        denom3d, _ = hist3d(truth_denom["truth_pt"], truth_denom["truth_pz"],
                            truth_denom["truth_ea"], truth_denom["w_truth"],
                            pt_edges, pz_edges, ea_edges)
        completeness3d = np.zeros_like(of_input3d)
        nz = denom3d > 0
        completeness3d[nz] = of_input3d[nz] / denom3d[nz]
        c_global = (of_input3d.sum() / denom3d.sum()
                    if denom3d.sum() > 0 else float("nan"))
        print(f"[CHECK] global completeness c = {c_global:.4f} "
              f"(expect ~1 in Phase-17 mode)")
    print(f"[CHECK] prior3d integral (counts): {prior3d.sum():.6g}")
    print(f"[CHECK] unfold3d integral (counts): {unfold3d.sum():.6g}")

    # --- Extract 3D cross section + projections ---
    flux_arr = np.asarray(flux_bins, float)
    xsec3d, good = extract_cross_section_3d(
        unfold3d, completeness3d, flux_arr, data_pot, n_nucleons,
        pt_edges, pz_edges, ea_edges)
    # Error propagation: relative error from counts and completeness, same as 2D.
    rel_u = np.zeros_like(unfold3d)
    np.divide(unfold_err, unfold3d, out=rel_u, where=unfold3d > 0)
    xsec3d_err = np.abs(xsec3d) * rel_u  # completeness err ~ MC-stat, sub-dominant

    xsec2d_marg = project_eavail_marginal(xsec3d, ea_edges)
    # Marginal error: quadrature over Eavail bins (each scaled by dEa).
    dea = np.diff(ea_edges)[None, None, :]
    marg_err = np.sqrt(((xsec3d_err * dea) ** 2).sum(axis=2))

    pt_e, x_pt = project_axis(xsec3d, pt_edges, pz_edges, ea_edges, "pt")
    pz_e, x_pz = project_axis(xsec3d, pt_edges, pz_edges, ea_edges, "pz")
    ea_e, x_ea = project_axis(xsec3d, pt_edges, pz_edges, ea_edges, "eavail")

    total = (xsec3d * np.diff(pt_edges)[:, None, None]
             * np.diff(pz_edges)[None, :, None]
             * np.diff(ea_edges)[None, None, :]).sum()
    print(f"[CHECK] total xsec (3D integral): {total:.4g} cm^2/nucleon")
    marg_total = (xsec2d_marg * np.diff(pt_edges)[:, None]
                  * np.diff(pz_edges)[None, :]).sum()
    print(f"[CHECK] total xsec (Eavail-marginal 2D integral): {marg_total:.4g} "
          f"cm^2/nucleon  (should equal the 3D integral)")

    # --- Closure residuals: 3D unfold vs the (optionally reweighted) truth ---
    # Reference truth counts = prior (CV) or prior*f(truth) (reweight closure),
    # pushed through the same extraction (c=1) so it lives in xsec units.
    ref3d = None
    if args.closure:
        ref_w = tw if closure_rw_truthpass is None else tw * closure_rw_truthpass
        ref3d, ref_err = hist3d(tpt, tpz, tea, ref_w, pt_edges, pz_edges, ea_edges)
        ref_xsec3d, _ = extract_cross_section_3d(
            ref3d, completeness3d, flux_arr, data_pot, n_nucleons,
            pt_edges, pz_edges, ea_edges)
        ref_marg = project_eavail_marginal(ref_xsec3d, ea_edges)
        _, ref_x_ea = project_axis(ref_xsec3d, pt_edges, pz_edges, ea_edges, "eavail")

        def _resid(num, den):
            m = den > 0
            r = np.full(num.shape, np.nan)
            r[m] = num[m] / den[m]
            return r

        r3 = _resid(xsec3d, ref_xsec3d)
        r2 = _resid(xsec2d_marg, ref_marg)
        rea = _resid(x_ea, ref_x_ea)
        print("\n=== CLOSURE RESIDUALS (unfold / truth-reference) ===")
        print(f"  3D bins      : median={np.nanmedian(r3):.4f} "
              f"mean={np.nanmean(r3):.4f} std={np.nanstd(r3):.4f} "
              f"max|dev|={np.nanmax(np.abs(r3-1)):.4f}")
        print(f"  Eavail-marg  : median={np.nanmedian(r2):.4f} "
              f"mean={np.nanmean(r2):.4f} std={np.nanstd(r2):.4f} "
              f"max|dev|={np.nanmax(np.abs(r2-1)):.4f}")
        print(f"  Eavail 1D    : " + ", ".join(
            f"{v:.3f}" for v in rea) + "  (should be ~1 per bin)")
        if args.closure_reweight_eavail:
            inj = closure_rw_truthpass
            print(f"  [injected Eavail bump recovered if the 1D ratios track the "
                  f"f(truth) shape; injected mean factor={inj.mean():.4f}]")

    # --- Write output ---
    f_out = ROOT.TFile.Open(args.out, "RECREATE")
    f_out.cd()
    ROOT.TParameter("double")("dataPOT", data_pot).Write()
    ROOT.TParameter("double")("mcPOT", mc_pot).Write()
    ROOT.TParameter("double")("globalCompleteness", c_global).Write()

    h3 = numpy_to_th3d(xsec3d, xsec3d_err, "hXSec3D",
                       "d^{3}#sigma/(dp_{T}dp_{||}dE_{avail});"
                       "p_{T} (GeV/c);p_{||} (GeV/c);E_{avail} (GeV)",
                       pt_edges, pz_edges, ea_edges)
    h3.Write()
    numpy_to_th3d(unfold3d, unfold_err, "hUnfold3D", "Unfolded counts (3D)",
                  pt_edges, pz_edges, ea_edges).Write()
    numpy_to_th3d(completeness3d, None, "hOFCompleteness3D",
                  "OmniFold input completeness (3D)",
                  pt_edges, pz_edges, ea_edges).Write()

    # Eavail-marginal as a TH2D named hXSec2D -> drop-in for the anchor check
    # (../2d-unfolding/compare_to_paper_fullcov.py reads 'hXSec2D').
    numpy_to_th2d(xsec2d_marg, marg_err, "hXSec2D",
                  "Eavail-marginal d^{2}#sigma/(dp_{T}dp_{||});"
                  "p_{T} (GeV/c);p_{||} (GeV/c)",
                  pt_edges, pz_edges).Write()

    numpy_to_th1d(pt_e, x_pt, "hXSec_pt",
                  "d#sigma/dp_{T};p_{T} (GeV/c);d#sigma/dp_{T}").Write()
    numpy_to_th1d(pz_e, x_pz, "hXSec_pz",
                  "d#sigma/dp_{||};p_{||} (GeV/c);d#sigma/dp_{||}").Write()
    numpy_to_th1d(ea_e, x_ea, "hXSec_eavail",
                  "d#sigma/dE_{avail};E_{avail} (GeV);d#sigma/dE_{avail}").Write()
    if ref3d is not None:
        numpy_to_th2d(ref_marg, None, "hXSec2D_closureRef",
                      "Closure truth reference, Eavail-marginal;"
                      "p_{T} (GeV/c);p_{||} (GeV/c)", pt_edges, pz_edges).Write()
        numpy_to_th1d(ea_e, ref_x_ea, "hXSec_eavail_closureRef",
                      "Closure truth ref;E_{avail} (GeV);d#sigma/dE_{avail}").Write()
    f_out.Close()
    print(f"[INFO] Wrote {args.out}")
    print("[INFO] Anchor check: run "
          "../2d-unfolding/compare_to_paper_fullcov.py --ours "
          f"{args.out} to compare the Eavail-marginal vs the paper covariance.")


if __name__ == "__main__":
    main()
