#!/usr/bin/env python3
"""Development study D1: is the nominal-truth residual a systematic bias, a half-split artifact,
or specific to candidate F2?

For each group of development experiments (split F2; no-split F2; split production estimator) it
reports, per reported functional, the mean relative residual (f_hat - f_true)/f_true over the
group's experiments, its standard error, and the mean residual in units of the Tier-S sigma; and the
fraction of (experiment, functional) pairs inside 1 and 1.96 sigma. A bias is called systematic
when |mean| exceeds 4 standard errors.

MEASURES: development behaviour of the pseudo-experiment pipeline at nominal truth. CANNOT
AUTHORIZE: a coverage verdict (validation seeds only), or any change to the frozen contract by
itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import s5c_coverage as sc


def group(files, U, sig):
    rel, r = [], []
    for f in files:
        z = np.load(f, allow_pickle=False)
        fh, ft = U @ z["xsec_flat"], U @ z["xtrue_flat"]
        rel.append((fh - ft) / ft)
        r.append((fh - ft) / sig)
    rel, r = np.array(rel), np.array(r)
    n = rel.shape[0]
    mean = rel.mean(0)
    se = rel.std(0, ddof=1) / np.sqrt(n) if n > 1 else np.full(rel.shape[1], np.nan)
    return {"n_experiments": n, "mean_rel": mean, "se_rel": se, "mean_r": r.mean(0),
            "frac_le1": float(np.mean(np.abs(r) <= 1)), "frac_le196": float(np.mean(np.abs(r) <= 1.96)),
            "systematic": np.abs(mean) > 4 * se}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--bootstrap", type=Path, required=True)
    ap.add_argument("--split", nargs="+", required=True)
    ap.add_argument("--nosplit", nargs="+", required=True)
    ap.add_argument("--prod", nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    U, names = sc.reported_functionals(json.loads(a.contract.read_text()))
    sig = np.sqrt(np.diag(sc.stat_covariance(U, a.bootstrap, 1, 200)))
    res = {"schema": "s5c-d1/1", "functional_names": names, "groups": {}}
    for label, files in (("split_F2", a.split), ("nosplit_F2", a.nosplit), ("split_production", a.prod)):
        g = group(files, U, sig)
        worst = np.argsort(-np.abs(g["mean_rel"]))[:12]
        res["groups"][label] = {
            "n_experiments": g["n_experiments"], "frac_le1": g["frac_le1"], "frac_le196": g["frac_le196"],
            "n_systematic": int(np.sum(g["systematic"])),
            "worst": [{"name": names[i], "mean_rel_pct": 100 * float(g["mean_rel"][i]),
                       "se_rel_pct": 100 * float(g["se_rel"][i]), "mean_r": float(g["mean_r"][i])} for i in worst],
            "mean_rel": g["mean_rel"].tolist(), "se_rel": g["se_rel"].tolist()}
    a.out.write_text(json.dumps(res, indent=1))
    for label, g in res["groups"].items():
        print(f"== {label}: n={g['n_experiments']} frac<=1sig {g['frac_le1']:.2f} frac<=1.96sig {g['frac_le196']:.2f} systematic {g['n_systematic']}/{len(names)}")
        for w in g["worst"][:8]:
            print(f"   {w['name']:>16} bias {w['mean_rel_pct']:+.3f}% +- {w['se_rel_pct']:.3f}%  ({w['mean_r']:+.1f} sigma)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
