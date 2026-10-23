#!/usr/bin/env python3
"""PV-2D: the vertex reweights r_k on the 14 x 16 (pT, p_parallel) truth cells, from the flux-repaired gen5d
predictions and the 2D prior of E_U.

For vertex k and cell c (pv2d_lib.build_ratio):
  g_kc = the vertex's 5D density integrated over (E_avail, q3, W) by gen5d_to_rootpreds.integrate, times the
         cell's (pT, p_parallel) area: its integrated cross section in the cell;
  t_c  = hTruth2D_c / (hOFCompleteness2D_c x hFlux_pt): E_U's MC truth prior (MnvTune v1) in the same units up to
         one constant;
  p_c  = hTruth2D_c, the prior's truth weight, for the normalization;
  r_kc = (g_kc / t_c) x k on the vertex's region, 1 off it, with k fixing the prior's truth weight summed over the
         region (a pure shape departure).
The region is E_U's 205 reported cells (hXSec2D > 0) where g_kc > 0, and for GiBUU only p_parallel < 10 GeV/c
(KNOWN_ISSUES 82: GiBUU has no E_nu > 20 GeV, and above about 10 GeV/c its deficit is that cut). Tune v1 is the
prior itself, so r = 1 exactly: the nominal control's file.

Writes one pv2d-ratio/1 JSON per vertex and projections.json (inputs, sha256, per-cell g/t/r and the vertex's
relative statistical error per cell) into --out. Refuses to overwrite. Run on Perlmutter in root_6_28.

MEASURES: fixed predictions and their ratios to the prior. CANNOT AUTHORIZE: any comparison verdict.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
for _p in (str(_HERE), str(_ROOT / "3d-unfolding" / "genie")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pv2d_lib as L  # noqa: E402
import gen5d_to_rootpreds as g5  # noqa: E402

PZ_GIBUU_MAX = 10.0


def read_th2(f, name):
    h = f.Get(name)
    if not h:
        raise SystemExit(f"[FAIL] {name} missing")
    return np.array([[h.GetBinContent(i, j) for j in range(1, L.NPZ + 1)] for i in range(1, L.NPT + 1)])


def project(npz):
    x, e = g5.load(npz)
    if tuple(e[0]) != L.PT_EDGES or tuple(e[1]) != L.PZ_EDGES:
        raise SystemExit(f"[FAIL] {npz}: (pT, p_parallel) edges differ from the paper binning")
    area = np.outer(np.diff(e[0]), np.diff(e[1]))
    g = g5.integrate(x, e, (0, 1)) * area
    z = np.load(npz, allow_pickle=True)
    s2 = np.asarray(z["sumw2_flat"], float).reshape(x.shape)
    vol = np.einsum("a,b,c,d,f->abcdf", *[np.diff(k) for k in e])
    var = (s2 * vol ** 2).sum(axis=(2, 3, 4))
    rel = np.divide(np.sqrt(var), g, out=np.full_like(g, np.inf), where=g > 0)
    return g, rel


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    targets = [a.out / f"{k}.json" for k in cfg["vertices"]] + [a.out / "projections.json"]
    if any(t.exists() for t in targets):
        raise SystemExit(f"[FAIL] refusing to overwrite in {a.out}")

    inputs = {}
    eu = cfg["inputs"]["E_U"]
    got = L.sha256_path(eu["path"])
    if got != eu["sha256"]:
        raise SystemExit(f"[FAIL] E_U sha256 {got} != {eu['sha256']}")
    inputs["E_U"] = {"path": eu["path"], "sha256": got}
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(eu["path"])
    p = read_th2(f, "hTruth2D")
    c = read_th2(f, "hOFCompleteness2D")
    xs = read_th2(f, "hXSec2D")
    hf = f.Get("hFlux_pt")
    flux = np.array([hf.GetBinContent(i) for i in range(1, L.NPT + 1)])
    f.Close()
    reported = xs > 0
    if int(reported.sum()) != 205:
        raise SystemExit(f"[FAIL] E_U has {int(reported.sum())} reported cells, expected 205")
    t = np.divide(p, c * flux[:, None], out=np.zeros_like(p), where=(c > 0))
    pz_hi = np.asarray(L.PZ_EDGES[1:])[None, :] * np.ones((L.NPT, 1))

    out = {"schema": "pv2d-projections/1", "definition": __doc__,
           "pt_edges": list(L.PT_EDGES), "pz_edges": list(L.PZ_EDGES),
           "reported_cells": [int(i) for i in np.flatnonzero(reported.ravel())],
           "prior": {"t": t.tolist(), "p": p.tolist(), "completeness": c.tolist(), "flux_pt": flux.tolist()},
           "vertices": {}, "inputs": inputs, "code": {
               "make_ratios.py": L.sha256_path(__file__), "pv2d_lib.py": L.sha256_path(L.__file__),
               "gen5d_to_rootpreds.py": L.sha256_path(g5.__file__)}}
    for name, spec in cfg["vertices"].items():
        if spec.get("identity"):
            r, k, region, g, rel = np.ones((L.NPT, L.NPZ)), 1.0, np.zeros_like(reported), None, None
        else:
            got = L.sha256_path(spec["path"])
            if got != spec["sha256"]:
                raise SystemExit(f"[FAIL] {name}: sha256 {got} != {spec['sha256']}")
            inputs[name] = {"path": spec["path"], "sha256": got}
            g, rel = project(spec["path"])
            region = reported & (g > 0) & (t > 0) & (p > 0)
            if spec.get("pz_max") is not None:
                region &= pz_hi <= float(spec["pz_max"])
            r, k = L.build_ratio(g, t, p, region)
        rec = {"schema": L.RATIO_SCHEMA, "vertex": name, "label": spec["label"], "pt_edges": list(L.PT_EDGES),
               "pz_edges": list(L.PZ_EDGES), "r": r.tolist(), "k": k,
               "region_cells": [int(i) for i in np.flatnonzero(region.ravel())],
               "source": inputs.get(name), "E_U": inputs["E_U"], "pz_max": spec.get("pz_max")}
        path = a.out / f"{name}.json"
        path.write_text(json.dumps(rec, indent=1) + "\n")
        rr = r[reported]
        out["vertices"][name] = {
            "ratio_file": path.name, "ratio_sha256": L.sha256_path(path), "k": k,
            "n_region": int(region.sum()),
            "n_reported_outside_region": int((reported & ~region).sum()),
            "g": None if g is None else g.tolist(), "stat_rel": None if rel is None else
            np.where(np.isfinite(rel), rel, -1.0).tolist(),
            "r_on_reported": {"median_abs_dev": float(np.median(np.abs(rr - 1))),
                              "p90_abs_dev": float(np.percentile(np.abs(rr - 1), 90)),
                              "min": float(rr.min()), "max": float(rr.max())},
            "stat_rel_on_region": None if rel is None else {
                "median": float(np.median(rel[region])), "max": float(rel[region].max())}}
        print(f"[pv2d] {name}: region {int(region.sum())} cells, k={k:.6f}, r on reported in "
              f"[{rr.min():.4f}, {rr.max():.4f}], median |r-1| {np.median(np.abs(rr - 1)):.4f}")
        if not spec.get("identity"):
            # The positive control's declared fallback: the same departure at amplitude A, 1 + A (r - 1) on the
            # region, renormalized the same way; written only if positive everywhere.
            amp = float(cfg["fallback_amplitude"])
            ra = np.ones_like(r)
            ra[region] = 1.0 + amp * (r[region] - 1.0)
            if np.all(ra > 0):
                ra[region] *= p[region].sum() / (p[region] * ra[region]).sum()
                fb = dict(rec, vertex=f"{name}_a{amp:g}", r=ra.tolist(), amplitude=amp,
                          k=None, base_ratio_sha256=out["vertices"][name]["ratio_sha256"])
                fpath = a.out / f"{name}_a{amp:g}.json"
                fpath.write_text(json.dumps(fb, indent=1) + "\n")
                out["vertices"][f"{name}_a{amp:g}"] = {
                    "ratio_file": fpath.name, "ratio_sha256": L.sha256_path(fpath), "amplitude": amp,
                    "base": name, "r_on_reported": {"min": float(ra[reported].min()),
                                                    "max": float(ra[reported].max())}}
            else:
                out["vertices"][name]["fallback_not_positive"] = amp
    cross = cfg.get("cross_check")
    if cross:
        got = L.sha256_path(cross["path"])
        if got != cross["sha256"]:
            raise SystemExit(f"[FAIL] cross-check sha256 {got} != {cross['sha256']}")
        inputs["cross_check"] = {"path": cross["path"], "sha256": got}
        g, _ = project(cross["path"])
        m = reported & (g > 0)
        rho = (g[m] / g[m].sum()) / (t[m] / t[m].sum())
        out["cross_check"] = {"what": cross["label"], "n_cells": int(m.sum()),
                              "shape_ratio_median_abs_dev": float(np.median(np.abs(rho - 1))),
                              "shape_ratio_max_abs_dev": float(np.max(np.abs(rho - 1)))}
        print(f"[pv2d] cross-check {cross['label']}: median |rho-1| "
              f"{out['cross_check']['shape_ratio_median_abs_dev']:.4g}, max "
              f"{out['cross_check']['shape_ratio_max_abs_dev']:.4g}")
    (a.out / "projections.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"[pv2d] wrote {len(cfg['vertices'])} ratio files and projections.json to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
