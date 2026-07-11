#!/usr/bin/env python3
"""
2D unbinned OmniFold unfolding for MINERvA CC inclusive cross section.

Unfolds the double-differential cross section d^2 sigma / (dp_T dp_||) in
muon transverse momentum (p_T) and longitudinal momentum (p_||), reproducing
arXiv:2106.16210 with OmniFold instead of D'Agostini (IBU).

Reads unbinned TTrees from runEventLoopOmniFold (with p_T and p_|| branches),
runs 2D OmniFold via the RooUnfoldOmnifold C++ wrapper, and extracts the
double-differential cross section.

Created: 2026-04-17
"""

import argparse
import math
from array import array

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


# ---------------------------------------------------------------------------
# Paper binning (arXiv:2106.16210, Phys. Rev. D 106, 032001)
# ---------------------------------------------------------------------------
PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]  # GeV/c, 14 bins

PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # GeV/c, 16 bins

TRACKER_MIN_Z_MM = 5980.0
TRACKER_MAX_Z_MM = 8422.0
TRACKER_APOTHEM_MM = 850.0
# From PlotUtils::TargetUtils::GetTrackerNNucleons(minZ=5980 mm, maxZ=8422 mm,
# isMC=true, apothem=850 mm). Keep this local so the 2D workflow is not
# sensitive to hadd summing a per-playlist TParameter<double>.
TRACKER_FIDUCIAL_N_NUCLEONS = 3.2352943296224835e30

# C++ truth phase-space cut from CCInclusiveSignal.h::GetCCInclusive2DPhaseSpace
# (MuonAngle(20.)). Mirrored here so the Python truth-pass gate matches the
# event loop's mc_truth_denom selection — without this, the diagonal corner
# (pT/pz > tan 20°) is admitted by the rectangle alone and inflates
# c = hOFInputTruth / hOFTruthDenom above 1.
MAX_MUON_THETA_RAD = math.radians(20.0)


def in_truth_phase_space(pt, pz, pt_lo, pt_hi, pz_lo, pz_hi):
    """C++ CCInclusive2DPhaseSpace mirror restricted to (pT, pz)-derivable cuts.

    Enforces the analysis rectangle plus θ_μ < 20° (computed from truth pT,
    pz). Truth-vertex fiducial (Tracker Z, Apothem) cuts in the C++ signal
    definition cannot be replicated here because the truth vertex isn't on
    the OmniFold trees; they are applied event-loop-side when mc_truth_denom
    is filled and are essentially redundant for events that reco-passed.
    """
    if not (math.isfinite(pt) and math.isfinite(pz)):
        return False
    if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
        return False
    return math.atan2(pt, pz) < MAX_MUON_THETA_RAD


# ---------------------------------------------------------------------------
# Utility helpers (shared with 1D script)
# ---------------------------------------------------------------------------
def make_th2d(name, title, xedges, yedges):
    h = ROOT.TH2D(name, title,
                   len(xedges) - 1, array("d", xedges),
                   len(yedges) - 1, array("d", yedges))
    h.Sumw2()
    h.SetDirectory(0)
    return h


def make_th1d(name, title, edges):
    h = ROOT.TH1D(name, title, len(edges) - 1, array("d", edges))
    h.Sumw2()
    h.SetDirectory(0)
    return h


def make_flux_hist(name, edges, vals):
    h = make_th1d(name,
                  "Flux integral per p_{T} bin;"
                  "p_{T} (GeV/c);Flux (m^{-2}/POT)",
                  edges)
    for i, x in enumerate(vals, start=1):
        h.SetBinContent(i, float(x))
    return h


def np_to_tvector(mask):
    v = ROOT.TVector(len(mask))
    for i, x in enumerate(mask):
        v[i] = 1.0 if bool(x) else 0.0
    return v


def np_to_tvectord(vals):
    v = ROOT.TVectorD(len(vals))
    for i, x in enumerate(vals):
        v[i] = float(x)
    return v


def tvectord_to_np(v):
    return np.asarray([float(v[i]) for i in range(v.GetNoElements())], dtype=float)


def get_pot_scales(f_in):
    data_par = f_in.Get("dataPOTUsed")
    mc_par = f_in.Get("mcPOTUsed")
    if not data_par or not mc_par:
        raise RuntimeError("Missing POT metadata in input file")
    data_pot = float(data_par.GetVal())
    mc_pot = float(mc_par.GetVal())
    if not (math.isfinite(data_pot) and math.isfinite(mc_pot) and mc_pot > 0):
        raise RuntimeError(f"Invalid POT: data={data_pot}, mc={mc_pot}")
    return data_pot, mc_pot, data_pot / mc_pot


def load_flux_bins(mc_path, hist_name, pt_edges):
    f_mc = ROOT.TFile.Open(mc_path, "READ")
    if not f_mc or f_mc.IsZombie():
        raise RuntimeError(f"Could not open {mc_path} (needed for flux histogram)")
    h_flux = f_mc.Get(hist_name)
    if not h_flux:
        raise RuntimeError(f"Missing {hist_name} in {mc_path}")
    if h_flux.GetNbinsX() != len(pt_edges) - 1:
        raise RuntimeError(
            f"Flux histogram has {h_flux.GetNbinsX()} bins but pt_edges expects "
            f"{len(pt_edges) - 1}")

    flux_bins = np.asarray(
        [h_flux.GetBinContent(i) for i in range(1, h_flux.GetNbinsX() + 1)],
        dtype=float)
    f_mc.Close()
    return flux_bins, make_flux_hist("hFlux_pt", pt_edges, flux_bins)


def load_flux_universe_bins(path, idx, pt_edges, cv_flux_bins):
    """Per-PPFX-universe flux integral for a Flux systematic universe.

    The 2D cross section divides by the integrated flux Phi(pT); the flux
    uncertainty enters mainly through this 1/Phi normalization. A flux
    universe must therefore divide by *its own* flux integral Phi_u, not the
    CV one (using CV in every universe is the Task #70 bug). The per-universe
    integrals live in `path` (built by uq/build_flux_universe_band.py):
        hFluxCV    TH1D  [n_pt]           CV flux integral
        hFluxUniv  TH2D  [n_pt x N_univ]  per-universe flux integral
    Column `idx` is PPFX universe idx, the same throw as w_{truth,reco}_Flux_idx
    in the omnifile (alignment verified, Pearson 0.96). Returns Phi_u (m^-2/POT)
    on the pt_edges binning. Guards that hFluxCV matches the loaded CV flux so
    the universe and CV come from the same flux production.
    """
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(
            f"[FAIL] --universe Flux:{idx} needs the per-universe flux file "
            f"{path}, which is missing. Build it with "
            f"uq/build_flux_universe_band.py. (Dividing a flux universe by the "
            f"CV flux integral silently re-introduces the Task #70 bug.)")
    huniv = f.Get("hFluxUniv")
    hcv = f.Get("hFluxCV")
    if not huniv or not hcv:
        f.Close()
        raise RuntimeError(f"[FAIL] {path} missing hFluxUniv/hFluxCV")
    n_pt, n_univ = huniv.GetNbinsX(), huniv.GetNbinsY()
    if n_pt != len(pt_edges) - 1:
        f.Close()
        raise RuntimeError(
            f"[FAIL] flux-universe file has {n_pt} pT bins but pt_edges "
            f"expects {len(pt_edges) - 1}")
    if not (0 <= idx < n_univ):
        f.Close()
        raise RuntimeError(
            f"[FAIL] Flux universe idx {idx} out of range [0,{n_univ})")
    phi_u = np.asarray(
        [huniv.GetBinContent(i, idx + 1) for i in range(1, n_pt + 1)],
        dtype=float)
    phi_cv = np.asarray(
        [hcv.GetBinContent(i) for i in range(1, n_pt + 1)], dtype=float)
    f.Close()
    max_rel = float(np.abs(phi_cv - cv_flux_bins).max()
                    / max(np.abs(cv_flux_bins).max(), 1e-300))
    if max_rel > 1e-6:
        raise RuntimeError(
            f"[FAIL] flux-universe file CV disagrees with --flux-hist CV "
            f"(max rel diff {max_rel:.2e}); they are not from the same flux "
            f"production. Rebuild uq/build_flux_universe_band.py against the "
            f"same playlists as --mcfile.")
    return phi_u


def count_negative_bins_2d(h):
    nneg = 0
    for ix in range(1, h.GetNbinsX() + 1):
        for iy in range(1, h.GetNbinsY() + 1):
            if h.GetBinContent(ix, iy) < 0:
                nneg += 1
    return nneg


# ---------------------------------------------------------------------------
# TTree readers — 2D versions
# ---------------------------------------------------------------------------
def fill_data_reco_2d(t_data, h_data_2d, pt_lo, pt_hi, pz_lo, pz_hi,
                      guard_max=1e3, verbose=False):
    """Read selected data events, return (pt_arr, pz_arr) and fill h_data_2d."""
    measured = array("d", [0.0])
    measured_pz = array("d", [0.0])
    measured_pass = array("B", [0])
    t_data.SetBranchAddress("measured", measured)
    t_data.SetBranchAddress("measured_pz", measured_pz)
    t_data.SetBranchAddress("measured_pass", measured_pass)

    pts, pzs = [], []
    n_skip = 0
    for i in range(t_data.GetEntries()):
        t_data.GetEntry(i)
        if measured_pass[0] == 0:
            n_skip += 1
            continue
        pt = float(measured[0])
        pz = float(measured_pz[0])
        if not (math.isfinite(pt) and math.isfinite(pz)):
            n_skip += 1
            continue
        if abs(pt) > guard_max or abs(pz) > guard_max:
            n_skip += 1
            continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            n_skip += 1
            continue
        pts.append(pt)
        pzs.append(pz)
        h_data_2d.Fill(pt, pz)

    if verbose:
        print(f"[INFO] data: kept={len(pts)}, skipped={n_skip}")
    return np.asarray(pts, dtype=float), np.asarray(pzs, dtype=float)


def fill_bkg_reco_2d(t_bkg, h_bkg_2d, pot_scale, pt_lo=None, pt_hi=None,
                     pz_lo=None, pz_hi=None, guard_max=1e3, verbose=False,
                     universe_branch=None):
    """Fill background TH2D with POT-scaled MC background events.

    Also returns the per-event background reco arrays (p_T, p_||, POT-scaled
    weight) for the unbinned negative-weight-injection background mode
    (`--bkg-mode negweight`). The histogram fill is unchanged, so the binned
    purity path (`--bkg-mode purity`, default) is byte-identical.

    The RETURNED arrays are restricted to the same fiducial reco window
    (pt_lo/pt_hi/pz_lo/pz_hi) that fill_data_reco_2d applies to the data, so the
    injected background lives on the same reco support as the measured data (and
    matches h_bkg_2d.Integral(), which excludes the out-of-range overflow). The
    histogram Fill is still called for every event (out-of-range -> overflow, as
    before) so the binned purity path is unaffected. Passing any bound as None
    disables that side of the fiducial cut on the returned arrays.

    When `universe_branch=(band, idx)` is set, the genuine-background subtraction
    is varied for that systematic universe (KNOWN_ISSUES #13): the weight is read
    from `w_bkg_<sanitized_band>_<idx>` instead of the CV `w_bkg`, and for LATERAL
    universes (shifted-kinematic branches present) the reco pt/pz swap to
    `sim_background_<band>_<idx>` / `sim_background_pz_<band>_<idx>`. Vertical
    universes shift the weight only. Both the binned purity down-weight (via
    h_bkg_2d) and the negweight injection (via the returned arrays) then track the
    per-universe background, so the systematic covariance finally includes
    background-modeling variation. Branches are written by the C++ event loop's
    BkgTreeReco context under MNV101_DUMP_UNIVERSES. `universe_branch=None`
    (CV / non-universe unfold) is byte-identical to the pre-#13 behaviour.
    Requires the per-universe branches to be present (raises if the weight branch
    is missing so a universe never silently falls back to CV).
    """
    sim_bkg = array("d", [0.0])
    sim_bkg_pz = array("d", [0.0])
    sim_bkg_pass = array("B", [0])
    w_bkg = array("d", [1.0])
    sb_name, sb_pz_name, w_name = "sim_background", "sim_background_pz", "w_bkg"
    if universe_branch is not None:
        w_name = _universe_bkg_branch(universe_branch)
        if not t_bkg.GetBranch(w_name):
            raise RuntimeError(
                f"[FAIL] per-universe background branch '{w_name}' missing from "
                f"mc_background; rebuild the omnifile with MNV101_DUMP_UNIVERSES "
                f"so the KNOWN_ISSUES #13 background branches exist.")
        lat_sb, lat_sb_pz = _universe_kine_branches(universe_branch, "bkg_tree_reco")
        if t_bkg.GetBranch(lat_sb) and t_bkg.GetBranch(lat_sb_pz):  # lateral
            sb_name, sb_pz_name = lat_sb, lat_sb_pz
            if verbose:
                print(f"[INFO] bkg lateral universe: reco kinematics {lat_sb}/"
                      f"{lat_sb_pz}, weight {w_name}")
        elif verbose:
            print(f"[INFO] bkg vertical universe: weight {w_name} (CV kinematics)")
    t_bkg.SetBranchAddress(sb_name, sim_bkg)
    t_bkg.SetBranchAddress(sb_pz_name, sim_bkg_pz)
    t_bkg.SetBranchAddress("sim_background_pass", sim_bkg_pass)
    t_bkg.SetBranchAddress(w_name, w_bkg)

    bkg_pt, bkg_pz, bkg_w = [], [], []
    n_filled, n_skip = 0, 0
    for i in range(t_bkg.GetEntries()):
        t_bkg.GetEntry(i)
        if sim_bkg_pass[0] == 0:
            n_skip += 1
            continue
        pt = float(sim_bkg[0])
        pz = float(sim_bkg_pz[0])
        w = float(w_bkg[0])
        if not (math.isfinite(pt) and math.isfinite(pz) and
                math.isfinite(w) and 0 <= w < 1e6):
            n_skip += 1
            continue
        h_bkg_2d.Fill(pt, pz, w * pot_scale)
        n_filled += 1
        # Returned arrays: fiducial reco window only (parity with the data).
        if pt_lo is not None and pt < pt_lo: continue
        if pt_hi is not None and pt > pt_hi: continue
        if pz_lo is not None and pz < pz_lo: continue
        if pz_hi is not None and pz > pz_hi: continue
        bkg_pt.append(pt)
        bkg_pz.append(pz)
        bkg_w.append(w * pot_scale)

    if verbose:
        print(f"[INFO] bkg: filled={n_filled}, skipped={n_skip}, "
              f"in-fiducial for injection={len(bkg_pt)}")
    return (np.asarray(bkg_pt, dtype=float),
            np.asarray(bkg_pz, dtype=float),
            np.asarray(bkg_w, dtype=float))


