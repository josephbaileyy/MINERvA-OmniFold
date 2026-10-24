"""PV ladder: the numpy-only pieces of the prior-variation test at each rung (no ROOT, no LightGBM).

The test is PV-2D's (``docs/orchestration/state/2d-closeout/stageF/methods/pv2d/``) on the rungs of
``docs/orchestration/state/measurement-scoping/pv-ladder/DECLARATION.md``: the Tune v1 prior reweighted by each
generator's shape relative to GENIE CV, per truth cell of the rung, with PV-2D's 5 % noise gate pooled over the s5p
J-coarse cells, applied to w_truth and w_reco with the binned truth denominator rescaled so completeness stays the
nominal one (s5p_universe.prior_inputs, copied here with a guard).

Cell semantics are np.histogramdd's (the s5 stack): bin k holds e[k] <= x < e[k+1], the last bin also holds x = e[-1].

MEASURES: the reweights, their application and the readouts. CANNOT AUTHORIZE: any claim change.
"""
import hashlib
import json

import numpy as np

# The 5D fine grid (s5p_stage1_inspect.FINE) and the s5p J-coarse edges (s5p_stage1_inspect.J_EDGES).
FINE = {
    "pt": (0.0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5),
    "pz": (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0),
    "eavail": (0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0),
    "q3": (0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0),
    "W": (0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0),
}
J_EDGES = {"pt": (0.0, 0.55, 0.85, 4.5), "pz": (1.5, 3.5, 6.0, 60.0), "eavail": (0.0, 0.4, 1.5, 100.0),
           "q3": (0.0, 1.2, 2.0, 100.0), "W": (0.0, 1.4, 2.2, 100.0)}
AXES5 = ("pt", "pz", "eavail", "q3", "W")
SUPPORT_MIN = 1000.0
GIBUU_PZ_MAX = 10.0
EW_UNSUPPORTED = (11, 36, 37)  # s5p amendment 1: the EW cells failing the support rule
RATIO_SCHEMA = "pvl-ratio/1"

# rung -> (the npz's axes, the reweight axes, the classifier features)
RUNGS = {
    "L-EW": (AXES5, ("eavail", "W"), ("eavail", "W")),
    "L-3D": (("pt", "pz", "eavail"), ("pt", "pz", "eavail"), ("pt", "pz", "eavail")),
    "L-4D": (("pt", "pz", "eavail", "q3"), ("pt", "pz", "eavail", "q3"), ("pt", "pz", "eavail", "q3")),
    "L-5D-PV": (AXES5, AXES5, AXES5),
}


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path) as f:
        return json.load(f)


def npz_axes(z):
    """The npz's axis names: (pt, pz) then its stored extras (nn_dump_inputs.py writes ``axes``)."""
    extras = [str(a) for a in np.asarray(z["axes"], dtype=object)]
    names = ("pt", "pz", *extras)
    if len(names) != int(z["nedges"]):
        raise ValueError(f"axes {names} do not match nedges {int(z['nedges'])}")
    return names


def check_edges(names, edges):
    for a, e in zip(names, edges):
        if not np.array_equal(np.asarray(e, float), np.asarray(FINE[a], float)):
            raise ValueError(f"the {a} edges differ from the fine grid")


def cell_index(x, edges):
    """Per-axis bin index with histogramdd semantics; -1 outside or non-finite."""
    x = np.asarray(x, float)
    e = np.asarray(edges, float)
    i = np.searchsorted(e, x, side="right") - 1
    i = np.where(x == e[-1], e.size - 2, i)
    ok = np.isfinite(x) & (i >= 0) & (i <= e.size - 2)
    return np.where(ok, i, -1)


def flat_index(coords, axes):
    """Flat (C-order) index on the fine grid of ``axes``; -1 if any coordinate is outside."""
    coords = np.atleast_2d(np.asarray(coords, float))
    shape = tuple(len(FINE[a]) - 1 for a in axes)
    idx = [cell_index(coords[:, k], FINE[a]) for k, a in enumerate(axes)]
    inside = np.logical_and.reduce([i >= 0 for i in idx])
    flat = np.ravel_multi_index([np.maximum(i, 0) for i in idx], shape)
    return np.where(inside, flat, -1)


def coarse_of_cells(axes):
    """The J-coarse cell id of every fine cell of ``axes``, by the fine cell's centre."""
    ids = []
    for a in axes:
        e = np.asarray(FINE[a])
        c = 0.5 * (e[:-1] + e[1:])
        ids.append(np.searchsorted(J_EDGES[a], c, side="right") - 1)
    grids = np.meshgrid(*ids, indexing="ij")
    cshape = tuple(len(J_EDGES[a]) - 1 for a in axes)
    return np.ravel_multi_index([g.ravel() for g in grids], cshape)


