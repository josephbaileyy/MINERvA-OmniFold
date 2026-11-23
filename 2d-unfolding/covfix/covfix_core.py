"""COVFIX shared math (COVFIX-DECLARATION.md rev 11.4, bound by COVFIX-BINDING-1 at M_C1 90b29087).

One implementation of the declaration's fixed rules, imported by P0 and, later, by the P2 builders and the PV readout:
  carry_factor / carry      section 2, V(t) = D_t V D_t with D_t = diag(x_t / x_R), refused unless finite and nonzero
  psd_check                 section 3.1 / 6.2 C-PSD, lambda_min >= -1e-12 lambda_max
  eig_basis                 section 5.2, numpy eigh, descending; exact ties canonicalised by Gram-Schmidt of the cell
                            axes; each vector's largest-magnitude component positive
  kept_mask                 section 2, lambda_i > 1e-12 lambda_1(V_F), referenced to the candidate's fluctuation block
  band_of                   section 2 / 5.2, R1 = ranks 1-73, R2 = 74-139, R3 >= 140; a 1e-9 near-tie cluster that
                            straddles an edge goes whole to the lower-rank band; a band needs >= 10 kept modes
  guard / label             section 2, h = t_{0.975, N-1} SE with SE = sd(psi, ddof 1) / sqrt(N); over < 0.8,
                            covers [0.8, 1.25], under > 1.25, read only when [X - h, X + h] lies inside one interval
  mode_readings             section 2, z, m_i, v_i, q_i (divisor N), M and its band means with their guards
  residual_rule             section 5.2, the directed residual ||(I - P_new,kept) U_ref,well||_2 against 0.1
  cut_diagnostic            section 5.2, the kept sets and the reference's kept modes outside the new kept span

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
BAND_EDGES = (("R1", 1, 73), ("R2", 74, 139), ("R3", 140, None))
BAND_MIN = 10
LABEL_LO, LABEL_HI = 0.8, 1.25


class Refusal(RuntimeError):
    """A declared refusal: the reading (or carry) that needs this input is refused, recorded unrepaired."""


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
    """diag(x) C_rel diag(x): C_model_abs(x) (section 2)."""
    return carry(C_rel, x)


# ------------------------------------------------------------------------------------------------- C-PSD
def psd_check(C: np.ndarray, name: str) -> dict:
    """lambda_min >= -1e-12 lambda_max over the symmetrised matrix's eigenvalues; the asymmetry is printed, not barred."""
    C = np.asarray(C, np.float64)
    lam = np.linalg.eigvalsh(0.5 * (C + C.T))
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


def _canonical_tied(U: np.ndarray) -> np.ndarray:
    """The ordered cell axes e_1, e_2, ... projected into span(U) and orthonormalised in that order, skipping null
    projections, until span(U) is spanned (section 5.2)."""
    n, k = U.shape
    out = []
    for j in range(n):
        v = U @ U[j, :]                       # projection of e_j into span(U)
        for w in out:
            v = v - (w @ v) * w
        nv = float(np.linalg.norm(v))
        if nv > 1e-10:
            out.append(v / nv)
            if len(out) == k:
                break
    if len(out) != k:
        raise Refusal(f"tied eigenspace: Gram-Schmidt spanned {len(out)} of {k} dimensions")
    return np.column_stack(out)


