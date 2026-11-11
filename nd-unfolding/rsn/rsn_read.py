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
# §3.3: at a principal deformed truth, the weighting is material if the noise-free closure's flag changes or its
# chi2 moves by more than this fraction of the equal-weight chi2
CHI2_FRACTION = 0.25
DEFORMED = ("gibuu", "q3")
# §3.5: the transfer diagnostic, read at the last iteration
TRANSFER_POINTS = ("data", "gibuu", "q3")
FLOOR_PRINTED = (0.133, 0.055, 0.252)   # FD-1B-INV-I0-REPORT.md:67, in %

CONCLUSIONS = {
    "P1": "the fake-data bias exceeds the reporting criteria at two truths (the GiBUU-family truth and the q3 tilt)",
    "P2": "the other fake-data truths meet the criteria only with the broader covariance terms, C_model among them",
    "P3": "the bias meets both criteria at the four held-out GENIE v3 records",
    "P4": "C_model is dominated by the GiBUU shift (0.890 of its trace)",
    "P5": "the reported per-cell relative uncertainty of the sixteen released cells",
    "P6": "the sixteen released central values, whose unmatched-event weights come from an unweighted regression",
    "P7": "the noise-free closures at the prior, at NuWro's shape, at the A7 GiBUU hybrid and at the q3 tilt",
    "P8": "the misses' step-1 weights transfer from the reconstructed events at fixed truth (limitation 8)",
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


def flagged(g: dict) -> bool:
    return bool(g["cells_abs_z_gt_2"] or g["p_lt_0.01"])


def deformed_class(rec: dict) -> str:
    w, u = rec["weighted"], rec["equal_weights"]
    if flagged(w) != flagged(u) or abs(w["chi2"] - u["chi2"]) > CHI2_FRACTION * u["chi2"]:
        return "material"
    return "immaterial"


def transfer_class(cell_bias, floor, sigma) -> tuple[str, list]:
    """T0 within twice the rounding floor in every cell, T1 within half the reported sigma, T2 otherwise (named);
    a cell without masked rows counts as failing T0 and T1."""
    t = np.array([np.inf if v is None else abs(v) for v in cell_bias])
    if np.all(t <= FLOOR_MULT * np.asarray(floor, float)):
        return "T0", []
    big = [f"R{c:02d}" for c in np.flatnonzero(t > HALF_SIGMA * np.asarray(sigma, float))]
    return ("T1", []) if not big else ("T2", big)


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
    cl, wd = cm["wr"]["closures"], rg["wr_directions"]
    floor_max = float(np.max(np.abs(cl["tune_v1"]["bias_weighted"])))
    p7 = {"floor": {"max_abs_weighted": floor_max,
                    "max_abs_equal_weights": float(np.max(np.abs(cl["tune_v1"]["bias_equal_weights"]))),
                    "breaks_the_prior_closure": floor_max > FLOOR_CLOSURE_MAX}}
    for t in ("nuwro",) + DEFORMED:
        bw, bu = cl[t]["bias_weighted"], cl[t]["bias_equal_weights"]
        p7[t] = {"rms_weighted": rms(bw), "rms_equal_weights": rms(bu),
                 "max_abs_change": float(np.max(np.abs(np.subtract(bw, bu)))), "rms_class": closure_class(bw, bu),
                 "chi2_weighted": wd[t]["weighted"]["chi2"], "chi2_equal_weights": wd[t]["equal_weights"]["chi2"],
                 "flag_weighted": flagged(wd[t]["weighted"]), "flag_equal_weights": flagged(wd[t]["equal_weights"]),
                 "change_along_equal_weight_bias": wd[t]["change_along_equal_weight_bias"],
                 "change_top_directions": wd[t]["change"]["top"]}
        if t in DEFORMED:
            p7[t]["class"] = deformed_class(wd[t])
    material = [t for t in DEFORMED if p7[t]["class"] == "material"]
    p8 = {}
    for pt in TRANSFER_POINTS:
        last = cm["transfer"][pt][-1]
        tc, tcells = transfer_class(last["cell_bias"], phi, sigma_rep)
        dec = [v for v in last["acceptance_decile_rel_bias"] if v is not None]
        p8[pt] = {"class": tc, "cells_beyond_half_sigma": tcells, "rel_bias": last["rel_bias"], "rel_rms": last["rel_rms"],
                  "cell_bias": last["cell_bias"], "lowest_vs_highest_acceptance": [dec[0], dec[-1]] if dec else None}
    out["arms"]["WR"] = {
        "P6": {"delta": delta.tolist(), "delta_over_floor": (np.abs(delta) / phi).tolist(),
               "delta_over_sigma": (np.abs(delta) / sigma_rep).tolist(), "class": wc, "cells_at_half_sigma": cells,
               "chi2": wd["data"]["grade"]["chi2"], "top_directions": wd["data"]["directions"]["top"]},
        "P7": p7,
        "verdict": ("the equal-weight regression is immaterial at the A7 GiBUU hybrid and the q3 tilt, and the data "
                    "move " + ("within the rounding floor" if wc == "W0" else "below half the reported sigma"))
        if not material and wc in ("W0", "W1") else
        ("the equal-weight regression is material: " + ", ".join(
            ([f"at {t}" for t in material]) + ([f"on data ({wc}: {cells})"] if wc == "W2" else [])))}
    out["arms"]["TR"] = {"P8": p8}
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
    lines.append(f"WR: {w['verdict']}. P6 {w['P6']['class']}"
                 + (f" at {w['P6']['cells_at_half_sigma']}" if w['P6']['cells_at_half_sigma'] else "")
                 + f" (max |delta|/floor {max(w['P6']['delta_over_floor']):.2f}, max |delta|/sigma "
                 f"{max(w['P6']['delta_over_sigma']):.3f}); P7 "
                 + "; ".join(f"{t} {w['P7'][t]['class']} (chi2 {w['P7'][t]['chi2_equal_weights']:.1f} -> "
                             f"{w['P7'][t]['chi2_weighted']:.1f})" for t in DEFORMED)
                 + f"; NuWro {w['P7']['nuwro']['rms_class']}; floor "
                 + ("BROKEN" if w["P7"]["floor"]["breaks_the_prior_closure"] else "kept"))
    lines.append("TR: P8 " + "; ".join(f"{pt} {v['class']}" + (f" at {v['cells_beyond_half_sigma']}" if v['cells_beyond_half_sigma'] else "")
                                       + f" (rel bias {v['rel_bias']:+.4f})" for pt, v in out["arms"]["TR"]["P8"].items()))
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
