#!/usr/bin/env python3
"""The s5n pre-expansion feasibility receipt: Tier-S sample sizes and assurance recomputed at the
development coverage estimates, and the priced remaining work (contract ``stage_2_preconditions``).

Assurance is the s5c construction (``s5c_samplesize.coverage_assurance``: exact Clopper-Pearson,
Bonferroni over m = F x G, lower bound 1 - m(1 - q) valid under any dependence), evaluated here with each
grid point's MINIMUM per-functional development coverage as the design value -- the gate is a minimum over
functionals, so the weakest functional sets the pass probability. The normal-model coverage (from each
functional's pull mean and spread) is used beside the empirical one because 60 experiments resolve a
per-functional coverage only to about +-0.06.

MEASURES: the probability that the frozen Tier-S gate could pass at the stated design values, and the cost
of the complete remaining work. CANNOT AUTHORIZE: a scientific PASS or FAIL (feasibility is not a verdict).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import s5c_samplesize as ss

N_GRID = (4000, 8000, 21152, 40000)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--dev-receipt", type=Path, required=True)
    ap.add_argument("--cost-per-experiment", type=float, required=True, help="measured CPU node-h per unfold")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    dev = json.loads(a.dev_receipt.read_text())
    F, G = len(dev["functional_names"]), len(dev["grid"])
    m = F * G
    out = {"schema": "s5n-feasibility/1", "functionals": F, "grid_points": G, "m": m, "points": {}}
    for tag, s in dev["grid"].items():
        rec = {}
        for label, thr in (("68", 0.66), ("95", 0.94)):
            pf = s["per_functional"]
            emp = min(pf[f"cov{label}"])
            nor = min(pf[f"normal_cov{label}"])
            rec[label] = {
                "min_empirical": emp, "min_normal_model": nor,
                "assurance_at_min_normal_model": {str(n): ss.coverage_assurance(n, max(nor, 1e-9), thr, m)["assurance_lower_bound"] for n in N_GRID},
            }
        out["points"][tag] = rec
    out["exactly_nominal"] = {
        "68": {str(n): ss.coverage_assurance(n, 0.6827, 0.66, m)["assurance_lower_bound"] for n in N_GRID},
        "95": {str(n): ss.coverage_assurance(n, 0.9545, 0.94, m)["assurance_lower_bound"] for n in N_GRID},
        "n_for_80pct_assurance_68": ss.smallest_n(lambda n: ss.coverage_assurance(n, 0.6827, 0.66, m), 0.8),
        "n_for_80pct_assurance_95": ss.smallest_n(lambda n: ss.coverage_assurance(n, 0.9545, 0.94, m), 0.8),
    }
    c = a.cost_per_experiment
    out["cost_cpu_node_h"] = {
        "per_experiment_measured": c,
        "tier_s_at_4000_per_point": 3 * 4000 * c,
        "tier_s_exactly_nominal_80pct": None,
        "sigma_bootstraps_data_and_pseudo_400": 400 * c,
        "systematic_construction_driver_arms_about_200_unfolds": 200 * 0.02,
        "tier_t_two_nuisance_points_8000": 8000 * c,
    }
    n68 = out["exactly_nominal"]["n_for_80pct_assurance_68"]
    if n68:
        out["cost_cpu_node_h"]["tier_s_exactly_nominal_80pct"] = 3 * n68["n"] * c
    a.out.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