def build_measured_training_2d(meas_pt, meas_pz, h_data_2d, h_bkg_2d, verbose=False):
    """Build a non-negative measured training target and per-event weights.

    OmniFold's measured-side interface accepts per-event sample weights but not
    negative weights. We therefore keep the raw `data - bkg` histogram for
    diagnostics and construct a separate training target that floors any
    negative reco-space bins to zero.
    """
    if meas_pt.shape != meas_pz.shape:
        raise RuntimeError("Measured p_T and p_|| arrays have mismatched shapes")

    h_train_2d = h_data_2d.Clone("hMeasTrain2D")
    h_train_2d.SetTitle("Measured (training, floored);p_{T} (GeV/c);p_{||} (GeV/c)")
    h_train_2d.Reset("ICES")

    xaxis = h_data_2d.GetXaxis()
    yaxis = h_data_2d.GetYaxis()
    weights = np.zeros(meas_pt.shape[0], dtype=float)
    n_zero = 0

    for i, (pt, pz) in enumerate(zip(meas_pt, meas_pz)):
        ix = xaxis.FindFixBin(float(pt))
        iy = yaxis.FindFixBin(float(pz))
        data_bin = h_data_2d.GetBinContent(ix, iy)
        if data_bin <= 0.0:
            n_zero += 1
            continue
        target_bin = max(0.0, data_bin - h_bkg_2d.GetBinContent(ix, iy))
        weight = target_bin / data_bin
        weights[i] = weight
        h_train_2d.Fill(float(pt), float(pz), weight)
        if weight <= 0.0:
            n_zero += 1

    if verbose:
        print(f"[INFO] measured training: effective sum={weights.sum():.6g}, "
              f"zero-weight events={n_zero}/{weights.size}")
    return weights, h_train_2d


def _make_bkg_classifier(estimator, params, device):
    """Construct a single binary classifier matching omnifold's step-1 backend
    defaults, for the Stay-Positive weight refinement (--bkg-mode
    negweight-refined). Mirrors the estimator dispatch in
    omnifold.OmniFold_helper_functions.omnifold so the refinement lives in the
    same estimator family (and honours --seed via random_state) as the unfold
    it feeds.
    """
    params = dict(params or {})
    if estimator == "exact":
        from sklearn.ensemble import GradientBoostingClassifier
        return GradientBoostingClassifier(**params)
    if estimator == "hist":
        from sklearn.ensemble import HistGradientBoostingClassifier
        d = dict(max_iter=100, max_leaf_nodes=8, learning_rate=0.1)
        return HistGradientBoostingClassifier(**{**d, **params})
    if estimator == "xgb":
        from xgboost import XGBClassifier
        d = dict(n_estimators=100, max_depth=3, learning_rate=0.1,
                 tree_method="hist", device=device)
        return XGBClassifier(**{**d, **params})
    if estimator == "lgbm":
        from lightgbm import LGBMClassifier
        d = dict(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)
        if device != "cpu":
            d["device"] = "gpu"
        return LGBMClassifier(**{**d, **params})
    raise ValueError(f"negweight-refined: unsupported estimator {estimator!r} "
                     "(use exact/hist/xgb/lgbm)")


def refine_stay_positive(feat, signed_w, estimator="exact", device="cpu",
                         params=None, verbose=False):
    """Stay-Positive (arXiv:2505.03724) refinement of a signed-weight sample.

    Given the measured (class-1) sample on the reco manifold with signed
    per-event weights `signed_w` -- data at +1, injected background at
    -w_bkg*pot_scale -- refine to an equivalent NON-NEGATIVE-weight sample that
    preserves the conditional average weight <w|x> = D(x) - B(x) everywhere, so
    OmniFold step-1 targets (D-B)/S with a WELL-POSED positive-weight fit
    instead of relying on the p/(1-p) >= 0 structural floor of the raw signed
    fit (which is ill-posed where B>D locally).

    Method (paper eqs 4-7, specialised to our two-population sample):
      Train a binary classifier g(x) separating positive-weight events (label
      1) from negative-weight events (label 0), each carrying |w| as its sample
      weight. Its population optimum is g*(x) = D(x)/(D(x)+B(x)), so
          2 g*(x) - 1 = (D-B)/(D+B),
      and the refined weight of EVERY event is
          w~_i = |w_i| * (2 g(x_i) - 1),
      which sums to D-B at each x (paper eq 6) and is >= 0 wherever D>=B. Where
      B>D locally the factor 2g-1 < 0; we clip w~ at 0 -- the principled
      unbinned analogue of the binned max(0,.) floor, now applied to a SMOOTH
      learned net/absolute ratio rather than to a per-event artifact of the
      [0,1] probability range.

    Returns (w_refined, g_at_events, frac_clipped).
    """
    feat = np.asarray(feat, dtype=float)
    if feat.ndim == 1:
        feat = feat.reshape(-1, 1)
    signed_w = np.asarray(signed_w, dtype=float)
    labels = (signed_w > 0).astype(int)
    absw = np.abs(signed_w)
    clf = _make_bkg_classifier(estimator, params, device)
    clf.fit(feat, labels, sample_weight=absw)
    g = np.clip(clf.predict_proba(feat)[:, 1], 1e-6, 1.0 - 1e-6)
    factor = 2.0 * g - 1.0
    n_clip = int((factor < 0.0).sum())
    w_ref = absw * np.clip(factor, 0.0, None)
    if verbose:
        print(f"[INFO] Stay-Positive refine: {int(labels.sum())} pos / "
              f"{int((labels == 0).sum())} neg events; g in "
              f"[{g.min():.3f},{g.max():.3f}]; clipped(2g-1<0) {n_clip} events; "
              f"sum(w_refined)={w_ref.sum():.6g} (signed sum "
              f"{signed_w.sum():.6g}).")
    return w_ref, g, n_clip / max(len(signed_w), 1)


def _sanitize_band_for_branch(s):
    """Mirror of the C++ SanitizeForRootBranchName in
    runEventLoopOmniFold.cpp: any character not in [A-Za-z0-9_] is
    replaced with '_'. Python sides of the universe-weight path must
    sanitize band names with this exact rule so the branch names line up
    with what the C++ event loop wrote.
    """
    return "".join(c if (c.isalnum() or c == "_") else "_" for c in s)


def _universe_truth_branch(universe_branch):
    """Return ('w_truth_<sanitized_band>_<idx>') or None."""
    if universe_branch is None:
        return None
    band, idx = universe_branch
    return f"w_truth_{_sanitize_band_for_branch(band)}_{int(idx)}"


def _universe_reco_branch(universe_branch):
    """Return ('w_reco_<sanitized_band>_<idx>') or None."""
    if universe_branch is None:
        return None
    band, idx = universe_branch
    return f"w_reco_{_sanitize_band_for_branch(band)}_{int(idx)}"


def _universe_bkg_branch(universe_branch):
    """Return ('w_bkg_<sanitized_band>_<idx>') or None.

    Per-universe genuine-background weight on the mc_background tree, written by
    the C++ event loop's BkgTreeReco context under MNV101_DUMP_UNIVERSES
    (KNOWN_ISSUES #13 fix). Read by und.collect_bkg_nd in place of the CV w_bkg
    so the OmniFold measured-target purity down-weight varies per systematic
    universe instead of freezing at CV.
    """
    if universe_branch is None:
        return None
    band, idx = universe_branch
    return f"w_bkg_{_sanitize_band_for_branch(band)}_{int(idx)}"


def _universe_kine_branches(universe_branch, kine_ctx):
    """Return (pt_branch, pz_branch) names for lateral universe kinematics.

    kine_ctx selects the host-tree naming convention:
      'truth_tree'      -> ('pT_truth_<band>_<idx>', 'pz_truth_<band>_<idx>')
      'reco_tree_truth' -> ('MC_<band>_<idx>',        'MC_pz_<band>_<idx>')
      'reco_tree_reco'  -> ('sim_<band>_<idx>',       'sim_pz_<band>_<idx>')
      'bkg_tree_reco'   -> ('sim_background_<band>_<idx>',
                            'sim_background_pz_<band>_<idx>')  # mc_background,
                            # KNOWN_ISSUES #13: own namespace, never aliases the
                            # signal reco 'sim_*' shadow branches.
    Returns (None, None) for vertical-only universes (caller detects by
    branch absence in the input ROOT).
    """
    if universe_branch is None:
        return None, None
    band, idx = universe_branch
    suffix = f"{_sanitize_band_for_branch(band)}_{int(idx)}"
    if kine_ctx == "truth_tree":
        return f"pT_truth_{suffix}", f"pz_truth_{suffix}"
    if kine_ctx == "reco_tree_truth":
        return f"MC_{suffix}",       f"MC_pz_{suffix}"
    if kine_ctx == "reco_tree_reco":
        return f"sim_{suffix}",      f"sim_pz_{suffix}"
    if kine_ctx == "bkg_tree_reco":
        return f"sim_background_{suffix}", f"sim_background_pz_{suffix}"
    raise ValueError(f"unknown kine_ctx={kine_ctx!r}")


def collect_truth_denom_arrays(t_truth_denom, pt_lo, pt_hi, pz_lo, pz_hi,
                                pot_scale, use_weights=False, verbose=False,
                                universe_branch=None):
    """Read mc_truth_denom TTree, return truth-only arrays for hEffDen.

    mc_truth_denom is the canonical efficiency denominator: it loops the
    Truth tree directly and includes truth-passing events whether or not
    they have a corresponding entry in the reco tree. mc_signal_reco only
    has truth-passing events that ALSO appear in the reco tree, so it is
    a proper subset (~25% smaller for ME FHC). Building hEffDen from
    mc_truth_denom is required for the standard MINERvA cross-section
    extraction; using the mc_signal_reco subset under-counts the true
    denominator and over-estimates efficiency.

    When `universe_branch` is set to a (band, idx) tuple, the truth
    weight is read from `w_truth_<sanitized_band>_<idx>` instead of the
    CV `w_truth`. The branch is written by the C++ event loop under
    `MNV101_DUMP_UNIVERSES=1` (or a comma-separated allowlist). Requires
    use_weights=True (the CV->universe swap only applies when we are
    reading any weight at all).
    """
    pt_arr = array("d", [0.0])
    pz_arr = array("d", [0.0])
    wt_arr = array("d", [1.0])
    pt_branch_name = "MC"
    pz_branch_name = "MC_pz"
    weight_branch = "w_truth"
    if use_weights and universe_branch is not None:
        weight_branch = _universe_truth_branch(universe_branch)
        if not t_truth_denom.GetBranch(weight_branch):
            raise RuntimeError(
                f"[FAIL] universe branch '{weight_branch}' missing from "
                f"mc_truth_denom; rebuild the input ROOT with "
                f"MNV101_DUMP_UNIVERSES set so the universe weights are "
                f"written.")
        # Lateral universes also carry shifted kinematics; swap if present.
        lat_pt, lat_pz = _universe_kine_branches(universe_branch, "truth_tree")
        if t_truth_denom.GetBranch(lat_pt) and t_truth_denom.GetBranch(lat_pz):
            pt_branch_name, pz_branch_name = lat_pt, lat_pz
            if verbose:
                print(f"[INFO] truth_denom: lateral universe — using "
                      f"{lat_pt}/{lat_pz} in place of MC/MC_pz")
    t_truth_denom.SetBranchAddress(pt_branch_name, pt_arr)
    t_truth_denom.SetBranchAddress(pz_branch_name, pz_arr)
    if use_weights:
        t_truth_denom.SetBranchAddress(weight_branch, wt_arr)

    pt_list, pz_list, w_list = [], [], []
    bad_w, dropped = 0, 0

    n_entries = t_truth_denom.GetEntries()
    for i in range(n_entries):
        t_truth_denom.GetEntry(i)
        pt = float(pt_arr[0])
        pz = float(pz_arr[0])
        w = float(wt_arr[0]) if use_weights else 1.0
        if not (math.isfinite(pt) and math.isfinite(pz) and
                math.isfinite(w) and 0 <= w < 1e4):
            bad_w += 1
            continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            dropped += 1
            continue
        w *= pot_scale
        pt_list.append(pt)
        pz_list.append(pz)
        w_list.append(w)

    if verbose:
        print(f"[INFO] truth_denom: kept={len(pt_list)}, "
              f"dropped={dropped}, bad_w={bad_w}, total={n_entries}")

    return {
        "truth_pt": np.asarray(pt_list, dtype=float),
        "truth_pz": np.asarray(pz_list, dtype=float),
        "w_truth": np.asarray(w_list, dtype=float),
    }


