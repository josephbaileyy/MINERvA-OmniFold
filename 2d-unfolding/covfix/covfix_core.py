"""COVFIX shared math (COVFIX-DECLARATION.md rev 11.4, bound by COVFIX-BINDING-1 at M_C1 90b29087).

One implementation of the declaration's fixed rules, imported by P0 and, later, by the P2 builders and the PV readout:
  carry_factor / carry      section 2, V(t) = D_t V D_t with D_t = diag(x_t / x_R), refused unless finite and nonzero
  psd_check                 section 3.1 / 6.2 C-PSD, lambda_min >= -1e-12 lambda_max
  eig_basis                 section 5.2, eigh (numpy, or scipy 'evr' for the section 8 comparison), descending; exact
                            ties canonicalised by Gram-Schmidt of the ordered cell axes; each vector's largest-magnitude
                            component positive
  kept_mask                 section 2, lambda_i > 1e-12 lambda_1(V_F), referenced to the candidate's fluctuation block
  band_of                   section 2 / 5.2, R1 = ranks 1-73, R2 = 74-139, R3 >= 140; a cluster of adjacent eigenvalues
                            each within 1e-9 relative of its neighbour that straddles an edge goes whole to the band of
                            its first (lowest-rank) member; a band is used only with >= 10 kept modes
  guard / label             section 2, h = t_{0.975, N-1} SE with SE = sd(psi, ddof 1) / sqrt(N); over < 0.8,
                            covers [0.8, 1.25], under > 1.25, read only when [X - h, X + h] lies inside one interval
  mode_readings             section 2, z, m_i, v_i, q_i (divisor N), M and its band means with their guards
  residual_rule             section 5.2, the directed residual ||(I - P_new,kept) U_ref,well||_2 against 0.1
  cut_diagnostic            section 5.2, the kept sets and the reference's kept modes outside the new kept span
  jsonable                  a record with every non-finite float as null, for strict JSON

One matrix representation: every covariance is used as its symmetric part (C + C^T) / 2 for the C-PSD check, the cut
and the readings; the raw asymmetry is printed by psd_check and barred by nothing (the declaration states no bar).

MEASURES: nothing by itself. CANNOT AUTHORIZE: any reading, bar or wording; the bars live in the declaration.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import linalg as sl
from scipy import stats

RANK_CUT = 1e-12          # section 2: kept iff lambda_i > 1e-12 lambda_1(V_F)
WELL_CUT = 1e-6           # section 5.2: well-determined iff lambda_i >= 1e-6 lambda_1(F_ref)
NEAR_TIE = 1e-9           # section 5.2: band assignment only
PSD_TOL = 1e-12           # section 3.1 / 6.2
RESIDUAL_MAX = 0.1        # section 5.2
OUTSIDE_SPAN = 1e-6       # cut diagnostic: a mode counts as outside a span above this residual (REGRADE's convention)
BAND_EDGES = (("R1", 1, 73), ("R2", 74, 139), ("R3", 140, None))
BAND_MIN = 10
LABEL_LO, LABEL_HI = 0.8, 1.25
EPS = float(np.finfo(np.float64).eps)


class Refusal(RuntimeError):
    """A declared refusal: the reading (or carry) that needs this input is refused, recorded unrepaired."""


def sym(C: np.ndarray) -> np.ndarray:
    C = np.asarray(C, np.float64)
    return 0.5 * (C + C.T)


# ------------------------------------------------------------------------------------------------ section 2: carry
def carry_factor(x_t: np.ndarray, x_R: np.ndarray) -> np.ndarray:
    """d = x_t / x_R on every aligned cell; refused unless every entry is finite and nonzero (section 2)."""
    x_t, x_R = np.asarray(x_t, np.float64), np.asarray(x_R, np.float64)
    if x_t.shape != x_R.shape or x_t.ndim != 1:
        raise Refusal(f"carry: shapes {x_t.shape} and {x_R.shape} are not one aligned vector")
    with np.errstate(divide="ignore", invalid="ignore"):
        d = x_t / x_R
    bad = ~np.isfinite(d) | (d == 0)
    if np.any(bad):
        raise Refusal(f"carry: D_t is not finite and nonzero at cells {np.flatnonzero(bad).tolist()}")
    return d


def carry(V: np.ndarray, d: np.ndarray) -> np.ndarray:
    """D V D with D = diag(d)."""
    d = np.asarray(d, np.float64)
    return d[:, None] * np.asarray(V, np.float64) * d[None, :]


def absolute(C_rel: np.ndarray, x: np.ndarray) -> np.ndarray:
    """diag(x) C_rel diag(x): C_model_abs(x) (section 2), the form cov2d_blocks.assemble uses."""
    return carry(C_rel, x)


# ------------------------------------------------------------------------------------------------- C-PSD
def psd_check(C: np.ndarray, name: str) -> dict:
    """lambda_min >= -1e-12 lambda_max over the symmetric part's eigenvalues; the raw asymmetry is printed."""
    C = np.asarray(C, np.float64)
    lam = np.linalg.eigvalsh(sym(C))
    top = float(lam[-1])
    scale = float(np.max(np.abs(C))) if np.any(C) else 0.0
    rec = {"name": name, "lambda_min": float(lam[0]), "lambda_max": top,
           "lambda_min_over_max": float(lam[0] / top) if top > 0 else None,
           "asymmetry_rel": float(np.max(np.abs(C - C.T)) / scale) if scale > 0 else 0.0}
    rec["pass"] = bool(lam[0] >= -PSD_TOL * top)
    return rec


