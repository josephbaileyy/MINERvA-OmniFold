#!/usr/bin/env python3
"""N-dimensional unbinned OmniFold driver (axis-list refactor).

Generalizes the 2D/3D drivers to an arbitrary axis list so a new observable is a
configuration entry, not a copy-pasted reader. The first two axes are ALWAYS the
muon (pt, pz): the analysis gates the fiducial phase space on (pt, pz) and the
flux integral Phi is per-pt -- these are structural to the measurement. Every
further axis is an "extra observable" (eavail, q3, ...) read from named branches
and NOT gated.

  features  = column_stack([pt, pz, *extras])     (OmniFold is dimension-agnostic)
  binning   = np.histogramdd over all axes
  xsec      = nd-unfolding/xsec_nd.extract_cross_section_nd
  anchors   = drop the trailing extra axes -> recover the lower-D cross section

Reuse: data/MC/flux/POT/nucleon loaders, the truth (pt,pz) phase-space gate, and
the pt/pz edges come from ../2d-unfolding/unfold_2d_omnifold_unbinned.py. Only the
generic multi-axis readers and the bin/extract/project path are new here.

Extra-axis registry (add a new observable by adding one entry):
  eavail : MC_eavail / sim_eavail / measured_eavail / sim_background_eavail
  q3     : MC_q3     / sim_q3     / measured_q3     / sim_background_q3

Examples
--------
  # 4D d^4 sigma/(dpt dpz dEavail dq3) on the q3 event-loop output:
  python unfold_nd_omnifold_unbinned.py \
      --omnifile runEventLoopOmniFold_4D_MEFHC.root \
      --axes eavail,q3 --iters 5 --use-weights --estimator lgbm \
      --out products/4d/xsec_4d_MEFHC_5iter_lgbm.root

  # reproduce the 3D result (eavail only):
  python unfold_nd_omnifold_unbinned.py --omnifile ... --axes eavail ...

  # closure with an injected bump on the q3 axis:
  python unfold_nd_omnifold_unbinned.py ... --axes eavail,q3 \
      --closure --closure-reweight-axis q3
"""
import argparse
import math
import sys
from array import array

import numpy as np
import ROOT

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_2D = f"{_REPO}/2d-unfolding"
_ND = f"{_REPO}/nd-unfolding"
for p in (_2D, _ND):
    if p not in sys.path:
        sys.path.insert(0, p)
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402
from xsec_nd import (  # noqa: E402
    extract_cross_section_nd, project_marginal, project_axis, total_xsec,
)

ROOT.gROOT.SetBatch(True)

# --- Extra-axis registry --------------------------------------------------
# Each extra axis names its truth/reco/data/bkg branches and default edges.
# Physics-motivated low-recoil bins + a catch-all top bin (so the marginal
# captures the full tail and the Jacobian identity holds: every event must land
# in some bin). q3 reco has calorimetric tails, hence the wide catch bin.
# `lateral_invariant`: whether the axis value is UNCHANGED under the lateral
# muon/beam universes. E_avail is invariant (the lateral bands touch only muon
# getters, not the recoil inputs -- Gap 1 finding), so a universe unfold keeps CV
# E_avail. q3 IS shifted by the lateral bands (it depends on the muon kinematics),
# so its per-universe shifted branch (sim_q3_<band>_<idx> / MC_q3_<band>_<idx>)
# must be swapped in for lateral universes. See runEventLoopOmniFold.cpp header.
EXTRA_AXES = {
    "eavail": dict(
        truth="MC_eavail", reco="sim_eavail", data="measured_eavail",
        bkg="sim_background_eavail",
        edges=[0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0],   # GeV
        label="E_{avail} (GeV)", lateral_invariant=True),
    "q3": dict(
        truth="MC_q3", reco="sim_q3", data="measured_q3",
        bkg="sim_background_q3",
        edges=[0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0],   # GeV
        label="q_{3} (GeV)", lateral_invariant=False),
    # Workstream F (docs/FUTURE_DIRECTIONS.md item B): hadronic invariant mass W as
    # the 5th axis to localise the open high-E_avail DIS-tail excess (DIS = high W).
    # Truth GetTrueExperimentersW(), reco RecoW() (both muon+recoil dependent), so W
    # is NOT lateral-invariant -- lateral universes dump shifted W (W_truth_/MC_W_/
    # sim_W_<band>_<idx>), exactly like q3. Edges (GeV): QE/elastic peak ~0.94, the
    # Delta resonance ~1.2, the transition/2nd-resonance region, then the DIS tail
    # (W>2) where the excess lives, plus a wide catch bin for the calorimetric tail.
    "W": dict(
        truth="MC_W", reco="sim_W", data="measured_W",
        bkg="sim_background_W",
        edges=[0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0],        # GeV
        label="W (GeV)", lateral_invariant=False),
}


# ---------------------------------------------------------------------------
# Generic histogram + ROOT helpers (any dimensionality)
# ---------------------------------------------------------------------------
def histnd(cols, w, edges):
    """Weighted np.histogramdd over len(edges) axes -> (counts, sqrt(sumw2))."""
    sample = np.column_stack(cols)
    bins = [np.asarray(e, float) for e in edges]
    counts, _ = np.histogramdd(sample, bins=bins, weights=w)
    sumw2, _ = np.histogramdd(sample, bins=bins, weights=np.asarray(w) ** 2)
    return counts, np.sqrt(sumw2)


def write_thnd(f_out, arr, err, name, title, edges, axis_labels):
    """Write an N-D array as a flat TH1D (canonical) + a TH2D when N==2.

    The flat TH1D (bin = C-order ravel index over `arr.shape`) is what the
    covariance/chi2 tools consume; the full N-D structure is recovered by
    reshaping with the known per-axis edges. (A THnSparseD was tried but its
    Python binding segfaults at 4D on this ROOT build, so we keep the robust flat
    form; the binning lives in the edges, recorded in the docs and the 1D/2D
    projections written alongside.)
    """
    ndim = arr.ndim
    flat = arr.ravel(order="C")
    flat_err = None if err is None else err.ravel(order="C")
    h1 = ROOT.TH1D(name + "_flat", title + ";global bin;value", flat.size, 0, flat.size)
    h1.SetDirectory(0)
    for i, v in enumerate(flat, start=1):
        h1.SetBinContent(i, float(v))
        if flat_err is not None:
            h1.SetBinError(i, float(flat_err[i - 1]))
    f_out.cd(); h1.Write()

    if ndim == 2:
        h = u2d.make_th2d(name, title, edges[0], edges[1])
        for ix in range(arr.shape[0]):
            for iy in range(arr.shape[1]):
                h.SetBinContent(ix + 1, iy + 1, float(arr[ix, iy]))
                if err is not None:
                    h.SetBinError(ix + 1, iy + 1, float(err[ix, iy]))
        f_out.cd(); h.Write()


def numpy_to_th1d(edges, vals, name, title):
    h = u2d.make_th1d(name, title, edges)
    for i, v in enumerate(vals, start=1):
        h.SetBinContent(i, float(v))
    return h