def gated_shape_ratio(g, var_g, gref, var_gref, region, coarse, stat_max):
    """pv2d_lib.gated_shape_ratio on flat cells with the coarse map passed in (unchanged otherwise)."""
    g, var_g, gref, var_gref = (np.asarray(a, float) for a in (g, var_g, gref, var_gref))
    region = np.asarray(region, bool)
    if np.any(g[region] <= 0) or np.any(gref[region] <= 0):
        raise ValueError("a region cell has an empty prediction")

    def rel(num, var):
        return np.sqrt(np.asarray(var, float)) / np.asarray(num, float)

    st = np.full(g.shape, np.inf)
    st[region] = np.hypot(rel(g[region], var_g[region]), rel(gref[region], var_gref[region]))
    fine = region & (st <= stat_max)
    rho = np.ones_like(g)
    rho[fine] = g[fine] / gref[fine]
    label = np.where(region, "noisy", "off").astype(object)
    label[fine] = "fine"
    for cid in np.unique(coarse):
        u = region & ~fine & (coarse == cid)
        if not u.any():
            continue
        sg, sr = g[u].sum(), gref[u].sum()
        if np.hypot(rel(sg, var_g[u].sum()), rel(sr, var_gref[u].sum())) <= stat_max:
            rho[u] = sg / sr
            label[u] = "coarse"
    assigned = (label == "fine") | (label == "coarse")
    return rho, assigned, label, st


def normalize(rho, assigned, p):
    """r = rho x k on the assigned cells, 1 elsewhere; k keeps the prior truth weight p summed over them."""
    rho, p = np.asarray(rho, float), np.asarray(p, float)
    assigned = np.asarray(assigned, bool)
    if np.any(p[assigned] <= 0):
        raise ValueError("an assigned cell has no prior truth weight")
    k = p[assigned].sum() / (p[assigned] * rho[assigned]).sum()
    r = np.ones_like(rho)
    r[assigned] = rho[assigned] * k
    return r, float(k)


def project_prediction(x, s2, edges, keep, pz_max=None):
    """A 5D density x (gen5d) as the integrated cross section per fine cell of ``keep``, and its variance from the
    per-event squared density s2 = sumw2 (make_ratios.project's convention); optionally over p_parallel < pz_max."""
    x, s2 = np.asarray(x, float), np.asarray(s2, float)
    vol = np.ones(x.shape)
    for ax, e in enumerate(edges):
        sh = [1] * 5
        sh[ax] = -1
        vol = vol * np.diff(e).reshape(sh)
    if pz_max is not None:
        e = np.asarray(edges[1])
        if pz_max not in e:
            raise ValueError("pz_max must be a p_parallel edge")
        keep_pz = (e[1:] <= pz_max).reshape(1, -1, 1, 1, 1)
        x, s2 = x * keep_pz, s2 * keep_pz
    drop = tuple(sorted(set(range(5)) - {AXES5.index(a) for a in keep}))
    g = (x * vol).sum(axis=drop)
    var = (s2 * vol ** 2).sum(axis=drop)
    return g.ravel(), var.ravel()


def row_weight(gen, names, ratio, pass_truth):
    """r per MC row from a pvl-ratio/1 file: r[cell of the row's truth on the ratio's axes] on truth-passing rows
    inside the npz's full grid (PV-2D's apply_prior_ratio convention); 1 for every other row (fakes, rows outside
    the grid on any axis, -9999 sentinels) and for rows failing the ratio's truth cut (GiBUU: p_parallel < 10)."""
    if ratio.get("schema") != RATIO_SCHEMA:
        raise ValueError("not a pvl-ratio/1 file")
    axes = tuple(ratio["axes"])
    cols = [names.index(a) for a in axes]
    r_cell = np.asarray(ratio["r"], float)
    if r_cell.size != int(np.prod([len(FINE[a]) - 1 for a in axes])) or np.any(r_cell <= 0):
        raise ValueError("the ratio needs one positive r per cell of its axes")
    gen = np.asarray(gen, float)
    c = flat_index(gen[:, cols], axes)
    ok = (c >= 0) & (flat_index(gen, names) >= 0) & np.asarray(pass_truth, bool)
    cut = ratio.get("truth_cut")
    if cut is not None:
        ok &= gen[:, names.index(cut["axis"])] < float(cut["below"])
    r = np.ones(gen.shape[0])
    r[ok] = r_cell[c[ok]]
    return r