# ------------------------------------------------------------------------------------------ the eigenbasis
def _sign_fix(U: np.ndarray) -> np.ndarray:
    idx = np.argmax(np.abs(U), axis=0)
    s = np.sign(U[idx, np.arange(U.shape[1])])
    s[s == 0] = 1.0
    return U * s


GS_NULL = 100.0 * EPS      # a tied-space Gram-Schmidt residual at or below this fraction of its own projection is null


def _canonical_tied(U: np.ndarray) -> np.ndarray:
    """The ordered cell axes e_1, e_2, ... projected into span(U) and orthonormalised in that order, skipping null
    projections, until span(U) is spanned (section 5.2). Done in span(U)'s own coordinates: P e_j = U c_j with
    c_j = U[j, :], so every accepted vector is U times an orthonormal k-vector and cannot leave span(U). Two
    orthogonalisation passes. The null test is relative to the projection itself: e_j is skipped when its projection is
    exactly zero, or when orthogonalisation leaves at most GS_NULL = 100 eps of its own norm (it lies in the span already
    built, to roundoff). A small but genuine projection is therefore kept in its order."""
    n, k = U.shape
    B = []
    for j in range(n):
        c = np.array(U[j, :], dtype=np.float64)
        n0 = float(np.linalg.norm(c))
        if n0 == 0.0:
            continue
        for _ in range(2):
            for b in B:
                c = c - (b @ c) * b
        nc = float(np.linalg.norm(c))
        if nc > GS_NULL * n0:
            B.append(c / nc)
            if len(B) == k:
                break
    if len(B) != k:
        raise Refusal(f"tied eigenspace: Gram-Schmidt spanned {len(B)} of {k} dimensions")
    return U @ np.column_stack(B)


def tie_groups(lam: np.ndarray) -> list:
    """[(i, j), ...]: the index ranges [i, j) of descending eigenvalues that are exactly equal, length >= 2."""
    out, i = [], 0
    while i < lam.size:
        j = i + 1
        while j < lam.size and lam[j] == lam[i]:
            j += 1
        if j - i > 1:
            out.append((i, j))
        i = j
    return out


def eig_basis(V: np.ndarray, driver: str = "numpy") -> tuple[np.ndarray, np.ndarray]:
    """(lambda descending, U) of V's symmetric part, exact ties canonicalised, signs fixed (section 5.2). ``driver`` is
    "numpy" (the grading solver) or "evr" (scipy, for section 8's agreement control), post-processed identically."""
    S = sym(V)
    if driver == "numpy":
        lam, U = np.linalg.eigh(S)
    elif driver == "evr":
        lam, U = sl.eigh(S, driver="evr")
    else:
        raise ValueError(driver)
    order = np.argsort(lam, kind="stable")[::-1]
    lam, U = lam[order], U[:, order]
    for i, j in tie_groups(lam):
        U[:, i:j] = _canonical_tied(U[:, i:j])
    return lam, _sign_fix(U)


def lambda_1(V: np.ndarray) -> float:
    """The largest eigenvalue from the grading solver's own routine (np.linalg.eigh), so a cut referenced to it uses the
    same spectrum the readings use: when V is V_F, lambda_1(V_F) is exactly the graded lambda_1."""
    return float(np.linalg.eigh(sym(V))[0][-1])