# ---------------------------------------------------------------------------
# Generic multi-axis TTree readers (CV weights; pt/pz fixed + extra branches)
# ---------------------------------------------------------------------------
def _addr(t, name):
    a = array("d", [0.0])
    t.SetBranchAddress(name, a)
    return a


def _axis_universe_branch(axis_name, suffix, ctx):
    """Per-axis shifted-branch name for a lateral universe, matching the C++
    schema (runEventLoopOmniFold.cpp BuildUniverseBranchTable q3BranchName):
      truth_tree      -> '<axis>_truth_<suffix>'  (e.g. q3_truth_MuonResolution_0)
      reco_tree_truth -> 'MC_<axis>_<suffix>'     (e.g. MC_q3_MuonResolution_0)
      reco_tree_reco  -> 'sim_<axis>_<suffix>'    (e.g. sim_q3_MuonResolution_0)
      bkg_tree        -> 'sim_background_<axis>_<suffix>'
                         (e.g. sim_background_q3_MuonResolution_0; mc_background
                          reco, KNOWN_ISSUES #13)
    Only the lateral-variant axes (q3, W) carry these; eavail is lateral-invariant.
    """
    if ctx == "truth_tree":
        return f"{axis_name}_truth_{suffix}"
    if ctx == "reco_tree_truth":
        return f"MC_{axis_name}_{suffix}"
    if ctx == "reco_tree_reco":
        return f"sim_{axis_name}_{suffix}"
    if ctx == "bkg_tree":
        return f"sim_background_{axis_name}_{suffix}"
    raise ValueError(f"unknown ctx={ctx!r}")


def collect_truth_denom_nd(t, extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                           use_weights=False, verbose=False, extra_wbranches=None,
                           universe_branch=None):
    """mc_truth_denom -> truth-only (pt, pz, *extras, w) for the completeness denom.

    extra_wbranches: optional list of truth-side universe weight branch names
    (e.g. w_truth_<band>_<idx>); read aligned to kept events and returned under
    out["extra_w"] as a list of arrays (POT-scaled). Used by the superposition /
    unified-throw cross-check (compare_unified_throw); default None = unchanged.

    universe_branch=(band, idx): systematic-universe unfold. The truth weight is
    read from w_truth_<band>_<idx>; for LATERAL universes (kinematic branches
    present) pt/pz swap to pT_truth_/pz_truth_<band>_<idx> and every lateral-variant
    extra axis (q3) swaps to <axis>_truth_<band>_<idx>. Lateral-invariant axes
    (eavail) keep their CV branch. Mirrors the 3D driver's --universe path + q3.
    """
    pt_name, pz_name = "MC", "MC_pz"
    ax_truth = [ax["truth"] for ax in extras]
    wt_name = "w_truth"
    if universe_branch is not None:
        wt_name = u2d._universe_truth_branch(universe_branch)
        if not t.GetBranch(wt_name):
            raise RuntimeError(f"[FAIL] '{wt_name}' missing from mc_truth_denom "
                               "(re-run event loop with MNV101_DUMP_UNIVERSES)")
        lpt, lpz = u2d._universe_kine_branches(universe_branch, "truth_tree")
        suffix = f"{u2d._sanitize_band_for_branch(universe_branch[0])}_{int(universe_branch[1])}"
        if t.GetBranch(lpt) and t.GetBranch(lpz):   # lateral
            pt_name, pz_name = lpt, lpz
            for k, ax in enumerate(extras):
                if not ax.get("lateral_invariant", True):
                    nm = _axis_universe_branch(ax["name"], suffix, "truth_tree")
                    if t.GetBranch(nm):
                        ax_truth[k] = nm
            if verbose:
                print(f"[INFO] truth_denom lateral universe: pt/pz+{ '/'.join(ax_truth)} swapped")
    pt_a = _addr(t, pt_name); pz_a = _addr(t, pz_name)
    ex_a = [_addr(t, nm) for nm in ax_truth]
    wt_a = array("d", [1.0])
    if use_weights:
        t.SetBranchAddress(wt_name, wt_a)
    xw_a = [_addr(t, nm) for nm in (extra_wbranches or [])]
    pt_l, pz_l, w_l = [], [], []
    ex_l = [[] for _ in extras]
    xw_l = [[] for _ in (extra_wbranches or [])]
    drop = bad = 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        pt, pz = float(pt_a[0]), float(pz_a[0])
        exv = [float(a[0]) for a in ex_a]
        w = float(wt_a[0]) if use_weights else 1.0
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(w)
                and all(math.isfinite(v) for v in exv) and 0 <= w < 1e4):
            bad += 1; continue
        if not u2d.in_truth_phase_space(pt, pz, pt_lo, pt_hi, pz_lo, pz_hi):
            drop += 1; continue
        pt_l.append(pt); pz_l.append(pz); w_l.append(w * pot_scale)
        for k, v in enumerate(exv):
            ex_l[k].append(v)
        for k, a in enumerate(xw_a):
            xw_l[k].append(float(a[0]) * pot_scale)
    if verbose:
        print(f"[INFO] truth_denom: kept={len(pt_l)} dropped={drop} bad={bad}")
    out = {"pt": np.asarray(pt_l), "pz": np.asarray(pz_l), "w": np.asarray(w_l)}
    out["extras"] = [np.asarray(c) for c in ex_l]
    out["extra_w"] = [np.asarray(c) for c in xw_l]
    return out


