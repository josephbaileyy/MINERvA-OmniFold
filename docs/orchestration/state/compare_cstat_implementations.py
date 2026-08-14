"""C_stat comparator (OI-121): element-wise comparison of two blind implementations.

Lane D. **THIS MODULE CONSTRUCTS NO COVARIANCE.** It ingests two finished artifacts and
compares them. The moment a comparator produces its own covariance it stops being able to
referee the two that exist, so there is deliberately no estimator in this file -- the only
matrices it ever creates are synthetic gaussians under --self-test, which exist to prove the
harness can fail and never touch a GATE5_REPLICA_XSEC.npz.

Thresholds and their justification are PREDECLARED in
docs/orchestration/COMPARATOR-PREDECLARATION-20260814-cstat.md, committed before either
artifact existed. A tolerance chosen after seeing the diff is not a test. Do not edit the two
constants below in response to an observed disagreement; a disagreement is the finding.

Mutation coverage -- for every check here, the perturbation that must make it fail -- is
executable in probe-cstat-comparator-mutations-20260814.py. A check nobody has made fail is
not evidence (BEN-173, BEN-180, BEN-185).
"""
import argparse
import hashlib
import json
import sys

import numpy as np

# --- predeclared thresholds. See section 1 of the predeclaration for the derivation. -------
# Floor: 50 terms x eps = 1.1e-14 worst case, so 1e-12 is ~90x headroom above any legitimate
# BLAS-vs-loop or pairwise-vs-naive summation difference.
# Ceiling: ddof=0 vs ddof=1 is exactly 49/50 = 0.98 -- every element 2.00% LOW relative to the
# ddof=1 value (2.04% high the other way; state the denominator or omit the percentage). A
# physics tolerance (~1e-3) would wave that through; 1e-12 catches it by ten orders of magnitude.
TOL_DIAG_REL = 1e-12    # relative, on the variances
TOL_CORR_ABS = 1e-12    # absolute, on the correlation matrix -- see below for why not relative

# Off-diagonal terms (x_i - xbar)(y_i - ybar) have mixed signs, so their relative error scales
# as ~n*eps/|rho| and DIVERGES as a pair's correlation approaches zero. Dividing by
# sqrt(A_ii*A_jj) removes the 1/|rho| exactly, leaving a uniform ~n*eps across all entries.
# That is why the off-diagonal criterion is absolute-on-the-correlation, not relative.

FROZEN_BIN_ORDER = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"
CANONICAL_PT_EDGES = np.array(
    [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30.0],
    dtype=float)
CANONICAL_PPARALLEL_EDGES = np.array(
    [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0,
     40.0, 60.0, 120.0], dtype=float)
N_PT, N_PP = len(CANONICAL_PT_EDGES) - 1, len(CANONICAL_PPARALLEL_EDGES) - 1
N_CELLS = N_PT * N_PP                       # 15 x 19 = 285
N_REPLICAS = 50

# What each builder's artifact must carry. The comparator cannot compare what nobody emitted,
# so this list is a SPEC REQUIREMENT, not a convenience -- it is routed to C as such.
# Names follow lane B's REQUIREMENTS-20260814-cstat-assembly-conventions.md, which is reasoned
# from assemble_ctotal_bkgsub.py -- the code that actually consumes the object -- rather than from
# the comparison. That is the right authority and it overrides the names I first guessed
# (cov/ddof/centring/replica_seeds).
REQUIRED_KEYS = ("C_stat", "reported_mask", "cv", "edges_pt", "edges_pparallel",
                 "layout_fingerprint", "central_sha256", "n_replicas", "replica_ids", "dof",
                 "rank_at_1em10_lambda_max", "ravel_order", "centering", "units",
                 # both promoted to REQUIRED on lane D's argument, 2026-08-14:
                 "member_sha256",                    # residual risk 4.B1 -- the shared output root
                 "asymmetry_before_symmetrisation")  # else the symmetry check is vacuous
OPTIONAL_KEYS = ("C_stat_reduced", "n_replicas_reported", "method_declaration",
                 "mean_vector", "nominal_vector")

# SHAPE IS DELIBERATELY NOT PINNED YET. C has not ruled on §3.1: full-grid (285,285)+mask, reduced
# (n_reported,n_reported), or both. Rather than hold the realignment and then rewrite twice, the
# shape is DERIVED from the shipped mask and either form is accepted and recorded. When C rules,
# this tightens to one line instead of a rewrite.
EXPECTED_CENTERING = "replica_mean"
EXPECTED_RAVEL_ORDER = "C"


