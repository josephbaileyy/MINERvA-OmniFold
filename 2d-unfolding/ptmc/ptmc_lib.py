#!/usr/bin/env python3
"""PTMC: the pure functions the paired runner and the scorer call (PTMC-DECLARATION.md, r2 and later).

No ROOT, no I/O. Cells are ROOT's (lower edges in, upper edges out), through oofvc_lib.global_index; the 224-cell
vector is in GlobalID = (pT bin - 1) * 16 + (p|| bin - 1) order, the order of ref_c2c1.th2_vector.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np

DATA_OFFSET, SIG_OFFSET, BKG_OFFSET = 0, 10_000_000, 20_000_000  # re2_driver: seed, seed + 1e7, seed + 2e7
N_CELLS = 224
N_REPLICAS = 200
RANK = 50


def digest(*arrays) -> str:
    """sha256 over the arrays' dtype, shape and bytes, in order (C-PAIR's identity)."""
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(np.asarray(a))
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------------------------------- the draws (D2)


def poisson(seed: int, n: int) -> np.ndarray:
    return np.random.default_rng(int(seed)).poisson(1.0, size=int(n)).astype(float)


def expected_factors(b: int, n_data: int, n_orig: int, n_entries: int, appended_entry) -> dict:
    """The factors section 2.2 prescribes for replica b, regenerated independently of the driver: data rows,
    original signal rows, every mc_background entry, and the appended rows (b_bkg at their entries, in order)."""
    app = np.asarray(appended_entry, dtype=np.int64)
    b_bkg = poisson(b + BKG_OFFSET, n_entries)
    if app.size and (app.min() < 0 or app.max() >= n_entries):
        raise ValueError("an appended entry lies outside the background tree")
    return {"data": poisson(b + DATA_OFFSET, n_data), "signal": poisson(b + SIG_OFFSET, n_orig), "bkg": b_bkg,
            "appended": b_bkg[app]}


def draw_check(b, *, n_data, n_entries, appended_entry, inj_entries, inj_cv, signed_w, w_truth_cv, w_reco_cv,
               w_truth_seen, w_reco_seen) -> dict:
    """C-DRAW-R, row level, exact. ``b`` None is a central unit, whose factors are all 1. The signed sample handed to
    the refinement must be [b_data, -inj_cv * b_bkg[inj_entries]]; the MC weights handed to OmniFold must be the CV
    weights times [b_signal, b_bkg[appended_entry]]. Any length mismatch fails."""
    app = np.asarray(appended_entry, dtype=np.int64)
    inj = np.asarray(inj_entries, dtype=np.int64)
    n_sig = int(np.asarray(w_truth_cv).shape[0])
    n_orig = n_sig - app.size
    out = {"n_data": int(n_data), "n_original": int(n_orig), "n_appended": int(app.size), "n_injected": int(inj.size)}
    shapes_ok = (n_orig >= 0 and np.asarray(signed_w).shape == (n_data + inj.size,)
                 and np.asarray(inj_cv).shape == (inj.size,)
                 and all(np.asarray(x).shape == (n_sig,) for x in (w_reco_cv, w_truth_seen, w_reco_seen)))
    if not shapes_ok:
        return {**out, "pass": False, "why": "shapes"}
    if b is None:
        f_data, f_sig, f_inj = np.ones(n_data), np.ones(n_sig), np.ones(inj.size)
    else:
        e = expected_factors(b, n_data, n_orig, n_entries, app)
        if inj.size and (inj.min() < 0 or inj.max() >= n_entries):
            return {**out, "pass": False, "why": "injected entry outside the tree"}
        f_data, f_sig, f_inj = e["data"], np.concatenate([e["signal"], e["appended"]]), e["bkg"][inj]
    want_signed = np.concatenate([np.ones(n_data) * f_data, -(np.asarray(inj_cv, float) * f_inj)])
    checks = {
        "signed": bool(np.array_equal(np.asarray(signed_w, float), want_signed)),
        "w_truth": bool(np.array_equal(np.asarray(w_truth_seen, float), np.asarray(w_truth_cv, float) * f_sig)),
        "w_reco": bool(np.array_equal(np.asarray(w_reco_seen, float), np.asarray(w_reco_cv, float) * f_sig)),
    }
    sums = {"data_sum": float(f_data.sum()), "original_sum": float(f_sig[:n_orig].sum()),
            "appended_sum": float(f_sig[n_orig:].sum()), "injected_sum": float(f_inj.sum()),
            "appended_sha256": digest(app), "factors_sha256": digest(f_data, f_sig, f_inj)}
    return {**out, **sums, "checks": checks, "pass": all(checks.values())}


# ------------------------------------------------------------------------------------- the completeness (2.2)


def cell_sums(gidx, w, mask, n=N_CELLS) -> np.ndarray:
    g = np.asarray(gidx)
    m = np.asarray(mask, bool) & (g >= 0)
    return np.bincount(g[m], weights=np.asarray(w, float)[m], minlength=n)


def c_star(t_star_all, t_star_orig, t_cv_orig, d_cv, c_cv) -> dict:
    """Section 2.2's replica completeness: c*_j = T*_all,j / (D_CV,j T*_orig,j / T_orig,CV,j). A cell with
    T_orig,CV,j = 0 keeps c_CV,j; a cell with T_orig,CV,j > 0 and T*_orig,j = 0 has D*_j = 0 and takes c*_j = 0, which
    the extraction turns into 0, as production's replica gives there (its unfolded count is 0)."""
    t_star_all, t_star_orig, t_cv_orig, d_cv, c_cv = (np.asarray(x, float) for x in
                                                       (t_star_all, t_star_orig, t_cv_orig, d_cv, c_cv))
    lost = (t_cv_orig > 0) & (t_star_orig == 0)
    keep = t_cv_orig == 0
    c = c_cv.copy()
    c[lost] = 0.0
    live = ~keep & ~lost
    d_star = d_cv[live] * t_star_orig[live] / t_cv_orig[live]
    c[live] = np.divide(t_star_all[live], d_star, out=np.zeros_like(d_star), where=d_star != 0)
    return {"c_star": c, "n_keep_cv": int(keep.sum()), "n_lost_support": int(lost.sum()),
            "n_lost_with_moved_weight": int((lost & (t_star_all > t_star_orig)).sum()),
            "finite": bool(np.all(np.isfinite(c)))}


