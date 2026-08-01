#!/usr/bin/env python3
"""Per-PPFX-universe flux integrals for the ND/5D kernels.

The cross section divides by the integrated flux Phi(pT), so the flux uncertainty
enters the measurement mainly through that 1/Phi normalization. A Flux systematic
universe must therefore divide by *its own* integral Phi_u, not the CV one; using
Phi_CV in every universe is the Task #70 bug, and it does not fail loudly -- it
just quietly understates the flux covariance.

`2d-unfolding/unfold_2d_omnifold_unbinned.py:load_flux_universe_bins` is the
correct reference implementation. This module is its ND port, factored so that
the ND/5D kernels share ONE guarded implementation instead of each repeating the
`d["flux"]` / `cv["flux"]` shortcut (AUDIT-FINDINGS-20260731 J28: three of those
sites are separate implementations, not one call path, so a single kernel fix
does not reach them).

Two things the ND path needs that the 2D reference does not:

  * The extended (FPS) pT grid carries more bins than the flux histogram, so the
    universe integrals must be remapped onto the analysis grid by the SAME
    bin-centre lookup the CV flux already uses. Asking the 14-bin histogram for
    bin `b+1` of a 15-bin grid reads its overflow, the `>0` validity test fails,
    and the scale silently stays at 1 for the final `[4.5,30]` bin (J29).
    `flux_ref_index` is that one shared remap, used by CV and universes alike.
  * The throw and sweep drivers work from saved per-universe ratio banks rather
    than from the ROOT file, so the same guards must hold for a banked table.

Everything here fails closed. A missing file, a missing histogram, a CV that
disagrees with the analysis CV, an out-of-range universe index, or a
non-positive integral raises -- none of them fall back to CV flux.

The ROOT import is deliberately local to the reader so that the arithmetic and
every guard can be exercised (and regression-tested) without a ROOT build; the
reader also accepts an `.npz` carrying the same two arrays, which is what the
synthetic-slab tests drive.
"""
import os

import numpy as np

FLUX_CV_KEY = "hFluxCV"
FLUX_UNIV_KEY = "hFluxUniv"

# Max fractional disagreement tolerated between the universe file's own CV and
# the analysis CV flux before we declare them different flux productions. Same
# threshold as the 2D reference.
CV_MATCH_RTOL = 1e-6

BANKED_RATIO_NAME = "flux_univ_ratio.npy"


# --------------------------------------------------------------------------- grid
def flux_ref_index(pt_edges, ref_edges):
    """Reference flux bin containing each analysis pT bin's centre.

    The integrated flux is pT-independent within the reference binning (constant
    per bin), so a bin-centre lookup is exact; bins beyond the histogram range
    fall back to the last reference bin. This reproduces the CV remap in
    `unfold_nd_omnifold_unbinned` verbatim -- that is the point of having it
    here, since CV and universe must ride the *same* mapping.
    """
    pt_edges = np.asarray(pt_edges, float)
    ref_edges = np.asarray(ref_edges, float)
    if pt_edges.ndim != 1 or pt_edges.size < 2:
        raise ValueError(f"pt_edges must be a 1D edge array, got shape {pt_edges.shape}")
    if ref_edges.ndim != 1 or ref_edges.size < 2:
        raise ValueError(f"ref_edges must be a 1D edge array, got shape {ref_edges.shape}")
    n_ref = ref_edges.size - 1
    ctrs = 0.5 * (pt_edges[:-1] + pt_edges[1:])
    return np.clip(np.digitize(ctrs, ref_edges) - 1, 0, n_ref - 1)