def r_constancy(inputs, r):
    """The largest relative spread of r over the truth-passing rows of one fine cell of the npz's grid. Rescaling a
    binned denominator by the ratio of truth-passing weights is exact only if r is constant on each cell."""
    m = np.asarray(inputs["pass_truth"], bool)
    edges = inputs["edges"]
    gen = np.asarray(inputs["MCgen"], float)[m]
    idx = [cell_index(gen[:, k], e) for k, e in enumerate(edges)]
    inside = np.logical_and.reduce([i >= 0 for i in idx])
    c = np.ravel_multi_index([i[inside] for i in idx], tuple(len(e) - 1 for e in edges))
    rr = np.asarray(r, float)[m][inside]
    n = int(np.prod([len(e) - 1 for e in edges]))
    hi = np.full(n, -np.inf)
    lo = np.full(n, np.inf)
    np.maximum.at(hi, c, rr)
    np.minimum.at(lo, c, rr)
    ok = np.isfinite(hi)
    return float(np.max(hi[ok] / lo[ok] - 1.0)) if ok.any() else 0.0


def prior_inputs(inputs, r, tol=1e-9):
    """s5p_universe.prior_inputs (w_truth, w_reco x r; the binned denominator rescaled per cell by the ratio of
    truth-passing weights), with two guards. r must be constant on each fine cell's truth-passing rows, the
    condition that makes the rescaling exact. The reweighted completeness must equal the nominal one; with a binned
    denominator that holds by construction, so it guards this code, not the physics. Returns (inputs, guards)."""
    spread = r_constancy(inputs, r)
    if spread > tol:
        raise RuntimeError(f"r varies inside a fine cell (relative spread {spread:.3e} > {tol:.0e})")
    ui = dict(inputs)
    wt = np.asarray(inputs["w_truth"], float)
    ui["w_truth"] = wt * r
    ui["w_reco"] = np.asarray(inputs["w_reco"], float) * r
    m = np.asarray(inputs["pass_truth"], bool)
    samp = np.asarray(inputs["MCgen"])[m]
    edges = inputs["edges"]
    dn = np.asarray(inputs["denom_nd"], float)
    of0, _ = np.histogramdd(samp, bins=edges, weights=wt[m])
    of1, _ = np.histogramdd(samp, bins=edges, weights=(wt * r)[m])
    # dn x (of1 / of0), not (dn x of1) / of0: exact at r = 1, so the NC can be bitwise
    ui["denom_nd"] = np.where(of0 > 0, dn * (of1 / np.where(of0 > 0, of0, 1)), dn)
    nz = dn > 0
    c0 = np.where(nz, of0 / np.where(nz, dn, 1), 0.0)
    c1 = np.where(ui["denom_nd"] > 0, of1 / np.where(ui["denom_nd"] > 0, ui["denom_nd"], 1), 0.0)
    if not np.array_equal(c0 > 0, c1 > 0):
        raise RuntimeError("completeness guard: the reweighted completeness has a different support")
    on = c0 > 0
    d = float(np.max(np.abs(c1[on] / c0[on] - 1.0))) if on.any() else 0.0
    if d > tol:
        raise RuntimeError(f"completeness guard: max |c_varied/c_nominal - 1| = {d:.3e} > {tol:.0e}")
    return ui, {"r_spread_in_cell": spread, "completeness": d}


