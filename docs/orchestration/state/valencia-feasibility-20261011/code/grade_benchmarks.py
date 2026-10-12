#!/usr/bin/env python3
"""Apply the frozen PLAN.md tolerances to the committed result files (B0-B5)."""
import json
import math
from pathlib import Path

R = Path(__file__).resolve().parent.parent / "results"
VUD2 = 0.97373 ** 2


def load(p):
    return json.loads((R / p).read_text())


def tot(p):
    return load(p)[0]["total_per_nucleon_cm2"]


out = {}
n8, n16 = tot("integrator-C12-nu-1GeV-n8.json"), tot("integrator-C12-nu-1GeV-n16.json")
b8, b16 = tot("integrator-C12-nubar-1GeV-n8.json"), tot("integrator-C12-nubar-1GeV-n16.json")
conv = max(abs(n8 / n16 - 1), abs(b8 / b16 - 1))
out["B0"] = {"max_rel_diff_n8_vs_n16": conv, "tolerance": 0.002, "grade": "PASS" if conv <= 0.002 else "FAIL"}

for bid, val, pub, (tp, tq) in (("B1", n8, 1.38, (0.07, 0.15)), ("B2", b8, 0.31, (0.12, 0.25))):
    per_nucleus = 12 * val / 1e-38
    dev = per_nucleus / pub - 1
    superseded = "PASS" if abs(dev) <= tp else ("QUALIFIED" if abs(dev) <= tq else "FAIL")
    alt = per_nucleus * VUD2 / pub - 1
    # REPAIR.md section 1, frozen status rule: the table's W12 encoding (W12 = Im W^{12}) is
    # generator-corroborated, not author-confirmed, so no PASS/QUALIFIED word is attached.
    out[bid] = {"integrator_per_nucleus_1e38": per_nucleus, "published_1e38": pub, "rel_dev": dev,
                "frozen_tolerances_pass_qualified": [tp, tq],
                "grade": "UNVALIDATED (table W12 encoding not author-confirmed)",
                "grade_at_d75987e1_superseded": superseded,
                "diagnostic_rel_dev_with_extra_Vud2": alt}

r1 = load("R1/analysis.json")
mc, err = r1["sigma_per_nucleon_cm2"], r1["sigma_mc_error_cm2"]
dev = mc / n8 - 1
tol = max(3 * err / n8, 0.01)
out["B3"] = {"nuwro_per_nucleon_cm2": mc, "mc_error_cm2": err, "integrator_per_nucleon_cm2": n8,
             "rel_dev": dev, "pulls": dev * n8 / err, "tolerance": tol,
             "grade": "PASS" if abs(dev) <= tol else "FAIL",
             "diagnostic_rel_dev_vs_integrator_times_nuwro_formula_factor": mc / (n8 * (1 - 0.003052)) - 1}

ch = load("integrator-C12-nu-1GeV-n8.json")[0]["per_nucleon_cm2"]
tot_i = sum(ch.values())
expect = {"pp": ch["pp"] / tot_i, "np+pn": (ch["np"] + ch["pn"]) / tot_i, "3p3h": ch["3p3h"] / tot_i}
b4 = {}
for k, (f, e) in r1["channel_fraction"].items():
    b4[k] = {"nuwro": f, "err": e, "integrator": expect[k], "pull": (f - expect[k]) / e}
out["B4"] = {"channels": b4, "grade": "PASS" if all(abs(v["pull"]) <= 3 for v in b4.values()) else "FAIL"}

r2 = load("R2/analysis.json")
b5 = {run: {"max_abs_dp_MeV": a["conservation"]["max_abs_dp_MeV"],
            "n_events_dp_over_1keV": a["conservation"]["n_events_dp_over_1keV"],
            "n_positive": a["n_positive"]} for run, a in (("R1", r1), ("R2", r2))}
out["B5"] = {"runs": b5, "tolerance_MeV": 1e-3,
             "grade": "PASS" if all(v["n_events_dp_over_1keV"] == 0 for v in b5.values()) else "FAIL"}
(R / "benchmarks.json").write_text(json.dumps(out, indent=1) + "\n")
for k, v in out.items():
    print(k, v["grade"], {kk: (round(vv, 5) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk not in ("grade", "channels", "runs")})
