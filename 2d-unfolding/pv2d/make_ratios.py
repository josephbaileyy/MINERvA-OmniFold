#!/usr/bin/env python3
"""PV-2D: the vertex reweights r_k on the 14 x 16 (pT, p_parallel) truth cells, from the flux-repaired gen5d
predictions, in the s5p convention (a generator's shape ratio to GENIE 2.12 CV, applied to the Tune v1 prior).

For vertex k and cell c:
  g_kc   = the vertex's 5D density integrated over (E_avail, q3, W) by gen5d_to_rootpreds.integrate, times the
           cell's (pT, p_parallel) area: its integrated cross section in the cell, with its variance from sumw2;
  gref_c = the same for the reference, untuned GENIE 2.12 CV (the base Tune v1 tunes and the s5p D1-D4 base);
  rho_kc = g_kc / gref_c, statistically gated (pv2d_lib.gated_shape_ratio): the cell's own ratio where its relative
           error is <= stat_max, else the pooled ratio over the cell's s5p coarse (pT, p_parallel) cell, else 1;
  r_kc   = rho_kc x k on the assigned cells, 1 elsewhere, with k fixing E_U's prior truth weight (hTruth2D) summed
           over the assigned cells (pv2d_lib.build_ratio: a pure shape departure).
The region is E_U's 205 reported cells (hXSec2D > 0) where both predictions are positive; for GiBUU only
p_parallel < 10 GeV/c (KNOWN_ISSUES 82: GiBUU has no E_nu > 20 GeV, and above about 10 GeV/c its deficit is that
cut, which GENIE's E_nu < 100 GeV reference does not share). Tune v1 is the prior itself, so r = 1 exactly: the
nominal control's file. The positive control's fallback for vertex k is r_k squared, renormalized the same way.

Writes one pv2d-ratio/1 JSON per vertex (and per fallback) and projections.json (inputs, sha256, per-cell g, rho,
labels and errors) into --out. Refuses to overwrite. Run on Perlmutter in root_6_28 (ROOT reads E_U).

MEASURES: fixed predictions and their shape ratios. CANNOT AUTHORIZE: any comparison verdict.
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


def read_th2(f, name):
    h = f.Get(name)
    if not h:
        raise SystemExit(f"[FAIL] {name} missing")
    return np.array([[h.GetBinContent(i, j) for j in range(1, L.NPZ + 1)] for i in range(1, L.NPT + 1)])


def project(npz):
    """Integrated cross section per (pT, p_parallel) cell and its variance (sumw2 is per-event squared density,
    so the integrated variance is sum over sub-cells of sumw2 x volume^2, the gen5d convention)."""
    x, e = g5.load(npz)
    if tuple(e[0]) != L.PT_EDGES or tuple(e[1]) != L.PZ_EDGES:
        raise SystemExit(f"[FAIL] {npz}: (pT, p_parallel) edges differ from the paper binning")
    area = np.outer(np.diff(e[0]), np.diff(e[1]))
    g = g5.integrate(x, e, (0, 1)) * area
    s2 = np.asarray(np.load(npz, allow_pickle=True)["sumw2_flat"], float).reshape(x.shape)
    vol = np.einsum("a,b,c,d,f->abcdf", *[np.diff(k) for k in e])
    return g, (s2 * vol ** 2).sum(axis=(2, 3, 4))


def checked(spec, what):
    got = L.sha256_path(spec["path"])
    if got != spec["sha256"]:
        raise SystemExit(f"[FAIL] {what}: sha256 {got} != {spec['sha256']}")
    return {"path": spec["path"], "sha256": got}


def write_ratio(out_dir, name, label, r, extra, E_U):
    rec = {"schema": L.RATIO_SCHEMA, "vertex": name, "label": label, "pt_edges": list(L.PT_EDGES),
           "pz_edges": list(L.PZ_EDGES), "r": r.tolist(), "E_U": E_U}
    rec.update(extra)
    path = out_dir / f"{name}.json"
    path.write_text(json.dumps(rec, indent=1) + "\n")
    return path.name, L.sha256_path(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text())
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to write into the existing {a.out}")
    a.out.mkdir(parents=True)
    stat_max = float(cfg["ratio"]["stat_max"])

    inputs = {"E_U": checked(cfg["inputs"]["E_U"], "E_U")}
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(inputs["E_U"]["path"])
    p = read_th2(f, "hTruth2D")
    xs = read_th2(f, "hXSec2D")
    f.Close()
    reported = xs > 0
    if int(reported.sum()) != 205:
        raise SystemExit(f"[FAIL] E_U has {int(reported.sum())} reported cells, expected 205")
    pz_hi = np.asarray(L.PZ_EDGES[1:])[None, :] * np.ones((L.NPT, 1))

    inputs["reference"] = checked(cfg["reference"], "reference")
    gref, vref = project(cfg["reference"]["path"])
    out = {"schema": "pv2d-projections/1", "definition": __doc__, "pt_edges": list(L.PT_EDGES),
           "pz_edges": list(L.PZ_EDGES), "reported_cells": [int(i) for i in np.flatnonzero(reported.ravel())],
           "stat_max": stat_max, "coarse_pt": list(L.COARSE_PT), "coarse_pz": list(L.COARSE_PZ),
           "prior_truth_weight": p.tolist(), "reference": {"label": cfg["reference"]["label"], "g": gref.tolist(),
                                                           "var": vref.tolist()},
           "vertices": {}, "inputs": inputs, "code": {
               "make_ratios.py": L.sha256_path(__file__), "pv2d_lib.py": L.sha256_path(L.__file__),
               "gen5d_to_rootpreds.py": L.sha256_path(g5.__file__)}}
    for name, spec in cfg["vertices"].items():
        if spec.get("identity"):
            fn, sha = write_ratio(a.out, name, spec["label"], np.ones((L.NPT, L.NPZ)), {"identity": True},
                                  inputs["E_U"])
            out["vertices"][name] = {"ratio_file": fn, "ratio_sha256": sha, "identity": True}
            print(f"[pv2d] {name}: identity")
            continue
        inputs[name] = checked(spec, name)
        g, var = project(spec["path"])
        region = reported & (g > 0) & (gref > 0)
        if spec.get("pz_max") is not None:
            region &= pz_hi <= float(spec["pz_max"])
        rho, assigned, label, st = L.gated_shape_ratio(g, var, gref, vref, region, stat_max)
        r, k = L.build_ratio(rho, np.ones_like(rho), p, assigned)
        rr = r[reported]
        counts = {lab: int((label == lab)[reported].sum()) for lab in ("fine", "coarse", "noisy", "off")}
        fn, sha = write_ratio(a.out, name, spec["label"], r,
                              {"k": k, "pz_max": spec.get("pz_max"), "stat_max": stat_max, "source": inputs[name],
                               "reference": inputs["reference"], "label_counts_on_reported": counts}, inputs["E_U"])
        rec = {"ratio_file": fn, "ratio_sha256": sha, "k": k, "label_counts_on_reported": counts,
               "prior_weight_frac_assigned": float(p[assigned].sum() / p[reported].sum()),
               "g": g.tolist(), "var": var.tolist(), "rho": rho.tolist(), "label": label.tolist(),
               "stat_rel": np.where(np.isfinite(st), st, -1.0).tolist(),
               "r_on_reported": {"median_abs_dev": float(np.median(np.abs(rr - 1))),
                                 "p90_abs_dev": float(np.percentile(np.abs(rr - 1), 90)),
                                 "max_abs_dev": float(np.max(np.abs(rr - 1))),
                                 "min": float(rr.min()), "max": float(rr.max())}}
        r2, k2 = L.build_ratio(rho ** 2, np.ones_like(rho), p, assigned)
        fn2, sha2 = write_ratio(a.out, f"{name}_sq", spec["label"] + "; PC fallback: rho squared", r2,
                                {"k": k2, "fallback_of": name, "base_ratio_sha256": sha}, inputs["E_U"])
        rec["fallback"] = {"ratio_file": fn2, "ratio_sha256": sha2}
        out["vertices"][name] = rec
        out["vertices"][f"{name}_sq"] = {"ratio_file": fn2, "ratio_sha256": sha2, "fallback_of": name}
        print(f"[pv2d] {name}: {counts}, prior weight assigned {rec['prior_weight_frac_assigned']:.3f}, "
              f"k={k:.6f}, r on reported in [{rr.min():.4f}, {rr.max():.4f}], median |r-1| "
              f"{rec['r_on_reported']['median_abs_dev']:.4f}, p90 {rec['r_on_reported']['p90_abs_dev']:.4f}")
    cross = cfg.get("cross_check")
    if cross:
        inputs["cross_check"] = checked(cross, "cross-check")
        g, _ = project(cross["path"])
        f = ROOT.TFile.Open(inputs["E_U"]["path"])
        t = read_th2(f, "hTruth2D") / np.where(read_th2(f, "hOFCompleteness2D") > 0,
                                                read_th2(f, "hOFCompleteness2D"), 1.0)
        f.Close()
        m = reported & (g > 0)
        rho = (g[m] / g[m].sum()) / (t[m] / t[m].sum())
        out["cross_check"] = {"what": cross["label"], "n_cells": int(m.sum()),
                              "shape_ratio_median_abs_dev": float(np.median(np.abs(rho - 1))),
                              "shape_ratio_max_abs_dev": float(np.max(np.abs(rho - 1))),
                              "argmax_cell": int(np.flatnonzero(m.ravel())[int(np.argmax(np.abs(rho - 1)))])}
        print(f"[pv2d] cross-check: median |rho-1| {out['cross_check']['shape_ratio_median_abs_dev']:.4g}, "
              f"max {out['cross_check']['shape_ratio_max_abs_dev']:.4g} at cell {out['cross_check']['argmax_cell']}")
    rank = sorted((v for v in out["vertices"] if "r_on_reported" in out["vertices"][v]),
                  key=lambda v: -out["vertices"][v]["r_on_reported"]["median_abs_dev"])
    out["pc_vertex_rule"] = {"rule": "the vertex with the largest median |r - 1| over the 205 reported cells",
                             "ranking": rank, "pc_vertex": rank[0]}
    (a.out / "projections.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"[pv2d] positive-control vertex by rule: {rank[0]} (ranking {rank})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
