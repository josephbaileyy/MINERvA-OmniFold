#!/usr/bin/env python3
"""Core 3D cross-section extraction and Eavail-marginal projection for the
higher-dimensional OmniFold extension d^3 sigma / (dpT dp|| dEavail).

This is the genuinely new piece of the 3D pipeline (Workstream C). It is kept
numpy-based and dependency-light so it can be unit-tested now, before the C++
event-loop re-run that adds the Eavail branches exists. The 2D driver's
ROOT-based machinery (data loading, the OmniFold call, universe/closure logic)
is reused from ../2d-unfolding/unfold_2d_omnifold_unbinned.py once the 3D
omnifile is available; only the cross-section/projection math is new and lives
here.

Axis decisions (see memory eavail-3d-extension / arXiv:2312.16631):
  truth Eavail = GetEAvailableTrue()  (MAT calculators/CCQE3DFitFunctions.h)
  reco  Eavail = NewEavail()          (MAT LowRecoilPionFunctions.h, x1.17)

Validation anchor: the Eavail-marginal of the 3D cross section must reproduce
the frozen 2D result d^2 sigma/(dpT dp||). project_eavail_marginal() implements
that marginalization; test_marginal_recovers_2d() proves it is exact for a
separable input.
"""
import numpy as np


def extract_cross_section_3d(counts, completeness, flux_pt, data_pot,
                             n_nucleons, pt_edges, pz_edges, eavail_edges):
    """d^3 sigma / (dpT dp|| dEavail) from unfolded truth-level counts.

    Per bin:  dsigma = U / (c . Phi . N . POT . dpT . dpz . dEavail) . 1e4
    Flux Phi is per-pT (broadcast over p|| and Eavail), matching the 2D
    convention in extract_cross_section_2d (flux varies only with pT).

    Parameters
    ----------
    counts, completeness : (n_pt, n_pz, n_ea) arrays  (U and c)
    flux_pt              : (n_pt,) flux integral m^-2/POT per pT bin
    pt_edges, pz_edges, eavail_edges : 1D bin-edge arrays

    Returns (xsec, nonzero_mask) with xsec in cm^2 / (GeV/c)^2 / GeV / nucleon.
    """
    n_pt, n_pz, n_ea = counts.shape
    assert flux_pt.shape == (n_pt,)
    assert completeness.shape == counts.shape
    dpt = np.diff(pt_edges)[:, None, None]
    dpz = np.diff(pz_edges)[None, :, None]
    dea = np.diff(eavail_edges)[None, None, :]
    flux = flux_pt[:, None, None]
    denom = completeness * flux * n_nucleons * data_pot * dpt * dpz * dea
    good = (denom > 0) & np.isfinite(denom)
    xsec = np.zeros_like(counts, dtype=float)
    np.divide(counts * 1.0e4, denom, out=xsec, where=good)
    return xsec, good


def project_eavail_marginal(xsec3d, eavail_edges):
    """Marginalize d^3 sigma over Eavail -> d^2 sigma / (dpT dp||).

        d^2sigma[i,j] = sum_k d^3sigma[i,j,k] * dEavail_k

    This is the validation anchor: it must reproduce the frozen 2D cross
    section. Returns a (n_pt, n_pz) array.
    """
    dea = np.diff(eavail_edges)[None, None, :]
    return (xsec3d * dea).sum(axis=2)


def project_axis(xsec3d, pt_edges, pz_edges, eavail_edges, axis):
    """1D projection onto 'pt', 'pz', or 'eavail' (integrate the other two)."""
    dpt = np.diff(pt_edges)
    dpz = np.diff(pz_edges)
    dea = np.diff(eavail_edges)
    w = xsec3d * dpt[:, None, None] * dpz[None, :, None] * dea[None, None, :]
    if axis == "pt":
        return pt_edges, w.sum(axis=(1, 2)) / dpt
    if axis == "pz":
        return pz_edges, w.sum(axis=(0, 2)) / dpz
    if axis == "eavail":
        return eavail_edges, w.sum(axis=(0, 1)) / dea
    raise ValueError(f"axis must be pt/pz/eavail, got {axis!r}")


# ---------------------------------------------------------------------------
# Self-tests (run: python xsec_3d.py) -- no ROOT, no real data needed.
# ---------------------------------------------------------------------------
def test_marginal_recovers_2d():
    """For a separable input U3d[i,j,k] = U2d[i,j] * shape_k, the
    Eavail-marginal of the 3D cross section equals the 2D cross section."""
    rng = np.random.default_rng(0)
    n_pt, n_pz, n_ea = 14, 16, 5
    pt_edges = np.linspace(0, 4.5, n_pt + 1)
    pz_edges = np.linspace(1.5, 60, n_pz + 1)
    ea_edges = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 2.0])
    assert len(ea_edges) == n_ea + 1

    flux_pt = rng.uniform(5e-4, 7e-4, n_pt)
    pot, nnuc = 1.2e21, 3.2e30
    c = np.full((n_pt, n_pz, n_ea), 1.0)

    # 2D truth counts, then split across Eavail by an arbitrary fractional shape
    U2d = rng.uniform(10, 1000, (n_pt, n_pz))
    frac = rng.uniform(0.1, 1.0, (n_pt, n_pz, n_ea))
    frac /= frac.sum(axis=2, keepdims=True)          # sum over Eavail = 1
    U3d = U2d[:, :, None] * frac

    xsec3d, _ = extract_cross_section_3d(
        U3d, c, flux_pt, pot, nnuc, pt_edges, pz_edges, ea_edges)
    xsec2d_marg = project_eavail_marginal(xsec3d, ea_edges)

    # The analytic 2D cross section from the same U2d (2D Jacobian).
    dpt = np.diff(pt_edges)[:, None]
    dpz = np.diff(pz_edges)[None, :]
    denom2d = 1.0 * flux_pt[:, None] * nnuc * pot * dpt * dpz
    xsec2d_direct = U2d * 1.0e4 / denom2d

    rel = np.abs(xsec2d_marg - xsec2d_direct) / np.abs(xsec2d_direct)
    assert rel.max() < 1e-12, f"marginal mismatch: max rel {rel.max():.2e}"
    print(f"[PASS] Eavail-marginal recovers 2D xsec (max rel diff {rel.max():.2e})")


def test_projection_integral_consistency():
    """sum over a 1D projection * bin width == total xsec-weighted integral
    computed directly, for all three axes."""
    rng = np.random.default_rng(1)
    pt_edges = np.linspace(0, 4.5, 15)
    pz_edges = np.linspace(1.5, 60, 17)
    ea_edges = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 2.0])
    xsec3d = rng.uniform(0, 1e-39, (14, 16, 5))
    dpt, dpz, dea = np.diff(pt_edges), np.diff(pz_edges), np.diff(ea_edges)
    total = (xsec3d * dpt[:, None, None] * dpz[None, :, None]
             * dea[None, None, :]).sum()
    for axis, dwidth in [("pt", dpt), ("pz", dpz), ("eavail", dea)]:
        _, y = project_axis(xsec3d, pt_edges, pz_edges, ea_edges, axis)
        assert abs((y * dwidth).sum() - total) / total < 1e-12
    print("[PASS] 1D projections integrate to the same total on all 3 axes")


if __name__ == "__main__":
    test_marginal_recovers_2d()
    test_projection_integral_consistency()
    print("all xsec_3d self-tests passed")