def flux_on_target_grid(values_ref, pt_edges, ref_edges=None):
    """Remap a per-reference-pT-bin flux quantity onto the analysis pT grid.

    With `ref_edges` given, every analysis bin takes the reference bin holding
    its centre (the identity when the two grids agree bin-for-bin). With
    `ref_edges` None the grids must already agree in length, else this raises
    rather than guess a correspondence.
    """
    values_ref = np.asarray(values_ref, float)
    n_pt = len(np.asarray(pt_edges, float)) - 1
    if ref_edges is None:
        if values_ref.size != n_pt:
            raise RuntimeError(
                f"[FAIL] flux-universe file has {values_ref.size} pT bins but the "
                f"analysis grid expects {n_pt}, and no reference pT edges were "
                "supplied to remap them. Pass ref_edges (u2d.PT_EDGES) so the "
                "universe rides the same bin-centre remap as the CV flux.")
        return values_ref.copy()
    if len(np.asarray(ref_edges, float)) - 1 != values_ref.size:
        raise RuntimeError(
            f"[FAIL] reference pT edges describe {len(np.asarray(ref_edges, float)) - 1} "
            f"bins but the flux histogram has {values_ref.size}")
    return values_ref[flux_ref_index(pt_edges, ref_edges)]


# --------------------------------------------------------------------------- read
def read_flux_universe_table(path):
    """(phi_cv, phi_univ) on the flux histogram's own binning, fail-closed.

    Accepts the production ROOT file (`hFluxCV` TH1D [n_ref], `hFluxUniv` TH2D
    [n_ref x n_univ], built by uq/build_flux_universe_band.py) or an `.npz`
    carrying the same two arrays under the same keys. Returns phi_cv (n_ref,)
    and phi_univ (n_univ, n_ref) -- universe-major, so `phi_univ[u]` is one
    universe's flux over pT.
    """
    if not path or not os.path.exists(path):
        raise RuntimeError(
            f"[FAIL] per-universe flux file {path!r} is missing; refusing to "
            "produce a Flux universe against the CV flux integral. Build it with "
            "uq/build_flux_universe_band.py. (Dividing a flux universe by the CV "
            "flux integral silently re-introduces the Task #70 bug.)")
    if path.endswith(".npz"):
        with np.load(path) as z:
            missing = [k for k in (FLUX_CV_KEY, FLUX_UNIV_KEY) if k not in z.files]
            if missing:
                raise RuntimeError(f"[FAIL] {path} missing {'/'.join(missing)}")
            phi_cv = np.asarray(z[FLUX_CV_KEY], float)
            phi_univ = np.asarray(z[FLUX_UNIV_KEY], float)
        if phi_univ.ndim != 2:
            raise RuntimeError(f"[FAIL] {path}:{FLUX_UNIV_KEY} must be 2D, got {phi_univ.shape}")
        # stored [n_ref x n_univ] to mirror the TH2D; return universe-major
        if phi_univ.shape[0] == phi_cv.size:
            phi_univ = phi_univ.T
        elif phi_univ.shape[1] != phi_cv.size:
            raise RuntimeError(
                f"[FAIL] {path}: {FLUX_UNIV_KEY}{phi_univ.shape} has no axis matching "
                f"{FLUX_CV_KEY} ({phi_cv.size} pT bins)")
        return phi_cv, phi_univ

    import ROOT
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(
            f"[FAIL] could not open per-universe flux file {path}; refusing to "
            "produce a Flux universe against the CV flux integral")
    try:
        hcv = f.Get(FLUX_CV_KEY)
        huniv = f.Get(FLUX_UNIV_KEY)
        if not hcv or not huniv:
            raise RuntimeError(f"[FAIL] {path} missing {FLUX_CV_KEY}/{FLUX_UNIV_KEY}")
        n_ref, n_univ = huniv.GetNbinsX(), huniv.GetNbinsY()
        if hcv.GetNbinsX() != n_ref:
            raise RuntimeError(
                f"[FAIL] {path}: {FLUX_CV_KEY} has {hcv.GetNbinsX()} pT bins but "
                f"{FLUX_UNIV_KEY} has {n_ref}")
        phi_cv = np.asarray([hcv.GetBinContent(b + 1) for b in range(n_ref)], float)
        phi_univ = np.asarray(
            [[huniv.GetBinContent(b + 1, u + 1) for b in range(n_ref)]
             for u in range(n_univ)], float)
    finally:
        f.Close()
    return phi_cv, phi_univ


