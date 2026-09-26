#!/usr/bin/env python3
"""s5p Stage 2 exit: the complete remaining-work forecast as a function of the estimator configuration.

Cost model (billed node-hours): one unfold step uses 32 threads, a CPU node runs 8 steps and a GPU node 4, so a
step-hour costs 1/8 CPU node-h or 1/4 GPU node-h; a packing factor covers idle tails. Unfold times are linear
in the iteration count, t = a + b K seconds, with (a, b) MEASURED from the products' own ``seconds_unfold``
(pseudo experiments on half the MC, real-data unfolds on the full MC) and a measured capacity factor on b.

Work items (counts from the forecast inputs; measurement and inference are separated):

* Stage 3: noise-free asimov bias at each development vertex, construction pseudo experiments per development
  truth (development coverage), the prior-variation data unfolds, the leave-one-out envelope calibration;
* Stage 4: the data bootstrap, every systematic universe, the lateral endpoints and the prior variations on
  data, the numerical jitters, the input dumps (measured pilot costs);
* Stage 5: fresh validation pseudo experiments at every declared point, plus the per-experiment bootstraps of
  the statistical-width source;
* verification: a fraction for independent re-computation; repair: the 20% reserve (kept separately);
* Stage 7 (inference, separately): per null the calibration ensemble and the size-validation ensemble, the
  power ensembles, the null-generator reweights (negligible).

MEASURES: forecast costs for declared configurations and sample sizes. CANNOT AUTHORIZE: a configuration,
an admission or a sample size by itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def unfold_h(kind: str, K: int, cap: float, m: dict) -> float:
    a, b = m[kind]
    return (a + b * K * (cap if cap else 1.0)) / 3600.0


def forecast(inp: dict, K: int, cap: float = 0.0) -> dict:
    m, n, pk = inp["measured_seconds"], inp["counts"], inp["packing"]
    step_node_h = 1.0 / 8.0
    p, d, asim = unfold_h("pseudo", K, cap, m), unfold_h("data", K, cap, m), unfold_h("asimov", K, cap, m)
    s3 = (n["stage3_asimov_vertices"] * asim + n["stage3_construction_pseudo"] * p + n["stage3_prior_data"] * d) * step_node_h * pk
    s4 = ((n["bootstrap"] + n["universes"] + n["laterals"] + n["priors"] + n["jitters"] + 1) * d) * step_node_h * pk + n["dump_node_h"]
    s5 = (n["validation_pseudo"] + n["validation_sigma_pseudo"]) * p * step_node_h * pk
    meas = s3 + s4 + s5
    verification = inp["verification_fraction"] * meas
    s7 = (n["nulls"] * (n["null_calibration"] + n["null_validation"]) + n["power_pseudo"]) * p * step_node_h * pk
    return {"K": K, "capacity_factor": cap or 1.0, "pseudo_h": p, "data_h": d, "stage3": s3, "stage4": s4, "stage5": s5,
            "measurement": meas, "verification": verification, "inference": s7,
            "measurement_plus_verification": meas + verification, "all": meas + verification + s7}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    inp = json.loads(a.inputs.read_text())
    rows = [forecast(inp, K, cap) for K, cap in inp["configurations"]]
    avail = inp["available_cpu_equivalent_node_h"]
    for r in rows:
        r["fits_measurement"] = r["measurement_plus_verification"] <= avail["measurement"]
        r["fits_all"] = r["all"] <= avail["measurement"] + avail["inference"]
    out = {"schema": "s5p-forecast/1", "inputs": inp, "rows": rows}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    for r in rows:
        print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