def collect_signal_arrays_2d(t_sig, pt_lo, pt_hi, pz_lo, pz_hi,
                              pot_scale, use_weights=False, verbose=False,
                              universe_branch=None,
                              alt_universe_branch=None):
    """Read mc_signal_reco TTree, return dict of 2D arrays for OmniFold.

    When `universe_branch` is set to a (band, idx) tuple, the per-event
    weights are read from `w_truth_<sanitized_band>_<idx>` and
    `w_reco_<sanitized_band>_<idx>` instead of the CV `w_truth` /
    `w_reco`. The branches are written by the C++ event loop under
    `MNV101_DUMP_UNIVERSES`. Requires use_weights=True.

    When `alt_universe_branch` is set, the CV w_truth/w_reco are still
    populated (so the response training is unchanged), AND additional
    arrays `w_truth_alt` / `w_reco_alt` are populated from the universe
    branches. Used by the alt-model closure to inject alt-model bias
    into closure pseudo-data and truth reference while keeping the
    response at CV. Mutually exclusive with `universe_branch`.
    """
    mc_pt = array("d", [0.0])
    mc_pz = array("d", [0.0])
    sim_pt = array("d", [0.0])
    sim_pz_arr = array("d", [0.0])
    sim_pass = array("B", [0])
    mc_pt_branch = "MC"
    mc_pz_branch = "MC_pz"
    sim_pt_branch = "sim"
    sim_pz_branch = "sim_pz"

    wt_arr = array("d", [1.0])
    wr_arr = array("d", [1.0])
    wt_branch = "w_truth"
    wr_branch = "w_reco"
    if use_weights and universe_branch is not None:
        wt_branch = _universe_truth_branch(universe_branch)
        wr_branch = _universe_reco_branch(universe_branch)
        for bname in (wt_branch, wr_branch):
            if not t_sig.GetBranch(bname):
                raise RuntimeError(
                    f"[FAIL] universe branch '{bname}' missing from "
                    f"mc_signal_reco; rebuild the input ROOT with "
                    f"MNV101_DUMP_UNIVERSES set so the universe weights "
                    f"are written.")
        # Lateral universes carry shifted kinematics on the reco tree as
        # MC_<band>_<idx> (truth-mode) and sim_<band>_<idx> (reco-mode);
        # swap both pairs if either is present.
        lat_mc, lat_mc_pz = _universe_kine_branches(universe_branch, "reco_tree_truth")
        lat_sim, lat_sim_pz = _universe_kine_branches(universe_branch, "reco_tree_reco")
        if t_sig.GetBranch(lat_mc) and t_sig.GetBranch(lat_mc_pz):
            mc_pt_branch, mc_pz_branch = lat_mc, lat_mc_pz
        if t_sig.GetBranch(lat_sim) and t_sig.GetBranch(lat_sim_pz):
            sim_pt_branch, sim_pz_branch = lat_sim, lat_sim_pz
        if verbose and (mc_pt_branch != "MC" or sim_pt_branch != "sim"):
            print(f"[INFO] signal: lateral universe — using "
                  f"{mc_pt_branch}/{mc_pz_branch} for truth and "
                  f"{sim_pt_branch}/{sim_pz_branch} for reco kinematics")

    t_sig.SetBranchAddress(mc_pt_branch, mc_pt)
    t_sig.SetBranchAddress(mc_pz_branch, mc_pz)
    t_sig.SetBranchAddress(sim_pt_branch, sim_pt)
    t_sig.SetBranchAddress(sim_pz_branch, sim_pz_arr)
    t_sig.SetBranchAddress("sim_pass", sim_pass)

    if use_weights:
        t_sig.SetBranchAddress(wt_branch, wt_arr)
        t_sig.SetBranchAddress(wr_branch, wr_arr)

    wt_alt_arr = array("d", [1.0])
    wr_alt_arr = array("d", [1.0])
    use_alt = use_weights and alt_universe_branch is not None
    if use_alt:
        if universe_branch is not None:
            raise RuntimeError(
                "[FAIL] alt_universe_branch and universe_branch are mutually "
                "exclusive: alt-model closure keeps the response at CV.")
        wt_alt_branch = _universe_truth_branch(alt_universe_branch)
        wr_alt_branch = _universe_reco_branch(alt_universe_branch)
        for bname in (wt_alt_branch, wr_alt_branch):
            if not t_sig.GetBranch(bname):
                raise RuntimeError(
                    f"[FAIL] alt-model universe branch '{bname}' missing "
                    f"from mc_signal_reco; rebuild input with "
                    f"MNV101_DUMP_UNIVERSES set.")
        t_sig.SetBranchAddress(wt_alt_branch, wt_alt_arr)
        t_sig.SetBranchAddress(wr_alt_branch, wr_alt_arr)

    truth_pt_list, truth_pz_list = [], []
    reco_pt_list, reco_pz_list = [], []
    pass_reco_list, pass_truth_list = [], []
    w_truth_list, w_reco_list = [], []
    w_truth_alt_list, w_reco_alt_list = [], []
    dropped, bad_w = 0, 0

    for i in range(t_sig.GetEntries()):
        t_sig.GetEntry(i)
        tru_pt = float(mc_pt[0])
        tru_pz = float(mc_pz[0])
        rec_pt = float(sim_pt[0])
        rec_pz = float(sim_pz_arr[0])
        passed = sim_pass[0] != 0

        wt = float(wt_arr[0]) if use_weights else 1.0
        wr = float(wr_arr[0]) if use_weights else wt
        if not (math.isfinite(wt) and math.isfinite(wr) and
                0 <= wt < 1e4 and 0 <= wr < 1e4):
            bad_w += 1
            continue
        wt *= pot_scale
        wr *= pot_scale

        if use_alt:
            wt_a = float(wt_alt_arr[0])
            wr_a = float(wr_alt_arr[0])
            if not (math.isfinite(wt_a) and math.isfinite(wr_a) and
                    0 <= wt_a < 1e4 and 0 <= wr_a < 1e4):
                bad_w += 1
                continue
            wt_a *= pot_scale
            wr_a *= pot_scale

        # Truth-pass gate matches C++ GetCCInclusive2DPhaseSpace (rectangle
        # + θ_μ < 20°) so c = hOFInputTruth / hOFTruthDenom ≡ 1 modulo MC
        # stats; reco gate stays as the 2D binning rectangle.
        tru_ok = in_truth_phase_space(tru_pt, tru_pz,
                                       pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(rec_pt) and math.isfinite(rec_pz) and
                  pt_lo <= rec_pt <= pt_hi and pz_lo <= rec_pz <= pz_hi)

        if not (tru_ok or (passed and rec_ok)):
            dropped += 1
            continue

        truth_pt_list.append(tru_pt if math.isfinite(tru_pt) else -9999.0)
        truth_pz_list.append(tru_pz if math.isfinite(tru_pz) else -9999.0)
        reco_pt_list.append(rec_pt if (passed and rec_ok) else -9999.0)
        reco_pz_list.append(rec_pz if (passed and rec_ok) else -9999.0)
        pass_reco_list.append(passed and rec_ok)
        pass_truth_list.append(tru_ok)
        w_truth_list.append(wt)
        w_reco_list.append(wr)
        if use_alt:
            w_truth_alt_list.append(wt_a)
            w_reco_alt_list.append(wr_a)

    if verbose:
        print(f"[INFO] signal: kept={len(truth_pt_list)}, dropped={dropped}, bad_w={bad_w}")

    out = {
        "truth_pt": np.asarray(truth_pt_list, dtype=float),
        "truth_pz": np.asarray(truth_pz_list, dtype=float),
        "reco_pt": np.asarray(reco_pt_list, dtype=float),
        "reco_pz": np.asarray(reco_pz_list, dtype=float),
        "pass_reco": np.asarray(pass_reco_list, dtype=bool),
        "pass_truth": np.asarray(pass_truth_list, dtype=bool),
        "w_truth": np.asarray(w_truth_list, dtype=float),
        "w_reco": np.asarray(w_reco_list, dtype=float),
    }
    if use_alt:
        out["w_truth_alt"] = np.asarray(w_truth_alt_list, dtype=float)
        out["w_reco_alt"] = np.asarray(w_reco_alt_list, dtype=float)
    return out


# ---------------------------------------------------------------------------
# Cross-section calculation
# ---------------------------------------------------------------------------
def compute_efficiency_2d(sig, pt_edges, pz_edges, truth_denom=None):
    """Compute the standard selection efficiency (diagnostic; mirrors paper Fig. 5).

    hEffNum = mc_signal_reco events with both truth-pass AND sim_pass=True
              (weighted by w_reco). This is the canonical "events passing
              reco selection."
    hEffDen = full truth denominator. From mc_truth_denom if `truth_denom`
              given; otherwise from the mc_signal_reco truth-pass subset
              (closure / fallback).
    hEff2D  = hEffNum / hEffDen (absolute selection efficiency). Used by
              `plot_efficiency_fig5_style.py` for diagnostic comparison
              with the paper. **Not** the right divisor for the OmniFold
              cross section — see `compute_omnifold_completeness_2d`.
    """
    hNum = make_th2d("hEffNum", "eff numerator", pt_edges, pz_edges)
    hDen = make_th2d("hEffDen", "eff denominator", pt_edges, pz_edges)

    for pt, pz, pr, ptru, wt, wr in zip(
            sig["truth_pt"], sig["truth_pz"],
            sig["pass_reco"], sig["pass_truth"],
            sig["w_truth"], sig["w_reco"]):
        if ptru:
            if truth_denom is None:
                hDen.Fill(pt, pz, wt)
            if pr:
                hNum.Fill(pt, pz, wr)

    if truth_denom is not None:
        for pt, pz, w in zip(truth_denom["truth_pt"],
                              truth_denom["truth_pz"],
                              truth_denom["w_truth"]):
            hDen.Fill(pt, pz, w)

    hEff = hNum.Clone("hEff2D")
    hEff.SetTitle("Selection efficiency;p_{T} (GeV/c);p_{||} (GeV/c)")
    hEff.Divide(hDen)
    return hEff, hNum, hDen


def compute_omnifold_completeness_2d(sig, pt_edges, pz_edges, truth_denom):
    """Compute the OmniFold input completeness ratio used to scale hUnfold2D.

    OmniFold's step-1 miss regression handles `sim_pass=False` events
    that are present in the input (mc_signal_reco contains both reco-
    passing and reco-failing truth-passing events). It does **not**
    handle truth events that are entirely absent from the input — those
    in mc_truth_denom but not in mc_signal_reco. So OmniFold's hUnfold2D
    represents the inferred truth-level data over the mc_signal_reco
    truth-pass subset, not the full truth space.

    The correction:
        hOFInputTruth = mc_signal_reco truth-pass events (regardless of
                        sim_pass), weighted by w_truth — i.e. the subset
                        of truth events that is visible to OmniFold.
        hTruthDenom   = mc_truth_denom (canonical full truth).
        hOFCompleteness = hOFInputTruth / hTruthDenom
                        = fraction of truth events that OmniFold sees.

    Cross section then uses
        σ = hUnfold2D / (hOFCompleteness · Φ · N · POT · ΔpT · Δp||)
    which scales each bin from the OmniFold-input subset to the full
    truth phase space.

    For the global ME FHC numbers this ratio is ~24.5M / 32.85M ≈ 0.745,
    matching the observed σ_total/σ_paper deficit of 0.752 to within ~1%.
    """
    hOFInputTruth = make_th2d(
        "hOFInputTruth2D",
        "OmniFold input truth-pass events (numerator of completeness)",
        pt_edges, pz_edges)
    hTruthDen = make_th2d(
        "hOFTruthDenom2D",
        "Full truth denominator (mc_truth_denom)",
        pt_edges, pz_edges)

    for pt, pz, ptru, wt in zip(sig["truth_pt"], sig["truth_pz"],
                                  sig["pass_truth"], sig["w_truth"]):
        if ptru:
            hOFInputTruth.Fill(pt, pz, wt)

    for pt, pz, w in zip(truth_denom["truth_pt"], truth_denom["truth_pz"],
                          truth_denom["w_truth"]):
        hTruthDen.Fill(pt, pz, w)

    hCompleteness = hOFInputTruth.Clone("hOFCompleteness2D")
    hCompleteness.SetTitle(
        "OmniFold input completeness "
        "(mc_signal_reco truth-pass / mc_truth_denom);"
        "p_{T} (GeV/c);p_{||} (GeV/c)")
    hCompleteness.Divide(hTruthDen)
    return hCompleteness, hOFInputTruth, hTruthDen


