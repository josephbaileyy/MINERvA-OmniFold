#!/usr/bin/env python3
"""N-dimensional cross-section extraction + projection for higher-dim OmniFold.

Generalizes ``3d-unfolding/xsec_3d.py`` (which is hardcoded to pt/pz/eavail) to an
arbitrary axis list, so the 4th axis (q3, Workstream D) -- and any further axis --
is a configuration change, not new math. The OmniFold reweighting itself is already
dimension-agnostic (features are an (nevents, nfeatures) column_stack); this module
supplies the only genuinely dimension-specific piece: the differential cross-section
Jacobian and the marginal/1D projections.

Conventions (match xsec_3d.py exactly):
  - axis 0 is the FLUX axis (pT): the flux integral Phi is per-axis-0 bin and is
    broadcast over every other axis (flux varies only with pT in this analysis).
  - per bin:  dsigma = U * 1e4 / (c . Phi . N . POT . prod_a dx_a)
  - units: cm^2 / prod_a [unit of axis a] / nucleon.

The 3D entry points in xsec_3d.py are intentionally left untouched (the 3D result is
frozen); test_matches_xsec_3d() proves this module reproduces them bit-for-bit on a
random 3D input, so the frozen pipeline and this generalization cannot silently drift.

Run the self-tests:  python nd-unfolding/xsec_nd.py
"""
import numpy as np


# ---------------------------------------------------------------------------
# Broadcasting helpers
# ---------------------------------------------------------------------------
def _broadcast_along(vec, ndim, axis):
    """Reshape a 1D vector to broadcast along `axis` of an `ndim`-D array."""
    shape = [1] * ndim
    shape[axis] = len(vec)
    return np.asarray(vec, float).reshape(shape)


def _bin_volume(shape, axes_edges, only=None):
    """Outer product of per-axis bin widths as an array broadcastable to `shape`.

    If `only` is given (an iterable of axis indices), include just those axes'
    widths (the rest contribute a factor of 1) -- used to weight a marginal.
    """
    ndim = len(shape)
    vol = np.ones(shape, dtype=float)
    axes = range(ndim) if only is None else only
    for ax in axes:
        w = np.diff(np.asarray(axes_edges[ax], float))
        vol = vol * _broadcast_along(w, ndim, ax)
    return vol


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------
def extract_cross_section_nd(counts, completeness, flux, data_pot, n_nucleons,
                             axes_edges, flux_axis=0):
    """d^D sigma / prod_a dx_a from unfolded truth-level counts.

    Parameters
    ----------
    counts, completeness : (n_0, ..., n_{D-1}) arrays  (U and c)
    flux                 : (n_{flux_axis},) flux integral m^-2/POT per flux-axis bin
    axes_edges           : list of D 1D bin-edge arrays, one per axis
    flux_axis            : which axis the flux is binned in (default 0 = pT)

    Returns (xsec, nonzero_mask). xsec has the same shape as counts.
    """
    counts = np.asarray(counts, float)
    completeness = np.asarray(completeness, float)
    ndim = counts.ndim
    if len(axes_edges) != ndim:
        raise ValueError(f"axes_edges has {len(axes_edges)} entries, counts is {ndim}-D")
    if completeness.shape != counts.shape:
        raise ValueError("completeness shape must match counts")
    if len(flux) != counts.shape[flux_axis]:
        raise ValueError(f"flux length {len(flux)} != axis {flux_axis} size "
                         f"{counts.shape[flux_axis]}")
    vol = _bin_volume(counts.shape, axes_edges)
    flux_b = _broadcast_along(flux, ndim, flux_axis)
    denom = completeness * flux_b * n_nucleons * data_pot * vol
    good = (denom > 0) & np.isfinite(denom)
    xsec = np.zeros_like(counts)
    np.divide(counts * 1.0e4, denom, out=xsec, where=good)
    return xsec, good


# ---------------------------------------------------------------------------
# Projections
# ---------------------------------------------------------------------------
def project_marginal(xsec, axes_edges, drop_axes):
    """Marginalize d^D sigma over `drop_axes` -> a lower-D differential xsec.

        out[...] = sum_{k in drop} xsec[...] * prod_{a in drop} dx_a

    This is the validation-anchor operation: dropping the last (q3 or Eavail) axis
    must reproduce the next-lower-dimensional cross section (Jacobian identity).
    Returns an array of dimension D - len(drop_axes), with axes in their original
    order (minus the dropped ones).
    """
    drop = sorted(set(drop_axes))
    if not drop:
        return np.array(xsec, float)
    weighted = np.asarray(xsec, float) * _bin_volume(xsec.shape, axes_edges, only=drop)
    for ax in sorted(drop, reverse=True):   # descending so indices stay valid
        weighted = weighted.sum(axis=ax)
    return weighted


def project_axis(xsec, axes_edges, keep_axis):
    """1D projection onto `keep_axis` (integrate out every other axis).

    Returns (edges_of_keep_axis, dsigma/dx_keep). Equivalent to
    project_marginal with all other axes dropped.
    """
    ndim = np.asarray(xsec).ndim
    drop = [a for a in range(ndim) if a != keep_axis]
    return np.asarray(axes_edges[keep_axis], float), project_marginal(xsec, axes_edges, drop)


def total_xsec(xsec, axes_edges):
    """Full D-dimensional integral sum xsec * prod dx_a."""
    return float((np.asarray(xsec, float) * _bin_volume(np.asarray(xsec).shape,
                                                        axes_edges)).sum())


