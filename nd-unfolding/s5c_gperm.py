#!/usr/bin/env python3
"""Contract gate G-perm: row-order permutations must not move any reported functional by more than
5% of its Tier-S statistical sigma.

``|f(perm) - f(ref)| / sigma_f <= 0.05`` for every one of the contract's 153 functionals and both
P1 permutations, with ``sigma_f`` from the declared Tier-S bootstrap (ddof=1 sample covariance of
replicas 1..200). Reads only committed or declared products.

MEASURES: the deterministic candidate's sensitivity to an irrelevant choice, in units of its own
statistical sigma. CANNOT AUTHORIZE: coverage, or any statement about other estimator choices.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import s5c_coverage as sc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--bootstrap", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True, help="P1 f2_s42.npz")
    ap.add_argument("--perm", type=Path, action="append", required=True, help="P1 f2_s42_perm*.npz")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    contract = json.loads(a.contract.read_text())
    U, names = sc.reported_functionals(contract)
    b0, b1 = contract["coverage"]["sigma"]["bootstrap_seeds"]
    sigma = np.sqrt(np.diag(sc.stat_covariance(U, a.bootstrap, b0, b1)))
    ref = U @ np.load(a.reference, allow_pickle=False)["xsec_flat"]
    res = {"schema": "s5c-gperm/1", "threshold": 0.05, "n_functionals": int(U.shape[0]),
           "sigma_over_value": {"min": float(np.min(sigma / np.abs(ref))), "median": float(np.median(sigma / np.abs(ref))),
                                "max": float(np.max(sigma / np.abs(ref)))}, "perms": {}}
    worst = 0.0
    for p in a.perm:
        f = U @ np.load(p, allow_pickle=False)["xsec_flat"]
        r = np.abs(f - ref) / sigma
        res["perms"][str(p)] = {"max_shift_over_sigma": float(r.max()), "argmax": names[int(r.argmax())]}
        worst = max(worst, float(r.max()))
    res["max_shift_over_sigma"] = worst
    res["verdict"] = "PASS" if worst <= 0.05 else "FAIL"
    a.out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("verdict", "max_shift_over_sigma", "sigma_over_value")}))
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
