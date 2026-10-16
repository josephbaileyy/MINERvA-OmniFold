#!/usr/bin/env python3
"""The 2D playlist-consistency block (DESIGN.md in the parent directory; frozen before any number was computed).

    python3 -I playlist_term.py ANALYSIS_JSON OUTDIR

Cluster only (root_6_28; login node, 0 node-h). ANALYSIS_JSON is the period-unfold test's committed analysis.json
(sha256 pinned below); its `_roles` and `_runs` name and pin every per-period unfold. The loader, the metric (VL175 =
hCov_combined + ML of work_cov.npz) and the step statistic are imported unchanged from the deployed, pinned
analyze_periods.py. Writes OUTDIR/playlist_term.npz and OUTDIR/playlist_term.json only if every check passes.

Construction (DESIGN §2), per cell over the 205 cells, periods X in (PA, PB, PC):
    r_X = x_X / t_X                     double ratio (each period's own MC truth)
    m   = sum_X e_X r_X                 exposure-weighted mean (e_X: the test's exposure share)
    g_X = r_X / m - 1                   so sum_X e_X g_X = 0
    k   = V2 / (1 - V2), V2 = sum_X e_X^2
    v_X = sqrt(k e_X) * x * g_X         x = E_U on the cells
    C_PL = sum_X v_X v_X^T
Sensitivities (reported, never the block): S_ref = sum_{B,C} b_X b_X^T, b_X = e_X (r_X/r_A - 1) x; S_raw (x for r);
S_ref_raw (x for r; its b_PB is the frozen bias_PB).
"""
import hashlib
import json
import os
import sys

import numpy as np

SCRIPTS = "/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/code/record/scripts"
COMMON = ("/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/code/repo/docs/orchestration/state/2d-closeout/"
          "playlist-spread-20261014/coverage/scripts/common.py")
PINS = {
    f"{SCRIPTS}/analyze_periods.py": "912af1ddfbae2e28a2cba6e6843b0985e2442adb4b1e775a22d4c547b8d8ebc5",
    f"{SCRIPTS}/periods.py": "d37c1a8fbda7119988643100039e28e335e4fc79eb30a10f0f5a3df984fa8514",
    COMMON: "dcb78c52f8a11c581942bb1887da29e435c10dfa288125df700789bd331c56a1",
}
ANALYSIS_SHA = "05edff61673fed987f487f8c19ad25ec055db8118491815b9c263f3a7c3de72b"
PER = ("PA", "PB", "PC")
TOL_CONTROL = 1e-9
TOL_ID = 1e-12
TOL_FUNC = 1e-10


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def stop(msg):
    raise SystemExit(f"[STOP] {msg}")