def verify_constants_against_loader(repo_root=None):
    """The canonical edges above are a COPY of fullevent_fps_dataloader.py:64-69.

    A copy that nobody re-checks is a stale value waiting to happen: if the frozen grid ever
    moves, this harness would go on validating builders against the old one and reporting
    tier-0 PASS. Importing the loader would cost a TensorFlow import, so the source literals
    are parsed with `ast` instead -- no import, no TF, and the rule is executable rather than
    a comment asking someone to remember. Returns a dict; `ok` False is a hard failure.
    """
    import ast
    import pathlib
    # this file lives at <root>/docs/orchestration/state/, so the root is parents[3]
    root = pathlib.Path(repo_root) if repo_root else pathlib.Path(__file__).resolve().parents[3]
    src = root / "nd-unfolding" / "pet" / "fullevent_fps_dataloader.py"
    out = {"loader": str(src), "found": src.is_file()}
    if not out["found"]:
        out["ok"] = False
        out["why"] = "loader not found; cannot verify the copied constants"
        return out
    tree = ast.parse(src.read_text())
    lit = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id in ("CANONICAL_PT_EDGES",
                                                    "CANONICAL_PPARALLEL_EDGES"):
                for a in ast.walk(node.value):
                    if isinstance(a, ast.List):
                        lit[t.id] = [float(ast.literal_eval(e)) for e in a.elts]
                        break
    out["parsed"] = sorted(lit)
    out["pt_matches"] = lit.get("CANONICAL_PT_EDGES") == CANONICAL_PT_EDGES.tolist()
    out["pparallel_matches"] = (lit.get("CANONICAL_PPARALLEL_EDGES")
                                == CANONICAL_PPARALLEL_EDGES.tolist())
    out["ok"] = bool(out["pt_matches"] and out["pparallel_matches"])
    if not out["ok"]:
        out["why"] = ("the frozen grid in the loader no longer matches this harness's copy; "
                      "N_CELLS and every tier-0 edge check are STALE")
    return out


def cell_ij(flat):
    """Flat pt-major index -> (i_pt, i_pparallel). Unreadable indices hide findings."""
    return int(flat) // N_PP, int(flat) % N_PP


def _fmt(flat_i, flat_j):
    a, b = cell_ij(flat_i), cell_ij(flat_j)
    return f"[{flat_i},{flat_j}] = (i_pt={a[0]},i_pp={a[1]}) x (i_pt={b[0]},i_pp={b[1]})"


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def load_artifact(path):
    """Read one builder's .npz. Fails LOUD on a missing required key rather than defaulting --
    a missing key is UNRESOLVED, which is not agreement."""
    z = np.load(path, allow_pickle=False)
    art = {"_path": str(path), "_sha256": sha256_file(path), "_keys": sorted(z.files)}
    missing = [k for k in REQUIRED_KEYS if k not in z.files]
    art["_missing_required"] = missing
    for k in REQUIRED_KEYS + OPTIONAL_KEYS:
        if k in z.files:
            v = z[k]
            art[k] = v.item() if v.shape == () else np.asarray(v)
    z.close()
    return art


# ---------------------------------------------------------------------------------------
# TIER 0 -- identity and comparability. EXACT. No tolerance anywhere in this function.
# ---------------------------------------------------------------------------------------
def tier0_identity(a, b):
    checks, fails = {}, []

    def chk(name, ok, detail=""):
        checks[name] = {"pass": bool(ok), "detail": detail}
        if not ok:
            fails.append(name)

    for art, tag in ((a, "A"), (b, "B")):
        chk(f"{tag}_required_keys_present", not art["_missing_required"],
            f"missing={art['_missing_required']}")

    if a["_missing_required"] or b["_missing_required"]:
        return {"checks": checks, "fails": fails, "comparable": False}

    ca, cb = np.asarray(a["C_stat"]), np.asarray(b["C_stat"])
    chk("shape_equal", ca.shape == cb.shape, f"A={ca.shape} B={cb.shape}")
    # Shape is NOT pinned to (285,285) pending C's REQUIREMENTS §3.1 ruling; it is required to be
    # square and consistent with the shipped mask, which is true under either convention.
    nrep = int(np.asarray(a["reported_mask"], bool).sum()) if "reported_mask" in a else None
    chk("shape_square_and_mask_consistent",
        ca.shape[0] == ca.shape[1] and ca.shape[0] in ({N_CELLS} | ({nrep} if nrep else set())),
        f"A={ca.shape} allowed=(285,285) or ({nrep},{nrep})")
    chk("dtype_float64", ca.dtype == np.float64 and cb.dtype == np.float64,
        f"A={ca.dtype} B={cb.dtype}")

    # ravel_order is the anti-silent-reshape declaration. Two implementations disagreeing on C-
    # vs F-order produce covariances that are both symmetric, both PSD, and both wrong --
    # invisible to every structural check (measured: mutations M3/M10). Assert the STRING, and
    # separately assert the layout_fingerprint, which binds it to the edges.
    for art, tag in ((a, "A"), (b, "B")):
        ro = art.get("ravel_order")
        ro = ro.decode() if isinstance(ro, bytes) else str(ro)
        chk(f"{tag}_ravel_order_C", ro == EXPECTED_RAVEL_ORDER, f"got={ro!r}")
    chk("layout_fingerprint_equal",
        str(a.get("layout_fingerprint")) == str(b.get("layout_fingerprint")),
        f"A={str(a.get('layout_fingerprint'))[:16]} B={str(b.get('layout_fingerprint'))[:16]}")
    chk("reported_mask_bit_identical",
        np.array_equal(np.asarray(a["reported_mask"], bool),
                       np.asarray(b["reported_mask"], bool)),
        "assemble_ctotal_bkgsub.py:105-107 fails closed on exactly this")

    # The paper-grid substitution is survivable and silent; assert_extended_fps_edges exists
    # in the loader for exactly this reason. Re-assert it here on each builder's own edges.
    for art, tag in ((a, "A"), (b, "B")):
        chk(f"{tag}_edges_pt_canonical",
            np.array_equal(np.asarray(art["edges_pt"], float), CANONICAL_PT_EDGES))
        chk(f"{tag}_edges_pparallel_canonical",
            np.array_equal(np.asarray(art["edges_pparallel"], float),
                           CANONICAL_PPARALLEL_EDGES))
        chk(f"{tag}_n_replicas", int(art["n_replicas"]) == N_REPLICAS,
            f"got={art.get('n_replicas')}")

    chk("dof_declared_and_equal", int(a["dof"]) == int(b["dof"]),
        f"A={a.get('dof')} B={b.get('dof')}")
    cen = (str(a["centering"]), str(b["centering"]))
    chk("centering_declared_and_equal", cen[0] == cen[1], f"A={cen[0]!r} B={cen[1]!r}")

    return {"checks": checks, "fails": fails, "comparable": not fails}


