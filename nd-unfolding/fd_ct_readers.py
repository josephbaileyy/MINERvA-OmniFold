#!/usr/bin/env python3
"""The cheap tier's three login-node readers (state/measurement-paper/5d-community-20261024/FD-CT-READERS-DECLARATION.md;
DECISION-20261028-joseph-d2-approved-and-cheap-tier.md item 2): descriptive readouts on the 16 H2 reporting cells
R00-R15 of configuration (e), at 0 node-h, from products that already exist.

* ``recoil`` (3a): W2b's whole-recoil data unfolds at s = 0.96 and 1.04 (``w2b_rr0``, ``w2b_rr1``) against their own
  delta = 0 chain (``w2b_rrzero``), integrated onto the cells with S1's rule, beside C_resp's and the reported
  matrix's per-cell sigma. A data-side sensitivity at a second construction (one coherent scale), not a mismatch
  closure.
* ``chi2`` (4C): per A7 calibration experiment i at truth T, r_i = X_i / Xtrue_i - 1 on the cells, and
  chi2_i = r_i^T M^-1 r_i (about the truth) and (r_i - b~)^T M^-1 (r_i - b~) (about the NuE-weighted mean b~), for
  M = (C_total + C_resp)/(f f^T) and C_e/(f f^T). Descriptive only: F0's offset control 7 failed, A7's draws are not
  S1's, the truths are hybrids on J and the products use half of the MC.
* ``period`` (5A): the 2D run-period offsets g_X (playlist_term.npz) averaged over each cell's (p_T, p_parallel)
  footprint with the cell's own fine-cell weights, and C_PL,16 = k sum_X e_X g_X,R g_X,R^T relative to f. A size
  under the assumption that the offset does not depend on E_avail, q3 or W inside a 2D bin, which only 5B can test.

Every output is relative. Nothing written or printed carries f, an absolute cell value or f - g: each output passes
``fd_f0_regrade.LeakGuard`` first (exit 3, nothing written). A control that refuses exits 1 with nothing written.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: a covariance component, a change to the reported
matrix or to kappa, a coverage or calibration statement, a claim or printed wording.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_f0_regrade as f0  # noqa: E402  (Stop, report, sa_call, LeakGuard, meta_problems, listed_set, weighted)
import s1_assemble as sa  # noqa: E402  (require_sha, fine_map, functional_matrix, flux_weights, check_meta)

N_CELLS, NPZ_2D = 16, 16
TOL = 1e-12
PRIMARY = ("proton", "meson", "em", "other")
PINS = {
    "s1_npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "cresp": "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a",
    "s5p_sums": "1a72cb439120d910ee509fa0be7915924eb36b6a42fda8bda8006a0a92609935",
    "f0b_readout": "b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b",
    "playlist_npz": "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476",
    "playlist_json": "5b023478eb5825a298fd3e851b614fd4780ab27b927214e253f5c4c0df52f7b9",
    "central": "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c",
    "prior": "bf7bd27873427d4b1ff9864403b895529931f113440acec3daa28479f958466c",
}
# 3a: variant -> (product sha256, input_npz_sha256, bkg_dump_sha256, recoil scale s), W2B-REPORT-20261006.md section 8
# and each product's own meta (re-measured on login08, 2026-10-28)
W2B = {
    "rr0": ("df11bfd8e879a051d3d0bf2aa5fc4e0131efa9065bcbd89d29a859ddb9f8639b",
            "45de5c7f54588bf82907a0490302500aa2668c81ac896844b7508854b7a55641",
            "7ab440f4524360badc9703b160faf871d48a031a9da21e99dc75b1fe2d92bd48", 0.96),
    "rr1": ("36313201ecffa85183fa83d642c9b0b71dc67f9ed1743dba7184eb22c41356a8",
            "4c98d8cbc087e3b32f600b7301673c96e60ab6830b81baa71921934cc6131a0e",
            "6a848eb425ed8ee298ab0e9f4ceabe8fd23b4982272c53f4a50cfed3e33fedd7", 1.04),
    "rrzero": ("ec5dc97d8554f008902a17428724e8482544d6e6de7db5ae1155d96d51dc4c4e",
               "6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f",
               "c715d07e02ac8e941c5deccd3c858f71653b997b4e6331e055bbe9144f3c98c3", 1.0),
}
# 4C: the five A7 calibration truths (FD-PLAN row 5), as fd_f0_regrade names them
CAL = tuple((t["name"], t["cal"], f0.HYP[t["d16"]]) for t in f0.TRUTHS if t["row"] == 4)
PERCENTILES = (5.0, 16.0, 50.0, 84.0, 95.0)
# 5A
PERIODS = ("PA", "PB", "PC")
EXTRAPOLATED = 0.10   # a cell whose footprint weight outside the 2D term's 205 cells exceeds this is labelled
LABELS = {
    "recoil": "data-side sensitivity at a second construction: W2b's whole simulated-recoil scale s = 0.96 and 1.04 "
              "(the test-beam agreement level, an exploratory size, not an uncertainty prescription), relative to "
              "its own delta = 0 chain, which is not bitwise the production product; not a mismatch closure and "
              "not a bias; beside C_resp, which it neither replaces nor validates",
    "chi2": "descriptive only, not a calibration: F0's offset control 7 failed (chi2_16 = 245.74); A7's draws are "
            "not S1's (one flux universe drawn uniformly, model bands move the response only, laterals not "
            "applied); the truths are hybrids on the J cells; the products unfold with half of the MC; "
            "C_model is not drawn, so the reported matrix is expected to over-cover the toys' scatter",
    "period": "a size under an untested assumption: the 2D period offset g_X does not depend on E_avail, q3 or W "
              "inside a (p_T, p_parallel) bin; only 5B can test it; built from the observed offsets, so it "
              "contains them by construction and cannot fail; not a 5D run-period block, and printed beside the "
              "reported matrix, not in it (LIMITATION-PLAN-ADDENDUM-20261028.md section 5.4)",
    "not_citable_for": ["a coverage, calibration or chi2-distribution result", "a covariance component or a change "
                        "to the reported matrix", "a bias under response mismatch", "a run-period effect in the "
                        "hadronic variables"],
}


# ---------------------------------------------------------------- shared


def common(a, U: np.ndarray) -> dict:
    """S1's assembly and the adopted C_resp, checked (control S): f, C_e, C_total, C_resp and M = C_total + C_resp."""
    f0.require("S", a.s1_npz, PINS["s1_npz"], "S1 assembly")
    f0.require("S", a.cresp, PINS["cresp"], "C_resp")
    with np.load(a.s1_npz, allow_pickle=False) as z:
        s = {k: np.asarray(z[k], float) for k in ("f", "C_e", "C_model_abs", "C_total")}
        U32 = np.asarray(z["U"])
    with np.load(a.cresp, allow_pickle=False) as z:
        Cr, Ctr = np.asarray(z["C_resp"], float), np.asarray(z["C_total_resp"], float)
        species = [np.asarray(z[f"C_resp_{p}"], float) for p in PRIMARY]
    f = s["f"]
    scale = np.abs(np.diag(s["C_total"])).max()
    checks = {
        "U is S1's float32 functional matrix": np.array_equal(U32, U.astype(np.float32)),
        "f is positive on every cell": bool(f.shape == (N_CELLS,) and np.all(f > 0)),
        "C_total = C_e + C_model_abs": np.allclose(s["C_e"] + s["C_model_abs"], s["C_total"], rtol=TOL, atol=TOL * scale),
        "C_resp is the sum of its four primary species": np.allclose(sum(species), Cr, rtol=TOL, atol=TOL * scale),
        "C_total_resp = S1's C_total + C_resp": np.allclose(s["C_total"] + Cr, Ctr, rtol=TOL, atol=TOL * scale),
    }
    for name, ok in checks.items():
        f0.report("S", name, bool(ok), "differs")
    ff = np.outer(f, f)
    return {"f": f, "ff": ff, "C_e": s["C_e"], "C_total": s["C_total"], "C_resp": Cr, "M": Ctr}