def rel_close(a, b, rtol) -> dict:
    """Per-cell relative agreement with exact zeros: where b == 0, a must be 0; elsewhere |a/b - 1| <= rtol. Any
    non-finite value fails."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return {"max_rel": math.inf, "pass": False}
    z = b == 0
    if np.any(a[z] != 0):
        return {"max_rel": math.inf, "pass": False}
    r = float(np.max(np.abs(a[~z] / b[~z] - 1))) if (~z).any() else 0.0
    return {"max_rel": r, "pass": bool(r <= rtol)}


# ------------------------------------------------------------------------------------- the scorer's gates


def shape_gate(delta, D, rank=RANK, n=N_REPLICAS, cells=N_CELLS) -> dict:
    """C-SHAPE: a finite cells-vector and a finite n x cells matrix, and at least ``rank`` strictly positive
    eigenvalues above the pseudo-inverse's own cut in the full covariance and in every leave-one-out covariance
    (ref_c2c1_read.pinv_rank keeps the top ``rank`` modes; a mode at or below the cut would be inverted as noise)."""
    delta, D = np.asarray(delta, float), np.asarray(D, float)
    if delta.shape != (cells,) or D.shape != (n, cells):
        return {"pass": False, "why": f"shapes {delta.shape} {D.shape}"}
    if not (np.all(np.isfinite(delta)) and np.all(np.isfinite(D))):
        return {"pass": False, "why": "non-finite"}

    def ok(X):
        lam = np.linalg.eigvalsh(np.cov(X, rowvar=False, ddof=1))
        cut = lam.max() * cells * np.finfo(float).eps
        return int(np.sum(lam > cut)) >= rank
    full = ok(D)
    loo_bad = [i for i in range(n) if not ok(np.delete(D, i, axis=0))]
    return {"pass": bool(full and not loo_bad), "full": full, "loo_failures": loo_bad[:10],
            "n_loo_failures": len(loo_bad)}


def finite_t(t: dict) -> bool:
    return all(math.isfinite(float(t[k])) for k in ("T", "q95", "max"))


def proto_eps(D_paired, D_B, C_B_diag) -> dict:
    """C-PROTO: eps = max over seeds and cells with C_bb > 0 of |D_paired - D_B| / sqrt(C_bb); a zero-variance cell
    needs an exact zero difference. Passes at eps <= 1e-3."""
    Dp, Db, c = (np.asarray(x, float) for x in (D_paired, D_B, C_B_diag))
    if Dp.shape != Db.shape or Dp.shape[-1] != c.shape[0] or not all(np.all(np.isfinite(x)) for x in (Dp, Db, c)):
        return {"eps": math.inf, "pass": False, "why": "shapes or non-finite"}
    diff = np.abs(Dp - Db)
    pos = c > 0
    if np.any(diff[:, ~pos] != 0):
        return {"eps": math.inf, "pass": False, "why": "a zero-variance cell differs"}
    eps = float(np.max(diff[:, pos] / np.sqrt(c[pos]))) if pos.any() else 0.0
    return {"eps": eps, "eps_per_seed": [float(np.max(d[pos] / np.sqrt(c[pos]))) for d in diff], "pass": eps <= 1e-3}


def staged_index(b: int) -> str:
    """REF-C2C1's read staged the publication as 000, E_R as 001 and S1_b as (b + 1) (ref_c2c1_read.py:81)."""
    if not 1 <= int(b) <= 300:
        raise ValueError(f"seed {b} outside Q_R's 1..300")
    return f"{int(b) + 1:03d}_xsec.root"