def collect_signal_nd(t, extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                      use_weights=False, verbose=False, extra_wbranches=None,
                      universe_branch=None):
    """mc_signal_reco -> dict of truth/reco arrays for OmniFold.

    Gating mirrors the 2D/3D drivers: truth-pass via the (pt,pz) gate, reco-pass
    via sim_pass AND the (pt,pz) rectangle. Extra axes are NOT gated; reco extra
    values are -9999 wherever the event does not reco-pass.

    extra_wbranches: optional list of (truth_branch, reco_branch) universe-weight
    name tuples (e.g. (w_truth_<band>_<idx>, w_reco_<band>_<idx>)); read aligned to
    kept events and returned under out["extra_wt"]/out["extra_wr"] (POT-scaled), for
    the superposition / unified-throw cross-check. Default None = unchanged. These
    must be VERTICAL bands (no kinematic swap) so the weights combine multiplicatively.

    universe_branch=(band, idx): systematic-universe unfold. Weights from
    w_truth_/w_reco_<band>_<idx>; for LATERAL universes the truth pt/pz swap to
    MC_/MC_pz_<band>_<idx>, the reco pt/pz to sim_/sim_pz_<band>_<idx>, and each
    lateral-variant extra axis (q3) swaps its truth->MC_<axis>_<band>_<idx> and
    reco->sim_<axis>_<band>_<idx>. eavail (lateral-invariant) stays CV.
    """
    pt_truth_name, pz_truth_name = "MC", "MC_pz"
    pt_reco_name, pz_reco_name = "sim", "sim_pz"
    ax_truth = [ax["truth"] for ax in extras]
    ax_reco = [ax["reco"] for ax in extras]
    wt_name, wr_name = "w_truth", "w_reco"
    if universe_branch is not None:
        wt_name = u2d._universe_truth_branch(universe_branch)
        wr_name = u2d._universe_reco_branch(universe_branch)
        for nm in (wt_name, wr_name):
            if not t.GetBranch(nm):
                raise RuntimeError(f"[FAIL] '{nm}' missing from mc_signal_reco "
                                   "(re-run event loop with MNV101_DUMP_UNIVERSES)")
        l_mc, l_mc_pz = u2d._universe_kine_branches(universe_branch, "reco_tree_truth")
        l_sim, l_sim_pz = u2d._universe_kine_branches(universe_branch, "reco_tree_reco")
        suffix = f"{u2d._sanitize_band_for_branch(universe_branch[0])}_{int(universe_branch[1])}"
        if t.GetBranch(l_sim) and t.GetBranch(l_mc):   # lateral
            pt_truth_name, pz_truth_name = l_mc, l_mc_pz
            pt_reco_name, pz_reco_name = l_sim, l_sim_pz
            for k, ax in enumerate(extras):
                if not ax.get("lateral_invariant", True):
                    nt = _axis_universe_branch(ax["name"], suffix, "reco_tree_truth")
                    nr = _axis_universe_branch(ax["name"], suffix, "reco_tree_reco")
                    if t.GetBranch(nt):
                        ax_truth[k] = nt
                    if t.GetBranch(nr):
                        ax_reco[k] = nr
            if verbose:
                print(f"[INFO] signal lateral universe: kinematics+q3 swapped "
                      f"(truth {pt_truth_name}, reco {pt_reco_name}, axes {ax_reco})")
    mc_pt = _addr(t, pt_truth_name); mc_pz = _addr(t, pz_truth_name)
    sim_pt = _addr(t, pt_reco_name); sim_pz = _addr(t, pz_reco_name)
    mc_ex = [_addr(t, nm) for nm in ax_truth]
    sim_ex = [_addr(t, nm) for nm in ax_reco]
    sim_pass = array("B", [0]); t.SetBranchAddress("sim_pass", sim_pass)
    wt_a = array("d", [1.0]); wr_a = array("d", [1.0])
    if use_weights:
        t.SetBranchAddress(wt_name, wt_a); t.SetBranchAddress(wr_name, wr_a)
    xwt_a = [_addr(t, bt) for bt, _ in (extra_wbranches or [])]
    xwr_a = [_addr(t, br) for _, br in (extra_wbranches or [])]
    tpt, tpz, rpt, rpz, pr, ptr, wtl, wrl = [], [], [], [], [], [], [], []
    tex = [[] for _ in extras]; rex = [[] for _ in extras]
    xwt_l = [[] for _ in (extra_wbranches or [])]
    xwr_l = [[] for _ in (extra_wbranches or [])]
    drop = bad = 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        a_pt, a_pz = float(mc_pt[0]), float(mc_pz[0])
        b_pt, b_pz = float(sim_pt[0]), float(sim_pz[0])
        passed = sim_pass[0] != 0
        wt = float(wt_a[0]) if use_weights else 1.0
        wr = float(wr_a[0]) if use_weights else wt
        if not (math.isfinite(wt) and math.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4):
            bad += 1; continue
        wt *= pot_scale; wr *= pot_scale
        tru_ok = u2d.in_truth_phase_space(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(b_pt) and math.isfinite(b_pz)
                  and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru_ok or (passed and rec_ok)):
            drop += 1; continue
        tpt.append(a_pt if math.isfinite(a_pt) else -9999.0)
        tpz.append(a_pz if math.isfinite(a_pz) else -9999.0)
        rpt.append(b_pt if (passed and rec_ok) else -9999.0)
        rpz.append(b_pz if (passed and rec_ok) else -9999.0)
        for k in range(len(extras)):
            tv = float(mc_ex[k][0])
            tex[k].append(tv if math.isfinite(tv) else -9999.0)
            rv = float(sim_ex[k][0])
            rex[k].append(rv if (passed and rec_ok and math.isfinite(rv)) else -9999.0)
        for k in range(len(xwt_a)):
            xwt_l[k].append(float(xwt_a[k][0]) * pot_scale)
            xwr_l[k].append(float(xwr_a[k][0]) * pot_scale)
        pr.append(passed and rec_ok); ptr.append(tru_ok)
        wtl.append(wt); wrl.append(wr)
    if verbose:
        print(f"[INFO] signal: kept={len(tpt)} dropped={drop} bad={bad}")
    return {
        "truth_pt": np.asarray(tpt), "truth_pz": np.asarray(tpz),
        "reco_pt": np.asarray(rpt), "reco_pz": np.asarray(rpz),
        "truth_extras": [np.asarray(c) for c in tex],
        "reco_extras": [np.asarray(c) for c in rex],
        "pass_reco": np.asarray(pr, bool), "pass_truth": np.asarray(ptr, bool),
        "w_truth": np.asarray(wtl), "w_reco": np.asarray(wrl),
        "extra_wt": [np.asarray(c) for c in xwt_l],
        "extra_wr": [np.asarray(c) for c in xwr_l],
    }


def collect_data_nd(t, extras, pt_lo, pt_hi, pz_lo, pz_hi, guard_max=1e3, verbose=False):
    meas = _addr(t, "measured"); meas_pz = _addr(t, "measured_pz")
    ex_a = [_addr(t, ax["data"]) for ax in extras]
    meas_pass = array("B", [0]); t.SetBranchAddress("measured_pass", meas_pass)
    pts, pzs = [], []; exs = [[] for _ in extras]; skip = 0
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        if meas_pass[0] == 0:
            skip += 1; continue
        pt, pz = float(meas[0]), float(meas_pz[0])
        exv = [float(a[0]) for a in ex_a]
        if not (math.isfinite(pt) and math.isfinite(pz) and all(math.isfinite(v) for v in exv)):
            skip += 1; continue
        if abs(pt) > guard_max or abs(pz) > guard_max:
            skip += 1; continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            skip += 1; continue
        pts.append(pt); pzs.append(pz)
        for k, v in enumerate(exv):
            exs[k].append(v)
    if verbose:
        print(f"[INFO] data: kept={len(pts)} skipped={skip}")
    return np.asarray(pts), np.asarray(pzs), [np.asarray(c) for c in exs]


