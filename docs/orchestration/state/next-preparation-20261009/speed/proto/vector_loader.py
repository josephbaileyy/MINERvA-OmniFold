"""Prototype 2: columnar replacement for the driver's ``collect_signal_arrays_2d``.

The pinned loader walks ``mc_signal_reco`` with one PyROOT ``GetEntry`` per row,
tests each row in Python and appends to Python lists. This prototype reads only
the needed columns with ``RDataFrame.AsNumpy`` (single-threaded, so entry order
is the tree's) and applies the same tests as array masks. It must return arrays
that are byte-identical to the pinned loader's on every input; the tests in
``bench/test_prototypes.py`` check that, including adversarial rows.

Two semantic details that a naive port gets wrong:

* the truth gate uses ``math.atan2(pt, pz) < radians(20)``; NumPy's ``arctan2``
  need not round identically, so rows whose NumPy angle lies within
  ``ATAN2_GUARD_ULPS`` of the cut are re-evaluated with ``math.atan2``;
* ``sim_pass`` is ``UChar_t`` and the driver tests ``!= 0``, not ``== 1``;
  ``AsNumpy`` returns it as a NumPy bool array whose bytes can still be 2.

Scope: CV and universe modes with ``use_weights`` either way; the alt-model
closure path is not implemented and raises.
"""

import math

import numpy as np
import ROOT

MAX_MUON_THETA_RAD = math.radians(20.0)
ATAN2_GUARD_ULPS = 64
SENTINEL = -9999.0


def _theta_below_cut(pt, pz):
    """Elementwise ``math.atan2(pt, pz) < MAX_MUON_THETA_RAD`` for finite inputs."""
    with np.errstate(invalid="ignore"):
        theta = np.arctan2(pt, pz)
    below = theta < MAX_MUON_THETA_RAD
    guard = ATAN2_GUARD_ULPS * np.spacing(MAX_MUON_THETA_RAD)
    near = np.flatnonzero(np.abs(theta - MAX_MUON_THETA_RAD) <= guard)
    for i in near:
        below[i] = math.atan2(float(pt[i]), float(pz[i])) < MAX_MUON_THETA_RAD
    return below, near.size


def collect_signal_arrays_columnar(tree, branches, pt_lo, pt_hi, pz_lo, pz_hi,
                                   pot_scale, use_weights=False, alt=False):
    """Return the pinned loader's output dict, computed column-wise.

    ``branches`` is ``(mc, mc_pz, sim, sim_pz, wt, wr)``; ``wt``/``wr`` are
    ignored when ``use_weights`` is false, as in the driver.
    """
    if alt:
        raise NotImplementedError("alt-model closure path is out of the prototype's scope")
    mc, mc_pz, sim, sim_pz, wt_b, wr_b = branches
    names = [mc, mc_pz, sim, sim_pz, "sim_pass"] + ([wt_b, wr_b] if use_weights else [])
    cols = ROOT.RDataFrame(tree).AsNumpy(names)
    tru_pt = np.asarray(cols[mc], dtype=np.float64)
    tru_pz = np.asarray(cols[mc_pz], dtype=np.float64)
    rec_pt = np.asarray(cols[sim], dtype=np.float64)
    rec_pz = np.asarray(cols[sim_pz], dtype=np.float64)
    # ROOT 6.36 AsNumpy returns this UChar_t column as dtype bool while keeping
    # the stored bytes (0, 1, 2 occur); test the bytes, as the driver does.
    raw = np.asarray(cols["sim_pass"])
    if raw.dtype == np.bool_:
        raw = raw.view(np.uint8)
    passed = raw != 0
    if use_weights:
        wt = np.asarray(cols[wt_b], dtype=np.float64)
        wr = np.asarray(cols[wr_b], dtype=np.float64)
    else:
        wt = np.ones_like(tru_pt)
        wr = wt.copy()

    good_w = (np.isfinite(wt) & np.isfinite(wr)
              & (0 <= wt) & (wt < 1e4) & (0 <= wr) & (wr < 1e4))
    tru_fin = np.isfinite(tru_pt) & np.isfinite(tru_pz)
    tru_rect = (pt_lo <= tru_pt) & (tru_pt <= pt_hi) & (pz_lo <= tru_pz) & (tru_pz <= pz_hi)
    cand = good_w & tru_fin & tru_rect
    tru_ok = np.zeros_like(cand)
    tru_ok[cand], n_guard = _theta_below_cut(tru_pt[cand], tru_pz[cand])
    rec_ok = (np.isfinite(rec_pt) & np.isfinite(rec_pz)
              & (pt_lo <= rec_pt) & (rec_pt <= pt_hi) & (pz_lo <= rec_pz) & (rec_pz <= pz_hi))
    pass_reco = passed & rec_ok
    keep = good_w & (tru_ok | pass_reco)

    out = {
        "truth_pt": np.where(np.isfinite(tru_pt), tru_pt, SENTINEL)[keep],
        "truth_pz": np.where(np.isfinite(tru_pz), tru_pz, SENTINEL)[keep],
        "reco_pt": np.where(pass_reco, rec_pt, SENTINEL)[keep],
        "reco_pz": np.where(pass_reco, rec_pz, SENTINEL)[keep],
        "pass_reco": pass_reco[keep],
        "pass_truth": tru_ok[keep],
        "w_truth": wt[keep] * pot_scale,
        "w_reco": wr[keep] * pot_scale,
    }
    out["_atan2_guard_rows"] = n_guard
    return out
