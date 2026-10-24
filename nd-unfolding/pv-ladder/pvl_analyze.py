#!/usr/bin/env python3
"""PV ladder: one rung and arm's controls and readouts, under DECLARATION.md §3-§4's rules (numpy only).

  NC  the rung's NC run against its recorded target on the headline cells (and, for L-EW and L-5D-PV, the J
      cells): PASS iff max |x / x_ref - 1| < 1e-5 (pv2d_lib.nominal_control); bitwise equality reported.
  PC  arm e: the data shift at NuWro against minus the closure bias at NuWro on the headline cells
      (pv2d_lib.positive_control: >= 20 cells with |bias| > 1 %, corr >= 0.7, slope in [0.67, 1.5]); on
      NOT_POWERED the rho-squared fallback's products, if present, are graded by the same rule. Ungraded on the
      secondary spaces.
  readouts per space: per vertex |shift| median / p90 / max and signed median; h = max_k |shift_k| with dominant
      counts; the fraction of PC cells with |shift| >= |bias|; the closure floor; the gate tiers; h / sigma for L-EW
      against the note's adopted EW covariance (--cov-ew), none for L-3D / L-4D.

Every product must carry the rung, arm, features, ratio sha256 (from ratios.json) and the inputs' sha256 the
config names; the analysis refuses otherwise.

MEASURES: arithmetic on the products. CANNOT AUTHORIZE: any claim change.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "2d-unfolding" / "pv2d"))
import pv2d_lib as P  # noqa: E402
import pvl_lib as L  # noqa: E402

VERTICES = ("genie_mec", "nuwro", "gibuu")
NC_TOL = 1e-5
DECLARED = {"estimator_seed": 42, "iters": 5, "threads": 32}
REFINE = {"n_estimators": 400, "num_leaves": 31, "random_state": 45}  # candidate R; random_state = seed + 3
COV_EW_SHA256 = "94679d6dcdf1ff25af739354a12b69b95f8bf110bda1eb0c60ffffde983009e8"
GUARD_TOL = 1e-9
CAVEAT = ("h is evidence about model dependence at these vertices, not a per-cell bias bound (s5p contract "
          "amendment 6; PV-2D REPORT §4)")


def tasks(path):
    rows = [ln.rstrip("\n").split("\t") for ln in open(path) if ln.strip() and not ln.startswith("#")]
    return {r[0]: dict(zip(("task", "rung", "arm", "features", "vertex", "mode", "job", "role"), r)) for r in rows}


def check_meta(name, meta, task, ratios, cfg_rung, ref):
    """Refuse a product whose provenance differs from the declaration or from the first product checked (ref):
    rung, arm, mode, inputs, ratio, exact features, seed / iterations / threads, the estimator parameters, the
    refinement (arm e data: ran at R's 400/31, random_state 45; otherwise not run), both prior guards, and the
    code sha256s."""
    npz_axes, _, rung_features = L.RUNGS[task["rung"]]
    want = {"rung": task["rung"], "arm": task["arm"], "closure": task["mode"] == "closure",
            "input_npz_sha256": cfg_rung["npz"]["sha256"], "bkg_dump_sha256": cfg_rung["bkg"]["sha256"],
            "ratio_sha256": ratios["vertices"][task["vertex"]]["ratio_sha256"],
            "features": list(npz_axes if task["features"] == "all" else rung_features), **DECLARED}
    if task["features"] not in ("all", ",".join(rung_features)):
        raise SystemExit(f"[FAIL] task {task['task']}: undeclared features {task['features']!r}")
    for k, v in want.items():
        if meta.get(k) != v:
            raise SystemExit(f"[FAIL] {name}: {k} = {meta.get(k)!r}, expected {v!r}")
    ref_ev = meta["refinement"]
    if task["arm"] == "e" and task["mode"] == "data":
        got = {k: ref_ev.get("classifier_params", {}).get(k) for k in REFINE}
        if not ref_ev.get("ran") or got != REFINE:
            raise SystemExit(f"[FAIL] {name}: refinement ran={ref_ev.get('ran')} with {got}, expected {REFINE}")
    elif ref_ev.get("ran"):
        raise SystemExit(f"[FAIL] {name}: a refinement ran where none is declared")
    g = meta["completeness_guard"]
    if task["mode"] == "data":
        if g is None or g["r_spread_in_cell"] > GUARD_TOL or g["completeness"] > GUARD_TOL:
            raise SystemExit(f"[FAIL] {name}: prior guards {g!r}")
    if ref is not None:
        for k in ("code_sha256", "estimator_params"):
            if meta[k] != ref[k]:
                raise SystemExit(f"[FAIL] {name}: {k} differs from {ref['_name']}'s")


def load_product(path, task, ratios, cfg_rung, ref):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    check_meta(path.name, meta, task, ratios, cfg_rung, ref)
    meta["_name"] = path.name
    out = {"x": np.asarray(z["xsec_flat"], float), "meta": meta}
    if "xtrue_flat" in z.files:
        out["xtrue"] = np.asarray(z["xtrue_flat"], float)
    return out


def q(a):
    a = np.abs(np.asarray(a, float))
    return {"median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(np.max(a))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--tasks", type=Path, default=_HERE / "tasks.tsv")
    ap.add_argument("--rung", required=True, choices=sorted(L.RUNGS))
    ap.add_argument("--arm", required=True, choices=("e", "c"))
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--ratios", type=Path, required=True, help="ratios/<rung>/ratios.json")
    ap.add_argument("--cells", type=Path, required=True, help="cells/<rung>.json")
    ap.add_argument("--cov-ew", type=Path, default=None, help="L-EW only: covariance_eavailW.npz")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    cfg = json.loads(a.config.read_text())["rungs"][a.rung]
    T = {k: v for k, v in tasks(a.tasks).items() if v["rung"] == a.rung and v["arm"] == a.arm}
    R = L.load_json(a.ratios)
    C = L.load_json(a.cells)
    if R["rung"] != a.rung or C["rung"] != a.rung:
        raise SystemExit("[FAIL] ratios or cells are for another rung")
    if R["inputs"]["npz"]["sha256"] != cfg["npz"]["sha256"] or C["inputs"]["npz"]["sha256"] != cfg["npz"]["sha256"]:
        raise SystemExit("[FAIL] ratios or cells were made from another npz")
    names = tuple(C["axes"])
    spaces = [C["headline"]] + C["secondary"]
    cells = {s: np.asarray(v["cells"]) for s, v in C["spaces"].items()}
    first = {}

    def get(task_name):
        p = a.products / f"{task_name}.npz"
        if not p.exists():
            return None
        prod = load_product(p, T[task_name], R, cfg, first.get("meta"))
        first.setdefault("meta", prod["meta"])
        return prod

    def on(x, s):
        return L.readout_space(L.integrated(x, names), names, s)[cells[s]]

    out = {"schema": "pvl-readout/1", "rung": a.rung, "arm": a.arm, "headline": C["headline"],
           "cells": {s: cells[s].tolist() for s in spaces}, "caveat": CAVEAT, "controls": {}, "spaces": {},
           "inputs": {"ratios_sha256": L.sha256_path(a.ratios), "cells_sha256": L.sha256_path(a.cells),
                      "config_sha256": L.sha256_path(a.config), "tasks_sha256": L.sha256_path(a.tasks)},
           "code": {"pvl_analyze.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__),
                    "pv2d_lib.py": L.sha256_path(P.__file__)}}

    nc_task = f"{a.rung}_{a.arm}_all_tune_v1" if a.rung == "L-EW" else f"{a.rung}_{a.arm}_tune_v1"
    ref = cfg["nc"][a.arm]
    if L.sha256_path(ref["path"]) != ref["sha256"]:
        raise SystemExit(f"[FAIL] NC target {ref['path']}: sha256 differs from the config")
    x_ref = np.asarray(np.load(ref["path"], allow_pickle=True)["xsec_flat"], float)
    ncp = get(nc_task)
    if ncp is None:
        raise SystemExit(f"[FAIL] the NC product {nc_task} is missing")
    nc_spaces = ["EW", "J"] if names == L.AXES5 else [C["headline"]]
    out["controls"]["NC"] = {"task": nc_task, "target": ref, "tol": NC_TOL,
                             "bitwise_full_grid": bool(np.array_equal(ncp["x"], x_ref)),
                             "by_space": {s: P.nominal_control(on(ncp["x"], s), on(x_ref, s), NC_TOL)
                                          for s in nc_spaces}}
    out["controls"]["NC"]["pass"] = all(v["pass"] for v in out["controls"]["NC"]["by_space"].values())

    zero = get(f"{a.rung}_{a.arm}_tune_v1")
    vert = {v: get(f"{a.rung}_{a.arm}_{v}") for v in VERTICES}
    missing = [v for v, p in vert.items() if p is None]
    pc = None
    if a.arm == "e":
        floor, bias_p, data_p = (get(f"{a.rung}_e_closure_tune_v1"), get(f"{a.rung}_e_closure_nuwro"),
                                 vert["nuwro"])
        if None not in (floor, bias_p, data_p, zero):
            s = C["headline"]
            bias = P.rel_shift(on(bias_p["x"], s), on(bias_p["xtrue"], s))
            shift = P.rel_shift(on(data_p["x"], s), on(zero["x"], s))
            pc = {"primary": P.positive_control(shift, bias), "closure_floor": q(
                P.rel_shift(on(floor["x"], s), on(floor["xtrue"], s)))}
            big = np.abs(bias) > 0.01
            pc["primary"]["shift_ge_bias_frac"] = float(np.mean(np.abs(shift)[big] >= np.abs(bias)[big])) \
                if big.any() else None
            pc["primary"]["bias"] = q(bias)
            pc["verdict"] = pc["primary"]["verdict"]
            if pc["verdict"] == "NOT_POWERED":
                fb_d, fb_c = get(f"{a.rung}_e_nuwro_sq"), get(f"{a.rung}_e_closure_nuwro_sq")
                if fb_d is not None and fb_c is not None:
                    fbias = P.rel_shift(on(fb_c["x"], s), on(fb_c["xtrue"], s))
                    fshift = P.rel_shift(on(fb_d["x"], s), on(zero["x"], s))
                    pc["fallback"] = P.positive_control(fshift, fbias)
                    pc["verdict"] = pc["fallback"]["verdict"]
            pc["ungraded"] = {}
            for s2 in C["secondary"]:
                b2 = P.rel_shift(on(bias_p["x"], s2), on(bias_p["xtrue"], s2))
                d2 = P.rel_shift(on(data_p["x"], s2), on(zero["x"], s2))
                pc["ungraded"][s2] = P.linear_response(d2, b2)
    out["controls"]["PC"] = pc
    if a.arm == "e":
        out["h_label"] = ("positive control not passed: h is not evidence" if pc is None or pc["verdict"] != "PASS"
                          else "positive control passed")
    else:
        out["h_label"] = "arm (c): no positive control of its own (the PC ran on arm e)"
    if zero is None or missing:
        out["incomplete"] = {"zero": zero is None, "missing_vertices": missing}
    else:
        sig = None
        if a.rung == "L-EW" and a.cov_ew is not None:
            if L.sha256_path(a.cov_ew) != COV_EW_SHA256:
                raise SystemExit("[FAIL] --cov-ew is not the declared covariance_eavailW.npz")
            cz = np.load(a.cov_ew, allow_pickle=False)
            if list(cz["row_index"]) != list(range(42)):
                raise SystemExit("[FAIL] the EW covariance's rows are not EW0..EW41")
            sig = (np.sqrt(np.diag(cz["C_eavailW"])) / cz["cv_marginal"])[cells["EW"]]
            out["inputs"]["cov_ew_sha256"] = L.sha256_path(a.cov_ew)
        for s in spaces:
            x0 = on(zero["x"], s)
            sh = {v: P.rel_shift(on(vert[v]["x"], s), x0) for v in VERTICES}
            h, dom = P.envelope(sh)
            rec = {"n_cells": int(cells[s].size),
                   "vertices": {v: dict(q(sh[v]), signed_median=float(np.median(sh[v])), shift=sh[v].tolist())
                                for v in VERTICES},
                   "envelope": dict(q(h), dominant_vertex_counts={v: dom.count(v) for v in VERTICES},
                                    h=h.tolist(), dominant=dom)}
            if sig is not None and s == "EW":
                rec["sigma"] = {"what": "the note's adopted (E_avail, W) covariance (Z-cv trunk 3d7465f6 projection, "
                                        "used under the 6.4 exception; its metadata records it as not passing)",
                                "median": float(np.median(sig)), "cells": sig.tolist()}
                rec["h_vs_sigma"] = P.compare_to_sigma(h, sig)
            else:
                rec["sigma"] = None
            out["spaces"][s] = rec
    out["tiers"] = {v: R["vertices"][v]["tiers_on_cv_positive_cells"] for v in VERTICES}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    nc = out["controls"]["NC"]
    print(f"[pvl] {a.rung} {a.arm}: NC {'PASS' if nc['pass'] else 'FAIL'} "
          + ", ".join(f"{s} {v['max_rel_diff']:.3g}" for s, v in nc["by_space"].items())
          + f" (bitwise {nc['bitwise_full_grid']})")
    if pc:
        pr = pc["primary"]
        print(f"[pvl] PC {pc['verdict']}: n {pr['n_cells']}, corr {pr['corr']}, slope {pr['slope']}")
    for s, rec in out["spaces"].items():
        e = rec["envelope"]
        print(f"[pvl] {s} ({rec['n_cells']} cells): h median {100 * e['median']:.2f} %, p90 {100 * e['p90']:.2f} %, "
              f"max {100 * e['max']:.2f} %" + (f"; h/sigma median {rec['h_vs_sigma']['ratio_median']:.3f}"
                                              if "h_vs_sigma" in rec else ""))
    return 0 if nc["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
