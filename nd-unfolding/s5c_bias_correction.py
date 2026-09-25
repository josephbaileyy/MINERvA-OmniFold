#!/usr/bin/env python3
"""Contract amendment 4 (F2 development revision 2): the nominal-truth relative closure-bias
correction and its standard error, per reported functional, from the D1 development summary.

``beta_f`` is the mean relative residual (f_hat - f_true)/f_true and ``se_f`` its standard error
over the group's nominal-truth development experiments (s5c_analyze_d1.py). Every functional is
corrected (no selection threshold); the evaluator divides f_hat by (1 + beta_f) and adds
``se_f * f`` in quadrature to sigma_f.

MEASURES: development-sample closure at nominal truth. CANNOT AUTHORIZE: a correction of real data
(its size there depends on the MC background shape's fidelity), or coverage by itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--d1-summary", type=Path, required=True)
    ap.add_argument("--group", default="split_F2")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    d1 = json.loads(a.d1_summary.read_text())
    g = d1["groups"][a.group]
    beta, se = np.asarray(g["mean_rel"], float), np.asarray(g["se_rel"], float)
    if not (np.all(np.isfinite(beta)) and np.all(np.isfinite(se)) and np.all(se > 0)):
        raise SystemExit("non-finite or non-positive entries in the development summary")
    out = {"schema": "s5c-bias-correction/1",
           "source": f"{a.d1_summary} group {a.group} (n={g['n_experiments']} nominal-truth development experiments)",
           "definition": "f = f_hat / (1 + beta_f); half-width z * sqrt(sigma_f^2 + (se_f * f)^2), z = 1 and 1.96",
           "functional_names": d1["functional_names"], "beta": beta.tolist(), "se": se.tolist(),
           "summary": {"max_abs_beta_pct": float(100 * np.max(np.abs(beta))),
                       "median_abs_beta_pct": float(100 * np.median(np.abs(beta))),
                       "median_se_pct": float(100 * np.median(se)), "max_se_pct": float(100 * np.max(se))}}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