# ---------------------------------------------------------------------------------------
# TIER 1 -- properties each matrix must have ON ITS OWN. Not a comparison.
# ---------------------------------------------------------------------------------------
def tier1_structure(m, tag, n_replicas=N_REPLICAS):
    m = np.asarray(m, float)

    # Finiteness FIRST, and return before any spectral work. Found by mutation M7: with a NaN
    # present, eigvalsh raises LinAlgError("Eigenvalues did not converge") and takes the whole
    # comparison down with a traceback instead of reporting a clean finiteness failure. A
    # harness that crashes on a bad input has not checked that input -- it has abstained, and
    # a crash is far too easy to read as "the run broke" rather than "the artifact is bad".
    if not np.isfinite(m).all():
        return {"finite": False, "n_nonfinite": int((~np.isfinite(m)).sum()),
                "spectral_checks_skipped": "matrix is not finite; eigvalsh would not converge",
                "fails": [f"{tag}_finite"]}

    ev = np.linalg.eigvalsh((m + m.T) / 2.0)
    lmax = float(np.max(np.abs(ev))) if ev.size else 0.0
    neg_tol = -np.finfo(float).eps * max(lmax, 1.0) * m.shape[0]
    asym = float(np.max(np.abs(m - m.T))) if m.size else 0.0
    diag = np.diag(m)
    # Symmetry is checked SCALED, not bit-exact. The standard formulations (np.cov, an explicit
    # Xc.T @ Xc) do come out bitwise symmetric -- element (i,j) and (j,i) are the same dot
    # product accumulated in the same order -- but a blocked/tiled BLAS is not obliged to, and
    # a false alarm here is exactly the "train everyone to ignore the check" failure the
    # predeclaration argues against. The raw max asymmetry is reported either way, so a
    # bit-exact result is still visible as one.
    dg = np.clip(diag, 0, None)
    sc = float(np.max(np.sqrt(np.outer(dg, dg)))) if dg.size else 0.0
    asym_scaled = (asym / sc) if sc > 0 else asym
    rank = int(np.linalg.matrix_rank(m))
    # rank <= n-1 mean-centred, <= n nominal-centred. A matrix reporting FULL rank on 50
    # replicas in 285 dimensions has been silently regularised, and that must be DECLARED.
    out = {
        "finite": bool(np.isfinite(m).all()),
        "n_nonfinite": int((~np.isfinite(m)).sum()),
        "symmetric_max_abs_asymmetry": asym,
        "symmetric_scaled_asymmetry": float(asym_scaled),
        "symmetric_bit_exact": bool(asym == 0.0),
        "symmetric": bool(asym_scaled <= TOL_CORR_ABS),
        "diag_min": float(diag.min()) if diag.size else None,
        "diag_nonnegative": bool((diag >= 0).all()),
        "measured_rank": rank,
        "rank_ceiling_mean_centred": n_replicas - 1,
        "rank_ceiling_nominal_centred": n_replicas,
        "rank_within_replica_ceiling": rank <= n_replicas,
        "eig_min": float(ev.min()) if ev.size else None,
        "eig_max": float(ev.max()) if ev.size else None,
        "n_eig_below_negative_tol": int((ev < neg_tol).sum()),
        "negative_eig_tol": neg_tol,
        "n_structurally_zero_rows": int((~m.any(axis=1)).sum()),
    }
    out["fails"] = [k for k, v in (
        (f"{tag}_finite", out["finite"]),
        (f"{tag}_symmetric", out["symmetric"]),
        (f"{tag}_diag_nonnegative", out["diag_nonnegative"]),
        (f"{tag}_rank_within_replica_ceiling", out["rank_within_replica_ceiling"]),
        (f"{tag}_no_negative_eigenvalues", out["n_eig_below_negative_tol"] == 0),
    ) if not v]
    return out