def closure_reweight_factor(shape, pt, pz,
                             amplitude=0.2, sigma=0.1, pt0=0.4,
                             alpha=0.1, pz_ref=5.0):
    """Multiplicative reweight on truth kinematics for the truth-reweight
    closure (Stage-1 plan deliverable #4). Both the pseudo-data
    (`measured_weights`) and the reweighted-truth reference (`hTruthRew2D`)
    use the same function, evaluated on truth kinematics — so a perfect
    unfold should map pseudo-data shifts back into the matching truth shift.

    Supported shapes:
      - 'gauss_pt': f = 1 + amplitude * exp(-((pT - pt0) / sigma)^2)
      - 'tilt_pz' : f = (pz / pz_ref)^alpha
    """
    pt_arr = np.asarray(pt, dtype=float)
    pz_arr = np.asarray(pz, dtype=float)
    if shape == "gauss_pt":
        return 1.0 + amplitude * np.exp(-((pt_arr - pt0) / sigma) ** 2)
    if shape == "tilt_pz":
        safe = np.clip(pz_arr, 1e-6, None)
        return (safe / pz_ref) ** alpha
    raise ValueError(f"Unknown closure_reweight shape: {shape}")


def extract_cross_section_2d(hUnfold, hCompleteness, flux_bins, data_pot,
                              n_nucleons, pt_edges, pz_edges):
    """Convert unfolded event counts to d^2 sigma / (dp_T dp_||).

    Formula (per bin):
        dσ = U / (c · Φ · N · POT · ΔpT · Δp||) · 1e4

    where:
        U   = hUnfold bin content (truth-level event count from OmniFold)
        c   = hCompleteness bin content
              = (events present in OmniFold input) / (all truth events)
              = hOFInputTruth / hOFTruthDenom
        Φ   = flux integral, m^-2/POT, per p_T bin (broadcast over p_||)
        N   = fiducial nucleon count
        POT = data POT
        1e4 = m^-2 → cm^-2

    Why divide by c rather than the absolute selection efficiency
    ε = hEffNum/hEffDen: OmniFold's step-1 miss regression handles the
    selection inefficiency for `sim_pass=False` events that are present
    in the input. It does **not** handle truth events absent from the
    input. So hUnfold2D is the inferred truth-level data over the
    "OmniFold input truth subset" (mc_signal_reco truth-pass events),
    not the full truth space. Dividing by c rescales from that subset
    to the full truth phase space (mc_truth_denom).

    Empirically, c_global ≈ 0.745 for ME FHC, which matches the
    observed σ_total / σ_paper deficit of 0.752 (Phase 16 of run log).

    Empty-c or empty-flux bins emit zero rather than blowing up.
    """
    hXSec = hUnfold.Clone("hXSec2D")
    hXSec.SetTitle("d^{2}#sigma/(dp_{T}dp_{||});p_{T} (GeV/c);p_{||} (GeV/c)")
    hXSec.Reset("ICES")

    nx = hUnfold.GetNbinsX()
    if flux_bins.shape[0] != nx:
        raise RuntimeError(
            f"flux_bins length ({flux_bins.shape[0]}) != hUnfold nBinsX ({nx})")
    if (hCompleteness.GetNbinsX(), hCompleteness.GetNbinsY()) != (nx, hUnfold.GetNbinsY()):
        raise RuntimeError(
            f"hCompleteness shape "
            f"({hCompleteness.GetNbinsX()}x{hCompleteness.GetNbinsY()}) "
            f"does not match hUnfold ({nx}x{hUnfold.GetNbinsY()})")

    for ix in range(1, nx + 1):
        dpt = hUnfold.GetXaxis().GetBinWidth(ix)
        flux_i = float(flux_bins[ix - 1])  # m^-2/POT
        for iy in range(1, hUnfold.GetNbinsY() + 1):
            dpz = hUnfold.GetYaxis().GetBinWidth(iy)
            u = hUnfold.GetBinContent(ix, iy)
            c = hCompleteness.GetBinContent(ix, iy)
            if (flux_i > 0 and n_nucleons > 0 and data_pot > 0 and c > 0):
                denom = c * flux_i * n_nucleons * data_pot * dpt * dpz
                xsec = (u / denom) * 1.0e4  # m^2 -> cm^2
                u_err = hUnfold.GetBinError(ix, iy)
                c_err = hCompleteness.GetBinError(ix, iy)
                rel_u = u_err / u if u > 0 else 0.0
                rel_c = c_err / c
                xerr = abs(xsec) * math.sqrt(rel_u * rel_u + rel_c * rel_c)
            else:
                xsec = 0.0
                xerr = 0.0
            hXSec.SetBinContent(ix, iy, xsec)
            hXSec.SetBinError(ix, iy, xerr)

    return hXSec