def kept_mask(lam: np.ndarray, lam1_F: float) -> np.ndarray:
    """lambda_i > 1e-12 lambda_1(V_F) (section 2)."""
    return np.asarray(lam) > RANK_CUT * float(lam1_F)


def band_of(lam_kept: np.ndarray) -> np.ndarray:
    """Band index (0, 1, 2 for R1, R2, R3) per kept mode, descending order, near-tie clusters assigned whole to the
    band of their first (lowest-rank) member. Clusters chain through adjacent gaps of at most 1e-9 relative."""
    lam_kept = np.asarray(lam_kept, np.float64)
    n = lam_kept.size
    rank = np.arange(1, n + 1)
    band = np.full(n, 2)
    band[rank <= 139] = 1
    band[rank <= 73] = 0
    start = 0
    for i in range(1, n + 1):
        if i == n or abs(lam_kept[i - 1] - lam_kept[i]) > NEAR_TIE * max(abs(lam_kept[i - 1]), abs(lam_kept[i])):
            band[start:i] = band[start]
            start = i
    return band


def bands_used(band: np.ndarray) -> dict:
    """{name: {"n": count, "used": n >= 10}} for R1-R3."""
    return {name: {"n": int(np.sum(band == b)), "used": bool(np.sum(band == b) >= BAND_MIN)}
            for b, (name, _, _) in enumerate(BAND_EDGES)}