# ------------------------------------------------------------------- universe Phi
def _check_cv_match(phi_cv_target, cv_flux_bins, path):
    """Universe file and analysis CV must come from the same flux production."""
    cv_flux_bins = np.asarray(cv_flux_bins, float)
    if cv_flux_bins.shape != phi_cv_target.shape:
        raise RuntimeError(
            f"[FAIL] flux-universe file CV has {phi_cv_target.size} pT bins after "
            f"remap but the analysis CV flux has {cv_flux_bins.size}")
    scale = max(float(np.abs(cv_flux_bins).max()), 1e-300)
    max_rel = float(np.abs(phi_cv_target - cv_flux_bins).max() / scale)
    if max_rel > CV_MATCH_RTOL:
        raise RuntimeError(
            f"[FAIL] flux-universe file CV disagrees with the analysis CV flux "
            f"(max rel diff {max_rel:.2e}); they are not from the same flux "
            f"production. Rebuild {path} against the same playlists as --mcfile.")


def _check_positive(phi, label, path):
    bad = ~np.isfinite(phi) | (phi <= 0.0)
    if np.any(bad):
        where = np.argwhere(bad)[:8].tolist()
        raise RuntimeError(
            f"[FAIL] {path}: {label} has {int(bad.sum())}/{phi.size} non-finite or "
            f"non-positive flux integrals (first at {where}). A zero universe "
            "integral cannot be normalized away silently -- that is exactly how "
            "the extended pT bin kept CV flux (J29); fix the flux file.")


def flux_universe_bins(path, idx, pt_edges, cv_flux_bins, ref_edges=None):
    """Phi_u (m^-2/POT) for PPFX universe `idx` on the analysis pT grid.

    ND port of `unfold_2d_omnifold_unbinned.load_flux_universe_bins`, with the
    reference-grid remap folded in. Column/row `idx` is the PPFX universe index,
    the same throw as `w_{truth,reco}_Flux_idx` in the omnifile. Guards that the
    file's own CV matches `cv_flux_bins` so universe and CV come from the same
    flux production.
    """
    phi_cv_ref, phi_univ_ref = read_flux_universe_table(path)
    idx = int(idx)
    n_univ = phi_univ_ref.shape[0]
    if not 0 <= idx < n_univ:
        raise RuntimeError(f"[FAIL] Flux universe idx {idx} out of range [0,{n_univ})")
    phi_u = flux_on_target_grid(phi_univ_ref[idx], pt_edges, ref_edges)
    phi_cv = flux_on_target_grid(phi_cv_ref, pt_edges, ref_edges)
    _check_positive(phi_u, f"{FLUX_UNIV_KEY}[u={idx}]", path)
    _check_cv_match(phi_cv, cv_flux_bins, path)
    return phi_u


def flux_universe_ratio_table(path, pt_edges, cv_flux_bins, ref_edges=None):
    """r[u, b] = Phi_u(b) / Phi_CV(b) for every PPFX universe, analysis grid.

    The whole table at once: the throw drivers pick universes at random and the
    rescale tool needs an arbitrary universe per saved throw, so reopening the
    file per universe would be the wrong shape. Fails closed on any non-positive
    integral rather than leaving that (universe, bin) at the CV ratio of 1.
    """
    phi_cv_ref, phi_univ_ref = read_flux_universe_table(path)
    phi_cv = flux_on_target_grid(phi_cv_ref, pt_edges, ref_edges)
    _check_positive(phi_cv, FLUX_CV_KEY, path)
    _check_cv_match(phi_cv, cv_flux_bins, path)
    idx = None if ref_edges is None else flux_ref_index(pt_edges, ref_edges)
    phi_u = phi_univ_ref if idx is None else phi_univ_ref[:, idx]
    if phi_u.shape[1] != phi_cv.size:
        raise RuntimeError(
            f"[FAIL] {path}: universe table remapped to {phi_u.shape[1]} pT bins "
            f"but the analysis grid has {phi_cv.size}")
    _check_positive(phi_u, FLUX_UNIV_KEY, path)
    return phi_u / phi_cv[None, :]