def collect_bkg_nd(t, extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi,
                   guard_max=1e3, verbose=False, universe_branch=None,
                   extra_wbranches=None):
    """mc_background -> reco (pt, pz, *extras, w) for the OmniFold measured target.

    The genuine background enters OmniFold only through the per-reco-bin purity
    down-weight max(0,data-bkg)/data (build_measured_training_nd); it is never
    injected as events. So a per-universe background = the same rebinning with a
    universe-varied bkg weight/kinematics.

    universe_branch=(band, idx): per-universe genuine background (KNOWN_ISSUES
    #13). The weight is read from w_bkg_<sanitized-band>_<idx> instead of the CV
    w_bkg; for LATERAL universes (shifted-kinematic branches present) the reco
    pt/pz swap to sim_background_/sim_background_pz_<band>_<idx> and each
    lateral-variant extra axis (q3, W) swaps to sim_background_<axis>_<band>_<idx>.
    eavail (lateral-invariant) keeps its CV branch; vertical universes shift the
    weight only. Branches are written by the C++ event loop's BkgTreeReco context
    under MNV101_DUMP_UNIVERSES. Without this the per-universe measured target
    reused the CV purity down-weight, freezing the background contribution to the
    systematic covariances at CV.

    extra_wbranches: optional list of per-universe bkg weight branch names
    (w_bkg_<band>_<idx>); read aligned to the CV-kept bkg events and returned as
    a 5th tuple element (list of POT-scaled arrays). Used by the banked VERTICAL
    sweep (sweep_bank/sweep_bank_5d) to reweight the CV background per universe
    without a re-read — vertical bands keep CV kinematics, so the kept-set is
    universe-independent and only the weight column changes. Passing
    extra_wbranches changes the return arity from 4 to 5.
    """
    sb_name, sb_pz_name = "sim_background", "sim_background_pz"
    ax_bkg = [ax["bkg"] for ax in extras]
    w_name = "w_bkg"
    if universe_branch is not None:
        w_name = u2d._universe_bkg_branch(universe_branch)
        if not t.GetBranch(w_name):
            raise RuntimeError(f"[FAIL] '{w_name}' missing from mc_background "
                               "(re-run event loop with MNV101_DUMP_UNIVERSES)")
        l_sb, l_sb_pz = u2d._universe_kine_branches(universe_branch, "bkg_tree_reco")
        suffix = f"{u2d._sanitize_band_for_branch(universe_branch[0])}_{int(universe_branch[1])}"
        if t.GetBranch(l_sb) and t.GetBranch(l_sb_pz):   # lateral
            sb_name, sb_pz_name = l_sb, l_sb_pz
            for k, ax in enumerate(extras):
                if not ax.get("lateral_invariant", True):
                    nm = _axis_universe_branch(ax["name"], suffix, "bkg_tree")
                    if t.GetBranch(nm):
                        ax_bkg[k] = nm
            if verbose:
                print(f"[INFO] bkg lateral universe: pt/pz+{'/'.join(ax_bkg)} swapped")
    sb = _addr(t, sb_name); sb_pz = _addr(t, sb_pz_name)
    ex_a = [_addr(t, nm) for nm in ax_bkg]
    sb_pass = array("B", [0]); t.SetBranchAddress("sim_background_pass", sb_pass)
    w_b = _addr(t, w_name)
    xw_a = [_addr(t, nm) for nm in (extra_wbranches or [])]
    pts, pzs, ws = [], [], []; exs = [[] for _ in extras]; skip = 0
    xw_l = [[] for _ in (extra_wbranches or [])]
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        if sb_pass[0] == 0:
            skip += 1; continue
        pt, pz, w = float(sb[0]), float(sb_pz[0]), float(w_b[0])
        exv = [float(a[0]) for a in ex_a]
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(w)
                and all(math.isfinite(v) for v in exv) and 0 <= w < 1e6):
            skip += 1; continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            skip += 1; continue
        pts.append(pt); pzs.append(pz); ws.append(w * pot_scale)
        for k, v in enumerate(exv):
            exs[k].append(v)
        for k, a in enumerate(xw_a):
            xw_l[k].append(float(a[0]) * pot_scale)
    if verbose:
        print(f"[INFO] bkg: kept={len(pts)} skipped={skip}"
              + (f" universe={universe_branch}" if universe_branch is not None else ""))
    out = (np.asarray(pts), np.asarray(pzs), [np.asarray(c) for c in exs], np.asarray(ws))
    if extra_wbranches is not None:
        return (*out, [np.asarray(c) for c in xw_l])
    return out