# ---------------------------------------------------------------------------------------
# TIER 2 -- the element-wise comparison. This is the tier the whole design exists for.
# ---------------------------------------------------------------------------------------
def tier2_elementwise(ca, cb):
    ca, cb = np.asarray(ca, float), np.asarray(cb, float)
    d = np.abs(ca - cb)

    wa = int(np.argmax(d))
    wa_ij = np.unravel_index(wa, d.shape)
    worst_abs = float(d[wa_ij])

    denom = np.maximum(np.abs(ca), np.abs(cb))
    rel = np.zeros_like(d)
    np.divide(d, denom, out=rel, where=denom > 0)
    wr_ij = np.unravel_index(int(np.argmax(rel)), rel.shape)
    worst_rel = float(rel[wr_ij])

    # Correlation-scaled: the uniform criterion (see the module header). Where a bin is
    # structurally zero the scale is 0 and no relative statement is possible -- those entries
    # are held to EXACT equality instead, which is the strictest available and costs nothing.
    dg = np.diag(ca).copy()
    scale = np.sqrt(np.outer(np.clip(dg, 0, None), np.clip(dg, 0, None)))
    live = scale > 0
    cs = np.zeros_like(d)
    np.divide(d, scale, out=cs, where=live)
    wc_ij = np.unravel_index(int(np.argmax(cs)), cs.shape) if cs.size else (0, 0)
    worst_corr = float(cs[wc_ij])

    # Structurally-zero entries: a 0.0 == 0.0 agreement is free and must not inflate the
    # headline. Report the restricted fraction beside the global one so the gap is visible.
    both_zero = (ca == 0.0) & (cb == 0.0)
    nontrivial = ~both_zero
    exact_zero_mismatch = ((ca == 0.0) ^ (cb == 0.0))

    within = (cs <= TOL_CORR_ABS) | (~live & (d == 0.0))
    diag_idx = np.arange(ca.shape[0])
    dd = np.abs(ca[diag_idx, diag_idx] - cb[diag_idx, diag_idx])
    ddn = np.maximum(np.abs(ca[diag_idx, diag_idx]), np.abs(cb[diag_idx, diag_idx]))
    drel = np.zeros_like(dd)
    np.divide(dd, ddn, out=drel, where=ddn > 0)
    worst_diag_rel = float(drel.max()) if drel.size else 0.0
    worst_diag_cell = cell_ij(int(np.argmax(drel))) if drel.size else None

    n_tot = int(d.size)
    n_nontrivial = int(nontrivial.sum())
    out = {
        "worst_absolute": {"value": worst_abs, "index": _fmt(*wa_ij),
                           "A": float(ca[wa_ij]), "B": float(cb[wa_ij])},
        "worst_relative": {"value": worst_rel, "index": _fmt(*wr_ij),
                           "A": float(ca[wr_ij]), "B": float(cb[wr_ij])},
        "worst_correlation_scaled": {"value": worst_corr, "index": _fmt(*wc_ij),
                                     "A": float(ca[wc_ij]), "B": float(cb[wc_ij]),
                                     "scale": float(scale[wc_ij])},
        "worst_diagonal_relative": {"value": worst_diag_rel, "cell": worst_diag_cell},
        "n_elements": n_tot,
        "n_both_exactly_zero": int(both_zero.sum()),
        "n_nontrivial": n_nontrivial,
        "agreement_fraction_global": float(within.sum()) / n_tot if n_tot else 1.0,
        "agreement_fraction_nontrivial": (float((within & nontrivial).sum()) / n_nontrivial
                                          if n_nontrivial else None),
        "n_exact_zero_vs_nonzero_mismatch": int(exact_zero_mismatch.sum()),
        "tol_corr_abs": TOL_CORR_ABS,
        "tol_diag_rel": TOL_DIAG_REL,
    }
    out["fails"] = [k for k, v in (
        ("offdiag_correlation_scaled_within_tol", worst_corr <= TOL_CORR_ABS),
        ("diagonal_relative_within_tol", worst_diag_rel <= TOL_DIAG_REL),
        ("no_exact_zero_vs_nonzero_mismatch", out["n_exact_zero_vs_nonzero_mismatch"] == 0),
    ) if not v]
    return out