def rel_sigma(C: np.ndarray, f: np.ndarray) -> np.ndarray:
    return np.sqrt(np.clip(np.diag(C), 0.0, None)) / f


def summary(v) -> dict:
    v = np.asarray(v, float)
    return {"median": float(np.median(v)), "min": float(v.min()), "max": float(v.max())}


def quad(v: np.ndarray, M: np.ndarray) -> float:
    """v^T M^-1 v by Cholesky (M positive definite)."""
    y = np.linalg.solve(np.linalg.cholesky(M), v)
    return float(y @ y)


def cells(idx=None) -> list[str]:
    return [f"R{c:02d}" for c in (range(N_CELLS) if idx is None else idx)]


def finite(obj):
    """JSON-safe: non-finite floats become None."""
    if isinstance(obj, dict):
        return {k: finite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [finite(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        return float(obj) if math.isfinite(obj) else None
    if isinstance(obj, np.integer):
        return int(obj)
    return obj


def write(a, out: dict, guard: f0.LeakGuard, lines: list[str]) -> int:
    out = finite(out)
    guard.check("readout", out)
    for ln in lines:
        guard.check("stdout", ln)
    a.out_json.write_text(json.dumps(out, indent=1, allow_nan=False) + "\n")
    for ln in lines:
        print(ln, flush=True)
    print(json.dumps({"wrote": str(a.out_json), "sha256": sa.sha256(a.out_json)}), flush=True)
    return 0


def code_sha() -> dict:
    return {"fd_ct_readers.py": sa.sha256(Path(__file__).resolve()),
            "fd_f0_regrade.py": sa.sha256(Path(f0.__file__).resolve()),
            "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve()),
            "s5p_stage1_inspect.py": sa.sha256(Path(sa.s1.__file__).resolve())}


# ---------------------------------------------------------------- 3a: recoil


def recoil_product(d: Path, v: str) -> np.ndarray:
    sha, npz, bkg, _ = W2B[v]
    p = d / f"w2b_{v}_b-_j-.npz"
    f0.require("R0", p, sha, f"W2b {v}")
    f0.sa_call("R0", sa.check_meta, p, "s5p-numerics/1", 42, False,
               {"input_npz_sha256": npz, "bkg_dump_sha256": bkg, "construction": "data", "truth": "nominal",
                "bootstrap_seed": None, "jitter_seed": None, "coords": "float32"})
    x = sa.xs(p)
    if x.shape != (int(np.prod(sa.s1.fine_shape())),) or not np.all(np.isfinite(x)):
        raise f0.Stop("R0", f"{v}: xsec_flat shape {x.shape} or non-finite entries")
    return x


def run_recoil(a) -> int:
    U = sa.functional_matrix(f0.sa_call("S", sa.fine_map, a.definition))
    x = {v: recoil_product(a.w2b_unf, v) for v in W2B}
    f0.report("R0", "the three W2b products match their recorded sha256 and were made by (e) on their own dumps", True)
    S = common(a, U)
    f, ff = S["f"], S["ff"]
    X = {v: U @ x[v] for v in W2B}
    f0.report("R1", "every W2b cell integral is positive", all(bool(np.all(X[v] > 0)) for v in W2B), "is not")
    guard = f0.LeakGuard(f, list(X.values()))
    z = X["rrzero"]
    s_minus, s_plus = X["rr0"] / z - 1.0, X["rr1"] / z - 1.0
    d = (X["rr1"] - X["rr0"]) / (2.0 * z)
    sig_resp, sig_tot, sig_m = rel_sigma(S["C_resp"], f), rel_sigma(S["C_total"], f), rel_sigma(S["M"], f)
    Cr_rel, M_rel, Ct_rel = S["C_resp"] / ff, S["M"] / ff, S["C_total"] / ff
    lam, V = np.linalg.eigh((Cr_rel + Cr_rel.T) / 2.0)
    keep = lam > TOL * lam.max()
    Pd = V[:, keep] @ (V[:, keep].T @ d)
    span = float(Pd @ Pd / (d @ d)) if d @ d > 0 else None
    curv = float(np.linalg.norm(s_plus + s_minus) / np.linalg.norm(s_plus - s_minus))
    with np.errstate(divide="ignore", invalid="ignore"):
        r_resp, r_m = np.abs(d) / sig_resp, np.abs(d) / sig_m
    out = {"schema": "fd-ct-recoil/1", "labels": {"what": LABELS["recoil"], "not_citable_for": LABELS["not_citable_for"]},
           "controls_passed": ["S", "R0", "R1"], "cells": cells(),
           "scales": {v: W2B[v][3] for v in W2B},
           "shift_minus": s_minus.tolist(), "shift_plus": s_plus.tolist(), "half_span": d.tolist(),
           "half_span_summary_abs": summary(np.abs(d)),
           "sigma_rel": {"C_resp": sig_resp.tolist(), "C_total": sig_tot.tolist(), "C_total_resp": sig_m.tolist()},
           "abs_half_span_over_sigma": {"C_resp": r_resp.tolist(), "C_total_resp": r_m.tolist(),
                                        "C_resp_summary": summary(r_resp[np.isfinite(r_resp)]),
                                        "C_total_resp_summary": summary(r_m)},
           "half_span_quadratic_form": {"C_total_resp": quad(d, M_rel), "C_total": quad(d, Ct_rel),
                                        "label": "d^T M^-1 d of the half-span: a length in sigma units, descriptive, not a test"},
           "fraction_of_half_span_in_C_resp_span": {"value": span, "C_resp_rank": int(keep.sum()),
                                                    "label": "||P d||^2 / ||d||^2, P the projector onto C_resp's "
                                                             "range (relative units); 1 means the scale moves the "
                                                             "cells only in C_resp's directions"},
           "curvature_ratio": {"value": curv, "label": "||s+ + s-|| / ||s+ - s-||, descriptive"},
           "inputs_sha256": {**{v: W2B[v][0] for v in W2B}, "s1_npz": PINS["s1_npz"], "cresp": PINS["cresp"],
                             "definition": sa.DEFINITION_SHA256},
           "code_sha256": code_sha(), "argv": sys.argv}
    lines = [f"[3a] median |d|/sigma_resp {out['abs_half_span_over_sigma']['C_resp_summary']['median']:.4f}, "
             f"median |d|/sigma_total_resp {out['abs_half_span_over_sigma']['C_total_resp_summary']['median']:.4f}, "
             f"in-span fraction {span:.4f}, curvature {curv:.4f}"]
    return write(a, out, guard, lines)


# ---------------------------------------------------------------- 4C: chi2


def chi2_quantile(q: float, ndf: int) -> float:
    """The q quantile of chi2_ndf (even ndf) by bisection on fd_f0_regrade.chi2_sf_even."""
    lo, hi = 0.0, 10.0 * ndf + 100.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 1.0 - f0.chi2_sf_even(mid, ndf) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def weighted_percentiles(v: np.ndarray, w: np.ndarray, ps) -> list[float]:
    """Inverted weighted ECDF: the smallest v whose cumulative weight share reaches p/100."""
    o = np.argsort(v, kind="stable")
    c = np.cumsum(w[o]) / w.sum()
    return [float(v[o][min(int(np.searchsorted(c, p / 100.0 - 1e-15)), v.size - 1)]) for p in ps]


def distribution(c2: np.ndarray, w: np.ndarray, ndf: int) -> dict:
    """Means and percentiles only, beside chi2_ndf's own: no p value and no tail fraction (the 3D binding's ruling 4)."""
    return {"weighted": {"mean": float(w @ c2 / w.sum()),
                         "percentiles": dict(zip(map(str, PERCENTILES), weighted_percentiles(c2, w, PERCENTILES)))},
            "unweighted": {"mean": float(c2.mean()),
                           "percentiles": dict(zip(map(str, PERCENTILES), np.percentile(c2, PERCENTILES).tolist()))},
            "reference_chi2": {"ndf": ndf, "mean": float(ndf),
                               "percentiles": {str(p): chi2_quantile(p / 100.0, ndf) for p in PERCENTILES}}}


def run_chi2(a) -> int:
    U = sa.functional_matrix(f0.sa_call("S", sa.fine_map, a.definition))
    f0.require("C0", a.s5p_sums, PINS["s5p_sums"], "s5p archive sums")
    f0.require("C0", a.f0b_readout, PINS["f0b_readout"], "F0b readout")
    man = f0.relative_manifest(a.s5p_sums, a.s5p_root)
    sets = {}
    for name, cal, _ in CAL:
        try:
            sets[name] = f0.listed_set(man, a.s5p_root / "runs/prod/cal" / cal)
        except f0.Stop as e:
            raise f0.Stop("C0", str(e.code)) from None
        for p in sets[name]:
            f0.require("C0", p, man[str(p)], name)
    f0.report("C0", f"{sum(map(len, sets.values()))} calibration products match the s5p archive sums", True)
    metas = {}
    for name, cal, hyp in CAL:
        metas[name] = []
        for p in sets[name]:
            m = f0.read_meta(p)
            bad = f0.meta_problems(p, m, "cal", {"hyp": hyp})
            if bad:
                raise f0.Stop("C1", f"{p.name}: {'; '.join(bad)}")
            metas[name].append(m)
        n = len(sets[name])
        if n != f0.COUNTS["cal"][cal] or len({m["pseudo_seed"] for m in metas[name]}) != n:
            raise f0.Stop("C1", f"{cal}: {n} products, {f0.COUNTS['cal'][cal]} declared, or a repeated seed")
    f0.report("C1", "every product is an A7 calibration experiment at its declared truth, in the declared count", True)
    S = common(a, U)
    f, ff = S["f"], S["ff"]
    w_all = f0.sa_call("C2", sa.flux_weights, a.flux_constraint)
    f0b = json.loads(a.f0b_readout.read_text())["controls"]["offset_control_7"]["B_eff_calibration"]
    W, R, ints = {}, {}, []
    for name, _, _ in CAL:
        W[name] = w_all[[m["nuisance_draw"]["flux"] for m in metas[name]]]
        beff = float(W[name].sum() ** 2 / (W[name] ** 2).sum())
        f0.report("C2", f"{name}: B_eff {beff:.6f} equals F0b's", abs(beff / f0b[name] - 1.0) <= TOL, f"F0b {f0b[name]}")
        Xh, Xt = [], []
        for p in sets[name]:
            with np.load(p, allow_pickle=False) as z:
                Xh.append(U @ np.asarray(z["xsec_flat"], float))
                Xt.append(U @ np.asarray(z["xtrue_flat"], float))
        Xh, Xt = np.array(Xh), np.array(Xt)
        if not np.all(Xt > 0):
            raise f0.Stop("C3", f"{name}: a truth integral is not positive")
        R[name] = Xh / Xt - 1.0
        ints += [Xh, Xt]
    f0.report("C3", "every truth integral is positive on all 16 cells", True)
    guard = f0.LeakGuard(f, ints)
    mats = {"C_total_resp": S["M"] / ff, "C_e": S["C_e"] / ff}
    truths, lines = {}, []
    for name, cal, _ in CAL:
        r, w = R[name], W[name]
        sets_cells = {"all16": list(range(N_CELLS))}
        if name == "A7_gibuu":
            sets_cells["gibuu8"] = list(f0.GIBUU_CELLS)
        rec = {"cal": cal, "n_experiments": int(r.shape[0]), "B_eff": float(w.sum() ** 2 / (w ** 2).sum()), "matrices": {}}
        for mn, M in mats.items():
            rec["matrices"][mn] = {}
            for cn, idx in sets_cells.items():
                Mi, ri = M[np.ix_(idx, idx)], r[:, idx]
                L = np.linalg.cholesky(Mi)
                b = (w[:, None] * ri).sum(axis=0) / w.sum()
                yt = np.linalg.solve(L, ri.T)
                yc = np.linalg.solve(L, (ri - b).T)
                c2t, c2c = (yt * yt).sum(axis=0), (yc * yc).sum(axis=0)
                cb = quad(b, Mi)
                gap = abs(float(w @ c2t / w.sum()) - float(w @ c2c / w.sum()) - cb)
                if gap > 1e-9 * max(1.0, float(w @ c2t / w.sum())):
                    raise f0.Stop("C4", f"{name} {mn} {cn}: mean chi2 about the truth is not the mean about b~ "
                                        f"plus b~'s own ({gap:.3e})")
                sd = np.sqrt((w[:, None] * (ri - b) ** 2).sum(axis=0) / w.sum())
                rec["matrices"][mn][cn] = {
                    "cells": cells(idx), "ndf": len(idx),
                    "about_truth": distribution(c2t, w, len(idx)),
                    "about_weighted_mean": distribution(c2c, w, len(idx)),
                    "chi2_of_weighted_mean_bias": cb,
                    "width_ratio": (sd / np.sqrt(np.diag(Mi))).tolist(),
                    "width_ratio_summary": summary(sd / np.sqrt(np.diag(Mi)))}
        truths[name] = rec
        m16 = rec["matrices"]["C_total_resp"]["all16"]
        lines.append(f"[4C] {name}: weighted mean chi2 about truth {m16['about_truth']['weighted']['mean']:.3f}, "
                     f"about b~ {m16['about_weighted_mean']['weighted']['mean']:.3f} (ndf 16, C_total + C_resp), "
                     f"median width ratio {m16['width_ratio_summary']['median']:.4f}")
    f0.report("C4", "the mean-chi2 decomposition holds for every truth, matrix and cell set", True, guard=guard)
    out = {"schema": "fd-ct-chi2/1", "labels": {"what": LABELS["chi2"], "not_citable_for": LABELS["not_citable_for"],
                                                "no_p_values": "no p value and no tail fraction is computed or written"},
           "controls_passed": ["S", "C0", "C1", "C2", "C3", "C4"],
           "constants": {"percentiles": list(PERCENTILES),
                         "weights": "nu-e + IMD constraint weight of each experiment's drawn flux universe",
                         "matrices": {"C_total_resp": "the reported C_total + C_resp, relative to f (no V_g)",
                                      "C_e": "S1's drawn-block analogue C_e, relative to f"}},
           "truths": truths,
           "inputs_sha256": {"s5p_sums": PINS["s5p_sums"], "f0b_readout": PINS["f0b_readout"], "s1_npz": PINS["s1_npz"],
                             "cresp": PINS["cresp"], "constraint": sa.CONSTRAINT_SHA256, "definition": sa.DEFINITION_SHA256},
           "code_sha256": code_sha(), "argv": sys.argv}
    return write(a, out, guard, lines)


# ---------------------------------------------------------------- 5A: period


def footprint(U: np.ndarray, fm: np.ndarray, x: np.ndarray, support: np.ndarray):
    """Per cell R and 2D cell b (index ipt * 16 + ipz): W_Rb = sum over R's fine cells in b of x_f vol_f. Returns the
    weights normalized over the supported 2D cells (16 x 205) and the share of R's weight outside them."""
    shape = sa.s1.fine_shape()
    idx = np.unravel_index(np.arange(fm.size), shape)
    c2 = idx[0] * NPZ_2D + idx[1]
    contrib = x * sa.s1.fine_volume()
    om, outside = np.zeros((N_CELLS, support.size)), np.zeros(N_CELLS)
    pos = {int(c): k for k, c in enumerate(support)}
    for R in range(N_CELLS):
        m = fm == R
        tot = contrib[m].sum()
        inside = np.isin(c2, support) & m
        sup = contrib[inside].sum()
        if not sup > 0:
            raise f0.Stop("P3", f"R{R:02d}: no positive weight on the 2D term's cells")
        for b in np.unique(c2[inside]):
            om[R, pos[int(b)]] = contrib[inside & (c2 == b)].sum() / sup
        outside[R] = (tot - sup) / tot
    return om, outside


def period_variant(om, outside, z, e, k, S) -> dict:
    g = {X: om @ z[f"g_{X}"] for X in PERIODS}
    r = {X: om @ z[f"r_{X}"] for X in PERIODS}
    ident = float(np.max(np.abs(sum(e[X] * g[X] for X in PERIODS))))
    if ident > TOL:
        raise f0.Stop("P4", f"sum_X e_X g_X,R is {ident:.3e}, not 0")
    C = k * sum(e[X] * np.outer(g[X], g[X]) for X in PERIODS)
    Sref = sum(np.outer(e[X] * (r[X] / r["PA"] - 1.0), e[X] * (r[X] / r["PA"] - 1.0)) for X in ("PB", "PC"))
    lam = np.linalg.eigvalsh(C)
    rank = int(np.sum(lam > TOL * lam.max())) if lam.max() > 0 else 0
    if rank > 2 or lam.min() < -TOL * max(lam.max(), 1e-300):
        raise f0.Stop("P4", f"C_PL,16 rank {rank} or min eigenvalue {lam.min():.3e}")
    M_rel = S["M"] / S["ff"]
    sig, sig_m = np.sqrt(np.diag(C)), np.sqrt(np.diag(M_rel))
    return {"g": {X: g[X].tolist() for X in PERIODS},
            "sigma_rel": {"C_PL16": sig.tolist(), "S_ref16": np.sqrt(np.diag(Sref)).tolist(), "C_total_resp": sig_m.tolist()},
            "sigma_rel_summary": {"C_PL16": summary(sig), "S_ref16": summary(np.sqrt(np.diag(Sref)))},
            "sigma_ratio_to_C_total_resp": (sig / sig_m).tolist(),
            "sigma_ratio_summary": summary(sig / sig_m),
            "trace_share": float(np.trace(C) / np.trace(M_rel + C)),
            "C_PL16_rel": C.tolist(), "rank": rank,
            "weight_outside_2d_support": outside.tolist(),
            "extrapolated_cells": [f"R{c:02d}" for c in range(N_CELLS) if outside[c] > EXTRAPOLATED]}


def run_period(a) -> int:
    fm = f0.sa_call("S", sa.fine_map, a.definition)
    U = sa.functional_matrix(fm)
    f0.require("P0", a.playlist_npz, PINS["playlist_npz"], "playlist_term.npz")
    f0.require("P0", a.playlist_json, PINS["playlist_json"], "playlist_term.json")
    pj = json.loads(a.playlist_json.read_text())
    with np.load(a.playlist_npz, allow_pickle=False) as zz:
        z = {k: np.asarray(zz[k]) for k in zz.files}
    support = z["cells"].astype(int)
    n2 = support.size
    e_vec = {X: z[f"e_{X}"].astype(float) for X in PERIODS}
    e = {X: float(np.mean(e_vec[X])) for X in PERIODS}
    V2 = sum(v * v for v in e.values())
    k = V2 / (1.0 - V2)
    x = z["x"].astype(float)
    C_re = k * sum(e[X] * np.outer(x * z[f"g_{X}"], x * z[f"g_{X}"]) for X in PERIODS)
    checks = {
        "the committed playlist_term.json names this npz": pj.get("npz", {}).get("sha256") == PINS["playlist_npz"],
        "205 distinct 2D cells on the 14 x 16 grid": bool(n2 == 205 and np.unique(support).size == n2
                                                          and support.min() >= 0 and support.max() < 14 * NPZ_2D),
        "every period array has one entry per cell": all(z[f"{q}_{X}"].shape == (n2,) for q in "egr" for X in PERIODS),
        "e_X is constant over cells": all(np.ptp(e_vec[X]) <= TOL * e[X] for X in PERIODS),
        "the e_X sum to 1": abs(sum(e.values()) - 1.0) <= TOL,
        "sum_X e_X g_X = 0 on every cell": float(np.max(np.abs(sum(e_vec[X] * z[f"g_{X}"] for X in PERIODS)))) <= TOL,
        "C_PL rebuilt from k, e, x and g equals the stored C_PL":
            float(np.max(np.abs(C_re - z["C_PL"])) / np.max(np.abs(z["C_PL"]))) <= TOL,
    }
    for name, ok in checks.items():
        f0.report("P0", name, bool(ok), "differs")
    f0.require("P1", a.central, PINS["central"], "the (e) central value")
    f0.sa_call("P1", sa.check_meta, a.central, "s5p-numerics/1", 42, True,
               {"construction": "data", "truth": "nominal", "bootstrap_seed": None, "jitter_seed": None})
    xc = sa.xs(a.central)
    S = common(a, U)
    f = S["f"]
    f0.report("P1", "the central value's cell integrals are S1's f", bool(np.allclose(U @ xc, f, rtol=TOL, atol=0)), "differ")
    f0.require("P2", a.prior, PINS["prior"], "MnvTune v1 prediction")
    with np.load(a.prior, allow_pickle=False) as zz:
        pm = json.loads(str(zz["meta_json"]))
        xp = np.asarray(zz["xsec_flat"], float)
        edges_ok = all(np.allclose(np.asarray(zz[f"edges_{ax}"], float), sa.s1.FINE[ax], rtol=0, atol=1e-12)
                       for ax in sa.s1.AXES)
    f0.report("P2", "the prior is MnvTune v1's s5p-mc-truth-pred/1 on the fine grid",
              bool(pm.get("schema") == "s5p-mc-truth-pred/1" and edges_ok and xp.shape == xc.shape), "is not")
    variants = {}
    for vn, xw in (("central", xc), ("prior", xp)):
        om, outside = footprint(U, fm, xw, support)
        variants[vn] = period_variant(om, outside, z, e, k, S)
    f0.report("P3", "every cell has positive weight on the 2D term's cells", True)
    f0.report("P4", "sum_X e_X g_X,R = 0 and C_PL,16 is PSD of rank <= 2, for both weightings", True)
    # the central value's integrals are f itself (P1), already in the guard's table; passing them again would
    # forbid f/f = 1 and refuse every '1' in a string
    guard = f0.LeakGuard(f, [U @ xp])
    out = {"schema": "fd-ct-period/1", "labels": {"what": LABELS["period"], "not_citable_for": LABELS["not_citable_for"]},
           "controls_passed": ["S", "P0", "P1", "P2", "P3", "P4"], "cells": cells(),
           "constants": {"periods": {"PA": "1A-1F", "PB": "1G 1L 1M", "PC": "1N-1P"}, "e": e, "k": k,
                         "extrapolated_above": EXTRAPOLATED,
                         "weights": {"central": "primary: the (e) central value's fine-cell contributions x_f vol_f",
                                     "prior": "sensitivity: MnvTune v1's fine-cell contributions"}},
           "variants": variants,
           "inputs_sha256": {**{k_: PINS[k_] for k_ in ("playlist_npz", "playlist_json", "central", "prior", "s1_npz", "cresp")},
                             "definition": sa.DEFINITION_SHA256},
           "code_sha256": code_sha(), "argv": sys.argv}
    lines = [f"[5A] {vn}: median sigma_PL16 {variants[vn]['sigma_rel_summary']['C_PL16']['median']:.5f}, median ratio "
             f"to sigma_total_resp {variants[vn]['sigma_ratio_summary']['median']:.4f}, trace share "
             f"{variants[vn]['trace_share']:.5f}, extrapolated {variants[vn]['extrapolated_cells']}" for vn in variants]
    return write(a, out, guard, lines)


# ---------------------------------------------------------------- main


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="reader", required=True)
    for name in ("recoil", "chi2", "period"):
        p = sub.add_parser(name)
        p.add_argument("--definition", type=Path, required=True)
        p.add_argument("--s1-npz", type=Path, required=True)
        p.add_argument("--cresp", type=Path, required=True)
        p.add_argument("--out-json", type=Path, required=True)
        if name == "recoil":
            p.add_argument("--w2b-unf", type=Path, required=True)
        elif name == "chi2":
            p.add_argument("--s5p-sums", type=Path, required=True)
            p.add_argument("--s5p-root", type=Path, required=True)
            p.add_argument("--f0b-readout", type=Path, required=True)
            p.add_argument("--flux-constraint", type=Path, required=True)
        else:
            p.add_argument("--playlist-npz", type=Path, required=True)
            p.add_argument("--playlist-json", type=Path, required=True)
            p.add_argument("--central", type=Path, required=True)
            p.add_argument("--prior", type=Path, required=True)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    if a.out_json.exists():
        print(f"FAIL refusing to overwrite {a.out_json}", file=sys.stderr)
        return 1
    try:
        return {"recoil": run_recoil, "chi2": run_chi2, "period": run_period}[a.reader](a)
    except f0.Stop as e:
        print(e.code, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
