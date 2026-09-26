#!/usr/bin/env python3
"""s5e costed next validation design, with sample-size and assurance calculations from measured inputs.

Three separately costed components, none run by this campaign:

A. Statistical-scope coverage validation at nominal truth (and, for a total-uncertainty claim, at
   nuisance-shifted points), restricted to the functionals a candidate could qualify for. Assurance is
   the s5c construction (``s5c_samplesize.coverage_assurance``: exact Clopper-Pearson lower bounds,
   Bonferroni over m = F x G). The design coverage of each functional is its normal-model coverage from
   the measured pull mean and spread at nominal; the gate is a minimum over functionals, so the weakest
   sets the pass probability. Also at exactly nominal coverage, the best case.
B. The model-dependence (unfolding-model) component: experiments per generator-anchored truth needed to
   measure each cell's departure residual to a precision delta = (adopted total sigma of the cell) / 3,
   from the measured per-experiment spread of the relative residual.
C. The numerical-reproducibility component: data unfolds under rounding-scale perturbations needed to
   estimate its per-functional spread to 10% (n = 1 + 1/(2 x 0.1^2)), plus a 200-replica data bootstrap.

MEASURES: the probability that a frozen gate could pass at measured design values, and costs.
CANNOT AUTHORIZE: a verdict or any of the runs (each is a separate decision).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import s5c_samplesize as ss

N_GRID = (500, 1000, 2000, 4000, 8000, 16000)


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_cov(mu, sd, z):
    return phi((z - mu) / sd) - phi((-z - mu) / sd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--assessment", type=Path, required=True, help="s5e candidate assessment receipt")
    ap.add_argument("--adopted-sigma", type=Path, required=True)
    ap.add_argument("--cost-pseudo", type=float, required=True, help="measured CPU node-h per pseudo-experiment")
    ap.add_argument("--cost-data", type=float, required=True, help="measured CPU node-h per data unfold")
    ap.add_argument("--generator-truths", type=int, default=6)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    rec = json.loads(a.assessment.read_text())
    names = rec["functional_names"]
    nom = rec["points"]["nominal"]["per_functional"]
    scope = rec["A4"]["cells_model_dependence_within_adopted_sigma"]
    groups = {"A4_scope_EW_cells": [names.index(c) for c in scope], "all_42_EW_cells": list(range(42)),
              "all_153_functionals": list(range(len(names)))}
    out = {"schema": "s5e-next-design/1", "inputs": {"assessment": str(a.assessment), "cost_pseudo": a.cost_pseudo,
                                                     "cost_data": a.cost_data, "n_nominal_experiments": rec["points"]["nominal"]["n"]},
           "A_statistical_scope_coverage": {}, "B_model_dependence": {}, "C_numerical_reproducibility": {}}
    for gname, idx in groups.items():
        if not idx:
            out["A_statistical_scope_coverage"][gname] = {"F": 0, "note": "empty scope: nothing to validate"}
            continue
        mu = np.array(nom["mean_pull"])[idx]
        sd = np.array(nom["pull_sd"])[idx]
        g = {"F": len(idx)}
        for label, z, thr, exact in (("68", 1.0, 0.66, 0.6827), ("95", 1.96, 0.94, 0.9545)):
            cov = np.array([normal_cov(m, s, z) for m, s in zip(mu, sd)])
            design = float(cov.min())
            for G, tag in ((1, "nominal_only"), (3, "nominal_plus_two_nuisance_points")):
                m = len(idx) * G
                row = {"m": m, "design_min_normal_model_coverage": design,
                       "assurance_at_design": {str(n): ss.coverage_assurance(n, max(design, 1e-9), thr, m)["assurance_lower_bound"] for n in N_GRID},
                       "assurance_at_exactly_nominal": {str(n): ss.coverage_assurance(n, exact, thr, m)["assurance_lower_bound"] for n in N_GRID}}
                best = ss.smallest_n(lambda n: ss.coverage_assurance(n, exact, thr, m), 0.8)
                dsn = ss.smallest_n(lambda n: ss.coverage_assurance(n, max(design, 1e-9), thr, m), 0.8) if design > thr else None
                row["n_for_80pct_assurance_exactly_nominal"] = best["n"] if best else None
                row["n_for_80pct_assurance_at_design"] = dsn["n"] if dsn else None
                row["cost_cpu_node_h_exactly_nominal"] = G * best["n"] * a.cost_pseudo if best else None
                row["cost_cpu_node_h_at_design"] = G * dsn["n"] * a.cost_pseudo if dsn else None
                g[f"{label}_{tag}"] = row
        out["A_statistical_scope_coverage"][gname] = g
    adopted = np.array([c["sigma_adopted_pct"] for c in json.loads(a.adopted_sigma.read_text())["cells"]]) / 100
    delta = adopted / 3.0
    per = {}
    for key in rec["points"]:
        if key == "nominal":
            continue
        sdr = np.array(rec["points"][key]["per_functional"]["rel_sd"])[:42]
        n_need = np.ceil((sdr / delta) ** 2)
        per[key] = {"median_n": float(np.median(n_need)), "max_n": float(n_need.max()),
                    "argmax": names[int(n_need.argmax())], "rel_sd_median_pct": 100 * float(np.median(sdr))}
    nmax = max(v["max_n"] for v in per.values())
    out["B_model_dependence"] = {"precision_target": "adopted total sigma of each EW cell / 3", "per_deformation": per,
                                 "n_per_truth": nmax, "generator_truths": a.generator_truths,
                                 "cost_cpu_node_h": a.generator_truths * nmax * a.cost_pseudo}
    n_c = int(math.ceil(1 + 1 / (2 * 0.1 ** 2)))
    out["C_numerical_reproducibility"] = {"rounding_probe_unfolds": n_c, "data_bootstrap_replicas": 200,
                                          "cost_cpu_node_h": (n_c + 200) * a.cost_data}
    a.out.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "A_statistical_scope_coverage"}, indent=1, default=str)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