# ------------------------------------------------------------------- banked table
def _validate_ratio_table(ratio, n_pt, n_flux, source):
    ratio = np.asarray(ratio, float)
    if ratio.ndim != 2:
        raise RuntimeError(f"[FAIL] {source}: flux ratio table must be 2D, got {ratio.shape}")
    if ratio.shape[1] != n_pt:
        raise RuntimeError(
            f"[FAIL] {source}: flux ratio table has {ratio.shape[1]} pT bins but the "
            f"analysis grid has {n_pt}. The bank was built on a different pT binning; "
            "re-dump it or pass the flux-universe file so the remap is redone here.")
    if n_flux is not None and ratio.shape[0] != n_flux:
        raise RuntimeError(
            f"[FAIL] {source}: flux ratio table covers {ratio.shape[0]} universes but "
            f"the bank carries {n_flux} flux weight sets")
    bad = ~np.isfinite(ratio) | (ratio <= 0.0)
    if np.any(bad):
        raise RuntimeError(
            f"[FAIL] {source}: {int(bad.sum())}/{ratio.size} flux ratios are "
            "non-finite or non-positive")
    if np.allclose(ratio, 1.0):
        raise RuntimeError(
            f"[FAIL] {source}: every flux ratio is exactly 1, i.e. every universe "
            "would divide by the CV flux integral. That is the J28/Task #70 bug, "
            "not a valid table -- it is what a missing or unreadable flux-universe "
            "file produces. Rebuild the bank against a readable flux file.")
    return ratio


def load_banked_flux_ratio_table(bank, n_pt, n_flux=None, name=BANKED_RATIO_NAME):
    """Load and validate `<bank>/flux_univ_ratio.npy` (written by unified_throw.py)."""
    path = os.path.join(bank, name)
    if not os.path.exists(path):
        raise RuntimeError(f"[FAIL] {path} is missing")
    return _validate_ratio_table(np.load(path), n_pt, n_flux, path)


def resolve_flux_ratio_table(n_pt, n_flux=None, bank=None, universe_file=None,
                             pt_edges=None, cv_flux_bins=None, ref_edges=None):
    """r[u, b] from the bank if it carries one, else from the flux-universe file.

    Preferring the bank matters operationally: the uthrow banks already store the
    table on their own pT grid, so a normalization fix does not force a re-dump
    of the 142 GB omnifile. Fails closed when neither source is usable -- the one
    outcome that must never be a silent fallback to CV flux.
    """
    errors = []
    if bank:
        try:
            return load_banked_flux_ratio_table(bank, n_pt, n_flux)
        except (RuntimeError, ValueError, OSError) as exc:
            errors.append(str(exc))
    if universe_file:
        if pt_edges is None or cv_flux_bins is None:
            raise RuntimeError(
                "[FAIL] rebuilding the flux ratio table from "
                f"{universe_file} needs pt_edges and cv_flux_bins")
        try:
            table = flux_universe_ratio_table(universe_file, pt_edges, cv_flux_bins,
                                              ref_edges)
            return _validate_ratio_table(table, n_pt, n_flux, universe_file)
        except (RuntimeError, ValueError, OSError) as exc:
            errors.append(str(exc))
    raise RuntimeError(
        "[FAIL] no usable per-universe flux table; refusing to run Flux universes "
        "against the CV flux integral (J28). Tried:\n  "
        + "\n  ".join(errors or ["no bank and no --flux-universe-file given"]))


# ------------------------------------------------------------------- flat rescale
def flat_flux_divisor(ratio_pt, shape):
    """Per-flat-bin divisor that turns a Phi_CV-normalized xsec into a Phi_u one.

    `extract_cross_section_nd` divides by the flux along the pT axis only, so the
    saved xsec is exactly linear in 1/Phi(pT): a universe that wrongly used
    Phi_CV is corrected by dividing flat bin (i0, ...) by r_u[i0]. No
    re-unfolding is needed, because flux normalization enters only at final
    extraction (J28 sizing note).
    """
    ratio_pt = np.asarray(ratio_pt, float)
    shape = tuple(int(s) for s in shape)
    if ratio_pt.ndim != 1 or ratio_pt.size != shape[0]:
        raise ValueError(
            f"ratio_pt has {ratio_pt.size} entries but the pT axis of {shape} is "
            f"{shape[0]}")
    if np.any(~np.isfinite(ratio_pt)) or np.any(ratio_pt <= 0.0):
        raise ValueError("flux ratios must be finite and positive")
    return np.broadcast_to(
        ratio_pt.reshape((shape[0],) + (1,) * (len(shape) - 1)), shape
    ).reshape(-1, order="C").copy()
