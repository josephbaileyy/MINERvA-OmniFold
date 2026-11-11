#!/usr/bin/env python3
"""RSN readings (RSN-DECLARATION.md §3): the outcome tables, applied to the prep, C_model and regrade records.
Numpy only; runs anywhere the records are.

    rsn_read.py --prep <OUT>/prep/prep.json --cmodel <OUT>/cmodel/rsn_cmodel.json --regrade <OUT>/regrade.json \
                --out <OUT>/rsn_readout.json

Every class and threshold below is the declaration's, fixed before any run. The readings are sensitivities of the
stated construction. None is a calibrated uncertainty, and no C^V, shift or delta is added to any reported covariance.

MEASURES: classification of recorded numbers. CANNOT AUTHORIZE: a paper sentence, a change to C_model, or a change to a
grade.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
_ROOT = _ND.parent
FD = _ROOT / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
I0 = FD / "receipts-1b/inv/i0/i0.json"
F1_READOUT = FD / "with-cpl/readout/fd_f1_readout.json"
CMODEL_JSON = _ND / "pv-ladder/readouts/cmodel_5d.json"
SIGMA_KEY = "relative_sigma_plus_C_resp + C_PL5D"

# §3.1: C^V against C_model, per cell q = sqrt(diag C^V) / sqrt(diag C_model)
Q_SMALLER, Q_LARGER, Q_CELL = 0.8, 1.25, (0.5, 2.0)
# §3.3: WR's data shift against the rounding floor and the reported sigma, and its closures
FLOOR_MULT, HALF_SIGMA = 2.0, 0.5
RMS_LOWER, RMS_HIGHER = 0.9, 1.1
FLOOR_CLOSURE_MAX = 1e-4
FLOOR_PRINTED = (0.133, 0.055, 0.252)   # FD-1B-INV-I0-REPORT.md:67, in %

CONCLUSIONS = {
    "P1": "the fake-data bias exceeds the reporting criteria at two truths (the GiBUU-family truth and the q3 tilt)",
    "P2": "the other fake-data truths meet the criteria only with the broader covariance terms, C_model among them",
    "P3": "the bias meets both criteria at the four held-out GENIE v3 records",
    "P4": "C_model is dominated by the GiBUU shift (0.890 of its trace)",
    "P5": "the reported per-cell relative uncertainty of the sixteen released cells",
    "P6": "the sixteen released central values, whose unmatched-event weights come from an unweighted regression",
    "P7": "the noise-free closures at the prior and at NuWro's shape",
}


def sigma_class(q: np.ndarray) -> str:
    q = np.asarray(q, float)
    med = float(np.median(q))
    if med < Q_SMALLER:
        return "C_model smaller"
    if med > Q_LARGER:
        return "C_model larger"
    if np.all((q >= Q_CELL[0]) & (q <= Q_CELL[1])):
        return "C_model similar"
    return "C_model reshaped"


def listed_class(nominal: list, arm: list) -> str:
    a, b = set(nominal), set(arm)
    if a == b:
        return "unchanged"
    if b < a:
        return "fewer flagged"
    if b > a:
        return "more flagged"
    return "different flagged"


def held_out_met(by_group: dict) -> bool:
    g = by_group["held-out"]
    return g["truths"] == 4 and g["cells_abs_z_gt_2"] == 0 and g["truths_p_lt_0.01"] == 0


def wr_class(delta, floor, sigma) -> tuple[str, list]:
    d, fl, sg = (np.abs(np.asarray(x, float)) for x in (delta, floor, sigma))
    if np.max(d / fl) <= FLOOR_MULT:
        return "W0", []
    big = [f"R{c:02d}" for c in np.flatnonzero(d / sg > HALF_SIGMA)]
    return ("W1", []) if not big else ("W2", big)


def rms(x) -> float:
    return float(np.sqrt(np.mean(np.square(np.asarray(x, float)))))


def closure_class(b_w, b_0) -> str:
    ratio = rms(b_w) / rms(b_0)
    if ratio < RMS_LOWER:
        return "lower"
    if ratio > RMS_HIGHER:
        return "higher"
    return "comparable"


def rounding_floor(i0: dict, cmodel: dict) -> np.ndarray:
    """sigma_J / f per cell: i0.json's data jitter spread over P5's integrals (cmodel_5d.json x), reproduced at the
    printed precision (RS1-DECLARATION.md R0's control)."""
    if i0["cells"] != [f"R{c:02d}" for c in range(16)]:
        raise SystemExit("[FAIL] i0.json's cells are not R00-R15")
    phi = np.asarray(i0["sigma_J_data"], float) / np.asarray(cmodel["x"], float)
    got = tuple(round(100 * v, 3) for v in (np.median(phi), phi.min(), phi.max()))
    if got != FLOOR_PRINTED:
        raise SystemExit(f"[FAIL] the rounding floor {got} % does not reproduce the printed {FLOOR_PRINTED}")
    return phi


def read(prep: dict, cm: dict, rg: dict, i0: dict, cmodel: dict, f1: dict) -> dict:
    sigma_rep = np.asarray(f1[SIGMA_KEY]["C_total"], float)
    nom = rg["arms"]["nominal"]
    if not np.allclose(nom["reported_relative_sigma"], sigma_rep, rtol=1e-12, atol=0):
        raise SystemExit("[FAIL] the regrade's nominal reported sigma is not the committed F1 readout's")
    if not np.allclose(cm["arms"]["nominal"]["sqrt_diag"], cmodel["sqrt_diag"], rtol=1e-12, atol=0):
        raise SystemExit("[FAIL] the nominal C_model is not cmodel_5d.json's")
    out = {"schema": "rsn-readout/1", "conclusions": CONCLUSIONS, "arms": {},
           "label": "sensitivities of the stated construction; not calibrated uncertainties; nothing here enters a "
                    "reported covariance"}
    sd0 = np.asarray(cm["arms"]["nominal"]["sqrt_diag"], float)
    for arm in ("G6", "SM"):
        if arm not in cm["arms"]:
            out["arms"][arm] = {"status": "not run: " + prep["sm"]["status"]}
            continue
        c, g = cm["arms"][arm], rg["arms"][arm]
        q = np.asarray(c["sqrt_diag"], float) / sd0
        lc = listed_class(nom["listed"], g["listed"])
        ho = held_out_met(g["by_group"])
        s = np.asarray(g["reported_relative_sigma"], float) / sigma_rep
        out["arms"][arm] = {
            "P4": {"gibuu_trace_share": c["trace_share_by_vertex"]["gibuu"],
                   "gibuu_trace_share_nominal": cm["arms"]["nominal"]["trace_share_by_vertex"]["gibuu"],
                   "trace_ratio": c["trace"] / cm["arms"]["nominal"]["trace"],
                   "q": q.tolist(), "q_median": float(np.median(q)), "class": sigma_class(q)},
            "P5": {"reported_sigma_ratio": s.tolist(), "median": float(np.median(s)), "min": float(s.min()),
                   "max": float(s.max())},
            "P1": {"listed_nominal": nom["listed"], "listed": g["listed"], "class": lc},
            "P2": {"by_group_nominal": nom["by_group"], "by_group": g["by_group"],
                   "chi2": {r["name"]: [a["grade"]["chi2"], r["grade"]["chi2"]]
                            for a, r in zip(nom["records"], g["records"])}},
            "P3": {"both_criteria_met_at_the_four_held_out_records": ho},
            "verdict": ("the fake-data conclusions survive " + arm) if lc == "unchanged" and ho
            else ("a fake-data conclusion changes under " + arm)}
        if arm == "SM":
            out["arms"][arm]["radius"] = prep["sm"]["radius"]
    phi = rounding_floor(i0, cmodel)
    delta = np.asarray(cm["wr"]["delta"], float)
    wc, cells = wr_class(delta, phi, sigma_rep)
    cl = cm["wr"]["closures"]
    floor_max = float(np.max(np.abs(cl["tune_v1"]["bias_weighted"])))
    out["arms"]["WR"] = {
        "P6": {"delta": delta.tolist(), "delta_over_floor": (np.abs(delta) / phi).tolist(),
               "delta_over_sigma": (np.abs(delta) / sigma_rep).tolist(), "class": wc, "cells_at_half_sigma": cells},
        "P7": {"nuwro": {"rms_weighted": rms(cl["nuwro"]["bias_weighted"]), "rms_frozen": rms(cl["nuwro"]["bias_frozen"]),
                         "max_abs_change": float(np.max(np.abs(np.subtract(cl["nuwro"]["bias_weighted"],
                                                                           cl["nuwro"]["bias_frozen"])))),
                         "class": closure_class(cl["nuwro"]["bias_weighted"], cl["nuwro"]["bias_frozen"])},
               "floor": {"max_abs_weighted": floor_max,
                         "max_abs_frozen": float(np.max(np.abs(cl["tune_v1"]["bias_frozen"]))),
                         "breaks_the_prior_closure": floor_max > FLOOR_CLOSURE_MAX}}}
    return out


def text(out: dict) -> str:
    lines = [out["label"]]
    for arm in ("G6", "SM"):
        a = out["arms"][arm]
        if "status" in a:
            lines.append(f"{arm}: {a['status']}")
            continue
        lines.append(f"{arm}: {a['verdict']}. P1 {a['P1']['class']} ({a['P1']['listed']} vs {a['P1']['listed_nominal']}); "
                     f"P3 {'met' if a['P3']['both_criteria_met_at_the_four_held_out_records'] else 'NOT met'}; "
                     f"P4 {a['P4']['class']} (median q {a['P4']['q_median']:.3f}, GiBUU share "
                     f"{a['P4']['gibuu_trace_share']:.3f} vs {a['P4']['gibuu_trace_share_nominal']:.3f}); "
                     f"P5 reported sigma x{a['P5']['median']:.3f} median [{a['P5']['min']:.3f}, {a['P5']['max']:.3f}]")
    w = out["arms"]["WR"]
    lines.append(f"WR: P6 {w['P6']['class']}" + (f" at {w['P6']['cells_at_half_sigma']}" if w['P6']['cells_at_half_sigma'] else "")
                 + f" (max |delta|/floor {max(w['P6']['delta_over_floor']):.2f}, max |delta|/sigma "
                 f"{max(w['P6']['delta_over_sigma']):.3f}); P7 NuWro closure {w['P7']['nuwro']['class']}, floor "
                 + ("BROKEN" if w["P7"]["floor"]["breaks_the_prior_closure"] else "kept"))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prep", type=Path, required=True)
    ap.add_argument("--cmodel", type=Path, required=True)
    ap.add_argument("--regrade", type=Path, required=True)
    ap.add_argument("--i0", type=Path, default=I0)
    ap.add_argument("--cmodel-json", type=Path, default=CMODEL_JSON)
    ap.add_argument("--f1-readout", type=Path, default=F1_READOUT)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    load = lambda p: json.loads(Path(p).read_text())  # noqa: E731
    out = read(load(a.prep), load(a.cmodel), load(a.regrade), load(a.i0), load(a.cmodel_json), load(a.f1_readout))
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(text(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