def build_measured_training_nd(cols, data_nd, bkg_nd, edges, verbose=False):
    """Per-event measured weight = max(0,data-bkg)/data in the reco-space bin.

    cols is [pt, pz, *extras] for the measured events; data_nd/bkg_nd are the
    binned data and background counts. Mirrors the 2D/3D floor-at-zero convention.
    """
    target = np.maximum(0.0, data_nd - bkg_nd)
    idx = [np.digitize(c, np.asarray(e, float)) - 1 for c, e in zip(cols, edges)]
    shape = data_nd.shape
    n = cols[0].shape[0]
    weights = np.zeros(n, float); n_zero = 0
    for i in range(n):
        coord = tuple(int(ix[i]) for ix in idx)
        if not all(0 <= coord[a] < shape[a] for a in range(len(shape))):
            n_zero += 1; continue
        d = data_nd[coord]
        if d <= 0.0:
            n_zero += 1; continue
        weights[i] = target[coord] / d
    if verbose:
        print(f"[INFO] measured training: sum={weights.sum():.6g} zero={n_zero}/{n}")
    return weights


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--mcfile", default=f"{_2D}/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--axes", default="eavail,q3",
                    help="comma list of extra axes after pt,pz (registry: "
                         + ",".join(EXTRA_AXES) + ")")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--use-weights", action="store_true")
    ap.add_argument("--bkg-mode",
                    choices=["purity", "negweight", "negweight-refined"],
                    default="purity",
                    help="Background subtraction on the OmniFold measured side "
                         "(mirrors the 2D driver; see 2d-unfolding/"
                         "HANDOFF_bkg_negweight/). 'purity' (default): binned "
                         "per-reco-bin max(0,(N_data-N_bkg)/N_data) data "
                         "down-weight. 'negweight': unbinned negative-weight "
                         "injection -- append the (universe-aware) mc_background "
                         "reco events at -w_bkg*pot_scale, data at +1, so step-1 "
                         "targets (D-B)/S continuously. 'negweight-refined': "
                         "Stay Positive (arXiv:2505.03724) refinement of the "
                         "signed sample to non-negative weights before step-1. "
                         "All modes honour --universe (collect_bkg_nd already "
                         "resolves per-universe background), --closure and "
                         "--bootstrap-seed.")
    ap.add_argument("--estimator", default="lgbm")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--bootstrap-seed", type=int, default=None)
    ap.add_argument("--universe", default=None, metavar="BAND:IDX",
                    help="systematic-universe unfold: read w_truth/w_reco_<band>_<idx> "
                         "(lateral bands also swap pt/pz + q3; eavail stays CV). "
                         "Requires --use-weights; incompatible with --closure/--bootstrap-seed.")
    ap.add_argument("--flux-universe-file",
                    default=f"{_2D}/baseline_flux/flux_integral_universes_MEFHC.root",
                    help="ROOT (hFluxCV/hFluxUniv) per-PPFX flux integrals; used only "
                         "with --universe Flux:IDX to divide by that universe's flux.")
    ap.add_argument("--edges", default=None,
                    help="override edges for one axis: 'axis:e0,e1,...' (repeatable, ';'-sep)")
    ap.add_argument("--pt-edges", default=None,
                    help="override the pT edges (comma list, GeV/c). FPS pilot use; "
                         "default = the frozen paper binning")
    ap.add_argument("--pz-edges", default=None,
                    help="override the p|| edges (comma list, GeV/c)")
    ap.add_argument("--full-phase-space", action="store_true",
                    help="FPS mode: lift the theta_mu<20deg truth gate (the rectangle "
                         "is set by --pt/--pz-edges). Use ONLY with an omnifile dumped "
                         "under MNV101_FULL_PHASE_SPACE, so the python truth gate "
                         "matches the event loop's mc_truth_denom selection.")
    ap.add_argument("--prior-reweight", default=None, metavar="FILE[:HIST]",
                    help="multiply the MC truth/reco weights by a (pT,pz) ratio looked "
                         "up at TRUTH kinematics (TH2D, default name hPriorRatio): a "
                         "truth-level prior swap for the FPS prior-dependence envelope. "
                         "Requires --use-weights.")
    ap.add_argument("--out", default="xsec_nd.root")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--closure", action="store_true",
                    help="MC reco (pass_reco & pass_truth) as pseudo-data; completeness=1")
    ap.add_argument("--closure-reweight-axis", default=None,
                    help="inject a Gaussian truth bump on this extra axis (needs --closure)")
    ap.add_argument("--closure-amplitude", type=float, default=0.3)
    ap.add_argument("--closure-center", type=float, default=0.3)
    ap.add_argument("--closure-sigma", type=float, default=0.15)
    args = ap.parse_args()

    axis_names = [a.strip() for a in args.axes.split(",") if a.strip()]
    for a in axis_names:
        if a not in EXTRA_AXES:
            ap.error(f"unknown axis {a!r}; registry: {list(EXTRA_AXES)}")
    extras = [dict(EXTRA_AXES[a], name=a) for a in axis_names]
    if args.closure_reweight_axis and not args.closure:
        ap.error("--closure-reweight-axis requires --closure")
    # hidden-variable closure: the bump axis may be any registry axis NOT being
    # unfolded -- its truth column is loaded for the injection only, so the
    # unfold stays blind to it (FPS extension-region validation).
    hidden_ax = None
    if args.closure_reweight_axis and args.closure_reweight_axis not in axis_names:
        if args.closure_reweight_axis not in EXTRA_AXES:
            ap.error(f"--closure-reweight-axis {args.closure_reweight_axis!r} not in "
                     f"--axes or the registry {list(EXTRA_AXES)}")
        hidden_ax = dict(EXTRA_AXES[args.closure_reweight_axis],
                         name=args.closure_reweight_axis)

    universe_branch = None
    if args.universe is not None:
        if not args.use_weights:
            ap.error("--universe requires --use-weights (CV->universe weight swap)")
        if args.closure:
            ap.error("--universe is incompatible with --closure")
        if args.bootstrap_seed is not None:
            ap.error("--universe and --bootstrap-seed cannot be combined (one variance "
                     "axis per unfold)")
        if ":" not in args.universe:
            ap.error(f"--universe expects 'BAND:IDX', got {args.universe!r}")
        b_str, _, i_str = args.universe.partition(":")
        universe_branch = (b_str, int(i_str))
        print(f"[INFO] universe unfold: band={b_str!r} idx={i_str} "
              f"-> w_truth/w_reco_{u2d._sanitize_band_for_branch(b_str)}_{i_str}")

    # axis edge overrides
    if args.edges:
        for tok in args.edges.split(";"):
            nm, _, ed = tok.partition(":")
            nm = nm.strip()
            vals = [float(x) for x in ed.split(",")]
            for ax in extras:
                if ax["name"] == nm:
                    ax["edges"] = vals

    pt_edges = ([float(x) for x in args.pt_edges.split(",")] if args.pt_edges
                else u2d.PT_EDGES)
    pz_edges = ([float(x) for x in args.pz_edges.split(",")] if args.pz_edges
                else u2d.PZ_EDGES)
    if args.full_phase_space:
        # lift the theta_mu<20deg truth gate inside u2d.in_truth_phase_space so the
        # python truth-pass matches the MNV101_FULL_PHASE_SPACE event-loop denominator
        u2d.MAX_MUON_THETA_RAD = math.pi
        print("[INFO] FULL PHASE SPACE: theta_mu truth gate lifted "
              "(rectangle from --pt/--pz-edges)")
    edges = [pt_edges, pz_edges] + [ax["edges"] for ax in extras]
    axis_labels = ["p_{T} (GeV/c)", "p_{||} (GeV/c)"] + [ax["label"] for ax in extras]
    pt_lo, pt_hi = pt_edges[0], pt_edges[-1]
    pz_lo, pz_hi = pz_edges[0], pz_edges[-1]
    ndim = len(edges)
    print(f"[INFO] axes ({ndim}D): pt, pz, " + ", ".join(axis_names))
    for nm, e in zip(["pt", "pz"] + axis_names, edges):
        print(f"[INFO]   {nm}: {len(e)-1} bins {e}")

    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"cannot open {args.omnifile}")
    t_sig = f_in.Get("mc_signal_reco"); t_bkg = f_in.Get("mc_background")
    t_data = f_in.Get("data"); t_td = f_in.Get("mc_truth_denom")
    if not (t_sig and t_bkg and t_data and t_td):
        raise RuntimeError("missing required TTrees")
    # verify the extra-axis branches exist (incl. a hidden closure-bump axis)
    load_extras = extras + ([hidden_ax] if hidden_ax is not None else [])
    for ax in load_extras:
        for tree, br in [(t_sig, ax["reco"]), (t_sig, ax["truth"]),
                         (t_bkg, ax["bkg"]), (t_data, ax["data"])]:
            if not tree.GetListOfBranches().FindObject(br):
                raise RuntimeError(f"branch '{br}' missing from '{tree.GetName()}' "
                                   f"(axis {ax['name']}); re-run the event loop")

    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f_in)
    print(f"[INFO] POT: data={data_pot:.4g} mc={mc_pot:.4g} scale={pot_scale:.6g}")
    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    if args.pt_edges:
        # Extended pT binning: the flux histogram is on the frozen paper edges, but
        # the integrated flux is pT-independent (constant per bin); map each new bin
        # to the flux bin containing its centre, falling back to the last flux bin
        # beyond the histogram range (exact for a constant flux, which it is).
        flux_ref, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, u2d.PT_EDGES)
        ref_e = np.asarray(u2d.PT_EDGES, float)
        ctrs = 0.5 * (np.asarray(pt_edges[:-1]) + np.asarray(pt_edges[1:]))
        ref_i = np.clip(np.digitize(ctrs, ref_e) - 1, 0, len(flux_ref) - 1)
        flux_bins = flux_ref[ref_i]
        spread = flux_ref.max() / flux_ref.min() - 1.0
        print(f"[INFO] flux remapped to {len(pt_edges)-1} pT bins "
              f"(reference flux pT-spread {100*spread:.2g}% -- constant)")
    else:
        flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_edges)
    print(f"[INFO] flux sum = {flux_bins.sum():.4g} m^-2/POT")

    meas_pt, meas_pz, meas_ex = collect_data_nd(
        t_data, load_extras, pt_lo, pt_hi, pz_lo, pz_hi, verbose=args.verbose)
    bkg_pt, bkg_pz, bkg_ex, bkg_w = collect_bkg_nd(
        t_bkg, load_extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi, verbose=args.verbose,
        universe_branch=universe_branch)   # KNOWN_ISSUES #13: per-universe background
    sig = collect_signal_nd(t_sig, load_extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                            use_weights=args.use_weights, verbose=args.verbose,
                            universe_branch=universe_branch)
    td = collect_truth_denom_nd(t_td, load_extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                                use_weights=args.use_weights, verbose=args.verbose,
                                universe_branch=universe_branch)
    hid_truth = None
    if hidden_ax is not None:
        # pop the hidden bump column off every loader output so the unfold,
        # binning, and completeness see only the declared axes
        hid_truth = sig["truth_extras"].pop()
        sig["reco_extras"].pop()
        td["extras"].pop()
        meas_ex.pop()
        bkg_ex.pop()
        print(f"[INFO] hidden-variable closure: truth {hidden_ax['name']} loaded "
              "for the bump only (not an unfolding axis)")

    # Truth-level prior reweight (FPS 3-prior envelope): multiply the MC truth AND
    # reco weights by ratio(truth pT, truth pz); the reco weight rides its event's
    # truth weight, so a truth-level prior change propagates to both sides.
    if args.prior_reweight:
        if not args.use_weights:
            ap.error("--prior-reweight requires --use-weights")
        pr_fn, _, pr_hn = args.prior_reweight.partition(":")
        f_pr = ROOT.TFile.Open(pr_fn)
        h_pr = f_pr.Get(pr_hn or "hPriorRatio")
        if not h_pr:
            raise RuntimeError(f"prior-ratio hist '{pr_hn or 'hPriorRatio'}' missing in {pr_fn}")
        npx, npy = h_pr.GetNbinsX(), h_pr.GetNbinsY()
        pr_xe = np.array([h_pr.GetXaxis().GetBinLowEdge(i + 1) for i in range(npx)]
                         + [h_pr.GetXaxis().GetBinUpEdge(npx)])
        pr_ye = np.array([h_pr.GetYaxis().GetBinLowEdge(i + 1) for i in range(npy)]
                         + [h_pr.GetYaxis().GetBinUpEdge(npy)])
        pr_arr = np.array([[h_pr.GetBinContent(i + 1, j + 1) for j in range(npy)]
                           for i in range(npx)])
        f_pr.Close()

        def _prior_lookup(a_pt, a_pz):
            ix = np.clip(np.digitize(a_pt, pr_xe) - 1, 0, npx - 1)
            iy = np.clip(np.digitize(a_pz, pr_ye) - 1, 0, npy - 1)
            return pr_arr[ix, iy]

        r_sig = _prior_lookup(sig["truth_pt"], sig["truth_pz"])
        sig["w_truth"] = sig["w_truth"] * r_sig
        sig["w_reco"] = sig["w_reco"] * r_sig
        r_td = _prior_lookup(td["pt"], td["pz"])
        td["w"] = td["w"] * r_td
        print(f"[INFO] prior reweight {pr_fn}: signal mean ratio {r_sig.mean():.4f}, "
              f"truth-denom mean {r_td.mean():.4f}")

    # Flux universe: divide by that PPFX universe's flux integral (mirrors 3D driver).
    if universe_branch is not None and universe_branch[0] == "Flux":
        fu = ROOT.TFile.Open(args.flux_universe_file)
        if fu and not fu.IsZombie():
            h_cv, h_un = fu.Get("hFluxCV"), fu.Get("hFluxUniv")
            if h_cv and h_un:
                uidx = int(universe_branch[1])
                scale = np.ones(len(flux_bins))
                for b in range(len(flux_bins)):
                    cvf = h_cv.GetBinContent(b + 1)
                    unf = h_un.GetBinContent(b + 1, uidx + 1)
                    if cvf > 0 and unf > 0:
                        scale[b] = unf / cvf
                flux_bins = np.asarray(flux_bins, float) * scale
                print(f"[INFO] Flux universe {uidx}: per-pT flux scaled "
                      f"(mean {scale.mean():.4f})")
            fu.Close()
        else:
            print(f"[WARN] flux universe file {args.flux_universe_file} unavailable; "
                  "using CV flux (Flux universe will be incomplete)")
    if sig["truth_pt"].size == 0 or meas_pt.size == 0:
        raise RuntimeError("empty signal or data after selection")

    # --- background-subtraction mode: prepare injected bkg (deferred) ---
    # negweight/refined inject the (universe-aware) mc_background reco events on
    # the measured side at -w; purity uses the binned per-reco-bin down-weight.
    # collect_bkg_nd (above) already resolved the per-universe background (weight
    # + lateral kinematics, KNOWN_ISSUES #13), so the injected background varies
    # per universe identically to the purity bkg_nd -> both modes target the same
    # rho1 = D - B_u. Fiducial-filter the injection AND the +1 data side to the
    # full analysis window on EVERY axis (the ND analogue of the 2D reco-window
    # parity fix, matching purity's support where out-of-binning events get
    # weight 0 via build_measured_training_nd's digitize). Injection itself is
    # deferred to AFTER closure + the data bootstrap (see below) so the Poisson(1)
    # data-stat bootstrap fluctuates only the data/pseudo-data side.
    def _fid_mask(cols):
        m = np.ones(np.asarray(cols[0]).shape[0], dtype=bool)
        for c, e in zip(cols, edges):
            c = np.asarray(c, float)
            m &= (c >= e[0]) & (c < e[-1])
        return m
    inj_cols = inj_w = None
    if args.bkg_mode in ("negweight", "negweight-refined"):
        bmask = _fid_mask([bkg_pt, bkg_pz] + bkg_ex)
        inj_cols = [bkg_pt[bmask], bkg_pz[bmask]] + [e[bmask] for e in bkg_ex]
        inj_w = bkg_w[bmask]
        print(f"[INFO] bkg-mode={args.bkg_mode}: prepared {int(bmask.sum())} "
              f"injected background events (of {bkg_pt.size} bkg); data side +1 "
              f"(injection deferred to after closure/bootstrap).")

    # --- pseudo-data (closure) or real-data training target ---
    closure_rw_truthpass = None
    if args.closure:
        print("[INFO] *** CLOSURE: MC reco as pseudo-data ***")
        cmask = sig["pass_reco"] & sig["pass_truth"]
        meas_pt = sig["reco_pt"][cmask].copy(); meas_pz = sig["reco_pz"][cmask].copy()
        meas_ex = [e[cmask].copy() for e in sig["reco_extras"]]
        # Pseudo-data weights must mirror the MC reco weights handed to OmniFold
        # (without --use-weights both are the constant pot_scale), or the
        # learned normalization and the binning weights double-count pot_scale.
        measured_weights = sig["w_reco"][cmask].copy()
        if args.closure_reweight_axis:
            if hidden_ax is not None:
                tcol = hid_truth[cmask]
                tcol_t = hid_truth[sig["pass_truth"]]
            else:
                ai = axis_names.index(args.closure_reweight_axis)
                tcol = sig["truth_extras"][ai][cmask]
                tcol_t = sig["truth_extras"][ai][sig["pass_truth"]]
            A, c0, s = args.closure_amplitude, args.closure_center, args.closure_sigma
            measured_weights = measured_weights * (1.0 + A * np.exp(-((tcol - c0) / s) ** 2))
            closure_rw_truthpass = 1.0 + A * np.exp(-((tcol_t - c0) / s) ** 2)
            print(f"[INFO] inject bump on {args.closure_reweight_axis}"
                  f"{' (hidden)' if hidden_ax is not None else ''}: A={A} c={c0} s={s}")
        if args.bkg_mode in ("negweight", "negweight-refined"):
            # negweight closure: pseudo-data = sim reco (signal) + injected bkg
            # CONTAMINATION at +inj_w; the mode subtraction (-inj_w / refinement)
            # is applied after the bootstrap block and removes it, so a correct
            # unfold recovers the CV truth prior (exercises the full signed-weight
            # subtraction plumbing end-to-end).
            meas_pt = np.concatenate([meas_pt, inj_cols[0]])
            meas_pz = np.concatenate([meas_pz, inj_cols[1]])
            meas_ex = [np.concatenate([meas_ex[k], inj_cols[2 + k]])
                       for k in range(len(meas_ex))]
            measured_weights = np.concatenate([measured_weights, inj_w])
            print(f"[INFO] negweight closure: added {inj_w.size} background "
                  f"contamination events at +w (sum={inj_w.sum():.6g}).")
    elif args.bkg_mode == "purity":
        data_nd, _ = histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
        bkg_nd, _ = histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
        measured_weights = build_measured_training_nd(
            [meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges, verbose=args.verbose)
    else:
        # negweight / negweight-refined real data: data side at +1, restricted to
        # the analysis window on every axis (matching purity's support).
        dmask = _fid_mask([meas_pt, meas_pz] + meas_ex)
        meas_pt = meas_pt[dmask]; meas_pz = meas_pz[dmask]
        meas_ex = [e[dmask] for e in meas_ex]
        measured_weights = np.ones(meas_pt.size, dtype=float)
        print(f"[INFO] bkg-mode={args.bkg_mode}: data side {int(dmask.sum())} "
              f"events (of {dmask.size}) in the analysis window at +1.")

    if args.bootstrap_seed is not None:
        # Data-statistical Poisson(1) on the data/pseudo-data side ONLY (the
        # injected background subtraction is appended after this block, so it is
        # never fluctuated here -- it carries independent MC statistics and a
        # fixed POT-scaled weight, matching the purity path where bkg_nd is
        # fixed). MC-statistical Poisson(1) rides the signal MC weights.
        rng_d = np.random.default_rng(args.bootstrap_seed)
        rng_m = np.random.default_rng(args.bootstrap_seed + 10_000_000)
        measured_weights = measured_weights * rng_d.poisson(1.0, measured_weights.shape[0])
        b_mc = rng_m.poisson(1.0, sig["w_truth"].shape[0]).astype(float)
        sig["w_truth"] = sig["w_truth"] * b_mc
        sig["w_reco"] = sig["w_reco"] * b_mc
        print(f"[INFO] bootstrap seed={args.bootstrap_seed}")

    # --- apply the background subtraction on the measured side (post-bootstrap) ---
    if args.bkg_mode == "negweight":
        n_data = meas_pt.size
        meas_pt = np.concatenate([meas_pt, inj_cols[0]])
        meas_pz = np.concatenate([meas_pz, inj_cols[1]])
        meas_ex = [np.concatenate([meas_ex[k], inj_cols[2 + k]])
                   for k in range(len(meas_ex))]
        measured_weights = np.concatenate([measured_weights, -inj_w])
        print(f"[INFO] bkg-mode=negweight: injected {inj_w.size} bkg events at "
              f"-w; data side {n_data}. Effective measured sum="
              f"{measured_weights.sum():.6g}.")
    elif args.bkg_mode == "negweight-refined":
        n_data = meas_pt.size
        sgn_cols = ([np.concatenate([meas_pt, inj_cols[0]]),
                     np.concatenate([meas_pz, inj_cols[1]])]
                    + [np.concatenate([meas_ex[k], inj_cols[2 + k]])
                       for k in range(len(meas_ex))])
        sgn_w = np.concatenate([measured_weights, -inj_w])
        refine_params = ({"random_state": int(args.seed) + 3}
                         if args.seed is not None else None)
        w_ref, _g, frac_clip = u2d.refine_stay_positive(
            np.column_stack(sgn_cols), sgn_w, estimator=args.estimator,
            device=args.device, params=refine_params, verbose=True)
        meas_pt, meas_pz = sgn_cols[0], sgn_cols[1]
        meas_ex = sgn_cols[2:]
        measured_weights = w_ref
        print(f"[INFO] bkg-mode=negweight-refined (Stay Positive): refined "
              f"{sgn_w.size} signed events ({n_data} data + {inj_w.size} bkg) to "
              f"non-negative weights; clipped frac={frac_clip:.4f}; effective "
              f"measured sum={measured_weights.sum():.6g}.")

    # --- OmniFold (dimension-agnostic core) ---
    _OF = f"{_REPO}/unbinned_unfolding/python"
    if _OF not in sys.path:
        sys.path.insert(0, _OF)
    from omnifold import OmniFold_helper_functions as ohf

    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"], *sig["truth_extras"]])
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"], *sig["reco_extras"]])
    measured = np.column_stack([meas_pt, meas_pz, *meas_ex])
    print(f"[INFO] OmniFold {args.iters} iters estimator={args.estimator} ndim={MCgen.shape[1]}")
    print(f"[INFO] MC={sig['truth_pt'].size} pass_truth={sig['pass_truth'].sum()} "
          f"pass_reco={sig['pass_reco'].sum()}  measured={meas_pt.size}")

    if args.seed is not None:
        c1 = {"random_state": int(args.seed)}
        c2 = {"random_state": int(args.seed) + 1}
        rg = {"random_state": int(args.seed) + 2}
    else:
        c1 = c2 = rg = None

    step1_w, step2_w = ohf.omnifold(
        MCgen, MCreco, measured,
        sig["pass_reco"], sig["pass_truth"], np.ones(meas_pt.size, dtype=bool),
        int(args.iters),
        # Always pass the collected (POT-scaled) weights: without --use-weights
        # they are the constant pot_scale, which the classifier needs to see or
        # it absorbs the data/MC normalization gap into the learned weights and
        # the pot-scaled binning below applies pot_scale a second time
        # (KNOWN_ISSUES #1: result globally low by pot_scale).
        MCgen_weights=sig["w_truth"],
        MCreco_weights=sig["w_reco"],
        measured_weights=measured_weights,
        classifier1_params=c1, classifier2_params=c2, regressor_params=rg,
        parameter_format="dict", estimator=args.estimator, device=args.device,
    )
    print(f"[INFO] done. step2 sum={step2_w.sum():.4g} mean={step2_w.mean():.4f}")

    # --- bin truth-pass events (prior, unfolded, completeness) ---
    m = sig["pass_truth"]
    tcols = [sig["truth_pt"][m], sig["truth_pz"][m]] + [e[m] for e in sig["truth_extras"]]
    tw = sig["w_truth"][m]
    if tcols[0].size != step2_w.size:
        raise RuntimeError(f"size mismatch truth={tcols[0].size} step2={step2_w.size}")
    prior_nd, prior_err = histnd(tcols, tw, edges)
    unfold_nd, unfold_err = histnd(tcols, step2_w * tw, edges)

    if args.closure:
        completeness = np.ones(prior_nd.shape); c_global = 1.0
        print("[INFO] closure: completeness=1")
    else:
        of_in, _ = histnd(tcols, tw, edges)
        dcols = [td["pt"], td["pz"]] + td["extras"]
        denom_nd, _ = histnd(dcols, td["w"], edges)
        completeness = np.zeros_like(of_in)
        nz = denom_nd > 0
        completeness[nz] = of_in[nz] / denom_nd[nz]
        c_global = of_in.sum() / denom_nd.sum() if denom_nd.sum() > 0 else float("nan")
        print(f"[CHECK] global completeness c={c_global:.4f}")

    # --- extract cross section + projections ---
    xsec, good = extract_cross_section_nd(unfold_nd, completeness, np.asarray(flux_bins, float),
                                          data_pot, n_nucleons, edges)
    rel = np.zeros_like(unfold_nd)
    np.divide(unfold_err, unfold_nd, out=rel, where=unfold_nd > 0)
    xsec_err = np.abs(xsec) * rel
    tot = total_xsec(xsec, edges)
    print(f"[CHECK] total xsec ({ndim}D integral): {tot:.4g} cm^2/nucleon")

    # --- write ---
    f_out = ROOT.TFile.Open(args.out, "RECREATE"); f_out.cd()
    ROOT.TParameter("double")("dataPOT", data_pot).Write()
    ROOT.TParameter("double")("globalCompleteness", c_global).Write()
    ROOT.TParameter("int")("ndim", ndim).Write()
    title = "d^{%d}#sigma/(" % ndim + "".join("d%s" % n for n in ["pt", "pz"] + axis_names) + ")"
    write_thnd(f_out, xsec, xsec_err, "hXSecND", title, edges, axis_labels)
    write_thnd(f_out, unfold_nd, unfold_err, "hUnfoldND", "unfolded counts", edges, axis_labels)
    write_thnd(f_out, completeness, None, "hCompletenessND", "completeness", edges, axis_labels)

    # 1D projections on every axis
    for ai in range(ndim):
        e, y = project_axis(xsec, edges, ai)
        nm = (["pt", "pz"] + axis_names)[ai]
        numpy_to_th1d(e, y, f"hXSec_{nm}", f"d#sigma/d{nm};{axis_labels[ai]};d#sigma").Write()

    # marginal anchors: drop the trailing extra axes one at a time
    #   drop the LAST extra axis -> the next-lower-D cross section (Jacobian id).
    #   e.g. 4D(pt,pz,eavail,q3): drop q3 -> 3D(pt,pz,eavail) as a TH2D? no, 3D.
    #   drop ALL extras -> the 2D d^2sigma/(dpt dpz): write as hXSec2D (anchor to paper).
    if extras:
        marg2d = project_marginal(xsec, edges, drop_axes=list(range(2, ndim)))
        # 2D marginal as the paper-anchor TH2D named hXSec2D
        h2 = u2d.make_th2d("hXSec2D",
                           "marginal d^{2}#sigma/(dp_{T}dp_{||});p_{T} (GeV/c);p_{||} (GeV/c)",
                           pt_edges, pz_edges)
        for ix in range(marg2d.shape[0]):
            for iy in range(marg2d.shape[1]):
                h2.SetBinContent(ix + 1, iy + 1, float(marg2d[ix, iy]))
        h2.Write()
        marg_tot = (marg2d * np.diff(pt_edges)[:, None] * np.diff(pz_edges)[None, :]).sum()
        print(f"[CHECK] 2D-marginal integral: {marg_tot:.4g}  (== {ndim}D integral: {tot:.4g})")
        # drop only the last axis -> (D-1) marginal, for the q3->3D anchor
        if ndim >= 4:
            marg_drop_last = project_marginal(xsec, edges, drop_axes=[ndim - 1])
            write_thnd(f_out, marg_drop_last, None, "hXSecND_dropLast",
                       "marginal dropping last axis", edges[:-1], axis_labels[:-1])

    # closure residuals
    if args.closure:
        ref_w = tw if closure_rw_truthpass is None else tw * closure_rw_truthpass
        ref_nd, _ = histnd(tcols, ref_w, edges)
        ref_xsec, _ = extract_cross_section_nd(ref_nd, completeness, np.asarray(flux_bins, float),
                                               data_pot, n_nucleons, edges)
        write_thnd(f_out, ref_xsec, None, "hClosureRefND",
                   "closure reference xsec (bump-reweighted truth)", edges, axis_labels)
        msk = ref_xsec > 0
        r = np.full(xsec.shape, np.nan)
        r[msk] = xsec[msk] / ref_xsec[msk]
        print("\n=== CLOSURE RESIDUALS (unfold/ref) ===")
        print(f"  {ndim}D bins: median={np.nanmedian(r):.4f} std={np.nanstd(r):.4f} "
              f"max|dev|={np.nanmax(np.abs(r-1)):.4f}")
        if args.closure_reweight_axis and hidden_ax is not None:
            print(f"  hidden-axis bump ({hidden_ax['name']}): per-cell recovery map = "
                  "hXSecND / hClosureRefND (region split via fps_extension_validation.py)")
            print(f"  injected mean factor={closure_rw_truthpass.mean():.4f}")
        elif args.closure_reweight_axis:
            ai = axis_names.index(args.closure_reweight_axis)
            _, y_unf = project_axis(xsec, edges, 2 + ai)
            _, y_ref = project_axis(ref_xsec, edges, 2 + ai)
            ratios = y_unf / np.where(y_ref > 0, y_ref, np.nan)
            print(f"  {args.closure_reweight_axis} 1D ratios: "
                  + ", ".join(f"{v:.3f}" for v in ratios))
            print(f"  injected mean factor={closure_rw_truthpass.mean():.4f}")

    f_out.Close()
    print(f"[INFO] wrote {args.out}")


if __name__ == "__main__":
    main()
