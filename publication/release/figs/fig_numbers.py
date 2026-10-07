#!/usr/bin/env python3
"""Recompute every number the article quotes from its Figs. 1-3 from the released arrays (numpy only), and check
each against the value printed in the article / values.tex.

Tolerance: the printed value's own precision -- |computed - printed| <= half a unit in its last printed digit.
A value outside it is reported as a DISCREPANCY, never adjusted. Exit 0 only if every check passes.

  python3 fig_numbers.py --npz fig_arrays.npz [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def half_ulp(printed: str) -> float:
    s = printed.lower().split("e")[0]
    dec = len(s.split(".")[1]) if "." in s else 0
    exp = int(printed.lower().split("e")[1]) if "e" in printed.lower() else 0
    return 0.5 * 10.0 ** (exp - dec)


def compute(z) -> dict:
    v = {}
    m = z["mask_reported"].astype(bool)
    ours, paper, cov = z["ours_v"], z["paper_v"], z["cov_total"]
    # Fig. 1: totals are INTEGRALS (content x bin area), see agreement_windows_receipt.bin_areas
    v["sigTwoD"] = float((ours * z["area_ours"]).sum())
    v["sigTwoDpaper"] = float((paper * z["area_paper"]).sum())
    v["ratioTot"] = float((ours * z["area_ours"])[m].sum() / (paper * z["area_paper"])[m].sum())
    use = m & (paper > 0)
    r = ours[use] / paper[use]
    v["binsTen"] = 100.0 * float((np.abs(r - 1.0) <= 0.10).sum()) / int(use.sum())
    v["n_reported"] = int(m.sum())
    d = (ours - paper)
    pull = d[m] / np.sqrt(np.diag(cov)[m])
    v["pullMean"], v["pullRMS"] = float(pull.mean()), float(pull.std())
    C = cov[np.ix_(m, m)]
    v["chiPaper"] = float(d[m] @ np.linalg.pinv(C) @ d[m]) / int(m.sum())
    for tag, dd in (("chi2ndf_data_vs_tune", paper - z["tune_v1_v"]), ("chi2ndf_ours_vs_tune", ours - z["tune_v1_v"])):
        v[tag] = float(dd[m] @ np.linalg.pinv(C) @ dd[m]) / int(m.sum())
    v["uqPaper_median_rel_pct"] = 100.0 * float(np.median(np.sqrt(np.diag(cov)[m]) / paper[m]))
    # Figs. 2-3 on the 7 x 6 (Eavail, W) grid
    ee, we = z["eavail_edges"], z["W_edges"]
    area = np.outer(np.diff(ee), np.diff(we))
    data = z["hData2D"] * area
    corner = np.outer(ee[:-1] >= 0.8, we[:-1] >= 1.8)
    jW = int(np.where(np.isclose(we[:-1], 2.2))[0][0])
    v["data_total"] = float(data.sum())
    for g in ("GENIE-CV", "GENIE+MEC", "NuWro", "GiBUU"):
        gs = z[f"gen_{g}"] * area
        v[f"ratio_total_{g}"] = float(data.sum() / gs.sum())
        v[f"ratio_corner_{g}"] = float(data[corner].sum() / gs[corner].sum())
        v[f"ratio_W2p2_{g}"] = float(data[:, jW].sum() / gs[:, jW].sum())
    gn = ("GENIE-CV", "GENIE+MEC", "NuWro")
    v["corner_over_total_max_dev_pct"] = 100.0 * max(abs(v[f"ratio_corner_{g}"] / v[f"ratio_total_{g}"] - 1) for g in gn)
    exc = z["hExcess2D"]
    pos = exc[exc > 0].sum()
    hi = ee[:-1] >= 0.8
    v["note_share_hiEavail_pct"] = 100.0 * float(exc[hi][exc[hi] > 0].sum() / pos)
    eh = exc[hi][:, we[:-1] >= 1.8]
    v["note_share_hiW_of_hiEavail_pct"] = 100.0 * float(eh[eh > 0].sum() / exc[hi][exc[hi] > 0].sum())
    ratio = z["hData2D"] / z["hGenCV2D"]
    hihi = ratio[ee[:-1] >= 0.8][:, we[:-1] >= 1.8]
    v["ratio_hihi_min_pct"], v["ratio_hihi_max_pct"] = 100 * (hihi.min() - 1), 100 * (hihi.max() - 1)
    loww = ratio[:, we[:-1] < 1.1]
    v["ratio_lowW_min_pct"], v["ratio_lowW_max_pct"] = 100 * (loww.min() - 1), 100 * (loww.max() - 1)
    v["share_catch_cell_pct"] = 100.0 * float(max(exc[-1, -1], 0.0) / pos)
    v["fig2_excess_equals_data_minus_comparator_maxabs"] = float(np.max(np.abs(exc - (z["hData2D"] - z["hGenCV2D"]) * area)))
    return v


# (quantity, printed value as in the article / values.tex, source of the printed value)
CHECKS = [
    ("sigTwoD", "3.073e-38", r"values.tex \sigTwoD"),
    ("sigTwoDpaper", "3.039e-38", r"values.tex \sigTwoDpaper"),
    ("ratioTot", "1.011", r"values.tex \ratioTot"),
    ("binsTen", "94.1", r"values.tex \binsTen"),
    ("pullMean", "0.089", r"values.tex \pullMean"),
    ("pullRMS", "0.598", r"values.tex \pullRMS"),
    ("chiPaper", "3.66", r"values.tex \chiPaper"),
    ("uqPaper_median_rel_pct", "6.85", r"values.tex \uqPaper"),
    ("chi2ndf_data_vs_tune", "33.04", "packet/claims (receipt_model_chi2_2d.json 33.039)"),
    ("chi2ndf_ours_vs_tune", "26.49", "receipt_model_chi2_2d.json 26.491"),
    ("data_total", "3.0699e-38", "VL157 data total"),
]
RANGES = [  # article ranges: every member must round into [lo, hi] at the printed precision
    (["ratio_total_GENIE-CV", "ratio_total_GENIE+MEC", "ratio_total_NuWro", "ratio_total_GiBUU"], "1.07", "1.39",
     "paper_body.tex: integrated data-to-prediction ratios 1.07--1.39"),
    (["ratio_W2p2_GENIE-CV", "ratio_W2p2_GENIE+MEC", "ratio_W2p2_NuWro"], "1.11", "1.13",
     "paper_body.tex: 2.2<=W<3.0 ratios 1.11--1.13 (GENIE, NuWro)"),
    (["ratio_total_GENIE-CV", "ratio_total_GENIE+MEC", "ratio_total_NuWro"], "1.07", "1.15",
     "paper_body.tex: 1.07--1.15 integrated (GENIE, NuWro)"),
    (["ratio_corner_GENIE-CV", "ratio_corner_GENIE+MEC", "ratio_corner_NuWro"], "1.14", "1.16",
     "paper_body.tex: corner 1.14--1.16 (GENIE, NuWro)"),
]
SINGLES = [("ratio_corner_GiBUU", "1.61", "paper_body.tex GiBUU corner"),
           ("ratio_total_GiBUU", "1.39", "paper_body.tex GiBUU overall")]
BOUNDS = [("corner_over_total_max_dev_pct", 7.0, "paper_body.tex: within 7% of their integrated ratios")]
# Fig. 2 statements (paper_body.tex, central-value results): two ranges at printed precision, and verbal shares
# checked against explicit intervals stated here.
RANGES += [(("ratio_hihi_min_pct", "ratio_hihi_max_pct"), "12", "30",
            "paper_body.tex: ratio 12--30% in the high-Eavail, high-W cells"),
           (("ratio_lowW_min_pct", "ratio_lowW_max_pct"), "23", "31",
            "paper_body.tex: ratio 23--31% at W<1.1 GeV for every Eavail")]
VERBAL = [("note_share_hiEavail_pct", 62.0, 71.0, "paper_body.tex: 'two thirds' of the positive cell-integrated difference at Eavail>=0.8"),
          ("note_share_hiW_of_hiEavail_pct", 50.0, 100.0, "paper_body.tex: 'most of that' at W>=1.8"),
          ("share_catch_cell_pct", 17.0, 23.0, "paper_body.tex: 'a fifth' in the single widest catch cell")]
NOT_COVERED = ["paper_body.tex 'higher energies carry 14--15% of this region ... and 7% of the total' and "
               "'1.37 against 1.29': from VL161 (E_nu >= 20 GeV shares), not recomputable from these arrays"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--values", type=Path, default=None,
                    help="values.tex to take macro-sourced printed values from (the authority); the built-in "
                         "table is then only a cross-check and any drift is reported")
    a = ap.parse_args(argv)
    v = compute(np.load(a.npz, allow_pickle=False))
    rows, ok = [], True
    checks = list(CHECKS)
    if a.values:
        import re
        macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", a.values.read_text()))
        resolved = []
        for k, printed, src in checks:
            m = re.match(r"values\.tex \\(\w+)$", src)
            if m and m.group(1) in macros:
                if macros[m.group(1)] != printed:
                    print(f"[drift] {src}: built-in {printed} -> values.tex {macros[m.group(1)]} (values.tex used)")
                printed = macros[m.group(1)]
            resolved.append((k, printed, src))
        checks = resolved
    else:
        print("[note] no --values given: printed values come from the built-in table, which can drift from values.tex")
    for k, printed, src in checks:
        good = abs(v[k] - float(printed)) <= half_ulp(printed)
        rows.append((k, v[k], printed, src, good)); ok &= good
    for k, printed, src in SINGLES:
        good = abs(v[k] - float(printed)) <= half_ulp(printed)
        rows.append((k, v[k], printed, src, good)); ok &= good
    for keys, lo, hi, src in RANGES:
        vals = [v[k] for k in keys]
        good = (min(vals) >= float(lo) - half_ulp(lo)) and (max(vals) <= float(hi) + half_ulp(hi)) \
            and abs(min(vals) - float(lo)) <= half_ulp(lo) and abs(max(vals) - float(hi)) <= half_ulp(hi)
        rows.append((",".join(keys), (min(vals), max(vals)), f"{lo}--{hi}", src, good)); ok &= good
    for k, bound, src in BOUNDS:
        good = v[k] <= bound
        rows.append((k, v[k], f"<= {bound}", src, good)); ok &= good
    for k, lo, hi, src in VERBAL:
        good = lo <= v[k] <= hi
        rows.append((k, round(v[k], 3), f"[{lo}, {hi}]", src, good)); ok &= good
    good = v["n_reported"] == 205
    rows.append(("n_reported", v["n_reported"], "205", "205 reported bins", good)); ok &= good
    for k, val, printed, src, good in rows:
        print(f"[{'ok' if good else 'DISCREPANCY'}] {k}: computed {val} | printed {printed} | {src}")
    print("Fig. 2 consistency |hExcess2D - (data - comparator) x area| max:", v["fig2_excess_equals_data_minus_comparator_maxabs"])
    print("NOT COVERED:", NOT_COVERED)
    print("FIG NUMBERS:", "PASS" if ok else "DISCREPANCY")
    if a.json:
        a.json.write_text(json.dumps({"values": v, "pass": ok, "not_covered": NOT_COVERED}, indent=1, default=float) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
