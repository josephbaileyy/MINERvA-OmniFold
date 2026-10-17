"""Stage F checklist F9: the S5 production total plus the playlist-consistency block C_PL (COMBINATION.md).

usage: python3 -I combine_s5.py <analysis.json> <playlist_term.npz> <production_cov.npz> <outdir>

Reads the S5 product and C_PL as bytes pinned by sha256, checks that they live on the same 205 cells with the same
31-functional map, and reports the budget with and without C_PL and the chi2 rows of DESIGN.md section 4 against S5
and S5 + C_PL. The per-period runs are reloaded through the same pinned period-unfold code as playlist_term.py, only
to rebuild the four reference vectors (the raw ones are not stored in the npz) and the VL175 metric for the control.
Nothing here is adopted: the combined matrix is a candidate for Joseph's decision (checklist J2).
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
PLAYLIST_NPZ_SHA = "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476"
S5_NPZ_SHA = "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc"   # s5_rollup.py 6c437004, S5 PASS
# playlist_term.json (committed, 5b023478...) report.reference_scenario_algebraic: the control values
CONTROL = {
    "b_PB_dr": {"pz_vs_VL175": 33.12202139692209, "pz_vs_VL175_plus_C_PL": 0.6768911919817413},
    "bias_PB_raw_frozen": {"pz_vs_VL175": 33.77885700582344, "pz_vs_VL175_plus_C_PL": 1.9761447595072923},
}
PER = ("PA", "PB", "PC")
TOL_ID = 1e-12
TOL_CONTROL = 1e-9
PSD_TOL = 1e-10    # S5's own frozen PSD and rank tolerance (s5_rollup.py PSD_TOL; production DESIGN)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def stop(msg):
    raise SystemExit(f"[STOP] {msg}")


def relmax(a, b):
    return float(np.max(np.abs(a - b)) / np.max(np.abs(b)))


def main(analysis_json, pl_npz, s5_npz, outdir):
    # ---- pins -----------------------------------------------------------------------------------------------------
    for p, want in PINS.items():
        if sha256(p) != want:
            stop(f"pin {p}")
    if sha256(analysis_json) != ANALYSIS_SHA:
        stop(f"pin {analysis_json}")
    if sha256(pl_npz) != PLAYLIST_NPZ_SHA:
        stop(f"pin {pl_npz}")
    if sha256(s5_npz) != S5_NPZ_SHA:
        stop(f"pin {s5_npz}")
    sys.path.insert(0, SCRIPTS)
    import analyze_periods as AP   # noqa: E402
    PD, C = AP.PD, AP.C
    if os.path.realpath(C.__file__) != os.path.realpath(COMMON):
        stop(f"common.py imported from {C.__file__}, not the pinned {COMMON}")
    inputs = {"work_cov": PD.check_pin("work_cov"),
              "analysis_json": {"path": os.path.abspath(analysis_json), "sha256": ANALYSIS_SHA},
              "playlist_term_npz": {"path": os.path.abspath(pl_npz), "sha256": PLAYLIST_NPZ_SHA},
              "production_cov_npz": {"path": os.path.abspath(s5_npz), "sha256": S5_NPZ_SHA},
              "scripts": dict(PINS), "combine_s5_sha256": sha256(__file__)}
    A = json.load(open(analysis_json))
    roles, runs_rec = A["_roles"], A["_runs"]
    W = np.load(PD.PINS["work_cov"][0])
    cells_all = W["cells"]
    if cells_all.size != 205:
        stop(f"work_cov has {cells_all.size} cells")
    keep = np.ones(205, bool)
    met = AP.Metric(W, keep)

    def load(path):
        r = AP.load(path, cells_all)
        if path not in runs_rec or r["sha256"] != runs_rec[path]["sha256"]:
            stop(f"sha256 of {path} differs from analysis.json _runs")
        return r

    s42 = {X: load(roles[X]["s42"]) for X in PER}
    xX = {X: s42[X]["x"] for X in PER}
    tX = {X: s42[X]["t"] for X in PER}
    rX = {X: xX[X] / tX[X] for X in PER}

    P = dict(np.load(pl_npz))
    S = dict(np.load(s5_npz))
    x = P["x"]
    C_PL = P["C_PL"]
    e = {X: P[f"e_{X}"] for X in PER}
    checks = {}

    shapes = {k: S[k].shape for k in ("total", "universe", "stat", "c08", "functionals", "area", "cells_x_EU")}
    shapes.update({"C_PL": C_PL.shape, "x": x.shape, "F": P["F"].shape})
    want = {**{k: (205, 205) for k in ("total", "universe", "stat", "c08", "C_PL")},
            **{k: (205,) for k in ("area", "cells_x_EU", "x")}, "functionals": (31, 205), "F": (31, 205)}
    if shapes != want:
        stop(f"shapes: {shapes}")

    # ---- check 1: the S5 product is internally what S5 says it is -----------------------------------------------
    T = S["total"]
    checks["s5_total_equals_universe_stat_c08"] = relmax(S["universe"] + S["stat"] + S["c08"], T)
    checks["s5_total_symmetry_rel"] = float(np.max(np.abs(T - T.T)) / np.max(np.abs(T)))
    lt = np.linalg.eigvalsh(0.5 * (T + T.T))
    checks["s5_total_min_eig_over_max"] = float(lt.min() / lt.max())
    if not (checks["s5_total_equals_universe_stat_c08"] <= TOL_ID and checks["s5_total_symmetry_rel"] <= TOL_ID
            and lt.min() >= -PSD_TOL * lt.max()):
        stop(f"S5 product: {checks}")

    # ---- check 2: same cells, same order, same functionals ---------------------------------------------------------
    checks["cells_npz_equal_work_cov"] = bool(np.array_equal(P["cells"], cells_all))
    checks["cells_work_cov_equal_E_U_nonzero"] = bool(np.array_equal(cells_all, np.flatnonzero(W["EU"].ravel(order="C") > 0)))
    checks["cells_x_s5_vs_playlist_rel"] = float(np.max(np.abs(S["cells_x_EU"] / x - 1)))
    checks["cells_x_playlist_vs_work_cov_rel"] = float(np.max(np.abs(met.x / x - 1)))
    checks["functionals_s5_vs_playlist_rel"] = relmax(S["functionals"], P["F"])
    checks["area_s5_vs_playlist_rel"] = relmax(S["area"], P["F"][0])
    if not (checks["cells_npz_equal_work_cov"] and checks["cells_work_cov_equal_E_U_nonzero"]
            and checks["cells_x_s5_vs_playlist_rel"] <= TOL_ID and checks["cells_x_playlist_vs_work_cov_rel"] <= TOL_ID
            and checks["functionals_s5_vs_playlist_rel"] <= TOL_ID and checks["area_s5_vs_playlist_rel"] <= TOL_ID):
        stop(f"cell/functional alignment: {checks}")
    F = S["functionals"]

    # ---- check 3: the npz is the block the reloaded runs give -----------------------------------------------------
    checks["r_npz_vs_reloaded_rel"] = max(float(np.max(np.abs(P[f"r_{X}"] / rX[X] - 1))) for X in PER)
    m = sum(e[X] * rX[X] for X in PER)
    V2 = sum(e[X] ** 2 for X in PER)
    kk = V2 / (1 - V2)
    rebuilt = sum(np.outer(np.sqrt(kk * e[X]) * x * (rX[X] / m - 1), np.sqrt(kk * e[X]) * x * (rX[X] / m - 1))
                  for X in PER)
    checks["C_PL_rebuilt_rel"] = relmax(rebuilt, C_PL)
    if not (checks["r_npz_vs_reloaded_rel"] <= TOL_ID and checks["C_PL_rebuilt_rel"] <= TOL_ID):
        stop(f"C_PL consistency: {checks}")

    # ---- check 4: the combination -----------------------------------------------------------------------------------
    Q = T + C_PL
    checks["combined_symmetry_rel"] = float(np.max(np.abs(Q - Q.T)) / np.max(np.abs(Q)))
    lq = np.linalg.eigvalsh(0.5 * (Q + Q.T))
    checks["combined_min_eig_over_max"] = float(lq.min() / lq.max())
    if not (checks["combined_symmetry_rel"] <= TOL_ID and lq.min() >= -PSD_TOL * lq.max()):
        stop(f"combined: {checks}")

    # ---- check 5: control: the committed chi2 against VL175 and VL175 + C_PL reproduce -----------------------------
    b = {"b_PB_dr": e["PB"] * (rX["PB"] / rX["PA"] - 1) * x, "b_PC_dr": e["PC"] * (rX["PC"] / rX["PA"] - 1) * x,
         "bias_PB_raw_frozen": e["PB"] * (xX["PB"] / xX["PA"] - 1) * x,
         "bias_PC_raw_frozen": e["PC"] * (xX["PC"] / xX["PA"] - 1) * x}

    def chi2(bvec, Cm, ax):
        Pm = met.P[ax]
        return C.mahalanobis2(Pm @ bvec, Pm @ Cm @ Pm.T)[0]

    ctl = {}
    for nm, want in CONTROL.items():
        got = {"pz_vs_VL175": chi2(b[nm], met.C, "pz"), "pz_vs_VL175_plus_C_PL": chi2(b[nm], met.C + C_PL, "pz")}
        ctl[nm] = {k: {"value": got[k], "committed": want[k], "rel": abs(got[k] / want[k] - 1)} for k in want}
    checks["control_chi2"] = ctl
    if not all(v["rel"] <= TOL_CONTROL for r in ctl.values() for v in r.values()):
        stop(f"control: {ctl}")

    # ---- reported (no pass/fail) ----------------------------------------------------------------------------------
    Fx = F @ x

    def summary(Cm):
        s = np.sqrt(np.maximum(np.diag(Cm), 0)) / x
        fs = np.sqrt(np.maximum(np.diag(F @ Cm @ F.T), 0)) / np.abs(Fx)
        return {"cell_rel_sigma_pct": {"median": 100 * float(np.median(s)), "p84": 100 * float(np.percentile(s, 84)),
                                       "max": 100 * float(s.max())},
                "integral_rel_sigma_pct": 100 * float(fs[0]),
                "pt_rel_sigma_pct": (100 * fs[1:15]).round(4).tolist(),
                "pz_rel_sigma_pct": (100 * fs[15:31]).round(4).tolist(),
                "median_cell_sigma_ratio_to_VL175": float(np.median(np.sqrt(np.maximum(np.diag(Cm), 0))
                                                                    / np.sqrt(np.diag(met.C))))}

    budget = {"VL175": summary(met.C), "S5_universe": summary(S["universe"]), "S5_stat": summary(S["stat"]),
              "S5_c08": summary(S["c08"]), "S5_total": summary(T), "C_PL": summary(C_PL),
              "S5_total_plus_C_PL": summary(Q)}

    def effect(Cm_with, Cm_without):
        dc = np.diag(Cm_with) / np.diag(Cm_without)
        df = np.diag(F @ Cm_with @ F.T) / np.diag(F @ Cm_without @ F.T)
        return {"cell_sigma_increase_pct": {"median": 100 * float(np.median(np.sqrt(dc) - 1)),
                                            "max": 100 * float(np.max(np.sqrt(dc) - 1))},
                "integral_sigma_increase_pct": 100 * float(np.sqrt(df[0]) - 1),
                "functional_sigma_increase_pct_max": 100 * float(np.max(np.sqrt(df) - 1)),
                "block_share_of_cell_variance_median": float(np.median(1 - 1 / dc)),
                "block_share_of_integral_variance": float(1 - 1 / df[0])}

    rows = {}
    for nm, bvec in b.items():
        rows[nm] = {f"{ax}_vs_{lab}": chi2(bvec, Cm, ax) for ax in ("pz", "pt")
                    for lab, Cm in (("VL175", met.C), ("VL175_plus_C_PL", met.C + C_PL), ("S5", T),
                                    ("S5_plus_C_PL", Q))}
        rows[nm]["first_order_in_span_bound"] = P_bound(nm, e, kk) if nm.endswith("_dr") else None
    rows["note"] = ("no pass/fail and no coverage reading for any row (DESIGN section 4): the dr vectors lie in C_PL's "
                    "span to first order, so their chi2 against any total that includes C_PL is bounded by an e-only "
                    "constant whatever the data. The raw rows are mostly out of span: informative as a sensitivity "
                    "only, and they include the MC-predicted flux difference DESIGN section 2 calls legitimate. "
                    "The 'vs S5' and 'vs VL175' columns differ by the whole recipe change, not only by C_PL.")

    rep = {"budget": budget, "effect_of_C_PL_on_S5": effect(Q, T), "S5_total_vs_VL175": {
        "median_cell_sigma_ratio": budget["S5_total"]["median_cell_sigma_ratio_to_VL175"]},
        "reference_scenario_algebraic": rows,
        "ranks_rcond_1e-10": {"S5_total": int(np.sum(lt > PSD_TOL * lt.max())),
                              "combined": int(np.sum(lq > PSD_TOL * lq.max()))}}

    os.makedirs(outdir, exist_ok=True)
    npz = os.path.join(outdir, "s5_plus_playlist.npz")
    np.savez(npz, total_plus_C_PL=Q, s5_total=T, C_PL=C_PL, cells_x_EU=x, functionals=F, area=S["area"])
    out = {"record": "docs/orchestration/state/2d-closeout/playlist-term/COMBINATION.md", "inputs": inputs,
           "checks": checks, "checks_passed": True, "report": rep, "adopted": False,
           "npz": {"path": npz, "sha256": sha256(npz)}}
    js = os.path.join(outdir, "combination.json")
    json.dump(out, open(js, "w"), indent=1, default=float)
    print(json.dumps({"checks": checks, "budget_cells": {k: v["cell_rel_sigma_pct"] for k, v in budget.items()},
                      "integral": {k: v["integral_rel_sigma_pct"] for k, v in budget.items()},
                      "effect": rep["effect_of_C_PL_on_S5"], "chi2": rows, "npz": out["npz"]}, indent=1, default=float))


def P_bound(nm, e, kk):
    X = "PB" if "PB" in nm else "PC"
    eX, eA = float(np.mean(e[X])), float(np.mean(e["PA"]))
    return eX ** 2 * (1 / eA + 1 / eX) / float(np.mean(kk))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
