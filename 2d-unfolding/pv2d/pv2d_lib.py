"""PV-2D: the numpy-only pieces of the 2D prior-variation test (no ROOT, so they are unit-tested locally).

The test (``docs/orchestration/state/2d-closeout/stageF/methods/pv2d/ASSIGNMENT.md``) unfolds the real 2D data with
the MC truth prior reweighted to a generator vertex: ``w_truth`` and ``w_reco`` of every truth-passing MC row are
multiplied by r(truth), and so is the truth denominator, so the per-cell completeness stays the nominal one (the
s5p study-P defect of 2026-09-26, ``RECORD-20260927-s5p-stage2-exit.md`` §1, ``s5p_universe.prior_inputs``).

r is piecewise constant on the 14 x 16 (pT, p_parallel) truth cells of the paper binning. A row whose truth lies
outside the grid (under- or overflow, including a value on the last edge, which ROOT's TH2D::Fill puts in the
overflow) keeps r = 1. Composition below the 2D binning (inside a cell) stays Tune v1's.

MEASURES: the reweight, its application and the readouts. CANNOT AUTHORIZE: any claim change.
"""
import hashlib
import json

import numpy as np

PT_EDGES = (0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50)
PZ_EDGES = (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0)
NPT, NPZ = len(PT_EDGES) - 1, len(PZ_EDGES) - 1
RATIO_SCHEMA = "pv2d-ratio/1"


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cell_index(x, edges):
    """TH1::FindBin's convention minus one: bin k holds edges[k] <= x < edges[k+1]; -1 below, len(edges)-1 on or
    above the last edge, and -1 for a non-finite x."""
    x = np.asarray(x, float)
    e = np.asarray(edges, float)
    i = np.searchsorted(e, x, side="right") - 1
    i = np.where(np.isfinite(x), i, -1)
    return i


def cell_ratio_weight(r, pt, pz):
    """r[ipt, ipz] at each row's truth cell; 1 for a row outside the grid on either axis."""
    r = np.asarray(r, float)
    if r.shape != (NPT, NPZ):
        raise ValueError(f"r has shape {r.shape}, expected {(NPT, NPZ)}")
    ipt = cell_index(pt, PT_EDGES)
    ipz = cell_index(pz, PZ_EDGES)
    inside = (ipt >= 0) & (ipt < NPT) & (ipz >= 0) & (ipz < NPZ)
    out = np.ones(ipt.shape, float)
    out[inside] = r[ipt[inside], ipz[inside]]
    return out


def load_ratio(path, expect_sha256):
    """A pv2d-ratio/1 file, refused unless its sha256, schema, edges and values are the declared ones."""
    got = sha256_path(path)
    if got != expect_sha256:
        raise SystemExit(f"[FAIL] ratio file {path}: sha256 {got} != expected {expect_sha256}")
    with open(path) as f:
        d = json.load(f)
    if d.get("schema") != RATIO_SCHEMA:
        raise SystemExit(f"[FAIL] ratio file {path}: schema {d.get('schema')!r} != {RATIO_SCHEMA!r}")
    if tuple(d["pt_edges"]) != PT_EDGES or tuple(d["pz_edges"]) != PZ_EDGES:
        raise SystemExit(f"[FAIL] ratio file {path}: edges differ from the paper binning")
    r = np.asarray(d["r"], float)
    if r.shape != (NPT, NPZ) or not np.all(np.isfinite(r)) or np.any(r <= 0):
        raise SystemExit(f"[FAIL] ratio file {path}: r must be a finite positive {NPT}x{NPZ} array")
    return r, d


def apply_prior_ratio(sig, truth_denom, r):
    """The prior variation in place: w_truth and w_reco of every truth-passing signal row, and w_truth of every
    truth-denominator row, times r(truth cell). Rows failing the truth selection (signal fakes, which are
    background by the paper's convention) keep their weights, so the background is unchanged.
    Returns the per-row factors (signal, denominator)."""
    rs = cell_ratio_weight(r, sig["truth_pt"], sig["truth_pz"])
    rs = np.where(np.asarray(sig["pass_truth"], bool), rs, 1.0)
    sig["w_truth"] = np.asarray(sig["w_truth"], float) * rs
    sig["w_reco"] = np.asarray(sig["w_reco"], float) * rs
    rd = cell_ratio_weight(r, truth_denom["truth_pt"], truth_denom["truth_pz"])
    truth_denom["w_truth"] = np.asarray(truth_denom["w_truth"], float) * rd
    return rs, rd


def hist2d(pt, pz, w):
    """The TH2D content (no under/overflow) of weighted rows, by the same cell convention as cell_ratio_weight."""
    ipt = cell_index(pt, PT_EDGES)
    ipz = cell_index(pz, PZ_EDGES)
    inside = (ipt >= 0) & (ipt < NPT) & (ipz >= 0) & (ipz < NPZ)
    flat = ipt[inside] * NPZ + ipz[inside]
    return np.bincount(flat, weights=np.asarray(w, float)[inside], minlength=NPT * NPZ).reshape(NPT, NPZ)


def completeness(sig, truth_denom):
    """c = (truth-passing signal w_truth) / (denominator w_truth) per cell; 0 where the denominator is empty."""
    m = np.asarray(sig["pass_truth"], bool)
    num = hist2d(np.asarray(sig["truth_pt"])[m], np.asarray(sig["truth_pz"])[m], np.asarray(sig["w_truth"])[m])
    den = hist2d(truth_denom["truth_pt"], truth_denom["truth_pz"], truth_denom["w_truth"])
    return np.divide(num, den, out=np.zeros_like(num), where=den > 0)