def main(analysis_json, outdir):
    # ---- pins ---------------------------------------------------------------------------------------------------
    for p, want in PINS.items():
        if sha256(p) != want:
            stop(f"pin {p}")
    if sha256(analysis_json) != ANALYSIS_SHA:
        stop(f"pin {analysis_json}")
    sys.path.insert(0, SCRIPTS)
    import analyze_periods as AP   # noqa: E402  (inserts the common.py directory itself)
    PD, C = AP.PD, AP.C
    if os.path.realpath(C.__file__) != os.path.realpath(COMMON):
        stop(f"common.py imported from {C.__file__}, not the pinned {COMMON}")
    inputs = {"E_U": PD.check_pin("E_U"), "work_cov": PD.check_pin("work_cov"),
              "analysis_json": {"path": os.path.abspath(analysis_json), "sha256": ANALYSIS_SHA},
              "scripts": {p: s for p, s in PINS.items()}}
    A = json.load(open(analysis_json))
    roles, runs_rec = A["_roles"], A["_runs"]
    W = np.load(PD.PINS["work_cov"][0])
    cells_all = W["cells"]

    def load(path):
        r = AP.load(path, cells_all)
        if path not in runs_rec or r["sha256"] != runs_rec[path]["sha256"]:
            stop(f"sha256 of {path} differs from analysis.json _runs")
        return r

    R = {"POOL": load(roles["POOL"])}
    for X in PER:
        R[X] = {"s42": load(roles[X]["s42"]), "s43": load(roles[X]["s43"]),
                "boot": [load(p) for p in roles[X]["boot"]]}
    runs = [R["POOL"]] + [r for X in PER for r in [R[X]["s42"], R[X]["s43"]] + R[X]["boot"]]
    keep = np.ones(cells_all.size, bool)
    for r in runs:
        keep &= (r["x"] > 0) & (r["t"] > 0)
    # check 6: populations
    if cells_all.size != 205 or not keep.all() or int(A["cells_used"]) != 205:
        stop(f"cells: work_cov {cells_all.size}, kept {int(keep.sum())}, analysis.json {A['cells_used']}; 205 required")
    for X in PER:
        if len(R[X]["boot"]) != 10 or int(A["n_boot_pairs"]) != 10:
            stop(f"{X}: {len(R[X]['boot'])} bootstrap draws, analysis.json {A['n_boot_pairs']}; 10 required")
    met = AP.Metric(W, keep)
    k_ = keep
    x = met.x                                                    # E_U on the cells
    xX = {X: R[X]["s42"]["x"][k_] for X in PER}
    tX = {X: R[X]["s42"]["t"][k_] for X in PER}
    rX = {X: xX[X] / tX[X] for X in PER}
    ipt, _ = C.cell_ipt_ipz(met.cells)
    expo = np.stack([R[X]["s42"]["pot"] * R[X]["s42"]["phi"] for X in PER])
    e = {X: (expo[i] / expo.sum(0))[ipt] for i, X in enumerate(PER)}
    checks = {}

    # ---- check 5: grid and central value against the pinned E_U ROOT file --------------------------------------
    import ROOT  # noqa: E402
    fe = ROOT.TFile.Open(PD.PINS["E_U"][0])
    he = fe.Get("hXSec2D") if fe and not fe.IsZombie() else None
    if not he:
        stop("E_U: no hXSec2D")
    ex = np.array([he.GetXaxis().GetBinLowEdge(i) for i in range(1, he.GetNbinsX() + 2)])
    ey = np.array([he.GetYaxis().GetBinLowEdge(i) for i in range(1, he.GetNbinsY() + 2)])
    xe = AP.th2(he).ravel(order="C")[cells_all][keep]
    fe.Close()
    grid_ok = ex.size == C.PT_A.size and ey.size == C.PZ_A.size and np.allclose(ex, C.PT_A, rtol=0, atol=1e-12) \
        and np.allclose(ey, C.PZ_A, rtol=0, atol=1e-12)
    checks["grid_equals_E_U_axes"] = bool(grid_ok)
    checks["x_vs_E_U_rel"] = float(np.max(np.abs(xe / x - 1)))
    if not (grid_ok and checks["x_vs_E_U_rel"] <= TOL_ID):
        stop(f"grid/central value: {grid_ok} {checks['x_vs_E_U_rel']}")

    # ---- check 2: control against the frozen analysis -------------------------------------------------------------
    step = AP.step_stat(xX["PB"], xX["PA"], met, tX["PB"], tX["PA"])
    step_ref = A["comparisons"]["dr_PB/PA"]["step"]["value"]
    bias_pb = e["PB"] * (xX["PB"] / xX["PA"] - 1)
    c2 = met.chi2(bias_pb)["pz"]
    c2_ref = A["comparisons"]["bias_PB"]["chi2_pz_marginal"]
    checks["control_dr_step"] = {"value": step, "frozen": step_ref, "rel": abs(step / step_ref - 1)}
    checks["control_bias_PB_chi2_pz"] = {"value": c2, "frozen": c2_ref, "rel": abs(c2 / c2_ref - 1)}
    for nm in ("control_dr_step", "control_bias_PB_chi2_pz"):
        if not checks[nm]["rel"] <= TOL_CONTROL:
            stop(f"{nm}: {checks[nm]}")

    # ---- construction --------------------------------------------------------------------------------------------
    def build(q):
        """q: dict X -> per-cell quantity (r or x). Returns (C, vectors, g)."""
        m = sum(e[X] * q[X] for X in PER)
        g = {X: q[X] / m - 1 for X in PER}
        V2 = sum(e[X] ** 2 for X in PER)
        kk = V2 / (1 - V2)
        v = {X: np.sqrt(kk * e[X]) * x * g[X] for X in PER}
        return sum(np.outer(v[X], v[X]) for X in PER), v, g, kk

    def build_ref(q):
        b = {X: e[X] * (q[X] / q["PA"] - 1) * x for X in ("PB", "PC")}
        return sum(np.outer(b[X], b[X]) for X in b), b

    C_PL, v, g, kfac = build(rX)
    S_raw, _, _, _ = build(xX)
    S_ref, b_dr = build_ref(rX)
    S_ref_raw, b_raw = build_ref(xX)

    # ---- check 3: identity, symmetry, PSD, rank ------------------------------------------------------------------
    gsum = np.max(np.abs(sum(e[X] * g[X] for X in PER)))
    lam = np.linalg.eigvalsh(0.5 * (C_PL + C_PL.T))
    asym = float(np.max(np.abs(C_PL - C_PL.T)) / np.max(np.abs(C_PL)))
    rank = int(np.sum(lam > TOL_ID * lam.max()))
    checks["identity_sum_e_g"] = gsum
    checks["symmetry_rel"] = asym
    checks["min_eig_over_max"] = float(lam.min() / lam.max())
    checks["rank"] = rank
    if not (gsum <= TOL_ID and asym <= TOL_ID and lam.min() >= -TOL_ID * lam.max() and rank <= 2):
        stop(f"identity/symmetry/PSD/rank: {gsum} {asym} {lam.min() / lam.max()} {rank}")

    # ---- check 4: functionals from vectors -----------------------------------------------------------------------
    F = np.vstack([C.area(met.cells)[None, :], C.proj_matrix("pt", met.cells), C.proj_matrix("pz", met.cells)])
    FCF = F @ C_PL @ F.T
    from_vec = sum(np.outer(F @ v[X], F @ v[X]) for X in PER)
    checks["functionals_from_vectors_rel"] = float(np.max(np.abs(FCF - from_vec)) / np.max(np.abs(FCF)))
    e_const = all(np.ptp(e[X]) <= TOL_ID * np.mean(e[X]) for X in PER)
    if e_const:
        kk = float(np.mean(kfac))
        proj = sum(kk * float(np.mean(e[X])) * np.outer(F @ (x * g[X]), F @ (x * g[X])) for X in PER)
        checks["functionals_projected_estimator_rel"] = float(np.max(np.abs(FCF - proj)) / np.max(np.abs(FCF)))
    else:
        checks["functionals_projected_estimator_rel"] = None    # e varies by cell: the diag form is the definition
    if not checks["functionals_from_vectors_rel"] <= TOL_FUNC or (
            e_const and not checks["functionals_projected_estimator_rel"] <= TOL_FUNC):
        stop(f"functionals: {checks['functionals_from_vectors_rel']} {checks['functionals_projected_estimator_rel']}")

    # ---- reported numbers ----------------------------------------------------------------------------------------
    Fx = F @ x

    def summary(Cm):
        s = np.sqrt(np.maximum(np.diag(Cm), 0)) / x
        fs = np.sqrt(np.maximum(np.diag(F @ Cm @ F.T), 0)) / np.abs(Fx)
        return {"cell_rel_sigma_pct": {"median": 100 * float(np.median(s)), "p84": 100 * float(np.percentile(s, 84)),
                                       "max": 100 * float(s.max())},
                "integral_rel_sigma_pct": 100 * float(fs[0]),
                "pt_rel_sigma_pct": (100 * fs[1:15]).round(4).tolist(),
                "pz_rel_sigma_pct": (100 * fs[15:31]).round(4).tolist(),
                "median_sigma_ratio_to_VL175": float(np.median(np.sqrt(np.maximum(np.diag(Cm), 0))
                                                               / np.sqrt(np.diag(met.C))))}

    rep = {"C_PL": summary(C_PL), "S_ref": summary(S_ref), "S_raw": summary(S_raw), "S_ref_raw": summary(S_ref_raw),
           "k_factor": float(np.mean(kfac)), "exposure_share": {X: float(np.mean(e[X])) for X in PER},
           "exposure_share_constant_over_cells": bool(e_const)}

    # noise share (DESIGN §4): the same estimator on noise-only inputs
    def frac_draws(X):
        b0 = rX[X]
        bd = [(b["x"][k_] / b["t"][k_]) / b0 - 1 for b in R[X]["boot"]]
        sd = (R[X]["s43"]["x"][k_] / R[X]["s43"]["t"][k_]) / b0 - 1
        return bd, sd

    D = {X: frac_draws(X) for X in PER}
    K = min(len(D[X][0]) for X in PER)
    V2 = sum(e[X] ** 2 for X in PER)
    kk_c = V2 / (1 - V2)

    def noise_cov(dd):
        mm = sum(e[X] * dd[X] for X in PER)
        return sum(np.outer(np.sqrt(kk_c * e[X]) * x * (dd[X] - mm), np.sqrt(kk_c * e[X]) * x * (dd[X] - mm))
                   for X in PER)

    Nb = np.mean([noise_cov({X: D[X][0][i] for X in PER}) for i in range(K)], axis=0)
    Ns = noise_cov({X: D[X][1] / np.sqrt(2) for X in PER})
    Ppz = C.proj_matrix("pz", met.cells)

    def share(Nm):
        return {"median_cell_variance_share": float(np.median(np.diag(Nm) / np.diag(C_PL))),
                "median_pz_marginal_variance_share": float(np.median(np.diag(Ppz @ Nm @ Ppz.T)
                                                                     / np.diag(Ppz @ C_PL @ Ppz.T)))}

    rep["noise_share"] = {"boot": share(Nb), "seed": share(Ns), "total": share(Nb + Ns), "n_boot": K}

    # the P_A-reference vectors against VL175 and VL175 + C_PL (reported; DESIGN §4: no pass/fail)
    def chi2s(bvec):
        o = {}
        for ax in ("pz", "pt"):
            P = met.P[ax]
            o[f"{ax}_vs_VL175"] = C.mahalanobis2(P @ bvec, P @ met.C @ P.T)[0]
            o[f"{ax}_vs_VL175_plus_C_PL"] = C.mahalanobis2(P @ bvec, P @ (met.C + C_PL) @ P.T)[0]
        return o

    # DESIGN §4 (amended): an algebraic property, not a coverage test. To first order b_X(dr) = e_X (u_X - u_A),
    # u = x g, lies in C_PL's span; there b^T C_PL^+ b = sum_i c_i^2 / (k e_i) for c = e_X (-1 at A, +1 at X), with
    # the null direction e of U removed (sum_i c_i = 0, so it needs none). Adding VL175 or projecting only lowers it.
    U = np.stack([x * g[X] for X in PER], axis=1)
    Uq, sv, _ = np.linalg.svd(U, full_matrices=False)
    Q = Uq[:, sv > TOL_ID * sv.max()]
    kk_b = float(np.mean(kfac))
    eA = float(np.mean(e["PA"]))

    def out_of_span(bvec):
        bo = bvec - Q @ (Q.T @ bvec)
        P = met.P["pz"]
        return {"euclid": float(np.linalg.norm(bo) / np.linalg.norm(bvec)),
                "pz_vl175_chi2_fraction": C.mahalanobis2(P @ bo, P @ met.C @ P.T)[0]
                / C.mahalanobis2(P @ bvec, P @ met.C @ P.T)[0]}

    cov = {}
    for nm, bvec, X in (("b_PB_dr", b_dr["PB"], "PB"), ("b_PC_dr", b_dr["PC"], "PC"),
                        ("bias_PB_raw_frozen", b_raw["PB"], "PB"), ("bias_PC_raw_frozen", b_raw["PC"], "PC")):
        eX = float(np.mean(e[X]))
        cov[nm] = {**chi2s(bvec), "out_of_span": out_of_span(bvec),
                   # a first-order bound for the dr vectors only; the raw vectors are not in C_PL's span
                   "first_order_in_span_bound": eX ** 2 * (1 / eA + 1 / eX) / kk_b if nm.endswith("_dr") else None}
    cov["note"] = ("no pass/fail: the dr vectors lie in C_PL's span to first order, so their chi2 against "
                   "VL175 + C_PL is bounded by an e-only constant whatever the data (DESIGN §4, §6 item 1)")
    rep["reference_scenario_algebraic"] = cov

    lamv, Vv = np.linalg.eigh(C_PL)
    modes = []
    epz = C.PZ_A
    hi = (epz[:-1] >= C.STEP_HI[0]) & (epz[1:] <= C.STEP_HI[1])
    for j in (-1, -2):
        u = np.sqrt(max(lamv[j], 0)) * Vv[:, j]
        if np.sum(((met.P["pz"] @ u) / met.m["pz"])[hi]) < 0:     # sign convention: + over p_par [8, 15)
            u = -u
        modes.append({"eigenvalue": float(lamv[j]),
                      "pz_marginal_rel_pct": (100 * (met.P["pz"] @ u) / met.m["pz"]).round(4).tolist(),
                      "pt_marginal_rel_pct": (100 * (met.P["pt"] @ u) / met.m["pt"]).round(4).tolist()})
    rep["eigenmodes"] = modes

    os.makedirs(outdir, exist_ok=True)
    npz = os.path.join(outdir, "playlist_term.npz")
    np.savez(npz, C_PL=C_PL, S_ref=S_ref, S_raw=S_raw, S_ref_raw=S_ref_raw, cells=met.cells, x=x, F=F,
             **{f"g_{X}": g[X] for X in PER}, **{f"e_{X}": e[X] for X in PER}, **{f"r_{X}": rX[X] for X in PER})
    out = {"design": "docs/orchestration/state/2d-closeout/playlist-term/DESIGN.md", "inputs": inputs,
           "runs": {r["path"]: r["sha256"] for r in runs}, "checks": checks, "checks_passed": True,
           "report": rep, "npz": {"path": npz, "sha256": sha256(npz)}}
    js = os.path.join(outdir, "playlist_term.json")
    json.dump(out, open(js, "w"), indent=1, default=float)
    print(json.dumps({"checks": checks, "C_PL": rep["C_PL"], "reference_scenario": cov, "noise_share": rep["noise_share"]},
                     indent=1, default=float))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