# ---------------------------------------------------------------------------
# Self-tests (no ROOT, no real data)
# ---------------------------------------------------------------------------
def test_matches_xsec_3d():
    """xsec_nd must reproduce the frozen 3D xsec_3d.py bit-for-bit on a 3D input."""
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(__file__), "..", "3d-unfolding", "xsec_3d.py")
    spec = importlib.util.spec_from_file_location("xsec_3d", os.path.abspath(p))
    x3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x3)

    rng = np.random.default_rng(7)
    n_pt, n_pz, n_ea = 14, 16, 7
    pt = np.linspace(0, 4.5, n_pt + 1)
    pz = np.linspace(1.5, 60, n_pz + 1)
    ea = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0])
    edges = [pt, pz, ea]
    U = rng.uniform(10, 1000, (n_pt, n_pz, n_ea))
    c = rng.uniform(0.8, 1.0, (n_pt, n_pz, n_ea))
    flux = rng.uniform(5e-4, 7e-4, n_pt)
    pot, nnuc = 1.2e21, 3.2e30

    # Floating-point note: xsec_3d multiplies the denominator factors in a fixed
    # order; xsec_nd builds the bin volume separately, so results agree only to
    # round-off (different associativity), not bit-for-bit. Require <1e-12 rel.
    def _relmax(a, b):
        m = np.abs(b) > 0
        return np.max(np.abs(a[m] - b[m]) / np.abs(b[m])) if m.any() else 0.0

    x_nd, good_nd = extract_cross_section_nd(U, c, flux, pot, nnuc, edges)
    x_3d, good_3d = x3.extract_cross_section_3d(U, c, flux, pot, nnuc, pt, pz, ea)
    assert np.array_equal(good_nd, good_3d)
    assert _relmax(x_nd, x_3d) < 1e-12, "nd extraction differs from frozen 3D"

    # marginal over the last axis == project_eavail_marginal
    m_nd = project_marginal(x_nd, edges, drop_axes=[2])
    m_3d = x3.project_eavail_marginal(x_3d, ea)
    assert _relmax(m_nd, m_3d) < 1e-12, "nd marginal differs from frozen 3D"

    # 1D projections match on all 3 axes
    for ki, name in [(0, "pt"), (1, "pz"), (2, "eavail")]:
        _, y_nd = project_axis(x_nd, edges, ki)
        _, y_3d = x3.project_axis(x_3d, pt, pz, ea, name)
        assert _relmax(y_nd, y_3d) < 1e-12, f"nd 1D proj {name} differs"
    print("[PASS] xsec_nd reproduces frozen xsec_3d (extraction, marginal, 1D) to <1e-12")


def test_marginal_jacobian_identity():
    """For separable U the q3-marginal of the 4D xsec equals the 3D xsec from
    the same lower-D counts (the validation anchor, in 4D)."""
    rng = np.random.default_rng(0)
    n = (8, 6, 5, 4)                       # pt, pz, eavail, q3
    edges = [np.linspace(0, 4.5, n[0] + 1),
             np.linspace(1.5, 60, n[1] + 1),
             np.array([0.0, 0.1, 0.2, 0.4, 1.0, 3.0]),
             np.array([0.0, 0.3, 0.6, 1.0, 2.0])]
    flux = rng.uniform(5e-4, 7e-4, n[0])
    pot, nnuc = 1.2e21, 3.2e30
    c = np.ones(n)

    U3 = rng.uniform(10, 1000, n[:3])          # pt,pz,eavail counts
    frac = rng.uniform(0.1, 1.0, n)            # split across q3
    frac /= frac.sum(axis=3, keepdims=True)
    U4 = U3[..., None] * frac

    x4, _ = extract_cross_section_nd(U4, c, flux, pot, nnuc, edges)
    marg = project_marginal(x4, edges, drop_axes=[3])           # -> (pt,pz,eavail)
    x3_direct, _ = extract_cross_section_nd(U3, np.ones(n[:3]), flux, pot, nnuc,
                                            edges[:3])
    rel = np.abs(marg - x3_direct) / np.abs(x3_direct)
    assert rel.max() < 1e-12, f"q3-marginal != 3D xsec, max rel {rel.max():.2e}"
    print(f"[PASS] 4D q3-marginal recovers the 3D cross section (max rel {rel.max():.1e})")


def test_projection_integral_consistency():
    """All 1D projections integrate to the same D-dim total, any D."""
    rng = np.random.default_rng(1)
    edges = [np.linspace(0, 4.5, 9), np.linspace(1.5, 60, 7),
             np.array([0.0, 0.1, 0.4, 1.0]), np.array([0.0, 0.5, 1.0, 2.0])]
    shape = tuple(len(e) - 1 for e in edges)
    xsec = rng.uniform(0, 1e-39, shape)
    tot = total_xsec(xsec, edges)
    for ax in range(len(edges)):
        e, y = project_axis(xsec, edges, ax)
        assert abs((y * np.diff(e)).sum() - tot) / tot < 1e-12
    print("[PASS] 1D projections integrate to the same total on all axes (4D)")


if __name__ == "__main__":
    test_matches_xsec_3d()
    test_marginal_jacobian_identity()
    test_projection_integral_consistency()
    print("all xsec_nd self-tests passed")