# ---------------------------------------------------------------------------------------
# TIER 3 -- redundant with tier 2 by construction. Kept because these are the numbers that
# actually reach the note, and a disagreement HERE is the one that matters.
# ---------------------------------------------------------------------------------------
def tier3_derived(ca, cb):
    ca, cb = np.asarray(ca, float), np.asarray(cb, float)

    # Same M7 lesson as tier 1, and it recurred here because I fixed the first site and not
    # the sibling -- the exact asymmetry this campaign keeps filing (BEN-173). Each function
    # guards ITSELF rather than trusting the caller to have checked.
    if not (np.isfinite(ca).all() and np.isfinite(cb).all()):
        return {"skipped": "one or both matrices are not finite; spectral work not attempted",
                "fails": ["tier3_skipped_nonfinite_input"]}

    def rel(x, y):
        m = max(abs(x), abs(y))
        return abs(x - y) / m if m > 0 else 0.0

    ta, tb = float(np.trace(ca)), float(np.trace(cb))
    sa, sb = np.sqrt(np.clip(np.diag(ca), 0, None)), np.sqrt(np.clip(np.diag(cb), 0, None))
    dsig = np.abs(sa - sb)
    nsig = np.maximum(sa, sb)
    rsig = np.zeros_like(dsig)
    np.divide(dsig, nsig, out=rsig, where=nsig > 0)
    ea = np.linalg.eigvalsh((ca + ca.T) / 2.0)
    eb = np.linalg.eigvalsh((cb + cb.T) / 2.0)
    de = np.abs(ea - eb)
    # Eigenvalues are compared ABSOLUTELY, scaled by |lambda_max| -- NOT relatively.
    # C_stat has rank <= 49 in 285 dimensions, so ~236 of its eigenvalues are numerically zero
    # (measured: 236 of 285 below 1e-10*|lambda_max|). A RELATIVE metric divides by ~1e-18 and
    # returns ~1.0 for ANY pair of matrices, including two bit-identical spectra: the first
    # version of this line reported 1.000e+00 for a PERMUTATION, which is a similarity
    # transform and provably preserves the spectrum. The metric was wrong, not the mutation.
    lmax = float(np.max(np.abs(ea))) if ea.size else 0.0
    re_ = de / lmax if lmax > 0 else de

    out = {
        "trace": {"A": ta, "B": tb, "relative_difference": rel(ta, tb)},
        "sqrt_trace": {"A": float(np.sqrt(max(ta, 0.0))), "B": float(np.sqrt(max(tb, 0.0))),
                       "relative_difference": rel(np.sqrt(max(ta, 0.0)),
                                                  np.sqrt(max(tb, 0.0)))},
        "per_bin_sigma_worst_relative": {
            "value": float(rsig.max()) if rsig.size else 0.0,
            "cell": cell_ij(int(np.argmax(rsig))) if rsig.size else None},
        "eigenvalue_spectrum_worst_abs_over_lambda_max": float(re_.max()) if re_.size else 0.0,
        "lambda_max": lmax,
        "n_eigenvalues_numerically_zero": int((np.abs(ea) < 1e-10 * lmax).sum()) if lmax else 0,
    }
    out["fails"] = [k for k, v in (
        ("trace_within_tol", out["trace"]["relative_difference"] <= TOL_DIAG_REL),
        ("per_bin_sigma_within_tol",
         out["per_bin_sigma_worst_relative"]["value"] <= TOL_DIAG_REL),
        ("eigenvalue_spectrum_within_tol",
         out["eigenvalue_spectrum_worst_abs_over_lambda_max"] <= TOL_DIAG_REL),
    ) if not v]
    return out


# ---------------------------------------------------------------------------------------
# TIER 4 -- the input lists. The ONLY part of the residual-risk set that this comparison can
# CLOSE rather than merely name: it converts "both builders read the same 50 correct files"
# from an assumption into a measurement. See predeclaration 4.B1 / 4.B2.
# ---------------------------------------------------------------------------------------
def tier4_inputs(a, b):
    def strs(v):
        v = np.asarray(v).ravel()
        return [x.decode() if isinstance(x, bytes) else str(x) for x in v]

    ma, mb = strs(a.get("member_sha256", [])), strs(b.get("member_sha256", []))
    sa = np.asarray(a.get("replica_ids", [])).ravel().tolist()
    sb = np.asarray(b.get("replica_ids", [])).ravel().tolist()
    out = {
        "n_members": {"A": len(ma), "B": len(mb)},
        "member_sha256_lists_identical": ma == mb,
        "member_sha256_symmetric_difference": sorted(set(ma) ^ set(mb))[:10],
        "seeds_identical": sa == sb,
        "seeds_distinct_A": len(set(sa)) == len(sa),
        "seeds_distinct_B": len(set(sb)) == len(sb),
        "n_distinct_seeds_A": len(set(sa)),
    }
    out["fails"] = [k for k, v in (
        ("member_count_is_50", len(ma) == N_REPLICAS and len(mb) == N_REPLICAS),
        ("member_sha256_lists_identical", out["member_sha256_lists_identical"]),
        ("seeds_identical", out["seeds_identical"]),
        ("seeds_distinct", out["seeds_distinct_A"] and out["seeds_distinct_B"]),
    ) if not v]
    return out


