#!/usr/bin/env python3
"""PV ladder: the vertex reweights r_k of one rung, on the rung's reweight cells, in PV-2D's convention.

For vertex k and fine cell c of the rung's reweight axes (DECLARATION.md §2.2):
  g_kc, gref_c = the vertex's and the reference's (GENIE 2.12 CV) flux-repaired gen5d density integrated over the
                 other axes, per cell, with variances from sumw2 (pvl_lib.project_prediction);
  rho_kc       = g_kc / gref_c, gated at stat_max with the J-coarse pooling (pvl_lib.gated_shape_ratio);
  r_kc         = rho_kc x k_k on the assigned cells, 1 elsewhere, with k_k keeping the rung's prior truth weight
                 (w_truth on truth-passing rows of the rung's npz) summed over the assigned cells.
The region is the cells where the recorded central value (the rung's NC target, (e)) is positive, projected onto
the reweight axes when they are fewer than the npz's, and both predictions are positive. GiBUU is defined only below
p_parallel = 10 GeV/c: a cell cut when p_parallel is a reweight axis; otherwise its predictions and the prior weight
are taken over p_parallel < 10 GeV/c only, and the ratio file carries the truth cut that pvl_lib.row_weight applies.

Writes one pvl-ratio/1 JSON per vertex, its rho-squared PC fallback, the identity (tune_v1), and ratios.json
(inputs, per-cell g, rho, labels, gate tiers with prior-weight shares) into --out/<rung>/. Refuses to overwrite.

MEASURES: fixed predictions and their shape ratios. CANNOT AUTHORIZE: any verdict.
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
import pvl_lib as L  # noqa: E402

TIERS = (("own ratio", ("fine",)), ("coarse cell", ("coarse",)), ("r = 1", ("noisy", "off")))


def checked(spec, what):
    got = L.sha256_path(spec["path"])
    if got != spec["sha256"]:
        raise SystemExit(f"[FAIL] {what}: sha256 {got} != {spec['sha256']}")
    return {"path": spec["path"], "sha256": got}


def load_gen5d(path):
    import gen5d_to_rootpreds as g5

    x, edges = g5.load(path)
    L.check_edges(L.AXES5, edges)
    s2 = np.asarray(np.load(path, allow_pickle=True)["sumw2_flat"], float).reshape(x.shape)
    return x, s2, edges


def prior_weight(z, names, axes, pz_max=None):
    m = np.asarray(z["pass_truth"], bool)
    gen = np.asarray(z["MCgen"], float)[m]
    w = np.asarray(z["w_truth"], float)[m]
    if pz_max is not None:
        keep = gen[:, names.index("pz")] < pz_max
        gen, w = gen[keep], w[keep]
    c = L.flat_index(gen[:, [names.index(a) for a in axes]], axes)
    n = int(np.prod([len(L.FINE[a]) - 1 for a in axes]))
    return np.bincount(c[c >= 0], weights=w[c >= 0], minlength=n)


def write_ratio(out_dir, name, label, axes, r, extra):
    rec = {"schema": L.RATIO_SCHEMA, "vertex": name, "label": label, "axes": list(axes),
           "edges": {a: list(L.FINE[a]) for a in axes}, "r": np.asarray(r, float).tolist()}
    rec.update(extra)
    path = out_dir / f"{name}.json"
    path.write_text(json.dumps(rec, indent=1) + "\n")
    return path.name, L.sha256_path(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--rung", required=True, choices=sorted(L.RUNGS))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text())
    rc = cfg["rungs"][a.rung]
    out_dir = a.out / a.rung
    if out_dir.exists():
        raise SystemExit(f"[FAIL] refusing to write into the existing {out_dir}")
    stat_max = float(cfg["ratio"]["stat_max"])
    npz_axes, axes, _ = L.RUNGS[a.rung]

    inputs = {"npz": checked(rc["npz"], "npz"), "cv": checked(rc["nc"]["e"], "recorded central value")}
    z = np.load(rc["npz"]["path"], allow_pickle=True)
    names = L.npz_axes(z)
    if names != npz_axes:
        raise SystemExit(f"[FAIL] the npz's axes {names} are not the rung's {npz_axes}")
    L.check_edges(names, [z[f"edges_{i}"] for i in range(int(z["nedges"]))])
    cv = np.asarray(np.load(rc["nc"]["e"]["path"], allow_pickle=True)["xsec_flat"], float)
    cv_cells = L.project_xsec(cv, names, axes) if axes != names else cv
    n = cv_cells.size
    p = prior_weight(z, names, axes)
    pz_hi = None
    if "pz" in axes:
        idx = np.unravel_index(np.arange(n), tuple(len(L.FINE[x]) - 1 for x in axes))
        pz_hi = np.asarray(L.FINE["pz"][1:])[idx[axes.index("pz")]]
    coarse = L.coarse_of_cells(axes)

    inputs["reference"] = checked(cfg["reference"], "reference")
    xr, sr, edges = load_gen5d(cfg["reference"]["path"])
    out_dir.mkdir(parents=True)
    out = {"schema": "pvl-ratios/1", "rung": a.rung, "definition": __doc__, "axes": list(axes),
           "n_cells": n, "stat_max": stat_max, "j_coarse_edges": {x: list(L.J_EDGES[x]) for x in axes},
           "cv_positive_cells": int((cv_cells > 0).sum()), "prior_truth_weight": p.tolist(),
           "inputs": inputs, "vertices": {},
           "code": {"pvl_ratios.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__)}}
    fn, sha = write_ratio(out_dir, "tune_v1", "MINERvA Tune v1 = the MC prior itself (r = 1 exactly)", axes,
                          np.ones(n), {"identity": True})
    out["vertices"]["tune_v1"] = {"ratio_file": fn, "ratio_sha256": sha, "identity": True}
    for name, spec in cfg["vertices"].items():
        inputs[name] = checked(spec, name)
        pz_max = spec.get("pz_max")
        x, s2, _ = load_gen5d(spec["path"])
        cut_as_truth = pz_max is not None and "pz" not in axes
        g, var = L.project_prediction(x, s2, edges, axes, pz_max if cut_as_truth else None)
        gref, vref = L.project_prediction(xr, sr, edges, axes, pz_max if cut_as_truth else None)
        pk = prior_weight(z, names, axes, pz_max) if cut_as_truth else p
        region = (cv_cells > 0) & (g > 0) & (gref > 0)
        if pz_max is not None and not cut_as_truth:
            region &= pz_hi <= float(pz_max)
        rho, assigned, label, st = L.gated_shape_ratio(g, var, gref, vref, region, coarse, stat_max)
        r, k = L.normalize(rho, assigned, pk)
        extra = {"k": k, "stat_max": stat_max, "source": inputs[name], "reference": inputs["reference"]}
        if cut_as_truth:
            extra["truth_cut"] = {"axis": "pz", "below": float(pz_max)}
        elif pz_max is not None:
            extra["pz_max_cells"] = float(pz_max)
        fn, sha = write_ratio(out_dir, name, spec["label"], axes, r, extra)
        on = cv_cells > 0
        tiers = {t: {"cells": int(np.isin(label[on], labs).sum()),
                     "prior_weight_share": float(pk[on & np.isin(label, labs)].sum() / pk[on].sum())}
                 for t, labs in TIERS}
        rr = r[on]
        rec = {"ratio_file": fn, "ratio_sha256": sha, "k": k, "tiers_on_cv_positive_cells": tiers,
               "label_counts": {lab: int((label == lab).sum()) for lab in ("fine", "coarse", "noisy", "off")},
               "g": g.tolist(), "var": var.tolist(), "gref": gref.tolist(), "rho": rho.tolist(),
               "label": label.tolist(), "stat_rel": np.where(np.isfinite(st), st, -1.0).tolist(),
               "r_on_cv_positive": {"median_abs_dev": float(np.median(np.abs(rr - 1))),
                                    "p90_abs_dev": float(np.percentile(np.abs(rr - 1), 90)),
                                    "max_abs_dev": float(np.max(np.abs(rr - 1))),
                                    "min": float(rr.min()), "max": float(rr.max())}}
        r2, k2 = L.normalize(rho ** 2, assigned, pk)
        extra2 = {"k": k2, "fallback_of": name, "base_ratio_sha256": sha}
        if cut_as_truth:
            extra2["truth_cut"] = extra["truth_cut"]
        fn2, sha2 = write_ratio(out_dir, f"{name}_sq", spec["label"] + "; PC fallback: rho squared", axes, r2, extra2)
        rec["fallback"] = {"ratio_file": fn2, "ratio_sha256": sha2}
        out["vertices"][name] = rec
        out["vertices"][f"{name}_sq"] = {"ratio_file": fn2, "ratio_sha256": sha2, "fallback_of": name}
        print(f"[pvl] {a.rung} {name}: tiers {json.dumps(tiers)}, k={k:.6f}, r on CV>0 cells in "
              f"[{rr.min():.4f}, {rr.max():.4f}], median |r-1| {rec['r_on_cv_positive']['median_abs_dev']:.4f}")
    (out_dir / "ratios.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