def project_xsec_1d(hXSec2D, axis, pt_edges, pz_edges):
    """
    Project 2D cross section onto one axis by summing over the other.

    d sigma / dp_T = sum_j [ d^2 sigma/(dp_T dp_||) * Delta_pz(j) ]
    d sigma / dp_|| = sum_i [ d^2 sigma/(dp_T dp_||) * Delta_pT(i) ]
    """
    if axis == "pt":
        h1d = make_th1d("hXSec_pt",
                         "d#sigma/dp_{T};p_{T} (GeV/c);d#sigma/dp_{T} (cm^{2}/GeV/nucleon)",
                         pt_edges)
        for ix in range(1, hXSec2D.GetNbinsX() + 1):
            val, err2 = 0.0, 0.0
            for iy in range(1, hXSec2D.GetNbinsY() + 1):
                dpz = hXSec2D.GetYaxis().GetBinWidth(iy)
                val += hXSec2D.GetBinContent(ix, iy) * dpz
                err2 += (hXSec2D.GetBinError(ix, iy) * dpz) ** 2
            h1d.SetBinContent(ix, val)
            h1d.SetBinError(ix, math.sqrt(err2))
        return h1d
    elif axis == "pz":
        h1d = make_th1d("hXSec_pz",
                         "d#sigma/dp_{||};p_{||} (GeV/c);d#sigma/dp_{||} (cm^{2}/GeV/nucleon)",
                         pz_edges)
        for iy in range(1, hXSec2D.GetNbinsY() + 1):
            val, err2 = 0.0, 0.0
            for ix in range(1, hXSec2D.GetNbinsX() + 1):
                dpt = hXSec2D.GetXaxis().GetBinWidth(ix)
                val += hXSec2D.GetBinContent(ix, iy) * dpt
                err2 += (hXSec2D.GetBinError(ix, iy) * dpt) ** 2
            h1d.SetBinContent(iy, val)
            h1d.SetBinError(iy, math.sqrt(err2))
        return h1d
    else:
        raise ValueError(f"Unknown axis: {axis}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="2D unbinned OmniFold unfolding for MINERvA CC inclusive (p_T, p_||).")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold.root",
                     help="Input ROOT file with unbinned TTrees (from runEventLoopOmniFold)")
    ap.add_argument("--iters", type=int, default=5,
                     help="Number of OmniFold iterations")
    ap.add_argument("--use-weights", action="store_true",
                     help="Use MC event weights (w_truth, w_reco) in OmniFold training")
    ap.add_argument("--bkg-mode",
                     choices=["purity", "negweight", "negweight-refined"],
                     default="purity",
                     help="Background subtraction on the OmniFold measured side. "
                          "'purity' (default, headline): per-reco-bin "
                          "max(0,(N_data-N_bkg)/N_data) data down-weight (binned). "
                          "'negweight': unbinned negative-weight injection — "
                          "append bkg-MC (+ signal-fake) reco events at "
                          "-w_bkg*pot_scale, data at +1, so step-1 targets "
                          "(D-B)/S continuously (arXiv:2507.09582). "
                          "'negweight-refined': Stay Positive (arXiv:2505.03724) "
                          "refinement of the signed sample to non-negative "
                          "weights (w~=|w|*(2g-1)) before step-1, well-posed "
                          "where B>D. All three support --closure, "
                          "--bootstrap-seed and --universe. See "
                          "2d-unfolding/HANDOFF_bkg_negweight/.")
    ap.add_argument("--out", default="2d_crossSection_omnifold.root",
                     help="Output ROOT file")
    ap.add_argument("--mcfile", default="runEventLoopMC.root",
                     help="ROOT file containing the flux histogram used for normalization")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated",
                     help="Histogram name inside --mcfile containing per-bin flux")
    ap.add_argument("--flux-universe-file",
                     default="baseline_flux/flux_integral_universes_MEFHC.root",
                     help="ROOT file (hFluxCV, hFluxUniv) with per-PPFX-universe "
                          "flux integrals (built by uq/build_flux_universe_band.py). "
                          "Used only when --universe Flux:IDX is set, to divide by "
                          "that universe's flux integral instead of the CV flux "
                          "(the Task #70 1/Phi normalization fix).")
    ap.add_argument("--closure", action="store_true",
                     help="Closure test: use MC reco events (pass_reco) as "
                          "pseudo-data instead of real data. Unfolded result "
                          "should recover the MC truth prior within GBT noise.")
    ap.add_argument("--closure-reweight",
                     choices=["gauss_pt", "tilt_pz"], default=None,
                     help="Truth-reweight closure (Stage-1 plan #4). Applies a "
                          "known shape to BOTH the closure pseudo-data weights "
                          "(via truth kinematics of reco-pass events) and the "
                          "reweighted-truth reference (hTruthRew2D / "
                          "hTruthRewXSec2D in the output ROOT). A correctly "
                          "unbiased unfold recovers the reweighted truth, not "
                          "the CV truth. Requires --closure.")
    ap.add_argument("--closure-reweight-amplitude", type=float, default=0.2,
                     help="gauss_pt amplitude A in f = 1 + A * exp(-((pT-pt0)/sigma)^2).")
    ap.add_argument("--closure-reweight-sigma", type=float, default=0.1,
                     help="gauss_pt sigma in f = 1 + A * exp(-((pT-pt0)/sigma)^2).")
    ap.add_argument("--closure-reweight-pt0", type=float, default=0.4,
                     help="gauss_pt center pt0 (GeV/c) in f = 1 + A * exp(-((pT-pt0)/sigma)^2).")
    ap.add_argument("--closure-reweight-alpha", type=float, default=0.1,
                     help="tilt_pz exponent alpha in f = (pz/pz_ref)^alpha.")
    ap.add_argument("--closure-reweight-pz-ref", type=float, default=5.0,
                     help="tilt_pz reference pz_ref (GeV/c) in f = (pz/pz_ref)^alpha.")
    ap.add_argument("--closure-hidden-dpt", action="store_true",
                     help="Hidden-variable closure (Stage-1 plan #4). Applies a "
                          "Gaussian bump to the closure pseudo-data weights "
                          "based on dpT = sim_pT - truth_pT (the reco-vs-truth "
                          "resolution), which is NOT in the OmniFold feature "
                          "set. Truth weights are LEFT UNCHANGED, so the "
                          "reference is the CV truth marginal (hTruthXSec2D). "
                          "A correctly unbiased unfold recovers the CV truth "
                          "even though the pseudo-data carries a hidden-axis "
                          "bias. Requires --closure; mutually exclusive with "
                          "--closure-reweight.")
    ap.add_argument("--closure-hidden-dpt-amplitude", type=float, default=0.3,
                     help="Hidden-dpT bump amplitude A in "
                          "f = 1 + A * exp(-((dpT - center)/sigma)^2).")
    ap.add_argument("--closure-hidden-dpt-center", type=float, default=0.1,
                     help="Hidden-dpT bump center (GeV/c).")
    ap.add_argument("--closure-hidden-dpt-sigma", type=float, default=0.05,
                     help="Hidden-dpT bump sigma (GeV/c).")
    ap.add_argument("--seed", type=int, default=None,
                     help="Master seed for the sklearn GBDT random_state. "
                          "When set, classifier1 uses --seed, classifier2 "
                          "uses --seed+1, regressor uses --seed+2 so the "
                          "three estimators are independently reproducible. "
                          "Used by the ML-stochasticity seed scan.")
    ap.add_argument("--bootstrap-seed", type=int, default=None,
                     help="Poisson-weight bootstrap replica seed. When set, "
                          "draw per-event Poisson(1) factors from "
                          "np.random.default_rng(--bootstrap-seed) and "
                          "multiply them into measured_weights and (with "
                          "--use-weights) sig['w_truth'] / sig['w_reco'] "
                          "before the OmniFold call. CV unfold corresponds "
                          "to omitting this flag. Data and MC draws are "
                          "independent (separate sub-RNGs) so data-stat and "
                          "MC-stat contribute jointly per replica.")
    ap.add_argument("--bootstrap-streams", choices=["both", "data", "mc"],
                     default="both",
                     help="Which sample(s) the Poisson(1) bootstrap fluctuates "
                          "(only with --bootstrap-seed). 'both' (default) is the "
                          "joint data+MC stat covariance; 'data' fluctuates only "
                          "the measured weights (data-statistical component); "
                          "'mc' fluctuates only sig['w_truth']/['w_reco'] "
                          "(MC-statistical component). The data and MC sub-RNGs "
                          "are independent, so C_both == C_data + C_mc up to "
                          "sampling noise -- a decomposition AND a closure check.")
    ap.add_argument("--universe", type=str, default=None, metavar="BAND:IDX",
                     help="Systematic-universe unfold. Argument is "
                          "'BAND:IDX' (e.g. 'MaCCQE:0' or 'Flux:42'). When "
                          "set, the truth/reco weight arrays are read from "
                          "w_truth_<sanitized_band>_<IDX> / "
                          "w_reco_<sanitized_band>_<IDX> instead of the CV "
                          "w_truth / w_reco. The input ROOT must have been "
                          "produced with MNV101_DUMP_UNIVERSES set in the "
                          "C++ event loop so the universe columns exist. "
                          "Sanitizer matches the C++ "
                          "SanitizeForRootBranchName rule (any non-alnum/"
                          "underscore character -> '_'). Requires "
                          "--use-weights. Incompatible with --closure (the "
                          "closure premise needs CV weights for "
                          "self-consistency) and --bootstrap-seed (per "
                          "Stage-1 UQ design, run one variance axis per "
                          "unfold so the rollup attributes each ROOT to a "
                          "single component).")
    ap.add_argument("--estimator",
                     choices=["exact", "hist", "xgb", "lgbm"],
                     default="exact",
                     help="GBDT backend. 'exact' = sklearn GradientBoosting "
                          "(single-threaded exact-split CART, original "
                          "behavior). 'hist' = sklearn HistGradientBoosting "
                          "(histogram-binned, OpenMP-parallel, typically "
                          "10-30x faster on >1M rows). 'xgb' = XGBoost "
                          "tree_method='hist'; supports GPU via --device. "
                          "'lgbm' = LightGBM leaf-wise; usually the fastest "
                          "CPU GBDT at this data shape. All four use matched "
                          "defaults: 100 trees, ~8 leaves (depth 3), lr=0.1.")
    ap.add_argument("--closure-alt-universe", type=str, default=None,
                     metavar="BAND:IDX",
                     help="Alt-model closure (Stage-1 plan #4). Argument is "
                          "'BAND:IDX' (e.g. 'MaCCQE:0', 'Rvp1pi:0'). The CV "
                          "w_truth / w_reco stay loaded so the OmniFold "
                          "response is unchanged, but the closure pseudo-data "
                          "weights are replaced by w_reco_<BAND>_<IDX> and a "
                          "matching truth reference (hTruthAlt2D / "
                          "hTruthAltXSec2D) is built using w_truth_<BAND>_<IDX>. "
                          "A correctly unbiased OmniFold should recover the "
                          "alt-model truth marginal from alt-model pseudo-data "
                          "even though the response was trained at CV. "
                          "Requires --closure --use-weights; mutually "
                          "exclusive with --universe, --closure-reweight, "
                          "--closure-hidden-dpt.")
    ap.add_argument("--device", choices=["cpu", "cuda"], default="cpu",
                     help="Compute device for xgb/lgbm backends. 'cpu' "
                          "(default) keeps everything on host. 'cuda' moves "
                          "the per-tree work to GPU (XGBoost: device='cuda'; "
                          "LightGBM: device='gpu', requires a GPU-enabled "
                          "build). For d<=2 features the host-device "
                          "transfer dominates; GPU wins at higher d. Ignored "
                          "by 'exact' and 'hist'.")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    # --closure + --bootstrap-seed: Stage-1 coverage-toy mode. The naive
    # closure invariant (step-1 reweight = 1 per event) is intentionally
    # broken: independent Poisson draws on the closure pseudo-data and the
    # MC weights model data-stat + MC-stat fluctuation. Across N toys, the
    # spread of unfolded values around the CV truth tests whether the
    # bootstrap covariance correctly covers the true truth (Stage-1 plan
    # deliverable #5). No guard; the run log records when this combo is
    # intentional.

    if args.closure_reweight and not args.closure:
        raise SystemExit(
            "[FAIL] --closure-reweight requires --closure: the reweight "
            "modifies the closure pseudo-data, which only exists in closure "
            "mode.")

    if args.closure_hidden_dpt and not args.closure:
        raise SystemExit(
            "[FAIL] --closure-hidden-dpt requires --closure: the hidden-axis "
            "bias only applies to closure pseudo-data.")
    if args.closure_hidden_dpt and args.closure_reweight:
        raise SystemExit(
            "[FAIL] --closure-hidden-dpt and --closure-reweight are mutually "
            "exclusive: each defines a different reference (CV truth vs "
            "reweighted truth). Run them as separate unfolds.")

    alt_universe_branch = None
    if args.closure_alt_universe is not None:
        if not args.closure:
            raise SystemExit(
                "[FAIL] --closure-alt-universe requires --closure: the "
                "alt-model bias only applies to closure pseudo-data.")
        if not args.use_weights:
            raise SystemExit(
                "[FAIL] --closure-alt-universe requires --use-weights: the "
                "alt-model swap is a weight substitution.")
        if args.closure_reweight or args.closure_hidden_dpt:
            raise SystemExit(
                "[FAIL] --closure-alt-universe is mutually exclusive with "
                "--closure-reweight / --closure-hidden-dpt: each defines a "
                "different reference. Run them as separate unfolds.")
        if args.universe is not None:
            raise SystemExit(
                "[FAIL] --closure-alt-universe and --universe are mutually "
                "exclusive: alt-model closure must keep the response at CV.")
        if ":" not in args.closure_alt_universe:
            raise SystemExit(
                f"[FAIL] --closure-alt-universe expects 'BAND:IDX', got "
                f"{args.closure_alt_universe!r}")
        alt_band, _, alt_idx = args.closure_alt_universe.partition(":")
        if not alt_band or not alt_idx:
            raise SystemExit(
                f"[FAIL] --closure-alt-universe expects 'BAND:IDX', got "
                f"{args.closure_alt_universe!r}")
        try:
            alt_idx_val = int(alt_idx)
        except ValueError as exc:
            raise SystemExit(
                f"[FAIL] --closure-alt-universe IDX must be int, got "
                f"{alt_idx!r}") from exc
        if alt_idx_val < 0:
            raise SystemExit(
                f"[FAIL] --closure-alt-universe IDX must be non-negative, "
                f"got {alt_idx_val}")
        alt_universe_branch = (alt_band, alt_idx_val)
        print(f"[INFO] Alt-model closure: band={alt_band!r}, idx={alt_idx_val} "
              f"-> alt pseudo-data and truth ref will use "
              f"w_*_{_sanitize_band_for_branch(alt_band)}_{alt_idx_val}; "
              f"response stays at CV.")

    universe_branch = None
    if args.universe is not None:
        if not args.use_weights:
            raise SystemExit(
                "[FAIL] --universe requires --use-weights: the CV->universe "
                "swap is a weight substitution, so there has to be a weight "
                "being read in the first place.")
        if args.closure:
            raise SystemExit(
                "[FAIL] --universe is not supported with --closure: closure "
                "uses CV MC reco weights as pseudo-data, so the closure "
                "premise (unfold recovers MC truth prior) requires CV "
                "weights everywhere.")
        if args.bootstrap_seed is not None:
            raise SystemExit(
                "[FAIL] --universe and --bootstrap-seed cannot be combined: "
                "Stage-1 UQ design runs one variance axis per unfold so each "
                "output ROOT is attributable to exactly one component "
                "(bootstrap = statistical, universe = systematic).")
        if ":" not in args.universe:
            raise SystemExit(
                f"[FAIL] --universe expects 'BAND:IDX', got {args.universe!r}")
        band_str, _, idx_str = args.universe.partition(":")
        if not band_str or not idx_str:
            raise SystemExit(
                f"[FAIL] --universe expects 'BAND:IDX', got {args.universe!r}")
        try:
            idx_val = int(idx_str)
        except ValueError as exc:
            raise SystemExit(
                f"[FAIL] --universe IDX must be an integer, got "
                f"{idx_str!r}") from exc
        if idx_val < 0:
            raise SystemExit(
                f"[FAIL] --universe IDX must be non-negative, got {idx_val}")
        universe_branch = (band_str, idx_val)
        print(f"[INFO] Universe unfold: band={band_str!r}, idx={idx_val} "
              f"-> reading w_truth_{_sanitize_band_for_branch(band_str)}_{idx_val} "
              f"and w_reco_{_sanitize_band_for_branch(band_str)}_{idx_val}")

    pt_edges = PT_EDGES
    pz_edges = PZ_EDGES
    pt_lo, pt_hi = pt_edges[0], pt_edges[-1]
    pz_lo, pz_hi = pz_edges[0], pz_edges[-1]
    print(f"[INFO] p_T range: [{pt_lo}, {pt_hi}] GeV/c ({len(pt_edges)-1} bins)")
    print(f"[INFO] p_|| range: [{pz_lo}, {pz_hi}] GeV/c ({len(pz_edges)-1} bins)")

    # --- Open input file ---
    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")

    t_sig = f_in.Get("mc_signal_reco")
    t_bkg = f_in.Get("mc_background")
    t_data = f_in.Get("data")
    t_truth_denom = f_in.Get("mc_truth_denom")
    if not t_sig or not t_bkg or not t_data:
        raise RuntimeError("Missing required TTrees")
    if not t_truth_denom and not args.closure:
        raise RuntimeError(
            "mc_truth_denom missing — required for the canonical efficiency "
            "denominator. Re-run runEventLoopOmniFold to produce it, or pass "
            "--closure for the legacy mc_signal_reco-only behaviour.")

    # Verify p_|| branches exist
    for tree, bname in [(t_sig, "sim_pz"), (t_sig, "MC_pz"),
                         (t_bkg, "sim_background_pz"), (t_data, "measured_pz")]:
        if not tree.GetListOfBranches().FindObject(bname):
            raise RuntimeError(
                f"Branch '{bname}' not found in TTree '{tree.GetName()}'. "
                "Re-run runEventLoopOmniFold with the updated C++ code that writes p_|| branches.")

    data_pot, mc_pot, pot_scale = get_pot_scales(f_in)
    print(f"[INFO] POT: data={data_pot:.4g}, mc={mc_pot:.4g}, scale={pot_scale:.6g}")

    # Phase 17 (2026-05): event loop now appends truth-only miss entries
    # (events with no AnaTuple reco-tree counterpart) to mc_signal_reco so
    # OmniFold's step-2 miss regression handles the previously
    # missing-from-input fraction natively. When that mode is on, the
    # input-completeness (c) correction below should be ≈ 1 per bin and the
    # division by c becomes a no-op. Older inputs without the flag still
    # get corrected by c (legacy path).
    p_has_misses = f_in.Get("hasTruthOnlyMisses")
    p_n_misses = f_in.Get("nTruthOnlyMisses")
    has_truth_only_misses = bool(int(p_has_misses.GetVal())) if p_has_misses else False
    n_truth_only_misses = int(p_n_misses.GetVal()) if p_n_misses else 0
    if has_truth_only_misses:
        print(f"[INFO] Phase-17 mode: mc_signal_reco contains "
              f"{n_truth_only_misses} truth-only miss entries — "
              f"c correction expected ≈ 1.")
    else:
        print("[INFO] Pre-Phase-17 input (no truth-only miss entries); "
              "c correction will scale up to full truth.")

    # Fiducial nucleons: do not trust the merged TParameter<double> because
    # hadd sums it across playlists. Use the known tracker geometry constant.
    nuc_par = f_in.Get("pTmu_fiducial_nucleons")
    n_nucleons = TRACKER_FIDUCIAL_N_NUCLEONS
    if nuc_par:
        file_nucleons = float(nuc_par.GetVal())
        print(f"[INFO] Fiducial nucleons (file metadata)  = {file_nucleons:.16e}")
        if not np.isclose(file_nucleons, n_nucleons, rtol=0.0, atol=0.0):
            print("[WARN] Ignoring merge-sensitive pTmu_fiducial_nucleons metadata; "
                  "using the tracker geometry constant instead.")
    print(f"[INFO] Fiducial nucleons (geometry)      = {n_nucleons:.16e}")

    # Load flux histogram from binned MC file. MINERvA flux histograms are
    # stored in units of m^-2/POT (per p_T bin); ExtractCrossSection.cpp:127
    # applies a 1e4 factor to convert to cm^-2 at the end of normalization.
    flux_bins, hFlux_pt = load_flux_bins(args.mcfile, args.flux_hist, pt_edges)
    flux_source = f"{args.mcfile}:{args.flux_hist}"
    # Flux systematic universes must divide by their *own* integrated flux
    # Phi_u, not the CV flux (Task #70: the 1/Phi normalization is the
    # dominant flux uncertainty). For non-Flux universes and the CV, Phi is
    # unchanged.
    if universe_branch is not None and universe_branch[0] == "Flux":
        phi_u = load_flux_universe_bins(
            args.flux_universe_file, universe_branch[1], pt_edges, flux_bins)
        ratio = flux_bins / phi_u
        flux_bins = phi_u
        hFlux_pt = make_flux_hist("hFlux_pt", pt_edges, flux_bins)
        flux_source = f"{args.flux_universe_file}:hFluxUniv[idx={universe_branch[1]}]"
        print(f"[INFO] Flux universe {universe_branch[1]}: dividing by per-universe "
              f"flux integral (Phi_CV/Phi_u per pT = "
              f"{np.array2string(ratio, precision=4)})")
    # Keep integrated flux in both native m^-2/POT units and correctly-converted
    # cm^-2/POT units for metadata reporting.
    flux_total_m2 = float(np.sum(flux_bins))
    flux_total_cm2 = flux_total_m2 / 1.0e4
    print(f"[INFO] Flux source: {flux_source}")
    print(f"[INFO] Flux bins (m^-2/POT): {flux_bins}")
    print(f"[INFO] Flux sum = {flux_total_m2:.4g} m^-2/POT "
          f"= {flux_total_cm2:.4g} cm^-2/POT")

    # --- Read data and MC ---
    hDataReco2D = make_th2d("hDataReco2D", "Data reco", pt_edges, pz_edges)
    hBkgReco2D = make_th2d("hBkgReco2D", "Background reco (POT-scaled)", pt_edges, pz_edges)

    meas_pt, meas_pz = fill_data_reco_2d(
        t_data, hDataReco2D, pt_lo, pt_hi, pz_lo, pz_hi, verbose=args.verbose)
    # KNOWN_ISSUES #13: vary the genuine background per systematic universe
    # (weight + lateral kinematics). universe_branch=None (CV/non-universe) keeps
    # the pre-#13 CV behaviour byte-identical. Both the purity down-weight (via
    # hBkgReco2D) and the negweight injection (via the returned arrays) then track
    # the per-universe background.
    bkg_reco_pt, bkg_reco_pz, bkg_reco_w = fill_bkg_reco_2d(
        t_bkg, hBkgReco2D, pot_scale, pt_lo=pt_lo, pt_hi=pt_hi,
        pz_lo=pz_lo, pz_hi=pz_hi, verbose=args.verbose,
        universe_branch=universe_branch)

    # --- Read signal MC arrays ---
    sig = collect_signal_arrays_2d(t_sig, pt_lo, pt_hi, pz_lo, pz_hi,
                                    pot_scale, use_weights=args.use_weights,
                                    verbose=args.verbose,
                                    universe_branch=universe_branch,
                                    alt_universe_branch=alt_universe_branch)
    if sig["truth_pt"].size == 0:
        raise RuntimeError("No signal events for OmniFold")
    if meas_pt.size == 0:
        raise RuntimeError("No measured data entries")

    # --- Read canonical truth denominator for efficiency ---
    # Skipped in --closure mode: the synthetic data lives in the
    # mc_signal_reco subset, so closure must use the same subset for
    # hEffDen to be self-consistent (truth_denom=None falls back to the
    # mc_signal_reco truth-pass subset inside compute_efficiency_2d).
    truth_denom = None
    if not args.closure and t_truth_denom is not None:
        truth_denom = collect_truth_denom_arrays(
            t_truth_denom, pt_lo, pt_hi, pz_lo, pz_hi,
            pot_scale, use_weights=args.use_weights, verbose=args.verbose,
            universe_branch=universe_branch)
        print(f"[INFO] truth_denom events kept (in binning): "
              f"{truth_denom['truth_pt'].size}")
        print(f"[INFO]   sum(w_truth) = {truth_denom['w_truth'].sum():.6g}")

    # Signal fakes: MC signal-truth events with reco inside the binning but
    # truth outside the measurement phase space. These are present in measured
    # data at reco level. Vintage note (2026-07-03 audit): since Phase 18
    # (d1bc881, 2026-05-18) the C++ puts out-of-PS signal directly into the
    # mc_background tree AND gates mc_signal_reco on truth-in-PS, so on every
    # post-Phase-18 omnifile is_fake below selects nothing (n_fakes = 0) and
    # this block is a structural no-op — the tree already carries the fakes
    # and they are subtracted exactly once. The block is kept for pre-Phase-18
    # omnifiles, whose mc_background lacked fakes: there, without this extra
    # subtraction, measured would contain fakes while MC reco would not,
    # inducing a reco-level mismatch that the step-1 classifier absorbs as a
    # spurious reweight. Fakes are background by paper convention; their
    # POT-scaled reco weights go into hBkgReco2D before the data-bkg
    # subtraction. See nd-unfolding/ND_OMNIFOLD_RUN_LOG.md (2026-07-03).
    is_fake = sig["pass_reco"] & (~sig["pass_truth"])
    n_fakes = int(is_fake.sum())
    # Kept for the negweight background mode: signal fakes are background by
    # paper convention and must be injected on the measured side alongside the
    # mc_background events (empty on post-Phase-18 omnifiles, where n_fakes=0).
    fake_pt = sig["reco_pt"][is_fake]
    fake_pz = sig["reco_pz"][is_fake]
    fake_wr = sig["w_reco"][is_fake]  # already POT-scaled in collect_signal_arrays_2d
    if n_fakes:
        fake_sum = 0.0
        for pt, pz, w in zip(fake_pt, fake_pz, fake_wr):
            hBkgReco2D.Fill(float(pt), float(pz), float(w))
            fake_sum += float(w)
        if args.verbose:
            print(f"[INFO] signal fakes added to bkg: n={n_fakes}, "
                  f"sum(w_reco)={fake_sum:.6g}")

    # Background subtraction (bkg now includes real backgrounds + signal fakes)
    hMeasSub2D = hDataReco2D.Clone("hMeasSub2D")
    hMeasSub2D.SetTitle("Measured (data - bkg)")
    hMeasSub2D.Add(hBkgReco2D, -1.0)
    measured_weights, hMeasTrain2D = build_measured_training_2d(
        meas_pt, meas_pz, hDataReco2D, hBkgReco2D, verbose=args.verbose)
    nneg_meas = count_negative_bins_2d(hMeasSub2D)

    print(f"[INFO] Data reco entries: {len(meas_pt)}")
    print(f"[INFO] hDataReco2D integral: {hDataReco2D.Integral():.6g}")
    print(f"[INFO] hBkgReco2D integral (incl. fakes): {hBkgReco2D.Integral():.6g}")
    print(f"[INFO] hMeasSub2D integral: {hMeasSub2D.Integral():.6g}")
    print(f"[INFO] hMeasTrain2D integral: {hMeasTrain2D.Integral():.6g}")
    if nneg_meas:
        print(f"[INFO] hMeasSub2D negative bins (floored in training target): {nneg_meas}")

    # --- Background-subtraction mode selection (advisor 2026-07-07) ---
    # purity            : per-reco-bin max(0,(N_data-N_bkg)/N_data) down-weight of
    #                     the data (the binned default; measured_weights above).
    # negweight         : unbinned negative-weight injection — append the
    #                     background-MC (+ signal-fake) reco events to the
    #                     MEASURED side with weight -w_bkg*pot_scale, data at +1.
    #                     The step-1 classifier then targets (D-B)/S continuously
    #                     (see 2d-unfolding/HANDOFF_bkg_negweight/). The learned
    #                     reweight p/(1-p) is structurally >=0, the unbinned
    #                     analogue of the max(0,.) floor.
    # negweight-refined : Stay Positive (arXiv:2505.03724) — refine the signed
    #                     measured sample to a positive-weight equivalent
    #                     (w~=|w|*(2g-1), g the D/(D+B) classifier) before
    #                     training, so step-1 is well-posed where B>D locally.
    # The actual injection / refinement is deferred to AFTER the closure and
    # bootstrap blocks (below), so that (a) the data-statistical Poisson(1)
    # bootstrap fluctuates only the data / pseudo-data side and never the
    # injected background-MC, and (b) negweight composes with closure. Here we
    # only PREPARE the injected-background arrays and set the data-side weights.
    inj_pt = inj_pz = inj_w = None
    if args.bkg_mode in ("negweight", "negweight-refined"):
        # Injected background = genuine bkg (bkg_reco_*, fiducial-filtered by
        # fill_bkg_reco_2d) + signal fakes (fake_* from collect_signal_arrays_2d,
        # re-filtered to the reco window). This is byte-for-byte the composition
        # of hBkgReco2D that the purity down-weight uses, so purity and negweight
        # target the SAME rho1 = D - B per universe. In a systematic universe
        # BOTH terms vary identically in the two modes: the genuine background via
        # the KNOWN_ISSUES #13 wiring in fill_bkg_reco_2d (w_bkg_<band>_<idx> +
        # lateral sim_background_<band>_<idx>, when those branches exist) and the
        # fakes via the universe-aware collect_signal_arrays_2d. So the negweight
        # systematics covariance matches purity's by construction, now INCLUDING
        # background-modeling variation (no universe silently frozen at CV).
        fpt = np.asarray(fake_pt, dtype=float)
        fpz = np.asarray(fake_pz, dtype=float)
        fw = np.asarray(fake_wr, dtype=float)
        fmask = ((fpt >= pt_lo) & (fpt <= pt_hi) &
                 (fpz >= pz_lo) & (fpz <= pz_hi))
        inj_pt = np.concatenate([bkg_reco_pt, fpt[fmask]])
        inj_pz = np.concatenate([bkg_reco_pz, fpz[fmask]])
        inj_w = np.concatenate([bkg_reco_w, fw[fmask]])
        # Data side carries +1 (the negweight construction); the binned purity
        # per-reco-bin down-weight is NOT applied. Overrides the purity
        # measured_weights built above (kept only for the diagnostic hists).
        # In --closure the data-side weights are set inside the closure block.
        if not args.closure:
            measured_weights = np.ones(meas_pt.shape[0], dtype=float)
        print(f"[INFO] bkg-mode={args.bkg_mode}: prepared {inj_pt.shape[0]} "
              f"injected background reco events (bkg-MC {bkg_reco_pt.shape[0]} + "
              f"fakes {int(fmask.sum())}); data side weight +1 "
              f"(injection deferred to after closure/bootstrap).")
    else:
        print("[INFO] bkg-mode=purity: binned per-reco-bin purity down-weight "
              "(default, headline path).")

    # --- Closure mode: replace measured arrays with MC reco pseudo-data ---
    # For a closure test, we substitute the `measured` input to OmniFold with
    # the MC reco events (where pass_reco is True). Since the pseudo-data and
    # the MCreco training sample come from the same MC, step1 should weight
    # to ~1 per event, and step2 should recover the MC truth prior within GBT
    # approximation noise. Tests normalization, fills, and phase-space
    # handling end-to-end without being confounded by data/MC mismodeling.
    if args.closure:
        print("[INFO] *** CLOSURE MODE: using MC reco as pseudo-data ***")
        # Restrict pseudo-data to truth-in-PS + reco-passing events. Excluding
        # fakes (pass_reco & ~pass_truth) matches what OmniFold unfolds against
        # (omnifold.py drops ~pass_truth events before training), so closure is
        # self-consistent.
        closure_mask = sig["pass_reco"] & sig["pass_truth"]
        meas_pt = sig["reco_pt"][closure_mask].copy()
        meas_pz = sig["reco_pz"][closure_mask].copy()
        # Measured weights must be on the same footing as MCreco_weights for the
        # step-1 classifier to learn ~identity. With --use-weights, MCreco is
        # passed as sig["w_reco"]; closure measured_weights must mirror that on
        # the same event subset. Unit weights here would induce a bias scaling
        # with the spread of w_reco.
        if args.use_weights:
            measured_weights = sig["w_reco"][closure_mask].copy()
        else:
            measured_weights = np.ones(meas_pt.shape[0], dtype=float)
        # Truth-reweight closure: apply f(pT_truth, pz_truth) to pseudo-data on
        # the truth kinematics of each reco-pass event. The matching
        # reweighted-truth reference is built below alongside hTruth2D.
        if args.closure_reweight:
            rw_data = closure_reweight_factor(
                args.closure_reweight,
                sig["truth_pt"][closure_mask],
                sig["truth_pz"][closure_mask],
                amplitude=args.closure_reweight_amplitude,
                sigma=args.closure_reweight_sigma,
                pt0=args.closure_reweight_pt0,
                alpha=args.closure_reweight_alpha,
                pz_ref=args.closure_reweight_pz_ref)
            measured_weights = measured_weights * rw_data
            print(f"[INFO] Closure reweight '{args.closure_reweight}': "
                  f"data factor mean={rw_data.mean():.4f}, "
                  f"range=({rw_data.min():.4f}, {rw_data.max():.4f})")
        if args.closure_hidden_dpt:
            # Hidden-variable closure: bump data weights on dpT = sim_pT -
            # truth_pT, which OmniFold does NOT see. Truth side is left at CV
            # so the reference stays the CV truth marginal.
            dpT = (sig["reco_pt"][closure_mask]
                   - sig["truth_pt"][closure_mask])
            amp = args.closure_hidden_dpt_amplitude
            ctr = args.closure_hidden_dpt_center
            sg = args.closure_hidden_dpt_sigma
            rw_hidden = 1.0 + amp * np.exp(-((dpT - ctr) / sg) ** 2)
            measured_weights = measured_weights * rw_hidden
            print(f"[INFO] Closure hidden-dpT bump: A={amp}, "
                  f"center={ctr} GeV/c, sigma={sg} GeV/c, "
                  f"mean factor={rw_hidden.mean():.4f}, "
                  f"max={rw_hidden.max():.4f}")
        if alt_universe_branch is not None:
            # Alt-model closure: replace closure pseudo-data weights with the
            # alt-model w_reco values. CV w_reco/w_truth stay in sig so the
            # response training is unchanged. The matching alt-truth reference
            # (hTruthAlt2D / hTruthAltXSec2D) is built below.
            measured_weights = sig["w_reco_alt"][closure_mask].copy()
            ratio = (sig["w_reco_alt"][closure_mask].sum()
                     / max(sig["w_reco"][closure_mask].sum(), 1e-30))
            print(f"[INFO] Alt-model closure: replaced pseudo-data weights "
                  f"with w_reco_alt; sum(alt)/sum(CV) = {ratio:.4f}")
        if args.bkg_mode in ("negweight", "negweight-refined"):
            # negweight closure: pseudo-data = sim reco (signal) + injected
            # background CONTAMINATION at +inj_w. The mode's subtraction
            # (-inj_w for negweight, or the Stay-Positive refinement) is applied
            # after the bootstrap block below and removes it, so a correct
            # unfold recovers the CV truth prior. This exercises the full signed-
            # weight subtraction plumbing (sign, POT scale, fiducial filter,
            # concatenation) end-to-end, unlike purity closure which uses the
            # signal reco directly.
            meas_pt = np.concatenate([meas_pt, inj_pt])
            meas_pz = np.concatenate([meas_pz, inj_pz])
            measured_weights = np.concatenate([measured_weights, inj_w])
            print(f"[INFO] negweight closure: added {inj_pt.shape[0]} background "
                  f"contamination events at +w to the pseudo-data "
                  f"(sum(+w)={inj_w.sum():.6g}); the mode subtraction removes it.")
        hDataReco2D.Reset("ICES")
        hBkgReco2D.Reset("ICES")
        for pt, pz, w in zip(meas_pt, meas_pz, measured_weights):
            hDataReco2D.Fill(float(pt), float(pz), float(w))
        hMeasSub2D = hDataReco2D.Clone("hMeasSub2D")
        hMeasSub2D.SetTitle("Pseudo-data (MC reco, closure test)")
        hMeasTrain2D = hDataReco2D.Clone("hMeasTrain2D")
        hMeasTrain2D.SetTitle("Pseudo-data (training, closure test)")
        print(f"[INFO] Closure pseudo-data entries: {meas_pt.size}, "
              f"sum(w)={float(measured_weights.sum()):.6g}")
        print(f"[INFO] hDataReco2D (closure) integral: {hDataReco2D.Integral():.6g}")

    # --- Poisson(1) bootstrap weights (Stage-1 statistical uncertainty) ---
    # Draws independent per-event Poisson(1) multipliers on data and MC, so
    # data-stat and MC-stat contribute jointly per replica (Practical Guide
    # 2507.09582 §5.1). Reseeded via np.random.default_rng so replicas are
    # reproducible. CV result is the unweighted unfold (flag omitted).
    if args.bootstrap_seed is not None:
        rng_data = np.random.default_rng(args.bootstrap_seed)
        rng_mc = np.random.default_rng(args.bootstrap_seed + 10_000_000)
        do_data = args.bootstrap_streams in ("both", "data")
        do_mc = args.bootstrap_streams in ("both", "mc")
        # Draw both sub-RNGs unconditionally (keeps the data/mc streams seed-
        # aligned across modes), then apply only the requested stream(s). With
        # independent streams, Cov(both) = Cov(data-only) + Cov(mc-only).
        b_data = rng_data.poisson(1.0, size=measured_weights.shape[0]).astype(float)
        b_truth = rng_mc.poisson(1.0, size=sig["w_truth"].shape[0]).astype(float)
        if do_data:
            measured_weights = measured_weights * b_data
        if do_mc:
            # Reco weights ride the truth draw so that a single MC event is
            # consistently up/down-weighted at both reco and truth level
            # (omnifold.py treats sig["w_truth"] and sig["w_reco"] as the same
            # event row).
            sig["w_truth"] = sig["w_truth"] * b_truth
            sig["w_reco"] = sig["w_reco"] * b_truth
        print(f"[INFO] Poisson bootstrap: seed={args.bootstrap_seed}, "
              f"streams={args.bootstrap_streams}, "
              f"data factor sum={b_data.sum():.6g} (n={b_data.size}, "
              f"{'APPLIED' if do_data else 'held'}), "
              f"mc factor sum={b_truth.sum():.6g} (n={b_truth.size}, "
              f"{'APPLIED' if do_mc else 'held'})")

    # --- Apply the background subtraction on the measured (class-1) side ---
    # Deferred to HERE (after closure + the data-statistical bootstrap) so:
    #  (a) the Poisson(1) DATA bootstrap fluctuated only the +1 data (or, in
    #      closure, the pseudo-data signal + injected contamination) events and
    #      NEVER the injected background subtraction, which carries independent
    #      MC statistics and a fixed POT-scaled weight -- exactly matching the
    #      purity path, where hBkgReco2D is fixed and only the data counts
    #      fluctuate. The genuine background-MC statistical uncertainty is
    #      intentionally NOT bootstrapped in either mode (out of scope here;
    #      would need its own Poisson stream over the mc_background events --
    #      see 2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md);
    #  (b) negweight composes with closure (the +bkg contamination was added to
    #      the pseudo-data above; here we append the matching -bkg subtraction).
    if args.bkg_mode == "negweight":
        n_data = meas_pt.shape[0]
        meas_pt = np.concatenate([meas_pt, inj_pt])
        meas_pz = np.concatenate([meas_pz, inj_pz])
        measured_weights = np.concatenate([measured_weights, -inj_w])
        print(f"[INFO] bkg-mode=negweight: injected {inj_pt.shape[0]} background "
              f"reco events at -w; data side {n_data} events. Effective measured "
              f"sum={measured_weights.sum():.6g} (cf hMeasSub2D integral "
              f"{hMeasSub2D.Integral():.6g}). Step-1 p/(1-p) >= 0 floors the "
              f"reweight structurally.")
    elif args.bkg_mode == "negweight-refined":
        n_data = meas_pt.shape[0]
        sgn_pt = np.concatenate([meas_pt, inj_pt])
        sgn_pz = np.concatenate([meas_pz, inj_pz])
        sgn_w = np.concatenate([measured_weights, -inj_w])
        refine_params = ({"random_state": int(args.seed) + 3}
                         if args.seed is not None else None)
        w_ref, _g_ev, frac_clip = refine_stay_positive(
            np.column_stack([sgn_pt, sgn_pz]), sgn_w,
            estimator=args.estimator, device=args.device,
            params=refine_params, verbose=True)
        meas_pt, meas_pz, measured_weights = sgn_pt, sgn_pz, w_ref
        print(f"[INFO] bkg-mode=negweight-refined (Stay Positive, "
              f"arXiv:2505.03724): refined {sgn_w.shape[0]} signed events "
              f"({n_data} data + {inj_pt.shape[0]} bkg) to NON-NEGATIVE weights; "
              f"clipped frac={frac_clip:.4f}; effective measured sum="
              f"{measured_weights.sum():.6g} (cf hMeasSub2D integral "
              f"{hMeasSub2D.Integral():.6g}).")

    # --- Run 2D OmniFold via direct Python helper call ---
    # NB: we bypass ROOT.RooUnfoldOmnifold().UnbinnedOmnifold() because its
    # DataFrame_to_python path (RooUnfoldOmnifold.cxx:216-249) column-order
    # handling is unreliable for multi-column RDataFrames, which produced a
    # 6.3x inflation of hUnfold2D on the first 2D run. The direct call with
    # explicit numpy arrays gives the correct step2 normalization. See
    # 2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md for the debug narrative.
    import sys
    _OF_PY = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python"
    if _OF_PY not in sys.path:
        sys.path.insert(0, _OF_PY)
    from omnifold import OmniFold_helper_functions as ohf

    print(f"[INFO] Running 2D OmniFold with {args.iters} iterations...")
    print(f"[INFO] MC events: {sig['truth_pt'].shape[0]}, "
          f"pass_truth: {sig['pass_truth'].sum()}, pass_reco: {sig['pass_reco'].sum()}")
    print(f"[INFO] Measured events: {meas_pt.shape[0]}, "
          f"effective training sum={measured_weights.sum():.6g}")

    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"]])
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"]])
    measured = np.column_stack([meas_pt, meas_pz])

    # ML-stochasticity seed scan: --seed pins sklearn GBDT random_state on
    # all three estimators (step1 classifier, step2 classifier, step1 miss
    # regressor) so each trial is independently reproducible. With None
    # (default), sklearn falls back to np.random's global state and natural
    # cross-process variation drives the spread.
    if args.seed is not None:
        c1_params = {"random_state": int(args.seed)}
        c2_params = {"random_state": int(args.seed) + 1}
        rg_params = {"random_state": int(args.seed) + 2}
        print(f"[INFO] Pinned GBDT seeds: step1={c1_params['random_state']}, "
              f"step2={c2_params['random_state']}, "
              f"regressor={rg_params['random_state']}")
    else:
        c1_params = c2_params = rg_params = None

    print(f"[INFO] GBDT estimator: {args.estimator} (device={args.device})")
    step1_weights, step2_weights = ohf.omnifold(
        MCgen, MCreco, measured,
        sig["pass_reco"], sig["pass_truth"],
        np.ones(meas_pt.shape[0], dtype=bool),
        int(args.iters),
        MCgen_weights=sig["w_truth"] if args.use_weights else None,
        MCreco_weights=sig["w_reco"] if args.use_weights else None,
        measured_weights=measured_weights,
        classifier1_params=c1_params,
        classifier2_params=c2_params,
        regressor_params=rg_params,
        parameter_format="dict",
        estimator=args.estimator,
        device=args.device,
    )
    print(f"[INFO] OmniFold complete. step1 weights: {step1_weights.shape[0]}, "
          f"step2 weights: {step2_weights.shape[0]}")
    print(f"[INFO] step2 sum={step2_weights.sum():.4g}, "
          f"mean={step2_weights.mean():.4f}, "
          f"min={step2_weights.min():.4f}, max={step2_weights.max():.4f}")

    # --- Fill unfolded histograms ---
    # The weights apply to MC events that pass truth (pass_truth mask was applied
    # internally by OmniFold before training)
    truth_pt_in = sig["truth_pt"][sig["pass_truth"]]
    truth_pz_in = sig["truth_pz"][sig["pass_truth"]]
    truth_w_in = sig["w_truth"][sig["pass_truth"]]

    if truth_pt_in.shape[0] != step2_weights.shape[0]:
        raise RuntimeError(
            f"Weight size mismatch: truth={truth_pt_in.shape[0]}, "
            f"step2={step2_weights.shape[0]}")

    # MC truth prior (original weights)
    hTruth2D = make_th2d("hTruth2D", "MC truth prior", pt_edges, pz_edges)
    for pt, pz, w in zip(truth_pt_in, truth_pz_in, truth_w_in):
        hTruth2D.Fill(float(pt), float(pz), float(w))

    # Truth-reweight closure reference: same reweight applied to truth events
    # as was applied to the pseudo-data above (on identical kinematics, so a
    # perfect unfold maps the reco shift back into this reweighted truth).
    hTruthRew2D = None
    if args.closure_reweight:
        rw_truth = closure_reweight_factor(
            args.closure_reweight, truth_pt_in, truth_pz_in,
            amplitude=args.closure_reweight_amplitude,
            sigma=args.closure_reweight_sigma,
            pt0=args.closure_reweight_pt0,
            alpha=args.closure_reweight_alpha,
            pz_ref=args.closure_reweight_pz_ref)
        hTruthRew2D = make_th2d(
            "hTruthRew2D",
            f"Reweighted MC truth (closure ref, {args.closure_reweight})",
            pt_edges, pz_edges)
        for pt, pz, w, f in zip(truth_pt_in, truth_pz_in, truth_w_in, rw_truth):
            hTruthRew2D.Fill(float(pt), float(pz), float(w) * float(f))
        print(f"[CHECK] hTruthRew2D integral: {hTruthRew2D.Integral():.6g}")

    # Alt-model closure reference: fill truth marginal with alt-model truth
    # weights (response stays at CV via truth_w_in for hTruth2D / hUnfold2D
    # normalization, but the closure reference is built explicitly here).
    hTruthAlt2D = None
    hTruthInAccept2D = None
    hTruthAltInAccept2D = None
    hTruthAltExtrapolated2D = None
    if alt_universe_branch is not None:
        truth_w_alt_in = sig["w_truth_alt"][sig["pass_truth"]]
        hTruthAlt2D = make_th2d(
            "hTruthAlt2D",
            f"Alt-model MC truth (full sample, "
            f"{args.closure_alt_universe})",
            pt_edges, pz_edges)
        for pt, pz, w in zip(truth_pt_in, truth_pz_in, truth_w_alt_in):
            hTruthAlt2D.Fill(float(pt), float(pz), float(w))
        print(f"[CHECK] hTruthAlt2D integral: {hTruthAlt2D.Integral():.6g}")

        # In-acceptance references: restrict to events that pass_reco. These
        # are what OmniFold can actually see and propagate to truth. The
        # ratio (alt-in-accept / CV-in-accept) per bin is the step-2 weight
        # OmniFold recovers, so the "extrapolated" alt-truth target is
        # hTruth2D[bin] x (alt-in-accept / CV-in-accept)[bin]. THAT is what
        # the unfold should reproduce, not the full alt-truth marginal.
        accept_mask = sig["pass_truth"] & sig["pass_reco"]
        ta_pt = sig["truth_pt"][accept_mask]
        ta_pz = sig["truth_pz"][accept_mask]
        ta_w_cv = sig["w_truth"][accept_mask]
        ta_w_alt = sig["w_truth_alt"][accept_mask]
        hTruthInAccept2D = make_th2d(
            "hTruthInAccept2D",
            "CV truth restricted to pass_reco (alt-model closure aux)",
            pt_edges, pz_edges)
        hTruthAltInAccept2D = make_th2d(
            "hTruthAltInAccept2D",
            f"Alt-model truth restricted to pass_reco "
            f"({args.closure_alt_universe})",
            pt_edges, pz_edges)
        for pt, pz, w in zip(ta_pt, ta_pz, ta_w_cv):
            hTruthInAccept2D.Fill(float(pt), float(pz), float(w))
        for pt, pz, w in zip(ta_pt, ta_pz, ta_w_alt):
            hTruthAltInAccept2D.Fill(float(pt), float(pz), float(w))
        print(f"[CHECK] hTruthInAccept2D    integral: "
              f"{hTruthInAccept2D.Integral():.6g}")
        print(f"[CHECK] hTruthAltInAccept2D integral: "
              f"{hTruthAltInAccept2D.Integral():.6g}")

        # Extrapolated alt-truth target: per-bin scale of CV truth by the
        # in-acceptance alt/CV ratio. Bins with zero in-acceptance CV are
        # filled with CV truth (no information from data, OmniFold reverts
        # to prior). This is what the unfold is mathematically capable of
        # recovering, so it is the right alt-model closure target.
        hTruthAltExtrapolated2D = hTruth2D.Clone("hTruthAltExtrapolated2D")
        hTruthAltExtrapolated2D.SetTitle(
            f"Alt-model truth target for OmniFold closure "
            f"(in-accept extrapolation, {args.closure_alt_universe})")
        for ix in range(1, hTruthAltExtrapolated2D.GetNbinsX() + 1):
            for iy in range(1, hTruthAltExtrapolated2D.GetNbinsY() + 1):
                cv_in = hTruthInAccept2D.GetBinContent(ix, iy)
                alt_in = hTruthAltInAccept2D.GetBinContent(ix, iy)
                cv_truth = hTruth2D.GetBinContent(ix, iy)
                if cv_in > 0:
                    hTruthAltExtrapolated2D.SetBinContent(
                        ix, iy, cv_truth * alt_in / cv_in)
                else:
                    hTruthAltExtrapolated2D.SetBinContent(ix, iy, cv_truth)
        print(f"[CHECK] hTruthAltExtrapolated2D integral: "
              f"{hTruthAltExtrapolated2D.Integral():.6g}")

    # OmniFold unfolded: step2 returns a truth-side density ratio. Convert it
    # back to event-count units by multiplying by the original truth weights.
    hUnfold2D = make_th2d("hUnfold2D", "Unfolded (2D OmniFold)", pt_edges, pz_edges)
    for pt, pz, ratio, wt in zip(truth_pt_in, truth_pz_in, step2_weights, truth_w_in):
        hUnfold2D.Fill(float(pt), float(pz), float(ratio) * float(wt))

    print(f"[CHECK] hTruth2D integral: {hTruth2D.Integral():.6g}")
    print(f"[CHECK] hUnfold2D integral: {hUnfold2D.Integral():.6g}")
    print(f"[CHECK] hMeasSub2D integral: {hMeasSub2D.Integral():.6g}")
    print(f"[CHECK] hMeasTrain2D integral: {hMeasTrain2D.Integral():.6g}")

    # --- Compute efficiency and completeness ---
    # hEff2D = absolute selection efficiency (sim_pass / full truth) — diagnostic only.
    # hCompleteness = OmniFold input completeness (input truth / full truth) — used
    # to convert hUnfold2D (over the OmniFold-input subset) to the full truth phase
    # space at cross-section extraction.
    hEff2D, hEffNum, hEffDen = compute_efficiency_2d(
        sig, pt_edges, pz_edges, truth_denom=truth_denom)
    eff_source = ("mc_truth_denom (canonical Truth-tree denominator)"
                  if truth_denom is not None
                  else "mc_signal_reco truth-pass subset (closure / fallback)")
    print(f"[INFO] hEffDen source: {eff_source}")
    print(f"[CHECK] hEffNum integral: {hEffNum.Integral():.6g}")
    print(f"[CHECK] hEffDen integral: {hEffDen.Integral():.6g}")

    if truth_denom is not None:
        hCompleteness2D, hOFInputTruth2D, hOFTruthDenom2D = \
            compute_omnifold_completeness_2d(
                sig, pt_edges, pz_edges, truth_denom)
        print(f"[CHECK] hOFInputTruth2D integral: {hOFInputTruth2D.Integral():.6g}")
        print(f"[CHECK] hOFTruthDenom2D integral: {hOFTruthDenom2D.Integral():.6g}")
        try:
            c_global = (hOFInputTruth2D.Integral() / hOFTruthDenom2D.Integral())
            print(f"[CHECK] global completeness c = {c_global:.4f} "
                  f"(expected ≈ N(mc_signal_reco truth-pass) / "
                  f"N(mc_truth_denom))")
            if has_truth_only_misses and abs(c_global - 1.0) > 0.005:
                print(f"[WARN] hasTruthOnlyMisses=1 but c_global deviates from 1 "
                      f"by {abs(c_global - 1.0)*100:.2f}% — check event-ID matching "
                      f"in runEventLoopOmniFold.cpp Phase-17 path and that the "
                      f"Python truth-pass gate (in_truth_phase_space) matches "
                      f"CCInclusive2DPhaseSpace.")
        except ZeroDivisionError:
            pass
    else:
        # Closure / fallback: completeness ≡ 1 (no scale-up), preserving
        # the legacy in-sample closure behaviour. The synthetic data lives
        # in the same subset as the training, so no completeness correction
        # is appropriate.
        hCompleteness2D = make_th2d("hOFCompleteness2D",
                                     "Completeness ≡ 1 (closure / fallback)",
                                     pt_edges, pz_edges)
        for ix in range(1, hCompleteness2D.GetNbinsX() + 1):
            for iy in range(1, hCompleteness2D.GetNbinsY() + 1):
                hCompleteness2D.SetBinContent(ix, iy, 1.0)
        hOFInputTruth2D = hCompleteness2D.Clone("hOFInputTruth2D")
        hOFTruthDenom2D = hCompleteness2D.Clone("hOFTruthDenom2D")
        print("[INFO] Closure/fallback: completeness set to 1.0 in all bins.")

    hXSec2D = extract_cross_section_2d(
        hUnfold2D, hCompleteness2D, flux_bins,
        data_pot, n_nucleons, pt_edges, pz_edges)

    # Closure reference xsec: push hTruthRew2D through the same normalization
    # machinery so it lives in the same units as hXSec2D.
    hTruthRewXSec2D = None
    if hTruthRew2D is not None:
        hTruthRewXSec2D = extract_cross_section_2d(
            hTruthRew2D, hCompleteness2D, flux_bins,
            data_pot, n_nucleons, pt_edges, pz_edges)
        hTruthRewXSec2D.SetName("hTruthRewXSec2D")
        hTruthRewXSec2D.SetTitle(
            f"Closure reference xsec ({args.closure_reweight})")

    # CV truth cross section: closure reference for the hidden-variable
    # closure (and a convenient sanity-check histogram for any closure run).
    hTruthXSec2D = None
    if args.closure:
        hTruthXSec2D = extract_cross_section_2d(
            hTruth2D, hCompleteness2D, flux_bins,
            data_pot, n_nucleons, pt_edges, pz_edges)
        hTruthXSec2D.SetName("hTruthXSec2D")
        hTruthXSec2D.SetTitle("CV MC truth cross section (closure reference)")

    # Alt-model truth cross section: closure reference for the alt-model
    # closure (push hTruthAlt2D through the same normalization machinery).
    hTruthAltXSec2D = None
    hTruthAltExtrapolatedXSec2D = None
    if hTruthAlt2D is not None:
        hTruthAltXSec2D = extract_cross_section_2d(
            hTruthAlt2D, hCompleteness2D, flux_bins,
            data_pot, n_nucleons, pt_edges, pz_edges)
        hTruthAltXSec2D.SetName("hTruthAltXSec2D")
        hTruthAltXSec2D.SetTitle(
            f"Alt-model truth cross section "
            f"(full sample, {args.closure_alt_universe})")
        hTruthAltExtrapolatedXSec2D = extract_cross_section_2d(
            hTruthAltExtrapolated2D, hCompleteness2D, flux_bins,
            data_pot, n_nucleons, pt_edges, pz_edges)
        hTruthAltExtrapolatedXSec2D.SetName("hTruthAltExtrapolatedXSec2D")
        hTruthAltExtrapolatedXSec2D.SetTitle(
            f"Alt-model truth cross section target for closure "
            f"(in-accept extrapolation, {args.closure_alt_universe})")

    # 1D projections
    hXSec_pt = project_xsec_1d(hXSec2D, "pt", pt_edges, pz_edges)
    hXSec_pz = project_xsec_1d(hXSec2D, "pz", pt_edges, pz_edges)

    # --- Summary checks ---
    pt_integral = sum(hXSec_pt.GetBinContent(i) * hXSec_pt.GetBinWidth(i)
                      for i in range(1, hXSec_pt.GetNbinsX() + 1))
    pz_integral = sum(hXSec_pz.GetBinContent(i) * hXSec_pz.GetBinWidth(i)
                      for i in range(1, hXSec_pz.GetNbinsX() + 1))
    print(f"[CHECK] Total xsec from p_T projection: {pt_integral:.4g} cm^2/nucleon")
    print(f"[CHECK] Total xsec from p_|| projection: {pz_integral:.4g} cm^2/nucleon")

    # --- Write output ---
    f_out = ROOT.TFile.Open(args.out, "RECREATE")
    if not f_out or f_out.IsZombie():
        raise RuntimeError(f"Could not create {args.out}")
    f_out.cd()

    # Metadata
    ROOT.TParameter("double")("dataPOT", data_pot).Write()
    ROOT.TParameter("double")("mcPOT", mc_pot).Write()
    ROOT.TParameter("double")("potScale", pot_scale).Write()
    ROOT.TParameter("int")("nIterations", int(args.iters)).Write()
    ROOT.TParameter("double")("fluxIntegral_m2_per_POT", flux_total_m2).Write()
    ROOT.TParameter("double")("fluxIntegral_cm2_per_POT", flux_total_cm2).Write()
    ROOT.TParameter("double")("nNucleons", n_nucleons).Write()
    ROOT.TNamed("fluxSource", flux_source).Write()

    # Histograms
    hist_list = [hDataReco2D, hBkgReco2D, hMeasSub2D, hMeasTrain2D,
                 hTruth2D, hUnfold2D, hEff2D, hEffNum, hEffDen,
                 hCompleteness2D, hOFInputTruth2D, hOFTruthDenom2D,
                 hXSec2D, hXSec_pt, hXSec_pz, hFlux_pt]
    if hTruthRew2D is not None:
        hist_list.append(hTruthRew2D)
    if hTruthRewXSec2D is not None:
        hist_list.append(hTruthRewXSec2D)
    if hTruthXSec2D is not None:
        hist_list.append(hTruthXSec2D)
    if hTruthAlt2D is not None:
        hist_list.append(hTruthAlt2D)
    if hTruthAltXSec2D is not None:
        hist_list.append(hTruthAltXSec2D)
    if hTruthInAccept2D is not None:
        hist_list.append(hTruthInAccept2D)
    if hTruthAltInAccept2D is not None:
        hist_list.append(hTruthAltInAccept2D)
    if hTruthAltExtrapolated2D is not None:
        hist_list.append(hTruthAltExtrapolated2D)
    if hTruthAltExtrapolatedXSec2D is not None:
        hist_list.append(hTruthAltExtrapolatedXSec2D)
    for h in hist_list:
        h.Write()
    ROOT.TNamed("hEffDenSource", eff_source).Write()

    f_out.Close()
    print(f"[OK] Wrote {args.out}")


if __name__ == "__main__":
    main()