def validate_single_artifact(art, repo_root=None, replica_dir=None):
    """SINGLE-ARTIFACT validation — the load-bearing path since the second builder was cancelled
    on 2026-08-14 (predeclaration banner; §4.F).

    Organised by the ONLY thing that matters once there is nothing to compare against: whether a
    check has power over an EXTERNAL fact, or merely re-reads the builder's own declarations.
    `BEN-186`'s lesson generalises — an artifact validated against its own metadata proves the
    builder was self-consistent, which is real and is not what anyone wants.

    Externally-powered checks recompute the declared value from an independent source. Everything
    else is labelled `self_declared` so a reader cannot mistake it for verification.
    """
    import pathlib
    root = pathlib.Path(repo_root) if repo_root else pathlib.Path(__file__).resolve().parents[3]
    ext, dec, fails = {}, {}, []

    def E(name, ok, detail=""):
        ext[name] = {"pass": bool(ok), "detail": detail, "power": "external"}
        if not ok:
            fails.append(name)

    def D(name, ok, detail=""):
        dec[name] = {"pass": bool(ok), "detail": detail,
                     "power": "self-declared -- proves consistency, not correctness"}
        if not ok:
            fails.append(name)

    missing = [k for k in REQUIRED_KEYS if k not in art or art.get(k) is None]
    if missing:
        return {"verdict": "UNRESOLVED", "missing_required": missing,
                "why": "required keys absent; this is NOT a pass"}

    c = np.asarray(art["C_stat"], float)
    mask = np.asarray(art["reported_mask"], bool).ravel()
    n_rep = int(mask.sum())

    # --- EXTERNAL: the frozen grid, re-asserted against the loader's own literals -------------
    E("edges_pt_canonical",
      np.array_equal(np.asarray(art["edges_pt"], float), CANONICAL_PT_EDGES))
    E("edges_pparallel_canonical",
      np.array_equal(np.asarray(art["edges_pparallel"], float), CANONICAL_PPARALLEL_EDGES))
    E("harness_constants_match_loader", verify_constants_against_loader(root)["ok"])

    # --- EXTERNAL: layout_fingerprint RECOMPUTED, not trusted -------------------------------
    # This is the single cheapest conversion of a declaration into a check. Reuses the production
    # function (fps_provenance.layout_fingerprint) rather than restating its payload, so a change
    # to the construction cannot silently desynchronise this from the thing it validates.
    try:
        sys.path.insert(0, str(root / "nd-unfolding"))
        import fps_provenance as FP
        recomputed = FP.layout_fingerprint(np.asarray(art["edges_pt"], float),
                                           np.asarray(art["edges_pparallel"], float))
        E("layout_fingerprint_recomputed", str(art["layout_fingerprint"]) == recomputed,
          f"declared={str(art['layout_fingerprint'])[:16]} recomputed={recomputed[:16]}")
        ext["mask_fingerprint_recomputed"] = {
            "value": FP.mask_fingerprint(mask), "power": "external",
            "note": "reported for adoption checking; NOT required to equal the canonical FPS "
                    "value -- require_reported_mask hard-codes 266 and would reject a correct "
                    "262-cell PET mask (lane B's REQUIREMENTS §0.1)"}
    except Exception as exc:                                   # noqa: BLE001
        E("layout_fingerprint_recomputed", False, f"could not recompute: {exc}")

    # --- EXTERNAL: which known mask is this? -------------------------------------------------
    known = {262: "PET nominal reported set (state/pet-nominal-reported-cells-20260814.json)",
             266: "canonical FPS lgbm mask (fps_reported_mask.json)"}
    ext["mask_identity"] = {"n_reported": n_rep, "matches_known_count": known.get(n_rep),
                            "power": "external",
                            "note": "262 is a strict subset of 266, verified in "
                                    "state/cstat-mask-nesting-262-in-266-20260814.json"}
    E("mask_is_full_grid_length", mask.size == N_CELLS, f"got {mask.size}, expected {N_CELLS}")

    # --- EXTERNAL: shape must follow the MASK, not a declaration ----------------------------
    # Shape is not pinned pending C's §3.1 ruling; either accepted form is recorded, and the
    # covariance is required to be consistent with the mask the builder itself shipped.
    full, reduced = c.shape == (N_CELLS, N_CELLS), c.shape == (n_rep, n_rep)
    E("shape_consistent_with_shipped_mask", full or reduced,
      f"C_stat {c.shape}; mask implies (285,285) or ({n_rep},{n_rep})")
    ext["shape_form"] = {"value": "full-grid" if full else ("reduced" if reduced else "neither"),
                         "power": "external", "pending": "C's REQUIREMENTS §3.1 ruling"}

    # --- EXTERNAL: the reduction, if both forms shipped -------------------------------------
    # Closes the object gap of BEN-185: if the compared object is the full grid but the PUBLISHED
    # object is the reduction, the reduction is verified by nobody. One numpy line, and under one
    # builder it is one of the few checks that can fail on a genuine arithmetic mistake.
    if "C_stat_reduced" in art and art["C_stat_reduced"] is not None and full:
        red = np.asarray(art["C_stat_reduced"], float)
        idx = np.flatnonzero(mask)
        E("reduced_equals_full_restricted_to_mask",
          red.shape == (n_rep, n_rep) and np.array_equal(red, c[np.ix_(idx, idx)]),
          f"reduced {red.shape} vs expected ({n_rep},{n_rep})")
    elif full:
        ext["reduced_form_absent"] = {
            "power": "n/a",
            "note": "no C_stat_reduced shipped, so the reduction to the published object is "
                    "OUTSIDE the verified scope (BEN-185 shape)"}

    # --- EXTERNAL: rank, measured rather than read ------------------------------------------
    t1 = tier1_structure(c, "artifact", n_replicas=int(art["n_replicas"]))
    if t1.get("finite"):
        ev = np.linalg.eigvalsh((c + c.T) / 2.0)
        lmax = float(np.max(np.abs(ev)))
        measured = int((np.abs(ev) >= 1e-10 * lmax).sum()) if lmax > 0 else 0
        E("rank_matches_declared", measured == int(art["rank_at_1em10_lambda_max"]),
          f"declared={art['rank_at_1em10_lambda_max']} measured={measured}")
        E("rank_within_replica_ceiling", measured <= int(art["n_replicas"]),
          f"measured={measured} n_replicas={art['n_replicas']}")
    fails += [f for f in t1["fails"] if f not in fails]

    # --- EXTERNAL: member digests recomputed from disk (the strongest check here) ------------
    declared = [x.decode() if isinstance(x, bytes) else str(x)
                for x in np.asarray(art["member_sha256"]).ravel()]
    if replica_dir:
        rd = pathlib.Path(replica_dir)
        found = sorted(rd.rglob("GATE5_REPLICA_XSEC.npz"))
        actual = [sha256_file(p) for p in found]
        E("member_digests_match_disk", sorted(declared) == sorted(actual),
          f"declared {len(declared)}, found {len(actual)} on disk")
        E("member_count_is_n_replicas", len(actual) == int(art["n_replicas"]))
    else:
        ext["member_digests_not_recomputed"] = {
            "power": "NONE", "note": "no --replica-dir given; the declared digests were NOT "
                                     "checked against disk, which is the whole point of the field"}
    E("member_digests_distinct", len(set(declared)) == len(declared),
      f"{len(set(declared))} distinct of {len(declared)}")
    ids = np.asarray(art["replica_ids"]).ravel().tolist()
    E("replica_ids_distinct", len(set(ids)) == len(ids))

    # --- EXTERNAL-ish: symmetry BEFORE symmetrisation ---------------------------------------
    # Post-symmetrisation symmetry is vacuous: the spec instructs builders to symmetrise, so it
    # holds by construction on every artifact forever. The informative number is the one that was
    # symmetrised away, which is why it is a REQUIRED field.
    asym = float(art["asymmetry_before_symmetrisation"])
    E("presymmetrisation_asymmetry_is_roundoff", asym <= 1e-9,
      f"{asym:.3e} -- existing gates demand <= 1e-9; a value far above is a real bug that "
      f"symmetrising hides")
    ext["presymmetrisation_asymmetry"] = {"value": asym, "power": "external"}

    # --- SELF-DECLARED: consistency only ----------------------------------------------------
    D("dof_equals_n_replicas_minus_1",
      int(art["dof"]) == int(art["n_replicas"]) - 1, f"dof={art['dof']} n={art['n_replicas']}")
    D("centering_as_specified", str(art["centering"]) == EXPECTED_CENTERING,
      f"got {art['centering']!r}")
    D("ravel_order_C", str(art["ravel_order"]) == EXPECTED_RAVEL_ORDER)
    D("n_replicas_matches_ids", len(ids) == int(art["n_replicas"]))

    return {
        "verdict": "PASS" if not fails else "FAIL",
        "fails": fails,
        "externally_powered": ext,
        "self_declared_only": dec,
        "structure": t1,
        "SCOPE": (
            "NOTHING HERE HAS POWER OVER THE COVARIANCE VALUES. Every element could be wrong by a "
            "factor, or computed from the wrong 50 vectors in the right files, and every check "
            "above still passes. With one builder there is no independent recomputation; see "
            "COMPARATOR-PREDECLARATION-20260814-cstat.md sec 4.F."),
        "single_builder": True,
    }


