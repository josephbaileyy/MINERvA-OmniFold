#!/usr/bin/env python3
"""PV-2D readout: the controls (with the pass rules fixed in DECLARATION.md) and the per-vertex shifts, the envelope
h and its comparison with the adopted sigma_tot (Q) and the published per-bin uncertainties.

Every run product is checked before use (a failed check makes that run not a result and the readout refuses):
  * its pv2d ratio TNamed sha256 equals the declared ratio file's;
  * on a prior run, hTruth2D / hTruth2D(nominal run) equals r per cell to 1e-9 on cells with content (the
    reweight was applied), and both completeness guards are present and <= 1e-9 (the denominator was reweighted);
  * on a closure run, hTruthRew2D / hTruth2D equals the closure r per cell to 1e-9.

  NC  nominal control: the tune_v1 (r = 1) run against E_U on the 205 cells; PASS iff max |x/x_EU - 1| < 1e-5.
  PC  positive control at the declared vertex: data shift against minus the closure bias at that vertex,
      pv2d_lib.positive_control (POWERED iff >= 20 cells with |bias| > 1%; PASS iff corr >= 0.7 and
      0.67 <= slope <= 1.5).

Run on Perlmutter in root_6_28 after every declared product exists. Writes --out (JSON); refuses to overwrite.

MEASURES: data-side prior dependence of the 2D estimator E_U at the declared vertices. CANNOT AUTHORIZE: a per-cell
bias bound (s5p amendment 6, LOW_items.bound_wording), an uncertainty component, or any claim change.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
for _p in (str(_HERE), str(_ROOT / "2d-unfolding" / "uq")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pv2d_lib as L  # noqa: E402

TOL_R = 1e-9
TOL_GUARD = 1e-9


def th2(f, name):
    h = f.Get(name)
    if not h:
        raise SystemExit(f"[FAIL] {f.GetName()}: {name} missing")
    return np.array([[h.GetBinContent(i, j) for j in range(1, L.NPZ + 1)] for i in range(1, L.NPT + 1)])


def named(f, name):
    o = f.Get(name)
    return None if not o else o.GetTitle()


def param(f, name):
    o = f.Get(name)
    return None if not o else float(o.GetVal())


def ratio_matches(num, den, r, what):
    ok = den > 0
    d = float(np.max(np.abs(num[ok] / den[ok] / r[ok] - 1.0)))
    if d > TOL_R:
        raise SystemExit(f"[FAIL] {what}: reweight not applied as declared (max rel {d:.3e})")
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--ratios", type=Path, default=_HERE / "ratios")
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--pc-vertex", required=True)
    ap.add_argument("--vertices", required=True, help="comma-separated prior vertices with a data product")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    import ROOT
    import _ours_only_chi2 as oo
    ROOT.gROOT.SetBatch(True)
    cfg = json.loads(a.config.read_text())
    proj = json.loads((a.ratios / "projections.json").read_text())
    inputs = {}

    def checked(key):
        spec = cfg["inputs"][key]
        got = L.sha256_path(spec["path"])
        if got != spec["sha256"]:
            raise SystemExit(f"[FAIL] {key} sha256 {got} != {spec['sha256']}")
        inputs[key] = {"path": spec["path"], "sha256": got}
        return spec["path"]

    f = ROOT.TFile.Open(checked("E_U"))
    x_eu = th2(f, "hXSec2D")
    f.Close()
    rep = x_eu > 0
    cells = np.flatnonzero(rep.ravel())
    if cells.size != 205 or cells.tolist() != proj["reported_cells"]:
        raise SystemExit("[FAIL] reported cells differ from projections.json")

    q = np.load(checked("Q"))
    if q["cells"].tolist() != cells.tolist() or not np.allclose(q["x"], x_eu.ravel()[cells], rtol=1e-12, atol=0):
        raise SystemExit("[FAIL] Q's cells or x differ from E_U")
    sig_q = np.sqrt(np.diag(q["Q"])) / q["x"]
    fp = ROOT.TFile.Open(checked("paper"))
    xp = oo.flatten_paper(fp.Get("pt_pl_cross_section"))
    vp = np.diag(oo.tmatrix_to_numpy(fp.Get("TotalCovariance")))
    fp.Close()
    if not np.array_equal(xp > 0, rep.ravel()):
        raise SystemExit("[FAIL] the paper's reported cells differ from E_U's")
    sig_paper = np.sqrt(vp[cells]) / xp[cells]

    ratios = {}
    for name in proj["vertices"]:
        path = a.ratios / proj["vertices"][name]["ratio_file"]
        sha = proj["vertices"][name]["ratio_sha256"]
        ratios[name] = (L.load_ratio(path, sha)[0], sha)

    def open_run(tag, flag, vertex):
        path = a.products / f"{tag}.root"
        if not path.exists():
            raise SystemExit(f"[FAIL] product {path} missing")
        g = ROOT.TFile.Open(str(path))
        r, sha = ratios[vertex]
        if named(g, f"pv2d_{flag}RatioSha256") != sha:
            raise SystemExit(f"[FAIL] {tag}: {flag} ratio sha256 {named(g, f'pv2d_{flag}RatioSha256')} != {sha}")
        out = {"x": th2(g, "hXSec2D"), "truth": th2(g, "hTruth2D"), "sha256": L.sha256_path(path),
               "driverSha256": named(g, "driverSha256"), "omnifoldHelperSha256": named(g, "omnifoldHelperSha256"),
               "omnifoldHelperFile": named(g, "omnifoldHelperFile")}
        if flag == "closure":
            out["truth_rew_xsec"] = th2(g, "hTruthRewXSec2D")
            out["truth_rew"] = th2(g, "hTruthRew2D")
            out["r_check"] = ratio_matches(out["truth_rew"], out["truth"], r, f"{tag} closure truth")
        else:
            for k in ("completeness_guard_numpy", "completeness_guard_product"):
                v = param(g, f"pv2d_{k}")
                if v is None or v > TOL_GUARD:
                    raise SystemExit(f"[FAIL] {tag}: {k} = {v}")
                out[k] = v
        g.Close()
        return out

    nom = open_run("data_tune_v1", "prior", "tune_v1")
    x0 = nom["x"].ravel()[cells]
    nc = L.nominal_control(x0, x_eu.ravel()[cells])
    runs = {"data_tune_v1": {k: nom[k] for k in nom if k not in ("x", "truth")}}

    shifts, per_vertex = {}, {}
    for v in a.vertices.split(","):
        run = open_run(f"data_{v}", "prior", v)
        run["r_check"] = ratio_matches(run["truth"], nom["truth"], ratios[v][0], f"data_{v} prior truth")
        s = L.rel_shift(run["x"].ravel()[cells], x0)
        shifts[v] = s
        per_vertex[v] = dict(L.summary(s), argmax_cell=int(cells[L.summary(s)["argmax"]]),
                             signed_median=float(np.median(s)),
                             integral_shift=float(_integral(run["x"]) / _integral(nom["x"]) - 1.0),
                             shift=s.tolist())
        runs[f"data_{v}"] = {k: run[k] for k in run if k not in ("x", "truth")}

    h, who = L.envelope(shifts)
    env = dict(L.summary(h), dominant_vertex_counts={v: who.count(v) for v in shifts}, h=h.tolist(),
               dominant=who)

    cn = open_run("closure_tune_v1", "closure", "tune_v1")
    cp = open_run(f"closure_{a.pc_vertex}", "closure", a.pc_vertex)
    floor = L.rel_shift(cn["x"].ravel()[cells], cn["truth_rew_xsec"].ravel()[cells])
    bias = L.rel_shift(cp["x"].ravel()[cells], cp["truth_rew_xsec"].ravel()[cells])
    if a.pc_vertex in shifts:
        pc_shift = shifts[a.pc_vertex]
    else:   # the declared fallback: a data run outside the envelope
        run = open_run(f"data_{a.pc_vertex}", "prior", a.pc_vertex)
        run["r_check"] = ratio_matches(run["truth"], nom["truth"], ratios[a.pc_vertex][0],
                                       f"data_{a.pc_vertex} prior truth")
        pc_shift = L.rel_shift(run["x"].ravel()[cells], x0)
        runs[f"data_{a.pc_vertex}"] = {k: run[k] for k in run if k not in ("x", "truth")}
    pc = L.positive_control(pc_shift, bias)
    big = np.abs(bias) > 0.01
    pc.update({"vertex": a.pc_vertex, "closure_floor": L.summary(floor), "bias": L.summary(bias),
               "bias_cells": bias.tolist(), "shift_cells": pc_shift.tolist(),
               "shift_ge_bias_frac": float(np.mean(np.abs(pc_shift)[big] >= np.abs(bias)[big]))
               if big.any() else None})
    runs["closure_tune_v1"] = {k: cn[k] for k in cn if k not in ("x", "truth", "truth_rew", "truth_rew_xsec")}
    runs[f"closure_{a.pc_vertex}"] = {k: cp[k] for k in cp if k not in ("x", "truth", "truth_rew", "truth_rew_xsec")}

    out = {"schema": "pv2d-readout/1", "estimator": "E_U, configuration (a): LightGBM 100 trees, 8 leaves, lr 0.1, "
           "--seed 42, purity subtraction, 5 iterations", "cells": cells.tolist(),
           "controls": {"NC": nc, "PC": pc}, "vertices": per_vertex, "envelope": env,
           "sigma_Q": {"median": float(np.median(sig_q)), "cells": sig_q.tolist()},
           "sigma_paper": {"median": float(np.median(sig_paper)), "cells": sig_paper.tolist()},
           "h_vs_sigma_Q": L.compare_to_sigma(h, sig_q), "h_vs_sigma_paper": L.compare_to_sigma(h, sig_paper),
           "h_vs_scalar": {"median_h_over_6.45pct": float(np.median(h) / 0.0645),
                           "median_h_over_6.87pct": float(np.median(h) / 0.0687)},
           "runs": runs, "inputs": inputs, "ratios_projection_sha256": L.sha256_path(a.ratios / "projections.json"),
           "code": {"pv2d_analyze.py": L.sha256_path(__file__), "pv2d_lib.py": L.sha256_path(L.__file__)},
           "caveat": "h is evidence about model dependence at these vertices, not a per-cell bias bound "
                     "(s5p contract amendment 6, LOW_items.bound_wording)"}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"NC": nc, "PC": {k: pc[k] for k in ("verdict", "n_cells", "corr", "slope")},
                      "vertices": {v: {k: per_vertex[v][k] for k in ("median", "p90", "max", "integral_shift")}
                                   for v in per_vertex},
                      "envelope": {k: env[k] for k in ("median", "p90", "max")},
                      "h_vs_sigma_Q": out["h_vs_sigma_Q"], "h_vs_sigma_paper": out["h_vs_sigma_paper"]}, indent=1))
    return 0


def _integral(x):
    area = np.outer(np.diff(L.PT_EDGES), np.diff(L.PZ_EDGES))
    return float((np.asarray(x) * area).sum())


if __name__ == "__main__":
    raise SystemExit(main())