def closure_inputs(inputs, r):
    """The noise-free signal-only closure (PV-2D's): pseudo-data are the MC's reco- and truth-passing rows (fakes
    excluded, as unfold_2d_pv2d.py's closure_mask) at w_reco x r inside the reco window, no background; returned as an s5 experiment with no template, and the truth reference
    x_true(r) through the nominal completeness."""
    import os
    import sys

    nd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if nd not in sys.path:
        sys.path.insert(0, nd)
    from xsec_nd import extract_cross_section_nd

    edges = inputs["edges"]
    reco = np.asarray(inputs["MCreco"])
    keep = np.asarray(inputs["pass_reco"], bool) & np.asarray(inputs["pass_truth"], bool)  # no fakes (PV-2D)
    for k, e in enumerate(edges):
        keep &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])
    w = np.asarray(inputs["w_reco"], float) * r
    keep &= w > 0
    exp = {k: inputs[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                  "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
    exp.update(obs=reco[keep], obs_counts=w[keep], tmpl=np.zeros((0, reco.shape[1]), reco.dtype),
               tmpl_w=np.zeros(0))
    m = np.asarray(inputs["pass_truth"], bool)
    gen, wt = np.asarray(inputs["MCgen"])[m], np.asarray(inputs["w_truth"], float)[m]
    unf, _ = np.histogramdd(gen, bins=edges, weights=wt * r[m])
    ofin, _ = np.histogramdd(gen, bins=edges, weights=wt)
    dn = np.asarray(inputs["denom_nd"], float)
    comp = np.where(dn > 0, ofin / np.where(dn > 0, dn, 1), 0.0)
    x_true, _ = extract_cross_section_nd(unf, comp, inputs["flux"], float(inputs["data_pot"]),
                                         float(inputs["n_nucleons"]), edges)
    return exp, x_true


def support(inputs, names):
    """s5p's support rule on the npz's own fine cells: expected reco-level signal (w_reco on reco-passing rows, by
    reco cell) and truth-selected weight (w_truth on truth-passing rows, by truth cell) both >= SUPPORT_MIN."""
    n = int(np.prod([len(FINE[a]) - 1 for a in names]))
    out = {}
    for key, coords, w, m in (("reco_signal", "MCreco", "w_reco", "pass_reco"),
                              ("truth_selected", "MCgen", "w_truth", "pass_truth")):
        c = flat_index(np.asarray(inputs[coords])[np.asarray(inputs[m], bool)], names)
        ww = np.asarray(inputs[w], float)[np.asarray(inputs[m], bool)]
        ok = c >= 0
        out[key] = np.bincount(c[ok], weights=ww[ok], minlength=n)
    out["supported"] = (out["reco_signal"] >= SUPPORT_MIN) & (out["truth_selected"] >= SUPPORT_MIN)
    return out


def project_xsec(xsec, names, keep):
    """Cell-integrated cross sections on the fine cells of ``keep`` (sum over the dropped axes of xsec x the cell
    volume): s5p's RD3 convention for the EW cells."""
    xsec = np.asarray(xsec, float).reshape(tuple(len(FINE[a]) - 1 for a in names))
    vol = np.ones(xsec.shape)
    for ax, a in enumerate(names):
        sh = [1] * len(names)
        sh[ax] = -1
        vol = vol * np.diff(FINE[a]).reshape(sh)
    drop = tuple(i for i, a in enumerate(names) if a not in keep)
    return (xsec * vol).sum(axis=drop).ravel()


def ew_headline():
    """The 39 supported EW cells (EWi = i_E x 6 + i_W)."""
    return np.array([i for i in range(42) if i not in EW_UNSUPPORTED])


def integrated(xsec, names):
    """Differential cross section per fine cell -> cell-integrated (x the cell volume), flat."""
    xsec = np.asarray(xsec, float).reshape(tuple(len(FINE[a]) - 1 for a in names))
    vol = np.ones(xsec.shape)
    for ax, a in enumerate(names):
        sh = [1] * len(names)
        sh[ax] = -1
        vol = vol * np.diff(FINE[a]).reshape(sh)
    return (xsec * vol).ravel()


def readout_space(xint, names, space):
    """Cell-integrated values on a readout space: "fine" (the npz's cells), "EW" (eavail, W), "PTPZ" (pt, pz) or "J"
    (the J-coarse cells of the npz's axes)."""
    shape = tuple(len(FINE[a]) - 1 for a in names)
    x = np.asarray(xint, float).reshape(shape)
    if space == "fine":
        return x.ravel()
    if space in ("EW", "PTPZ"):
        keep = ("eavail", "W") if space == "EW" else ("pt", "pz")
        return x.sum(axis=tuple(i for i, a in enumerate(names) if a not in keep)).ravel()
    if space == "J":
        c = coarse_of_cells(names)
        return np.bincount(c, weights=x.ravel(), minlength=int(np.prod([len(J_EDGES[a]) - 1 for a in names])))
    raise ValueError(space)


STEP = 0.1  # PV-2D REPORT §5's step threshold in r
CLASS_ORDER = ("gate", "cut", "generator", "none")


def classify_cells(r, label, shape, step=STEP):
    """report_tables.classify_cell on an N-dimensional grid, for every cell at once: over the cell's axis neighbours
    with |r - r_nb| > step, "gate" if any such pair has a coarse-pooled or noisy (r = 1) side, else "cut" if any has
    an "off" side, else "generator" if any is fine|fine, else "none"."""
    r = np.asarray(r, float).reshape(shape)
    lab = np.asarray(label, dtype=object).reshape(shape)
    gatey = np.isin(lab, ("coarse", "noisy"))
    fine = lab == "fine"
    has = {k: np.zeros(shape, bool) for k in ("gate", "cut", "generator")}
    for ax in range(len(shape)):
        n = shape[ax]
        if n < 2:
            continue
        lo = [slice(None)] * len(shape)
        hi = [slice(None)] * len(shape)
        lo[ax], hi[ax] = slice(0, n - 1), slice(1, n)
        lo, hi = tuple(lo), tuple(hi)
        big = np.abs(r[lo] - r[hi]) > step
        g = big & (gatey[lo] | gatey[hi])
        gen = big & fine[lo] & fine[hi]
        c = big & ~g & ~gen
        for kind, m in (("gate", g), ("cut", c), ("generator", gen)):
            has[kind][lo] |= m
            has[kind][hi] |= m
    out = np.full(shape, "none", dtype=object)
    for kind in ("generator", "cut", "gate"):  # later assignments take precedence
        out[has[kind]] = kind
    return out.ravel()