def eig_basis(V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(lambda descending, U) from numpy eigh, exact ties canonicalised, signs fixed (section 5.2)."""
    V = np.asarray(V, np.float64)
    lam, U = np.linalg.eigh(V)
    order = np.argsort(lam, kind="stable")[::-1]
    lam, U = lam[order], U[:, order]
    i = 0
    while i < lam.size:
        j = i + 1
        while j < lam.size and lam[j] == lam[i]:
            j += 1
        if j - i > 1:
            U[:, i:j] = _canonical_tied(U[:, i:j])
        i = j
    return lam, _sign_fix(U)


def kept_mask(lam: np.ndarray, lam1_F: float) -> np.ndarray:
    """lambda_i > 1e-12 lambda_1(V_F) (section 2)."""
    return np.asarray(lam) > RANK_CUT * float(lam1_F)


def band_of(lam_kept: np.ndarray) -> np.ndarray:
    """Band index (0, 1, 2 for R1, R2, R3) per kept mode, descending order, near-tie clusters assigned whole to the
    band of their first (lowest-rank) member."""
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
def guard(psi: np.ndarray) -> dict:
    """X = mean(psi), SE = sd(psi, ddof 1) / sqrt(N), h = t_{0.975, N-1} SE. A zero or non-finite SE refuses."""
    psi = np.asarray(psi, np.float64)
    n = psi.size
    X = float(psi.mean())
    se = float(psi.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    if not (math.isfinite(se) and se > 0):
        return {"X": X, "SE": se, "h": None, "refused": "zero or non-finite SE"}
    h = float(stats.t.ppf(0.975, n - 1) * se)
    return {"X": X, "SE": se, "h": h, "label": label(X, h), "upper": X + h}


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
def mode_readings(E: np.ndarray, V: np.ndarray, V_F: np.ndarray) -> dict:
    """Section 2's per-mode readings of the errors E (N x n) against V, kept under V_F's lambda_1."""
    E = np.asarray(E, np.float64)
    N = E.shape[0]
    lam, U = eig_basis(V)
    lamF1 = float(np.linalg.eigvalsh(np.asarray(V_F, np.float64))[-1])
    keep = kept_mask(lam, lamF1)
    lk, Uk = lam[keep], U[:, keep]
    ndf = int(keep.sum())
    Z = (E @ Uk) / np.sqrt(lk)
    m = Z.mean(axis=0)
    v = ((Z - m) ** 2).mean(axis=0)
    q = (Z ** 2).mean(axis=0)
    band = band_of(lk)
    chi2 = np.sum(Z * Z, axis=1)
    out = {"N": N, "ndf": ndf, "lambda_F1": lamF1, "lambda_kept": lk, "m": m, "v": v, "q": q, "band": band,
           "identity_q_m2_v_max_abs": float(np.max(np.abs(q - m * m - v))) if ndf else 0.0,
           "M": guard(chi2 / ndf), "M_split": {"mean_part": float(np.sum(m * m) / ndf), "spread_part": float(np.sum(v) / ndf)},
           "bands": {}}
    for b, (name, _, _) in enumerate(BAND_EDGES):
        sel = band == b
        nb = int(sel.sum())
        rec = {"n": nb, "used": nb >= BAND_MIN}
        if nb:
            rec.update(Q_R=float(q[sel].mean()), F_R=float(v[sel].mean()), B_R=float((m[sel] ** 2).mean()))
        if nb >= BAND_MIN:
            rec["guard"] = guard(np.sum(Z[:, sel] ** 2, axis=1) / nb)
        else:
            rec["dropped"] = f"{name} holds {nb} kept modes, fewer than {BAND_MIN}"
        out["bands"][name] = rec
    out["_Z"], out["_U"] = Z, Uk
    return out


def evr_agreement(E: np.ndarray, V: np.ndarray, V_F: np.ndarray, rd: dict, unresolved: float = 0.01) -> dict:
    """T2A's descriptive precision readout: numpy eigh against scipy eigh(driver='evr') on the same V and E; per rank
    d_k = max(|b_k - b_k'|, |f_k - f_k'|) / (b_k + f_k), with b = m^2 and f = v (sign-invariant)."""
    lam2, V2 = sl.eigh(np.asarray(V, np.float64), driver="evr")
    order = np.argsort(lam2, kind="stable")[::-1]
    lam2, V2 = lam2[order], V2[:, order]
    keep2 = kept_mask(lam2, rd["lambda_F1"])
    rec = {"ndf_numpy": rd["ndf"], "ndf_evr": int(keep2.sum())}
    if rec["ndf_evr"] != rd["ndf"]:
        rec["note"] = "the two drivers keep different counts; no per-rank comparison is made"
        return rec
    Z2 = (np.asarray(E, np.float64) @ V2[:, keep2]) / np.sqrt(lam2[keep2])
    m2 = Z2.mean(axis=0)
    b1, f1 = rd["m"] ** 2, rd["v"]
    b2, f2 = m2 ** 2, ((Z2 - m2) ** 2).mean(axis=0)
    d = np.maximum(np.abs(b1 - b2), np.abs(f1 - f2)) / (b1 + f1)
    rec.update(max_d=float(d.max()), unresolved_ranks=[int(i + 1) for i in np.flatnonzero(d > unresolved)],
               lambda_rel_diff_max=float(np.max(np.abs(lam2[keep2] / rd["lambda_kept"] - 1))))
    return rec


# ----------------------------------------------------------------------------------- section 5.2: residual rule
def _kept_basis(V: np.ndarray, V_F: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lam, U = eig_basis(V)
    lamF1 = float(np.linalg.eigvalsh(np.asarray(V_F, np.float64))[-1])
    return lam, U, kept_mask(lam, lamF1)


def residual_rule(V_ref: np.ndarray, F_ref: np.ndarray, V_new: np.ndarray, F_new: np.ndarray) -> dict:
    """Directed residual of the reference's well-determined modes (lambda_i >= 1e-6 lambda_1(F_ref)) outside the new
    matrix's kept span; fires iff it exceeds 0.1. The maximum principal angle is arcsin of the residual."""
    lam_r, U_r = eig_basis(V_ref)
    lamF1 = float(np.linalg.eigvalsh(np.asarray(F_ref, np.float64))[-1])
    well = lam_r >= WELL_CUT * lamF1
    kept_r = kept_mask(lam_r, lamF1)
    _, U_n, kept_n = _kept_basis(V_new, F_new)
    Uk = U_n[:, kept_n]
    Uw = U_r[:, well]
    R = Uw - Uk @ (Uk.T @ Uw)
    resid = float(np.linalg.norm(R, 2)) if Uw.shape[1] else 0.0
    tail = kept_r & ~well
    Rt = U_r[:, tail] - Uk @ (Uk.T @ U_r[:, tail])
    return {"n_well": int(well.sum()), "ndf_ref": int(kept_r.sum()), "ndf_new": int(kept_n.sum()),
            "ndf_difference": int(kept_n.sum() - kept_r.sum()), "residual": resid,
            "max_principal_angle_deg": float(np.degrees(np.arcsin(min(resid, 1.0)))),
            "fires": bool(resid > RESIDUAL_MAX), "bar": RESIDUAL_MAX,
            "tail_modes": int(tail.sum()),
            "tail_max_residual": float(np.linalg.norm(Rt, axis=0).max()) if tail.any() else None}


def cut_diagnostic(V_ref: np.ndarray, F_ref: np.ndarray, V_new: np.ndarray, F_new: np.ndarray) -> dict:
    """Section 5.2's cut diagnostic of V_new against V_ref, each kept set under its own fluctuation block's lambda_1."""
    lam_r, U_r, kr = _kept_basis(V_ref, F_ref)
    lam_n, U_n, kn = _kept_basis(V_new, F_new)
    Uk = U_n[:, kn]
    res = np.linalg.norm(U_r[:, kr] - Uk @ (Uk.T @ U_r[:, kr]), axis=0)
    return {"ndf_ref": int(kr.sum()), "ndf_new": int(kn.sum()),
            "ref_kept_outside_new_kept_span": int(np.sum(res > 1e-6)),
            "max_residual_of_ref_kept_modes": float(res.max()) if res.size else 0.0,
            "new_smallest_kept": float(lam_n[kn].min()) if kn.any() else None,
            "new_largest_dropped": float(lam_n[~kn].max()) if (~kn).any() else None}


def principal_angles_deg(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Principal angles between span(A) and span(B), in degrees, largest first (scipy.linalg.subspace_angles)."""
    return np.degrees(sl.subspace_angles(np.asarray(A, np.float64), np.asarray(B, np.float64)))