def compare(a, b):
    """Three-branch verdict. UNRESOLVED is NOT agreement and must never be reported as one."""
    t0 = tier0_identity(a, b)
    report = {"tier0_identity": t0}
    if not t0["comparable"]:
        report["verdict"] = "UNRESOLVED"
        report["verdict_why"] = ("tier 0 failed: the two artifacts are not comparable. This is "
                                 "NOT agreement and NOT disagreement.")
        report["tier0_fails"] = t0["fails"]
        return report

    ca, cb = np.asarray(a["C_stat"], float), np.asarray(b["C_stat"], float)
    t1a, t1b = tier1_structure(ca, "A"), tier1_structure(cb, "B")
    t2 = tier2_elementwise(ca, cb)
    t3 = tier3_derived(ca, cb)
    t4 = tier4_inputs(a, b)
    report.update({"tier1_structure_A": t1a, "tier1_structure_B": t1b,
                   "tier2_elementwise": t2, "tier3_derived": t3, "tier4_inputs": t4})
    fails = t1a["fails"] + t1b["fails"] + t2["fails"] + t3["fails"] + t4["fails"]
    report["all_fails"] = fails
    report["verdict"] = "AGREE" if not fails else "DISAGREE"
    report["verdict_why"] = ("every tier passed" if not fails
                             else f"{len(fails)} check(s) failed: {fails}")
    return report