# ------------------------------------------------------------------------------------- the readings (4, 5)

WORDS = ("agree", "marginal", "differ")


def disposition(r_ok: bool, mandatory_ok: bool, optional_absent: bool, optional_mismatch: bool,
                repoff_pass: bool | None) -> str:
    """Section 3.3, in order, fixed before any T: 'stop' | 'unavailable' | 'formed'."""
    if not r_ok or not mandatory_ok:
        return "stop"
    if optional_mismatch or repoff_pass is False:
        return "stop"
    if optional_absent:
        return "unavailable"
    if repoff_pass is not True:
        return "stop"
    return "formed"


PROTO_R = "under R (one shared refinement)"
PROTO_B = "under the production convention in REF-C2C1's separate-refit protocol"


def statement(r1: str, disp: str, b: str | None) -> dict:
    """Section 5's table: exactly one row for every reachable (PTMC-R1, B) pair. No row says "all else held fixed"."""
    if r1 not in WORDS:
        raise ValueError(f"PTMC-R1 {r1!r}")
    if disp == "stop":
        raise ValueError("a STOP disposition reads nothing")
    if disp == "unavailable":
        return {"row": 4, "text": f"Under R, the paired test reads {r1} at N = 200."}
    if disp != "formed" or b not in WORDS:
        raise ValueError(f"PTMC-B {b!r} with B {disp!r}")
    if b != "differ":
        return {"row": 3, "text": f"Under R the paired test reads {r1}; the matched baseline reads {b}, so it does not "
                                  "reproduce the original's differ and no change of reading is stated."}
    if r1 == "differ":
        return {"row": 1, "text": "Under OOFVC's R reclassification, binned IBU and 2D OmniFold stay distinguishable by "
                                  f"the paired test: it reads differ {PROTO_R}, as it does {PROTO_B} on the same "
                                  "draws, N and rank."}
    return {"row": 2, "text": f"{PROTO_R[0].upper() + PROTO_R[1:]}, the paired test reads {r1}, where {PROTO_B}, on "
                              "the same draws, N and rank, it reads differ. The two arms also differ in refinement "
                              "protocol, so the change of reading is not isolated to the convention."}

# ------------------------------------------------------------------------------- the premise and the support


def injected_entries(fill_rows: dict, pt_lo, pt_hi, pz_lo, pz_hi) -> np.ndarray:
    """The ordered mc_background entries of the injected rows, recomputed from the background loader's fill rows by
    the driver's own fiducial rule (closed rectangle), written independently of re2_injected_entries."""
    pt, pz = np.asarray(fill_rows["pt"], float), np.asarray(fill_rows["pz"], float)
    keep = (pt >= pt_lo) & (pt <= pt_hi) & (pz >= pz_lo) & (pz <= pz_hi)
    return np.asarray(fill_rows["entry"], dtype=np.int64)[keep]


def coupling(t_orig_cv, d_cv, tol=1e-9) -> dict:
    """C-COUPLE: KNOWN_ISSUES 84's premise per cell, |T_orig,CV / D_CV - 1| <= tol where either is positive, and the
    two vanish together."""
    t, d = np.asarray(t_orig_cv, float), np.asarray(d_cv, float)
    if t.shape != d.shape or not (np.all(np.isfinite(t)) and np.all(np.isfinite(d))):
        return {"pass": False, "why": "shapes or non-finite"}
    one_sided = (t > 0) != (d > 0)
    both = (t > 0) & (d > 0)
    dev = float(np.max(np.abs(t[both] / d[both] - 1))) if both.any() else 0.0
    neg = bool(np.any(t < 0) or np.any(d < 0))
    return {"max_dev": dev, "n_one_sided": int(one_sided.sum()), "n_supported": int(both.sum()),
            "n_structural_zero": int(((t == 0) & (d == 0)).sum()),
            "pass": bool(not one_sided.any() and not neg and dev <= tol)}


