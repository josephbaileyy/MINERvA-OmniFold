#!/usr/bin/env python3
"""RE-1 F: the note's printed 3D numbers on the current 3D product and on P3, by one fixed definition each.

    re1_f_numbers.py --current CUR3D.root --p3 P3.root --eu E_U.root --ec E_C.root --anc PAPER.root --out N.json

``sec_3d.tex`` prints them without a recorded producer (their source is ``3D_OMNIFOLD_STATUS.md:62-66``).
So every candidate definition below is evaluated on the CURRENT product as well. A definition is used for
P3 only where it reproduces the printed current value at its printed precision (K3 for numbers); the
others are reported and not used.

* the E_avail spectrum's first and catch-bin values (``hXSec_eavail``; printed 2.19e-38 and 6.8e-41);
* the E_avail marginal (``hXSec2D``) against a 2D reference on the reference's reported cells
  (``> 0``): total change (printed +0.95 %) and median per-cell ratio (printed 1.0016), with the
  published cross section, ``E_U`` and ``E_C`` as candidate references.

The chi^2 (printed 4.98) and the generator percentages come from the producers' own printed summaries
(``compare_to_paper_fullcov.py``, ``redraw_central_only.py``), not from here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PRINTED = {"eavail_first": "2.19e-38", "eavail_catch": "6.8e-41", "total_change_percent": "0.95", "median_ratio": "1.0016"}


def th(path: Path, name: str) -> tuple[np.ndarray, np.ndarray | None]:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name)
    if h.GetDimension() == 1:
        v = np.array([h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)])
        w = np.array([h.GetXaxis().GetBinWidth(i) for i in range(1, h.GetNbinsX() + 1)])
        out = (v, w)
    else:
        v = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
        a = np.array([[h.GetXaxis().GetBinWidth(i) * h.GetYaxis().GetBinWidth(j) for j in range(1, h.GetNbinsY() + 1)]
                      for i in range(1, h.GetNbinsX() + 1)])
        out = (v, a)
    f.Close()
    return out


def numbers(p3d: Path, refs: dict) -> dict:
    ea, _ = th(p3d, "hXSec_eavail")
    marg, area = th(p3d, "hXSec2D")
    out = {"eavail_first": float(ea[0]), "eavail_catch": float(ea[-1])}
    for name, ref in refs.items():
        cells = ref > 0
        out[f"vs_{name}"] = {
            "total_change_percent": float(100 * ((marg[cells] * area[cells]).sum() / (ref[cells] * area[cells]).sum() - 1)),
            "median_ratio": float(np.median(marg[cells] / ref[cells])), "n_cells": int(cells.sum())}
    return out


def reproduces(value: float, printed: str) -> bool:
    """The value, formatted as the note prints it (same significant digits, or same decimals), is the printed text."""
    if "e" in printed:
        mantissa = printed.split("e")[0].replace("-", "")
        return f"{value:.{len(mantissa.replace('.', '')) - 1}e}" == f"{float(printed):.{len(mantissa.replace('.', '')) - 1}e}"
    return f"{value:.{len(printed.split('.')[1])}f}" == printed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("current", "p3", "eu", "ec", "anc"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    import ROOT
    f = ROOT.TFile.Open(str(a.anc))
    h = f.Get("pt_pl_cross_section")
    paper = np.array([[h.GetBinContent(i, j) for j in range(1, 17)] for i in range(1, 15)])
    f.Close()
    refs = {"paper": paper, "E_U": th(a.eu, "hXSec2D")[0], "E_C": th(a.ec, "hXSec2D")[0]}
    cur, p3 = numbers(a.current, refs), numbers(a.p3, refs)
    k3 = {"eavail_first": reproduces(cur["eavail_first"], PRINTED["eavail_first"]),
          "eavail_catch": reproduces(cur["eavail_catch"], PRINTED["eavail_catch"])}
    for name in refs:
        for key in ("total_change_percent", "median_ratio"):
            k3[f"vs_{name}.{key}"] = reproduces(cur[f"vs_{name}"][key], PRINTED[key])
    out = {"printed": PRINTED, "current": cur, "p3": p3, "k3_reproduces_printed": k3}
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(k3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