# ---------------------------------------------------------------------------------------- guard and labels
def guard(psi: np.ndarray, X: float | None = None, labelled: bool = True) -> dict:
    """h = t_{0.975, N-1} SE with SE = sd(psi, ddof 1) / sqrt(N), psi the per-toy influence term (section 2). X is
    mean(psi) for M and the total band means; for a spread, X is the spread itself and psi its delta-method
    influence term (mean zero), with ``labelled`` False because only a normalised spread (F~) carries a label.
    A zero or non-finite SE refuses. The interval is approximate for quadratic toy scores (section 2)."""
    psi = np.asarray(psi, np.float64)
    n = psi.size
    X = float(psi.mean()) if X is None else float(X)
    se = float(psi.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    if not (math.isfinite(se) and se > 0):
        return {"X": X if math.isfinite(X) else None, "SE": se if math.isfinite(se) else None, "h": None,
                "refused": "zero or non-finite SE"}
    h = float(stats.t.ppf(0.975, n - 1) * se)
    out = {"X": X, "SE": se, "h": h, "upper": X + h, "coverage": "approximate for quadratic toy scores (section 2)"}
    if labelled:
        out["label"] = label(X, h)
    return out


def label(X: float, h: float) -> str:
    """Section 2's labels on [X - h, X + h]."""
    lo, hi = X - h, X + h
    if hi < LABEL_LO:
        return "over"
    if lo >= LABEL_LO and hi <= LABEL_HI:
        return "covers"
    if lo > LABEL_HI:
        return "under"
    touched = [name for name, hit in (("over", lo < LABEL_LO), ("covers", lo <= LABEL_HI and hi >= LABEL_LO),
                                      ("under", hi > LABEL_HI)) if hit]
    return "unresolved across " + "/".join(touched)


# ---------------------------------------------------------------------------------------- per-mode readings
def mode_readings(E: np.ndarray, V: np.ndarray, V_F: np.ndarray, driver: str = "numpy") -> dict:
    """Section 2's per-mode readings of the errors E (N x n) against V, kept under V_F's lambda_1. Refused if no mode
    is kept. Band statistics are given for used bands only; a dropped band is named with its count."""
    E = np.asarray(E, np.float64)
    N = E.shape[0]
    lam, U = eig_basis(V, driver)
    lamF1 = lambda_1(V_F)
    keep = kept_mask(lam, lamF1)
    ndf = int(keep.sum())
    if ndf == 0:
        raise Refusal("readings: no kept mode")
    lk, Uk = lam[keep], U[:, keep]
    Z = (E @ Uk) / np.sqrt(lk)
    m = Z.mean(axis=0)
    v = ((Z - m) ** 2).mean(axis=0)
    q = (Z ** 2).mean(axis=0)
    band = band_of(lk)
    chi2 = np.sum(Z * Z, axis=1)
    infl = (Z - m) ** 2 - v                                   # the spread's per-toy influence terms
    out = {"N": N, "ndf": ndf, "lambda_F1": lamF1, "lambda_kept": lk, "m": m, "v": v, "q": q, "band": band,
           "exact_tie_groups_kept": len(tie_groups(lk)),
           "identity_q_m2_v_max_abs": float(np.max(np.abs(q - m * m - v))),
           "M": guard(chi2 / ndf), "M_split": {"mean_part": float(np.sum(m * m) / ndf), "spread_part": float(np.sum(v) / ndf)},
           "F": guard(infl.sum(axis=1) / ndf, X=float(v.mean()), labelled=False), "bands": {}}
    for b, (name, _, _) in enumerate(BAND_EDGES):
        sel = band == b
        nb = int(sel.sum())
        if nb >= BAND_MIN:
            out["bands"][name] = {"n": nb, "used": True, "Q_R": float(q[sel].mean()), "F_R": float(v[sel].mean()),
                                  "B_R": float((m[sel] ** 2).mean()),
                                  "guard": guard(np.sum(Z[:, sel] ** 2, axis=1) / nb),
                                  "guard_F_R": guard(infl[:, sel].sum(axis=1) / nb, X=float(v[sel].mean()),
                                                     labelled=False)}
        else:
            out["bands"][name] = {"n": nb, "used": False, "dropped": f"{name} holds {nb} kept modes, fewer than {BAND_MIN}"}
    out["_Z"], out["_U"] = Z, Uk
    return out


def evr_agreement(E: np.ndarray, V: np.ndarray, V_F: np.ndarray, rd: dict, unresolved: float = 0.01) -> dict:
    """Section 8 / T2A's descriptive precision readout: the same readings with scipy's 'evr' driver, post-processed by
    the same canonical basis rule; per rank d_k = max(|b_k - b_k'|, |f_k - f_k'|) / (b_k + f_k), b = m^2, f = v.
    Ranks are compared only where the two drivers' exact-tie partitions agree: a rank in a tie group that the other
    driver does not reproduce exactly is listed as partition-differs (its individual mode is not matched). A rank
    with b_k + f_k = 0 has no d_k and is counted. A refused evr reading is a diagnostic here, not a stop."""
    rec = {"ndf_numpy": rd["ndf"]}
    try:
        r2 = mode_readings(E, V, V_F, driver="evr")
    except Refusal as e:
        rec |= {"ndf_evr": 0, "note": f"the evr reading is refused ({e}); no per-rank comparison is made"}
        return rec
    rec["ndf_evr"] = r2["ndf"]
    if r2["ndf"] != rd["ndf"]:
        rec["note"] = "the two drivers keep different counts; no per-rank comparison is made"
        return rec
    g1, g2 = set(tie_groups(rd["lambda_kept"])), set(tie_groups(r2["lambda_kept"]))
    differs = np.zeros(rd["ndf"], bool)
    for i, j in g1 ^ g2:
        differs[i:j] = True
    b1, f1, b2, f2 = rd["m"] ** 2, rd["v"], r2["m"] ** 2, r2["v"]
    den = b1 + f1
    ok = (den > 0) & ~differs
    d = np.maximum(np.abs(b1 - b2), np.abs(f1 - f2))[ok] / den[ok]
    ranks = np.flatnonzero(ok) + 1
    rec.update(max_d=float(d.max()) if d.size else None, unresolved_ranks=[int(r) for r in ranks[d > unresolved]],
               ranks_without_d=int(((den <= 0) & ~differs).sum()),
               partition_differs_ranks=[int(r) for r in np.flatnonzero(differs) + 1], unresolved_threshold=unresolved,
               lambda_rel_diff_max=float(np.max(np.abs(r2["lambda_kept"] / rd["lambda_kept"] - 1))))
    return rec


# ----------------------------------------------------------------------------------- section 5.2: residual rule
def _kept_basis(V: np.ndarray, V_F: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lam, U = eig_basis(V)
    return lam, U, kept_mask(lam, lambda_1(V_F))


def _modes(rank_mask: np.ndarray, lam: np.ndarray, res: np.ndarray, **flags) -> list:
    idx = np.flatnonzero(rank_mask)
    return [{"rank": int(i + 1), "lambda": float(lam[i]), "residual": float(r),
             **{k: bool(f[i]) for k, f in flags.items()}} for i, r in zip(idx, res)]


def residual_rule(V_ref: np.ndarray, F_ref: np.ndarray, V_new: np.ndarray, F_new: np.ndarray) -> dict:
    """Section 5.2's rule. The trigger is the directed residual ||(I - P_new,kept) U_ref,well||_2 of the reference's
    well-determined modes (lambda_i >= 1e-6 lambda_1(F_ref)) outside the new matrix's kept span: it fires iff it
    exceeds 0.1. Printed, not barred:
      directed_angle_deg      arcsin(residual): reference well-determined span -> new kept span
      well_spans_max_angle_deg  the maximum principal angle between the two well-determined spans (the new one under
                              1e-6 lambda_1(F_new)), as section 3.1 prints it
      the ndf difference, and every reference mode below the well-determined cut with its rank, lambda, residual
      outside the new kept span, and whether the reference keeps it."""
    lam_r, U_r = eig_basis(V_ref)
    lamF1 = lambda_1(F_ref)
    well = lam_r >= WELL_CUT * lamF1
    kept_r = kept_mask(lam_r, lamF1)
    lam_n, U_n = eig_basis(V_new)
    lamF1n = lambda_1(F_new)
    kept_n = kept_mask(lam_n, lamF1n)
    well_n = lam_n >= WELL_CUT * lamF1n
    Uk = U_n[:, kept_n]
    Uw = U_r[:, well]
    R = Uw - Uk @ (Uk.T @ Uw)
    resid = float(np.linalg.norm(R, 2)) if Uw.shape[1] else 0.0
    tail = ~well
    Rt = np.linalg.norm(U_r[:, tail] - Uk @ (Uk.T @ U_r[:, tail]), axis=0)
    ww = (float(principal_angles_deg(Uw, U_n[:, well_n]).max()) if Uw.shape[1] and well_n.any() else None)
    return {"n_well": int(well.sum()), "n_well_new": int(well_n.sum()), "ndf_ref": int(kept_r.sum()),
            "ndf_new": int(kept_n.sum()), "ndf_difference": int(kept_n.sum() - kept_r.sum()), "residual": resid,
            "directed_angle_deg": float(np.degrees(np.arcsin(min(resid, 1.0)))),
            "well_spans_max_angle_deg": ww, "fires": bool(resid > RESIDUAL_MAX), "bar": RESIDUAL_MAX,
            "below_well_modes": _modes(tail, lam_r, Rt, ref_kept=kept_r),
            "below_well_max_residual": float(Rt.max()) if Rt.size else None}


def cut_diagnostic(V_ref: np.ndarray, F_ref: np.ndarray, V_new: np.ndarray, F_new: np.ndarray) -> dict:
    """Section 5.2's cut diagnostic of V_new against V_ref, each kept set under its own fluctuation block's lambda_1."""
    lam_r, U_r, kr = _kept_basis(V_ref, F_ref)
    lam_n, U_n, kn = _kept_basis(V_new, F_new)
    Uk = U_n[:, kn]
    res = np.linalg.norm(U_r[:, kr] - Uk @ (Uk.T @ U_r[:, kr]), axis=0)
    outside = res > OUTSIDE_SPAN
    out_mask = np.zeros_like(kr)
    out_mask[np.flatnonzero(kr)[outside]] = True
    return {"ndf_ref": int(kr.sum()), "ndf_new": int(kn.sum()), "outside_span_threshold": OUTSIDE_SPAN,
            "kept_ref_lambda": lam_r[kr], "kept_new_lambda": lam_n[kn],
            "ref_kept_outside_new_kept_span": _modes(out_mask, lam_r, res[outside]),
            "n_ref_kept_outside_new_kept_span": int(outside.sum()),
            "max_residual_of_ref_kept_modes": float(res.max()) if res.size else None,
            "new_smallest_kept": float(lam_n[kn].min()) if kn.any() else None,
            "new_largest_dropped": float(lam_n[~kn].max()) if (~kn).any() else None}


def principal_angles_deg(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Principal angles between span(A) and span(B), in degrees, largest first (scipy.linalg.subspace_angles)."""
    return np.degrees(sl.subspace_angles(np.asarray(A, np.float64), np.asarray(B, np.float64)))


# ------------------------------------------------------------------------------------------------ strict JSON
def jsonable(o):
    """The record with numpy types converted and every non-finite float as None (JSON null)."""
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return float(o) if math.isfinite(float(o)) else None
    if o is None or isinstance(o, str):
        return o
    raise TypeError(type(o))