def _print(report):
    print(f"\n=== VERDICT: {report['verdict']} -- {report['verdict_why']} ===")
    t2 = report.get("tier2_elementwise")
    if t2:
        print(f"  worst |A-B|           : {t2['worst_absolute']['value']:.6e}  at "
              f"{t2['worst_absolute']['index']}")
        print(f"  worst relative        : {t2['worst_relative']['value']:.6e}  at "
              f"{t2['worst_relative']['index']}")
        print(f"  worst corr-scaled     : {t2['worst_correlation_scaled']['value']:.6e}  "
              f"(tol {TOL_CORR_ABS:.0e})  at {t2['worst_correlation_scaled']['index']}")
        print(f"  worst diag relative   : {t2['worst_diagonal_relative']['value']:.6e}  "
              f"(tol {TOL_DIAG_REL:.0e})")
        print(f"  agreement  global     : {t2['agreement_fraction_global']:.9f}  "
              f"({t2['n_both_exactly_zero']} entries are 0==0 and are FREE)")
        af = t2['agreement_fraction_nontrivial']
        print(f"  agreement  nontrivial : "
              f"{'n/a' if af is None else format(af, '.9f')}   <-- the honest number")
        print(f"  exact 0-vs-nonzero    : {t2['n_exact_zero_vs_nonzero_mismatch']}")
    for t in ("tier1_structure_A", "tier1_structure_B"):
        if t in report:
            r = report[t]
            print(f"  {t}: rank={r['measured_rank']} (ceiling {r['rank_ceiling_mean_centred']}"
                  f"/{r['rank_ceiling_nominal_centred']}) symmetric={r['symmetric']} "
                  f"finite={r['finite']} neg_eig={r['n_eig_below_negative_tol']}")


def _self_test():
    """Synthetic gaussians only. Proves the harness RUNS and that M0 (B := A) passes.
    The failing directions are the mutation probe's job, not this function's."""
    rng = np.random.default_rng(20260814)
    x = rng.normal(size=(N_REPLICAS, N_CELLS))
    c = np.cov(x, rowvar=False, ddof=1)
    art = {"_path": "<synthetic>", "_sha256": "n/a", "_missing_required": [],
           "C_stat": c, "ravel_order": EXPECTED_RAVEL_ORDER,
           "reported_mask": np.ones(N_CELLS, bool), "layout_fingerprint": "f" * 64,
           "edges_pt": CANONICAL_PT_EDGES,
           "edges_pparallel": CANONICAL_PPARALLEL_EDGES, "n_replicas": N_REPLICAS,
           "dof": N_REPLICAS - 1, "centering": EXPECTED_CENTERING,
           "replica_ids": np.arange(N_REPLICAS),
           "member_sha256": np.array([f"{i:064x}" for i in range(N_REPLICAS)])}
    b = dict(art)
    b["C_stat"] = c.copy()
    rep = compare(art, b)
    _print(rep)
    assert rep["verdict"] == "AGREE", "M0 negative control failed: harness rejects B == A"
    print("\nM0 negative control OK: an identical pair is reported AGREE.")
    return rep


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a", help="builder 1 artifact (.npz)")
    p.add_argument("--b", help="builder 2 artifact (.npz)")
    p.add_argument("--out", help="write the receipt JSON here")
    p.add_argument("--self-test", action="store_true",
                   help="run against synthetic gaussians; touches no campaign product")
    args = p.parse_args(argv)

    if args.self_test:
        rep = _self_test()
    else:
        if not (args.a and args.b):
            p.error("--a and --b are required unless --self-test")
        a, b = load_artifact(args.a), load_artifact(args.b)
        rep = compare(a, b)
        rep["artifacts"] = {"A": {"path": a["_path"], "sha256": a["_sha256"]},
                            "B": {"path": b["_path"], "sha256": b["_sha256"]}}
        _print(rep)

    rep["predeclaration"] = "docs/orchestration/COMPARATOR-PREDECLARATION-20260814-cstat.md"
    rep["comparator_built_no_covariance"] = True
    if args.out:
        with open(args.out, "w") as f:
            json.dump(rep, f, indent=1, sort_keys=True, default=str)
        print(f"\nreceipt -> {args.out}")
    return 0 if rep["verdict"] == "AGREE" else 1


if __name__ == "__main__":
    sys.exit(main())