def completeness_guard(c_nominal, c_varied, tol=1e-9):
    """The denominator-defect guard: with r constant on each cell, the varied completeness equals the nominal one
    to rounding. Returns the maximum relative difference over cells with nominal content; raises if it exceeds
    tol (the defective form, which leaves the denominator unreweighted, moves c by the cell's r)."""
    c0 = np.asarray(c_nominal, float)
    c1 = np.asarray(c_varied, float)
    m = c0 > 0
    if not np.array_equal(m, c1 > 0):
        raise SystemExit("[FAIL] completeness guard: the varied completeness has a different support")
    d = float(np.max(np.abs(c1[m] / c0[m] - 1.0))) if m.any() else 0.0
    if d > tol:
        raise SystemExit(f"[FAIL] completeness guard: max |c_varied/c_nominal - 1| = {d:.3e} > {tol:.0e} "
                         "(the truth denominator was not reweighted with the prior)")
    return d


# ------------------------------------------------------------------------------------------- ratios


def build_ratio(g, t, p, region):
    """The vertex reweight on the 2D cells.

    g      : the vertex's integrated cross section per (pT, p_parallel) cell (any common unit);
    t      : the prior's integrated cross section per cell, up to one constant (hTruth2D / completeness);
    p      : the prior's truth weight per cell (hTruth2D), for the normalization;
    region : bool mask of the cells where the ratio is defined.

    On the region, r = (g / t) x k, with the one constant k chosen so the prior's truth weight summed over the region
    is unchanged (a pure shape departure, s5n_pseudo.eavail_ratio_weight's convention). Off it, r = 1. A region cell
    with g <= 0 or t <= 0 is refused rather than silently set to 1."""
    g, t, p = (np.asarray(a, float) for a in (g, t, p))
    region = np.asarray(region, bool)
    if np.any(g[region] <= 0) or np.any(t[region] <= 0) or np.any(p[region] <= 0):
        raise ValueError("a region cell has an empty vertex, prior or truth weight")
    raw = np.ones_like(g)
    raw[region] = g[region] / t[region]
    k = p[region].sum() / (p[region] * raw[region]).sum()
    r = np.ones_like(g)
    r[region] = raw[region] * k
    return r, float(k)


# ------------------------------------------------------------------------------------------- readouts


def rel_shift(x_var, x_nom):
    """(x_var / x_nom - 1) on the cells given (x_nom > 0 is required)."""
    x_var, x_nom = np.asarray(x_var, float), np.asarray(x_nom, float)
    if np.any(x_nom <= 0):
        raise ValueError("nominal cell with no content")
    return x_var / x_nom - 1.0


def summary(a):
    a = np.abs(np.asarray(a, float))
    return {"median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(np.max(a)),
            "argmax": int(np.argmax(a))}


def nominal_control(x_run, x_ref, tol=1e-5):
    """NC: the nominal-prior run against E_U on the reported cells; PASS iff max |x_run/x_ref - 1| < tol."""
    d = float(np.max(np.abs(rel_shift(x_run, x_ref))))
    return {"max_rel_diff": d, "tol": tol, "bitwise": bool(np.array_equal(np.asarray(x_run), np.asarray(x_ref))),
            "pass": d < tol}


def linear_response(shift, bias, min_abs_bias=0.01):
    """Pearson correlation and least-squares slope (through the origin) of shift against -bias, over the cells with
    |bias| > min_abs_bias. Both inputs are relative per-cell quantities."""
    shift, bias = np.asarray(shift, float), np.asarray(bias, float)
    m = np.abs(bias) > min_abs_bias
    n = int(m.sum())
    if n < 3:
        return {"n_cells": n, "corr": None, "slope": None}
    y, x = shift[m], -bias[m]
    corr = float(np.corrcoef(x, y)[0, 1])
    slope = float((x * y).sum() / (x * x).sum())
    return {"n_cells": n, "corr": corr, "slope": slope}


def positive_control(shift, bias, min_cells=20, min_abs_bias=0.01, min_corr=0.7, slope_range=(0.67, 1.5)):
    """PC: does the data-side shift at the control vertex track minus the closure bias at that vertex?

    POWERED iff at least min_cells cells have |bias| > min_abs_bias; else the verdict is NOT_POWERED (the test of
    a bias of that size cannot be made, and the declared fallback applies). If powered: PASS iff corr >= min_corr
    and slope_range[0] <= slope <= slope_range[1]; else FAIL."""
    lr = linear_response(shift, bias, min_abs_bias)
    out = dict(lr, min_cells=min_cells, min_abs_bias=min_abs_bias, min_corr=min_corr, slope_range=list(slope_range))
    if lr["n_cells"] < min_cells:
        out["verdict"] = "NOT_POWERED"
    elif lr["corr"] >= min_corr and slope_range[0] <= lr["slope"] <= slope_range[1]:
        out["verdict"] = "PASS"
    else:
        out["verdict"] = "FAIL"
    return out


def envelope(shifts):
    """h per cell = max over vertices of |shift|, and the vertex that sets it."""
    names = list(shifts)
    a = np.abs(np.vstack([np.asarray(shifts[k], float) for k in names]))
    return a.max(axis=0), [names[i] for i in a.argmax(axis=0)]


def compare_to_sigma(h, sigma):
    """h against a per-cell relative sigma: medians, the ratio's quantiles and the fraction of cells with h > sigma."""
    h, sigma = np.asarray(h, float), np.asarray(sigma, float)
    q = h / sigma
    return {"median_h": float(np.median(h)), "median_sigma": float(np.median(sigma)),
            "ratio_median": float(np.median(q)), "ratio_p90": float(np.percentile(q, 90)),
            "ratio_max": float(np.max(q)), "frac_h_gt_sigma": float(np.mean(h > sigma)),
            "frac_h_gt_half_sigma": float(np.mean(h > 0.5 * sigma))}