def support(gidx_truth, w_truth_cv, mask_orig_truth, n_orig: int, seeds, n=N_CELLS) -> dict:
    """C-SUPPORT (printed, read by nothing): for each seed, the cells with T_orig,CV,j > 0 whose original rows all
    draw 0 (the original rows' signal-stream draw, exactly as the driver makes it). Such a cell gives 0 in that replica
    under both conventions."""
    g = np.asarray(gidx_truth)
    w = np.asarray(w_truth_cv, float)
    m = np.asarray(mask_orig_truth, bool)
    if g.shape != w.shape or m.shape != w.shape or not m[n_orig:].sum() == 0:
        return {"pass": False, "why": "the original-row mask does not end at n_orig"}
    t_cv = cell_sums(g, w, m, n)
    bad = {}
    for b in seeds:
        f = np.concatenate([poisson(b + SIG_OFFSET, n_orig), np.zeros(w.size - n_orig)])
        t_star = cell_sums(g, w * f, m, n)
        lost = np.flatnonzero((t_cv > 0) & (t_star == 0))
        if lost.size:
            bad[int(b)] = lost.tolist()
    return {"n_seeds": len(list(seeds)), "failures": bad, "n_seed_cells": int(sum(len(v) for v in bad.values())),
            "pass": True}


def coupling_exact(g_d, pt_d, pz_d, w_d, g_s, pt_s, pz_s, w_s) -> dict:
    """C-COUPLE (r4): KNOWN_ISSUES 84's premise as an exact identity. Per truth cell, the multiset of (pT, p||, w_truth)
    of the canonical denominator's rows equals that of the original truth-passing signal rows, rows with w = 0
    excluded (they enter no sum). Equal multisets give the bijection that makes D*_j = T*_orig,j: each denominator row
    takes the factor of its value-identical signal row. No float tolerance is involved."""
    def key(g, pt, pz, w):
        g, pt, pz, w = (np.asarray(x) for x in (g, pt, pz, w))
        m = (g >= 0) & (np.asarray(w, float) != 0)
        rec = np.rec.fromarrays([g[m].astype(np.int64), np.asarray(pt, float)[m], np.asarray(pz, float)[m],
                                 np.asarray(w, float)[m]], names="g,pt,pz,w")
        rec.sort(order=["g", "pt", "pz", "w"])
        return rec
    if not all(np.all(np.isfinite(np.asarray(x, float))) for x in (pt_d, pz_d, w_d, pt_s, pz_s, w_s)):
        return {"pass": False, "why": "non-finite"}
    a, b = key(g_d, pt_d, pz_d, w_d), key(g_s, pt_s, pz_s, w_s)
    same = a.size == b.size and bool(np.array_equal(a, b))
    out = {"n_denominator": int(a.size), "n_signal": int(b.size), "pass": same}
    if not same:  # describe the mismatch per cell (printed with the STOP)
        ca = np.bincount(a["g"], minlength=N_CELLS)
        cb = np.bincount(b["g"], minlength=N_CELLS)
        out["cells_with_count_mismatch"] = np.flatnonzero(ca != cb).tolist()[:50]
        out["n_cells_differing"] = int(sum(1 for j in range(N_CELLS)
                                           if not np.array_equal(a[a["g"] == j], b[b["g"] == j])))
    return out


def appended_identity(rows: dict, appended_entry, pot_scale: float, tail: dict) -> dict:
    """C-DRAW-R (r4): the appended rows at the end of the signal arrays are the rows file's rows for the recorded
    entries: coordinates exactly, weights as the driver forms them (w * pot_scale), both masks True."""
    e = np.asarray(rows["entry"], np.int64)
    pos = {int(x): i for i, x in enumerate(e)}
    app = np.asarray(appended_entry, np.int64)
    if any(int(x) not in pos for x in app):
        return {"pass": False, "why": "an appended entry is not in the rows file"}
    idx = np.array([pos[int(x)] for x in app], dtype=np.int64)
    checks = {
        "reco_pt": np.array_equal(tail["reco_pt"], np.asarray(rows["reco_pt"], float)[idx]),
        "reco_pz": np.array_equal(tail["reco_pz"], np.asarray(rows["reco_pz"], float)[idx]),
        "truth_pt": np.array_equal(tail["truth_pt"], np.asarray(rows["true_pt"], float)[idx]),
        "truth_pz": np.array_equal(tail["truth_pz"], np.asarray(rows["true_pz"], float)[idx]),
        "w_truth": np.array_equal(tail["w_truth"], np.asarray(rows["w_truth"], float)[idx] * pot_scale),
        "w_reco": np.array_equal(tail["w_reco"], np.asarray(rows["w_reco"], float)[idx] * pot_scale),
        "masks": bool(np.all(tail["pass_reco"]) and np.all(tail["pass_truth"])),
    }
    return {"checks": {k: bool(v) for k, v in checks.items()}, "pass": all(checks.values())}
